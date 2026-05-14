"""
Data catalog — loads shipments / fleet / warehouses / services from JSON.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


DATA_DIR = Path(__file__).parent.parent / "data"


class Catalog:
    def __init__(self):
        with open(DATA_DIR / "shipments.json", "r", encoding="utf-8") as f:
            self._shipments = json.load(f)["shipments"]
        with open(DATA_DIR / "operations.json", "r", encoding="utf-8") as f:
            ops = json.load(f)
            self._fleet = ops["fleet"]
            self._warehouses = ops["warehouses"]
        with open(DATA_DIR / "services.json", "r", encoding="utf-8") as f:
            svc = json.load(f)
            self._services = svc["services"]
            self._zones = svc["zones"]
            self._prohibited = svc["prohibited_items"]
            self._addresses = svc["address_book"]

    # ── Shipments ──────────────────────────────────────
    def shipments(self) -> list[dict]:
        return list(self._shipments)

    def shipment_by_tracking(self, tracking_number: str) -> Optional[dict]:
        tn = tracking_number.upper().strip()
        for s in self._shipments:
            if s["tracking_number"].upper() == tn:
                return s
        return None

    def active_shipment(self) -> dict:
        """First non-delivered shipment, used when no tracking number given."""
        for s in self._shipments:
            if s["status"] not in ("delivered",):
                return s
        return self._shipments[0]

    def delivered_shipment(self) -> Optional[dict]:
        for s in self._shipments:
            if s["status"] == "delivered":
                return s
        return None

    # ── Fleet & warehouses ─────────────────────────────
    def fleet(self) -> list[dict]:
        return list(self._fleet)

    def warehouses(self) -> list[dict]:
        return list(self._warehouses)

    # ── Services & zones ───────────────────────────────
    def services(self) -> list[dict]:
        return list(self._services)

    def service_by_id(self, service_id: str) -> Optional[dict]:
        for s in self._services:
            if s["id"] == service_id:
                return s
        return None

    def zones(self) -> list[dict]:
        return list(self._zones)

    def prohibited_items(self) -> list[dict]:
        return list(self._prohibited)

    def addresses(self) -> list[dict]:
        return list(self._addresses)

    # ── Quote helper ───────────────────────────────────
    def zone_for(self, origin: Optional[str], destination: Optional[str]) -> dict:
        """Pick a shipping zone from origin/destination. Defaults to National."""
        o = (origin or "").lower()
        d = (destination or "").lower()
        if any(x in d for x in ("ae", "dubai", "singapore")) or any(x in o for x in ("ae", "dubai")):
            return self._zones[4]  # International
        if not origin and not destination:
            return self._zones[2]  # National default
        if origin and destination:
            same_city = origin.split(",")[0].strip() == destination.split(",")[0].strip()
            if same_city:
                return self._zones[0]  # Intra-city
            # Gujarat-internal or neighbouring = Regional
            if ("gj" in o and "gj" in d) or ("mh" in d and "gj" in o) or ("gj" in d and "mh" in o):
                return self._zones[1]  # Regional
        return self._zones[2]  # National


catalog = Catalog()
