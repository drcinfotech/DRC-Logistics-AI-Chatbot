"""
Intent classifier for the Logistics & Transportation chatbot.

Safety detection (see safety.py) runs BEFORE this classifier.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class IntentSpec:
    name: str
    patterns: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)


INTENTS: list[IntentSpec] = [
    IntentSpec(
        "greeting",
        patterns=[r"^\s*(hi|hello|hey|hola|namaste|good (morning|afternoon|evening))\b"],
        keywords=["hi", "hello", "hey", "hola", "namaste"],
    ),
    IntentSpec(
        "goodbye",
        patterns=[r"\b(bye|goodbye|see ya|see you|cya|take care)\b"],
        keywords=["bye", "goodbye"],
    ),
    IntentSpec(
        "thanks",
        patterns=[r"^\s*(thanks|thank you|thx|ty|appreciate it)\b"],
        keywords=["thanks", "thank"],
    ),
    IntentSpec(
        "track_shipment",
        patterns=[
            r"\b(track|trace|where is|status of|locate)\b.{0,20}\b(my\s+)?(shipment|package|parcel|order|consignment|delivery|courier)\b",
            r"\btrack(ing)?\s+(number|id)?\s*[: ]?\s*nw\d+",
            r"\bnw\d{6,}\b",
            r"\bwhere'?s\s+my\s+(package|parcel|shipment|order|delivery)\b",
        ],
        keywords=["track", "tracking", "where is my", "trace shipment"],
    ),
    IntentSpec(
        "get_quote",
        patterns=[
            r"\b(quote|rate|cost|price|how much)\b.{0,30}\b(ship|send|courier|deliver|shipping|delivery)\b",
            r"\b(ship|send|courier)\b.{0,30}\b(cost|rate|price|charge)\b",
            r"\bshipping\s+(cost|rate|quote|estimate|charges?)\b",
            r"\bhow much\b.{0,20}\bto (ship|send|courier)\b",
        ],
        keywords=["quote", "shipping cost", "shipping rate", "how much to ship"],
    ),
    IntentSpec(
        "schedule_pickup",
        patterns=[
            r"\b(schedule|book|arrange|request|set up)\b.{0,20}\b(a\s+)?pickup\b",
            r"\bpickup\b.{0,20}\b(scheduled|booking|request)\b",
            r"\b(collect|pick up)\b.{0,20}\b(my\s+)?(package|parcel|shipment|order)\b",
        ],
        keywords=["schedule pickup", "book pickup", "arrange pickup", "request pickup"],
    ),
    IntentSpec(
        "delivery_estimate",
        patterns=[
            r"\b(when will|what time|how long|eta|estimated)\b.{0,30}\b(deliver|arrive|reach|get here)\b",
            r"\bdelivery\s+(estimate|time|date|eta)\b",
            r"\bwhen\s+(is|will)\b.{0,20}\b(it|my (package|parcel|shipment|order))\b.{0,15}\barrive\b",
        ],
        keywords=["delivery estimate", "eta", "when will it arrive", "delivery time"],
    ),
    IntentSpec(
        "service_options",
        patterns=[
            r"\b(service|shipping|delivery)\s+(options?|types?|tiers?|plans?|levels?)\b",
            r"\b(express|standard|freight|same.?day)\b.{0,20}\b(vs|versus|or|compare|difference)\b",
            r"\bwhat\s+(services|shipping options)\b.{0,15}\b(do you|are there|available)\b",
            r"\bcompare\s+(shipping|delivery|service)\b",
        ],
        keywords=["service options", "shipping options", "compare services", "delivery types"],
    ),
    IntentSpec(
        "fleet_status",
        patterns=[
            r"\b(fleet|vehicle|truck|van|driver)\s+(status|location|tracking|overview)\b",
            r"\bwhere\s+(are|is)\b.{0,15}\b(my\s+)?(trucks?|vehicles?|drivers?|fleet)\b",
            r"\b(show|view)\b.{0,15}\b(the\s+)?(fleet|vehicles?|trucks?|drivers?)\b",
        ],
        keywords=["fleet status", "vehicle location", "where are my trucks", "driver status"],
    ),
    IntentSpec(
        "warehouse_inventory",
        patterns=[
            r"\b(warehouse|inventory|stock|fulfilment|fulfillment)\s+(status|level|capacity|overview|utilization|utilisation)\b",
            r"\b(show|view|check)\b.{0,15}\b(the\s+)?(warehouse|inventory|stock levels?)\b",
            r"\bhow\s+(full|much capacity)\b.{0,20}\bwarehouse\b",
        ],
        keywords=["warehouse", "inventory", "stock levels", "warehouse capacity"],
    ),
    IntentSpec(
        "file_claim",
        patterns=[
            r"\b(file|raise|submit|open|start)\b.{0,15}\b(a\s+)?claim\b",
            r"\b(my\s+)?(package|parcel|shipment|order)\b.{0,20}\b(damaged|broken|lost|missing|stolen|never arrived)\b",
            r"\b(damaged|broken|lost|missing)\b.{0,20}\b(package|parcel|shipment|delivery)\b",
            r"\breport\b.{0,15}\b(damage|loss|missing)\b",
        ],
        keywords=["file claim", "damaged package", "lost shipment", "missing parcel"],
    ),
    IntentSpec(
        "proof_of_delivery",
        patterns=[
            r"\bproof\s+of\s+delivery\b",
            r"\b(pod|delivery\s+(proof|receipt|confirmation|signature))\b",
            r"\bwho\s+(signed|received|got)\b.{0,20}\b(my\s+)?(package|parcel|delivery)\b",
            r"\bwas\s+(it|my (package|parcel|shipment))\s+delivered\b",
        ],
        keywords=["proof of delivery", "pod", "delivery signature", "who signed"],
    ),
    IntentSpec(
        "shipment_history",
        patterns=[
            r"\b(my|all|recent|past|previous)\s+shipments?\b",
            r"\bshipment\s+history\b",
            r"\b(show|view|list)\b.{0,15}\b(my\s+)?(shipments?|orders?|deliveries|packages)\b",
        ],
        keywords=["my shipments", "shipment history", "all my packages", "recent orders"],
    ),
    IntentSpec(
        "customs_info",
        patterns=[
            r"\bcustoms?\b.{0,20}\b(duty|duties|clearance|charges?|fee|documents?|info)\b",
            r"\b(import|export)\s+(duty|duties|tax|clearance|documents?)\b",
            r"\b(international|cross.?border|overseas)\s+(shipping|shipment|delivery)\b.{0,20}\b(duty|customs|tax|cost)\b",
            r"\bduty\s+(estimate|calculator|charges?)\b",
        ],
        keywords=["customs", "import duty", "export documents", "customs clearance"],
    ),
    IntentSpec(
        "reroute_shipment",
        patterns=[
            r"\b(reroute|redirect|divert|change\s+(the\s+)?(delivery\s+)?address)\b.{0,20}\b(my\s+)?(shipment|package|parcel|order|delivery)\b",
            r"\b(hold|pause|reschedule)\b.{0,15}\b(my\s+)?(shipment|package|parcel|delivery)\b",
            r"\bchange\b.{0,15}\bwhere\b.{0,20}\b(deliver|delivered)\b",
            r"\bdeliver\b.{0,15}\bto\s+a\s+different\b",
        ],
        keywords=["reroute", "redirect package", "change delivery address", "hold shipment"],
    ),
    IntentSpec(
        "prohibited_items_info",
        patterns=[
            r"\bwhat\s+(can'?t|cannot|can not|am i not allowed to)\b.{0,15}\b(ship|send|courier|mail)\b",
            r"\b(prohibited|restricted|banned|not allowed|forbidden)\b.{0,15}\b(items?|goods?|things?)\b",
            r"\b(items?|goods?|things?)\b.{0,15}\b(are\s+)?(prohibited|restricted|banned|forbidden|not allowed)\b",
            r"\b(prohibited|restricted|banned|forbidden)\b.{0,15}\bto\s+(ship|send|courier|mail)\b",
            r"\b(can|am i allowed to)\b.{0,15}\b(ship|send)\b.{0,25}\b(allowed|prohibited|restricted)\b",
            r"\bdangerous\s+goods\s+(policy|list|rules)\b",
        ],
        keywords=["prohibited items", "what can't i ship", "restricted goods", "banned items"],
    ),
    IntentSpec(
        "talk_to_human",
        patterns=[
            r"\b(speak|talk|connect|chat)\s+to\s+(a\s+)?(human|agent|person|representative|someone|support)\b",
            r"\b(real|live)\s+(person|agent|human)\b",
            r"\bcustomer\s+(care|support|service)\b",
        ],
        keywords=["human", "agent", "customer care", "speak to someone"],
    ),
]


# ─── Entity extraction ─────────────────────────────────────
CITY_ALIASES = {
    "surat": "Surat, GJ", "mumbai": "Mumbai, MH", "bombay": "Mumbai, MH",
    "delhi": "Delhi, DL", "new delhi": "Delhi, DL", "bengaluru": "Bengaluru, KA",
    "bangalore": "Bengaluru, KA", "chennai": "Chennai, TN", "kolkata": "Kolkata, WB",
    "ahmedabad": "Ahmedabad, GJ", "pune": "Pune, MH", "hyderabad": "Hyderabad, TS",
    "jaipur": "Jaipur, RJ", "dubai": "Dubai, AE", "singapore": "Singapore",
    "vadodara": "Vadodara, GJ", "nagpur": "Nagpur, MH",
}

SERVICE_ALIASES = {
    "same_day":      ["same day", "same-day", "sameday"],
    "express":       ["express", "priority", "fast", "fastest", "urgent"],
    "standard":      ["standard", "surface", "economy", "regular", "cheapest"],
    "freight":       ["freight", "ltl", "pallet", "bulk", "heavy"],
    "international": ["international", "overseas", "cross border", "cross-border", "abroad"],
}

TRACKING_RE = re.compile(r"\b(NW\d{6,})\b", re.IGNORECASE)
WEIGHT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(kg|kgs|kilo|kilos|kilogram|g|gram|grams)\b", re.IGNORECASE)


def extract_tracking_number(text: str) -> Optional[str]:
    m = TRACKING_RE.search(text)
    return m.group(1).upper() if m else None


def extract_cities(text: str) -> tuple[Optional[str], Optional[str]]:
    """Extract (origin, destination) from 'from X to Y' or 'X to Y' phrasing."""
    t = text.lower()
    origin = destination = None

    m = re.search(r"from\s+([a-z ]+?)\s+to\s+([a-z ]+?)(?:[,.]|$|\s+(?:by|with|via|for|using))", t)
    if not m:
        m = re.search(r"\b([a-z]+)\s+to\s+([a-z]+)\b", t)
    if m:
        o_raw = m.group(1).strip()
        d_raw = m.group(2).strip()
        for alias, full in CITY_ALIASES.items():
            if alias in o_raw:
                origin = full
            if alias in d_raw:
                destination = full

    # Fallback: any single city mention as destination
    if not destination:
        for alias, full in CITY_ALIASES.items():
            if re.search(rf"\bto\s+{alias}\b", t):
                destination = full
    return origin, destination


def extract_weight(text: str) -> Optional[float]:
    m = WEIGHT_RE.search(text)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2).lower()
    if unit.startswith("g"):
        return round(val / 1000, 3)
    return val


def extract_service(text: str) -> Optional[str]:
    t = text.lower()
    for key, words in SERVICE_ALIASES.items():
        if any(w in t for w in words):
            return key
    return None


# ─── Classifier ────────────────────────────────────────────
@dataclass
class Classification:
    intent: str
    confidence: float
    entities: dict


def classify(text: str) -> Classification:
    raw = text
    text_lc = text.lower().strip()

    scores: dict[str, float] = {}
    for spec in INTENTS:
        score = 0.0
        for p in spec.patterns:
            if re.search(p, text_lc, re.IGNORECASE):
                score += 2.0
        for kw in spec.keywords:
            if re.search(rf"\b{re.escape(kw)}\b", text_lc):
                score += 0.6
        if score > 0:
            scores[spec.name] = score

    if not scores:
        intent, conf = "unknown", 0.0
    else:
        intent = max(scores, key=scores.get)
        top = scores[intent]
        rest = sorted(scores.values(), reverse=True)[1] if len(scores) > 1 else 0.1
        conf = min(1.0, top / (top + rest))

    origin, destination = extract_cities(raw)
    entities = {
        "tracking_number": extract_tracking_number(raw),
        "origin":          origin,
        "destination":     destination,
        "weight_kg":       extract_weight(raw),
        "service":         extract_service(raw),
    }
    return Classification(intent=intent, confidence=round(conf, 2), entities=entities)
