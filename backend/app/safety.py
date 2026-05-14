"""
Safety layer — runs BEFORE intent classification.

In a logistics chatbot, the domain-specific harms are:
  • Shipping prohibited / dangerous goods (explosives, weapons, narcotics, hazmat)
  • Privacy breaches — leaking another person's address, or letting someone
    redirect / track a parcel they don't own
  • Prompt-injection / social-engineering attempts against the assistant

This module screens for these patterns and short-circuits to a safe response
that refuses to help, explains why, and points to the right channel.

Conservative by design — for prohibited goods and privacy, a false positive
just means we ask the user to clarify with a human; a false negative could
mean facilitating something genuinely dangerous or unlawful.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Literal


@dataclass
class SafetyResult:
    flag: Optional[Literal["prohibited", "privacy", "social_engineering"]]
    reason: str = ""


# ─── Prohibited / dangerous goods ──────────────────────────
# Detects requests to SHIP items that are banned or restricted on
# standard logistics networks. Note the `s?` suffixes — plurals would
# otherwise break the trailing word boundary.
PROHIBITED_PATTERNS = [
    # Explosives & pyrotechnics
    r"\b(ship|send|courier|deliver|transport|mail|move)\b.{0,40}\b(explosives?|dynamite|detonators?|tnt|grenades?|fireworks?|firecrackers?|cracker bombs?|blasting)\b",
    r"\b(explosives?|dynamite|detonators?|grenades?|fireworks?)\b.{0,30}\b(ship|send|courier|deliver|transport)\b",
    # Weapons & ammunition
    r"\b(ship|send|courier|deliver|transport|mail|move)\b.{0,40}\b(guns?|hand-?guns?|shot-?guns?|firearms?|pistols?|revolvers?|rifles?|weapons?|ammunition|ammo|bullets?|live rounds?)\b",
    r"\b(guns?|hand-?guns?|shot-?guns?|firearms?|pistols?|revolvers?|rifles?|weapons?|ammunition)\b.{0,30}\b(ship|send|courier|deliver|transport|mail|move)\b",
    # Drugs & narcotics
    r"\b(ship|send|courier|deliver|transport|mail|smuggle|move)\b.{0,40}\b(cocaine|heroin|mdma|meth|methamphetamine|narcotics?|illegal drugs?|drugs?|ganja|charas|contraband)\b",
    r"\b(smuggle|traffic|trafficking)\b.{0,30}\b(drugs?|narcotics?|contraband|substances?)\b",
    # Hazmat / dangerous goods
    r"\b(ship|send|courier|deliver|transport)\b.{0,40}\b(radioactive|toxic gas|poison gas|nerve agents?|corrosive acids?|hazardous chemicals?)\b",
    # Wildlife
    r"\b(ship|send|courier|deliver|transport|smuggle)\b.{0,40}\b(ivory|rhino horns?|tiger skins?|pangolins?|endangered animals?|protected species)\b",
    # Concealment intent — strong signal regardless of item
    r"\b(hide|conceal|disguise|mislabel|misdeclare|mis-?declare)\b.{0,40}\b(packages?|parcels?|shipments?|contents?|consignments?)\b",
    r"\bship\b.{0,30}\bwithout\b.{0,20}\b(declaring|declaration|customs|inspection)\b",
    r"\bget\b.{0,20}\b(past|around|through)\b.{0,15}\b(customs|x-?ray|scanner|inspection)\b",
]

# ─── Privacy / security ────────────────────────────────────
# Detects attempts to access OTHER people's shipment data, or to
# redirect parcels that aren't the user's.
PRIVACY_PATTERNS = [
    r"\b(track|find|locate|check)\b.{0,30}\b(someone else'?s|somebody else'?s|other person'?s|another person'?s|my (ex|neighbou?r|friend'?s|colleague'?s))\b.{0,20}\b(package|parcel|shipment|order|delivery)\b",
    r"\b(track|find|locate)\b.{0,20}\b(my (ex|neighbou?r|friend|colleague|boss))\b",
    r"\b(home |residential )?address\b.{0,30}\b(of the (recipient|sender|customer|person)|for tracking|for this parcel|behind tracking)\b",
    r"\bwho (lives|stays) at\b",
    r"\bwhere does\b.{0,30}\b(the recipient|the customer|this person|he|she|they)\b.{0,10}\blive\b",
    r"\b(reroute|redirect|divert|change.{0,15}address)\b.{0,40}\b(someone else'?s|somebody else'?s|another|not mine|isn'?t mine|that isn'?t)\b",
    r"\b(reroute|redirect|divert)\b.{0,30}\bwithout\b.{0,20}\b(them knowing|their knowledge|telling them|notifying)\b",
    r"\bgive me\b.{0,20}\b(the )?(phone number|contact|personal details)\b.{0,20}\b(of the (recipient|sender|customer)|behind)\b",
]

# ─── Social engineering / prompt injection ─────────────────
SOCIAL_ENGINEERING_PATTERNS = [
    r"\b(ignore|disregard|forget)\s+(\w+\s+){0,4}(instructions|rules|guidelines|system\s+prompt)",
    r"\byou\s+are\s+now\s+(in\s+|an?\s+)?(admin|administrator|dev|developer|debug|root)\s+(mode|user)?",
    r"\bpretend\s+(you\s+are|to\s+be)\s+(an?\s+)?(admin|root|developer)\b",
    r"\b(give|provide|reveal|show|tell)\s+(me\s+)?(your\s+)?(system\s+prompt|instructions|api\s+key|source\s+code)",
    r"\benable\s+(developer|admin|debug|root)\s+mode\b",
    r"\bjailbreak\b",
    r"\bDAN\s+mode\b",
]


def check_safety(text: str) -> SafetyResult:
    text_lc = text.lower()

    for pat in SOCIAL_ENGINEERING_PATTERNS:
        if re.search(pat, text_lc):
            return SafetyResult(flag="social_engineering", reason=pat)

    for pat in PROHIBITED_PATTERNS:
        if re.search(pat, text_lc):
            return SafetyResult(flag="prohibited", reason=pat)

    for pat in PRIVACY_PATTERNS:
        if re.search(pat, text_lc):
            return SafetyResult(flag="privacy", reason=pat)

    return SafetyResult(flag=None)


def build_prohibited_block() -> dict:
    return {
        "type": "prohibited_alert",
        "headline": "I can't help arrange that shipment.",
        "message": (
            "What you've described looks like a prohibited or dangerous-goods item. These can't be "
            "moved on standard logistics networks — for safety reasons and under transport law. "
            "I won't help package, label, or route anything that falls into these categories."
        ),
        "indicators": [
            "Explosives, fireworks, weapons, and ammunition are banned outright",
            "Narcotics and other controlled substances are illegal to ship",
            "Hazardous chemicals and radioactive material need a licensed dangerous-goods carrier",
            "Mislabelling or concealing contents to get past inspection is a serious offence",
        ],
        "contact": {
            "label": "Dangerous Goods team",
            "detail": "For genuinely regulated goods (e.g. certain batteries, chemicals), our certified DG desk can advise on whether a compliant shipping option exists.",
        },
    }


def build_privacy_block() -> dict:
    return {
        "type": "prohibited_alert",
        "headline": "I can't share that — it's someone else's information.",
        "message": (
            "I can only help with shipments tied to your own account. I won't look up another "
            "person's address or contact details, and I can't reroute or track a parcel that "
            "isn't yours. This protects everyone's privacy and safety."
        ),
        "indicators": [
            "Recipient and sender addresses are private to the parties on that shipment",
            "Only the account holder can reroute or redirect their own parcel",
            "If you're expecting a delivery, I can track it using your account",
            "For a genuine dispute, our support team can verify identity and help properly",
        ],
        "contact": {
            "label": "Customer support",
            "detail": "If you believe you have a legitimate reason to access this shipment, our team can verify your identity and assist.",
        },
    }


def build_social_engineering_block() -> dict:
    return {
        "type": "prohibited_alert",
        "headline": "I can't do that.",
        "message": (
            "I'm not able to bypass my instructions, switch into a different 'mode', or reveal "
            "internal configuration. If you have a genuine logistics need — tracking, quotes, "
            "pickups, claims — I'm glad to help with that instead."
        ),
        "indicators": [
            "I can track shipments, quote rates, schedule pickups, and file claims",
            "I can show fleet status and warehouse capacity for your operations",
            "I can't change my own rules or act outside them",
        ],
        "contact": {
            "label": "Support team",
            "detail": "A human agent can help with anything outside what I'm able to do.",
        },
    }
