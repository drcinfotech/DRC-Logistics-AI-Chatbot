"""
Logistics chatbot engine.

Flow:
  1. Safety check first — prohibited goods, privacy breaches, and
     social-engineering attempts short-circuit to a safe response
  2. Otherwise, classify intent
  3. Dispatch to handler
  4. Return rich blocks

The engine NEVER:
  • Helps ship prohibited or dangerous goods
  • Reveals another person's address or contact details
  • Reroutes / tracks a parcel that isn't the user's
  • Acts on social-engineering attempts

The engine ALWAYS:
  • Treats quotes, ETAs, and customs figures as estimates (with a disclaimer)
  • Keeps the user's own shipment data scoped to their session
  • Offers a human handoff for anything outside its scope
"""
from __future__ import annotations

import secrets

from .catalog import catalog
from .intents import Classification, classify
from .safety import (
    check_safety,
    build_prohibited_block,
    build_privacy_block,
    build_social_engineering_block,
)
from .sessions import Session


# ─── Block builders ────────────────────────────────────────
def _text(content: str) -> dict:
    return {"type": "text", "content": content}


def _disclaimer(content: str) -> dict:
    return {"type": "disclaimer", "content": content}


# ─── Intent handlers ───────────────────────────────────────
def _handle_greeting(_s: Session):
    return [
        _text(
            "Hi, I'm Routara — your logistics companion. I can track shipments, quote shipping rates, "
            "schedule pickups, check fleet and warehouse status, file claims, and more. "
            "What would you like to do?"
        )
    ], ["Track a shipment", "Get a shipping quote", "My shipments", "Service options"]


def _handle_goodbye(_s: Session):
    return [_text("Safe travels — and I'll keep an eye on your shipments.")], []


def _handle_thanks(_s: Session):
    return [_text("Happy to help! Anything else on the logistics front?")], \
           ["Track a shipment", "Schedule a pickup", "Fleet status"]


def _handle_track_shipment(c: Classification, s: Session):
    tn = c.entities.get("tracking_number") or s.last_tracking_number
    shipment = catalog.shipment_by_tracking(tn) if tn else None

    if tn and not shipment:
        return [
            _text(
                f"I couldn't find a shipment with tracking number **{tn}**. "
                "Double-check the number, or I can show you all shipments on your account."
            )
        ], ["Show my shipments", "Try another number", "Talk to a human"]

    if not shipment:
        shipment = catalog.active_shipment()

    s.last_tracking_number = shipment["tracking_number"]

    blocks = [
        _text(
            f"Here's the latest on **{shipment['tracking_number']}** "
            f"({shipment['origin_city']} → {shipment['destination_city']}). "
            f"Status: **{shipment['status_label']}** · ETA: {shipment['estimated_delivery']}."
        ),
        {"type": "shipment_tracking", "shipment": shipment},
        {
            "type": "route_map",
            "tracking_number": shipment["tracking_number"],
            "origin_city": shipment["origin_city"],
            "destination_city": shipment["destination_city"],
            "nodes": shipment["route"],
        },
    ]
    if shipment["status"] == "exception":
        blocks.append(_disclaimer(
            "This shipment has a delivery exception. Revised ETAs are best estimates and may shift "
            "again depending on conditions. You can file a claim if it's significantly delayed."
        ))
    return blocks, ["Delivery estimate", "Proof of delivery", "File a claim", "Reroute this shipment"]


def _handle_get_quote(c: Classification, _s: Session):
    origin = c.entities.get("origin") or "Surat, GJ"
    destination = c.entities.get("destination") or "Bengaluru, KA"
    weight = c.entities.get("weight_kg") or 5.0
    service_id = c.entities.get("service") or "express"

    service = catalog.service_by_id(service_id) or catalog.service_by_id("express")
    zone = catalog.zone_for(c.entities.get("origin"), c.entities.get("destination"))

    base = service["base_rate"] * zone["multiplier"]
    weight_charge = service["per_kg"] * weight * zone["multiplier"]
    subtotal = base + weight_charge
    fuel = round(subtotal * 0.08, 2)
    gst = round((subtotal + fuel) * 0.18, 2)
    total = round(subtotal + fuel + gst, 2)

    blocks = [
        _text(
            f"Here's an estimated **{service['name']}** quote for {weight} kg, "
            f"{origin} → {destination} ({zone['name']} zone):"
        ),
        {
            "type": "quote",
            "quote": {
                "origin": origin,
                "destination": destination,
                "weight_kg": weight,
                "zone": zone["name"],
                "service_name": service["name"],
                "transit": service["transit"],
                "base_rate": round(base, 2),
                "weight_charge": round(weight_charge, 2),
                "fuel_surcharge": fuel,
                "gst": gst,
                "total": total,
            },
        },
        _disclaimer(
            "This is an indicative estimate. Final charges depend on actual weight/volumetric weight, "
            "exact pin codes, packaging, and any surcharges (remote area, fuel, handling). "
            "GST is calculated at 18%."
        ),
    ]
    return blocks, ["Compare service options", "Schedule a pickup", "Change weight", "International rates"]


def _handle_schedule_pickup(_c: Classification, _s: Session):
    addresses = catalog.addresses()
    default_addr = next((a for a in addresses if a["default"]), addresses[0])
    addr_str = f"{default_addr['label']} — {default_addr['line']}, {default_addr['city']} {default_addr['pincode']}"

    blocks = [
        _text(
            "I can set up a pickup. In this demo I won't dispatch a real courier, but here's how "
            "a pickup booking looks — using your default address:"
        ),
        {
            "type": "pickup",
            "confirmation": {
                "pickup_id": "PU-" + secrets.token_hex(3).upper(),
                "address": addr_str,
                "window": "Tomorrow, 10:00 AM – 1:00 PM",
                "service": "Express",
                "estimated_items": "1–3 parcels",
                "status": "Demo — not dispatched",
            },
        },
        _disclaimer(
            "For a real pickup, you'd confirm the address, parcel count, approximate weight, and a "
            "time window. Pickups booked before 3 PM are usually serviced the next working day."
        ),
    ]
    return blocks, ["Change pickup address", "Change time window", "Get a quote first", "My addresses"]


def _handle_delivery_estimate(c: Classification, s: Session):
    tn = c.entities.get("tracking_number") or s.last_tracking_number
    shipment = catalog.shipment_by_tracking(tn) if tn else None
    if not shipment:
        shipment = catalog.active_shipment()
    s.last_tracking_number = shipment["tracking_number"]

    confidence = "Lower — delivery exception in play" if shipment["status"] == "exception" else "High"

    blocks = [
        _text(f"Here's the delivery estimate for **{shipment['tracking_number']}**:"),
        {
            "type": "eta",
            "result": {
                "tracking_number": shipment["tracking_number"],
                "destination_city": shipment["destination_city"],
                "estimated_delivery": shipment["estimated_delivery"],
                "current_location": shipment["current_location"],
                "status_label": shipment["status_label"],
                "confidence": confidence,
            },
        },
    ]
    if shipment["status"] == "exception":
        blocks.append(_disclaimer(
            "Estimates for delayed shipments are less certain. If it slips past the revised window, "
            "you can file a claim and I'll start that for you."
        ))
    return blocks, ["Track full timeline", "File a claim", "Reroute this shipment", "Talk to a human"]


def _handle_service_options(_c: Classification, _s: Session):
    services = catalog.services()
    blocks = [
        _text("Here are the service tiers, from fastest to most economical for heavy freight:"),
        {"type": "service_options", "items": services},
        _disclaimer(
            "Transit times are business-day estimates for typical lanes and exclude customs hold time "
            "on international shipments. Rates shown elsewhere are zone-adjusted."
        ),
    ]
    return blocks, ["Get an Express quote", "Get a Standard quote", "Freight for heavy goods", "International shipping"]


def _handle_fleet_status(_c: Classification, _s: Session):
    fleet = catalog.fleet()
    en_route = sum(1 for v in fleet if v["status"] in ("en_route", "out_for_delivery"))
    blocks = [
        _text(
            f"Here's your fleet overview — **{en_route} of {len(fleet)} vehicles** are currently active "
            "on the road:"
        ),
        {"type": "fleet", "items": fleet},
    ]
    return blocks, ["Warehouse status", "Assign idle vehicle", "Vehicle in maintenance", "Talk to dispatch"]


def _handle_warehouse_inventory(_c: Classification, _s: Session):
    warehouses = catalog.warehouses()
    avg_util = round(sum(w["used_pct"] for w in warehouses) / len(warehouses))
    blocks = [
        _text(
            f"Here's the warehouse network — **average utilisation is {avg_util}%**. "
            "Bengaluru and Mumbai are running hot:"
        ),
        {"type": "warehouse", "items": warehouses},
    ]
    return blocks, ["Fleet status", "Rebalance stock", "Capacity alerts", "Talk to operations"]


def _handle_file_claim(c: Classification, s: Session):
    tn = c.entities.get("tracking_number") or s.last_tracking_number
    shipment = catalog.shipment_by_tracking(tn) if tn else None
    if not shipment:
        shipment = catalog.active_shipment()

    issue_type = "Delivery delay"
    if shipment["status"] == "exception":
        issue_type = "Delivery delay (weather exception)"

    blocks = [
        _text(
            f"I've started a claim for **{shipment['tracking_number']}**. In this demo it isn't "
            "actually submitted, but here's how the claim record looks:"
        ),
        {
            "type": "claim",
            "confirmation": {
                "claim_id": "CLM-" + secrets.token_hex(3).upper(),
                "tracking_number": shipment["tracking_number"],
                "issue_type": issue_type,
                "status": "Demo — not submitted",
                "next_step": "Upload photos / invoice, then a claims agent reviews within 2 working days",
                "resolution_eta": "5–7 working days after documents are verified",
            },
        },
        _disclaimer(
            "Real claims need supporting documents — photos of damage, the original invoice, and the "
            "packaging. Claim payouts are capped at the declared value unless additional insurance was purchased."
        ),
    ]
    return blocks, ["Upload documents", "Check claim status", "Track the shipment", "Talk to a human"]


def _handle_proof_of_delivery(c: Classification, s: Session):
    tn = c.entities.get("tracking_number") or s.last_tracking_number
    shipment = catalog.shipment_by_tracking(tn) if tn else None

    # POD only exists for delivered shipments
    if not shipment or not shipment.get("pod"):
        delivered = catalog.delivered_shipment()
        if delivered:
            shipment = delivered
        else:
            return [_text(
                "None of your current shipments have been delivered yet, so there's no proof of "
                "delivery available. I can track an in-progress shipment instead."
            )], ["Track a shipment", "My shipments", "Delivery estimate"]

    s.last_tracking_number = shipment["tracking_number"]
    blocks = [
        _text(f"Here's the proof of delivery for **{shipment['tracking_number']}**:"),
        {
            "type": "proof_of_delivery",
            "tracking_number": shipment["tracking_number"],
            "service": shipment["service"],
            "origin_city": shipment["origin_city"],
            "destination_city": shipment["destination_city"],
            "pod": shipment["pod"],
        },
    ]
    return blocks, ["Track another shipment", "My shipments", "Download receipt", "File a claim"]


def _handle_shipment_history(_c: Classification, _s: Session):
    shipments = catalog.shipments()
    active = sum(1 for s in shipments if s["status"] != "delivered")
    blocks = [
        _text(
            f"Here are all shipments on your account — **{active} active**, "
            f"{len(shipments) - active} delivered:"
        ),
        {"type": "shipment_list", "items": shipments},
    ]
    return blocks, ["Track a specific shipment", "File a claim", "Schedule a pickup", "Get a quote"]


def _handle_customs_info(c: Classification, _s: Session):
    destination = c.entities.get("destination") or "Dubai, AE"
    declared = 25000.0
    duty = round(declared * 0.05, 2)
    vat = round((declared + duty) * 0.05, 2)
    clearance = 750.0
    total = round(declared + duty + vat + clearance, 2)

    blocks = [
        _text(
            f"Here's an indicative customs breakdown for an international shipment to **{destination}** "
            f"with a declared value of ₹{declared:,.0f}:"
        ),
        {
            "type": "customs",
            "breakdown": {
                "destination": destination,
                "declared_value": declared,
                "duty_estimate": duty,
                "vat_estimate": vat,
                "clearance_fee": clearance,
                "total_landed_cost": total,
                "documents": [
                    "Commercial invoice (3 copies)",
                    "Packing list",
                    "KYC of sender & consignee",
                    "Export declaration / shipping bill",
                    "Certificate of origin (if claiming preferential duty)",
                ],
            },
        },
        _disclaimer(
            "Duty and tax rates vary by destination country, product HS code, and trade agreements. "
            "This is a rough estimate only — the destination customs authority sets the final amount. "
            "Restricted or licensed goods may need additional permits."
        ),
    ]
    return blocks, ["International rate quote", "Required documents", "Restricted for export?", "Talk to a human"]


def _handle_reroute_shipment(c: Classification, s: Session):
    tn = c.entities.get("tracking_number") or s.last_tracking_number
    shipment = catalog.shipment_by_tracking(tn) if tn else None
    if not shipment:
        shipment = catalog.active_shipment()
    s.last_tracking_number = shipment["tracking_number"]

    if shipment["status"] in ("delivered",):
        return [_text(
            f"Shipment **{shipment['tracking_number']}** has already been delivered, so it can't be "
            "rerouted. I can help with a different shipment if you like."
        )], ["My shipments", "Track a shipment", "Schedule a pickup"]

    if shipment["status"] == "out_for_delivery":
        blocks = [
            _text(
                f"**{shipment['tracking_number']}** is already out for delivery, so rerouting options "
                "are limited. You can usually still request a hold for pickup at the destination hub, "
                "or a redelivery to the same address."
            ),
            _disclaimer(
                "Once a parcel is out for delivery, address changes generally aren't possible. "
                "A hold-at-hub or next-day redelivery is the safer option."
            ),
        ]
        return blocks, ["Hold at destination hub", "Request redelivery", "Track this shipment", "Talk to a human"]

    blocks = [
        _text(
            f"I can set up a reroute for **{shipment['tracking_number']}**, currently at "
            f"{shipment['current_location']}. In this demo nothing actually changes, but you'd be able to:\n"
            "• Redirect to another of **your** saved addresses\n"
            "• Hold the parcel at the destination hub for self-pickup\n"
            "• Reschedule the delivery date"
        ),
        _disclaimer(
            "Reroutes are only allowed to addresses on your own account, and may add 1 working day plus "
            "a small redirection fee. A parcel can't be redirected to a third party you don't control."
        ),
    ]
    return blocks, ["Redirect to my office", "Hold at hub", "Reschedule delivery", "My addresses"]


def _handle_prohibited_items_info(_c: Classification, _s: Session):
    items = catalog.prohibited_items()
    # Render as a readable text summary (educational, not the red alert block)
    lines = "\n".join(f"• **{it['category']}** — {it['note']}" for it in items)
    blocks = [
        _text(
            "Here's a summary of items that are **prohibited or restricted** on our network. "
            "If you're unsure about something specific, our Dangerous Goods desk can advise:"
        ),
        _text(lines),
        _disclaimer(
            "This list is a guide, not exhaustive. Some 'restricted' items can still be shipped with the "
            "right packaging, documentation, and service — others are banned outright by law. When in "
            "doubt, ask before you pack."
        ),
    ]
    return blocks, ["Can I ship a laptop battery?", "Dangerous Goods desk", "Get a quote", "Service options"]


def _handle_talk_to_human(_c: Classification, _s: Session):
    return [_text(
        "Sure — I can connect you to the right team. Typical wait is around 3 minutes. "
        "Who would you like to reach?"
    )], ["Customer support", "Dispatch / operations", "Claims team", "Dangerous Goods desk"]


def _handle_unknown(_c: Classification, _s: Session):
    blocks = [_text(
        "I'm not quite sure what you meant there. I'm best at tracking shipments, quoting rates, "
        "scheduling pickups, checking fleet and warehouse status, customs info, and claims. "
        "Could you rephrase, or pick one below?"
    )]
    return blocks, ["Track a shipment", "Get a quote", "My shipments", "Talk to a human"]


# ─── Engine ────────────────────────────────────────────────
class ChatbotEngine:
    def respond(self, message: str, session: Session) -> dict:
        # 1️⃣ Safety check first
        safety = check_safety(message)
        if safety.flag == "prohibited":
            return {
                "session_id": session.session_id,
                "intent": "prohibited_blocked",
                "confidence": 1.0,
                "blocks": [build_prohibited_block()],
                "suggestions": ["What can I ship?", "Dangerous Goods desk", "Service options"],
                "safety_flag": "prohibited",
            }
        if safety.flag == "privacy":
            return {
                "session_id": session.session_id,
                "intent": "privacy_blocked",
                "confidence": 1.0,
                "blocks": [build_privacy_block()],
                "suggestions": ["Track my own shipment", "My shipments", "Talk to a human"],
                "safety_flag": "privacy",
            }
        if safety.flag == "social_engineering":
            return {
                "session_id": session.session_id,
                "intent": "social_engineering_blocked",
                "confidence": 1.0,
                "blocks": [build_social_engineering_block()],
                "suggestions": ["Track a shipment", "Get a quote", "Service options"],
                "safety_flag": "social_engineering",
            }

        # 2️⃣ Classify intent
        c = classify(message)
        session.last_intent = c.intent
        session.history.append({"role": "user", "text": message})

        handler_map = {
            "greeting":               lambda: _handle_greeting(session),
            "goodbye":                lambda: _handle_goodbye(session),
            "thanks":                 lambda: _handle_thanks(session),
            "track_shipment":         lambda: _handle_track_shipment(c, session),
            "get_quote":              lambda: _handle_get_quote(c, session),
            "schedule_pickup":        lambda: _handle_schedule_pickup(c, session),
            "delivery_estimate":      lambda: _handle_delivery_estimate(c, session),
            "service_options":        lambda: _handle_service_options(c, session),
            "fleet_status":           lambda: _handle_fleet_status(c, session),
            "warehouse_inventory":    lambda: _handle_warehouse_inventory(c, session),
            "file_claim":             lambda: _handle_file_claim(c, session),
            "proof_of_delivery":      lambda: _handle_proof_of_delivery(c, session),
            "shipment_history":       lambda: _handle_shipment_history(c, session),
            "customs_info":           lambda: _handle_customs_info(c, session),
            "reroute_shipment":       lambda: _handle_reroute_shipment(c, session),
            "prohibited_items_info":  lambda: _handle_prohibited_items_info(c, session),
            "talk_to_human":          lambda: _handle_talk_to_human(c, session),
        }
        handler = handler_map.get(c.intent, lambda: _handle_unknown(c, session))
        blocks, suggestions = handler()

        bot_text = " | ".join(b.get("content", "") for b in blocks if b.get("type") == "text")
        session.history.append({"role": "bot", "text": bot_text})

        return {
            "session_id":  session.session_id,
            "intent":      c.intent,
            "confidence":  c.confidence,
            "blocks":      blocks,
            "suggestions": suggestions,
            "safety_flag": None,
        }


engine = ChatbotEngine()
