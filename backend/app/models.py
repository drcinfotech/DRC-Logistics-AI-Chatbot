"""
Pydantic models for the Logistics & Transportation chatbot.
"""
from __future__ import annotations

from typing import Optional, Literal
from pydantic import BaseModel, Field


# ─── Request ───────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)
    session_id: Optional[str] = None


# ─── Domain entities ───────────────────────────────────────
class TimelineEvent(BaseModel):
    label: str
    location: str
    timestamp: str
    done: bool
    exception: bool = False


class RouteNode(BaseModel):
    label: str
    type: Literal["origin", "hub", "transit", "destination"]
    done: bool
    exception: bool = False


class ProofOfDelivery(BaseModel):
    delivered_at: str
    received_by: str
    signature: bool
    location_note: str


class Shipment(BaseModel):
    id: str
    tracking_number: str
    status: str
    status_label: str
    service: str
    origin_city: str
    destination_city: str
    weight_kg: float
    package_type: str
    sender: str
    recipient: str
    estimated_delivery: str
    current_location: str
    cost: float
    timeline: list[TimelineEvent] = []
    route: list[RouteNode] = []
    pod: Optional[ProofOfDelivery] = None


class Vehicle(BaseModel):
    id: str
    type: str
    driver: str
    status: str
    status_label: str
    current_location: str
    route: str
    load_pct: int
    capacity_kg: int
    next_stop: str
    eta: str


class InventoryCategory(BaseModel):
    name: str
    units: int
    pct: int


class Warehouse(BaseModel):
    id: str
    name: str
    location: str
    capacity_sqft: int
    used_pct: int
    staff_on_shift: int
    inbound_today: int
    outbound_today: int
    inventory: list[InventoryCategory]


class Service(BaseModel):
    id: str
    name: str
    transit: str
    base_rate: int
    per_kg: int
    max_weight_kg: int
    features: list[str]
    best_for: str


class Address(BaseModel):
    id: str
    label: str
    name: str
    line: str
    city: str
    pincode: str
    phone: str
    default: bool


class QuoteResult(BaseModel):
    origin: str
    destination: str
    weight_kg: float
    zone: str
    service_name: str
    transit: str
    base_rate: float
    weight_charge: float
    fuel_surcharge: float
    gst: float
    total: float


class PickupConfirmation(BaseModel):
    pickup_id: str
    address: str
    window: str
    service: str
    estimated_items: str
    status: str


class ClaimConfirmation(BaseModel):
    claim_id: str
    tracking_number: str
    issue_type: str
    status: str
    next_step: str
    resolution_eta: str


class EtaResult(BaseModel):
    tracking_number: str
    destination_city: str
    estimated_delivery: str
    current_location: str
    status_label: str
    confidence: str


class CustomsBreakdown(BaseModel):
    destination: str
    declared_value: float
    duty_estimate: float
    vat_estimate: float
    clearance_fee: float
    total_landed_cost: float
    documents: list[str]


# ─── Rich message blocks ───────────────────────────────────
class TextBlock(BaseModel):
    type: Literal["text"] = "text"
    content: str


class DisclaimerBlock(BaseModel):
    type: Literal["disclaimer"] = "disclaimer"
    content: str


class ProhibitedAlertBlock(BaseModel):
    type: Literal["prohibited_alert"] = "prohibited_alert"
    headline: str
    message: str
    indicators: list[str]
    contact: dict   # {label, detail}


class ShipmentTrackingBlock(BaseModel):
    type: Literal["shipment_tracking"] = "shipment_tracking"
    shipment: Shipment


class ShipmentListBlock(BaseModel):
    type: Literal["shipment_list"] = "shipment_list"
    title: Optional[str] = None
    items: list[Shipment]


class RouteMapBlock(BaseModel):
    type: Literal["route_map"] = "route_map"
    tracking_number: str
    origin_city: str
    destination_city: str
    nodes: list[RouteNode]


class QuoteBlock(BaseModel):
    type: Literal["quote"] = "quote"
    quote: QuoteResult


class ServiceOptionsBlock(BaseModel):
    type: Literal["service_options"] = "service_options"
    title: Optional[str] = None
    items: list[Service]


class PickupBlock(BaseModel):
    type: Literal["pickup"] = "pickup"
    confirmation: PickupConfirmation


class FleetBlock(BaseModel):
    type: Literal["fleet"] = "fleet"
    title: Optional[str] = None
    items: list[Vehicle]


class WarehouseBlock(BaseModel):
    type: Literal["warehouse"] = "warehouse"
    title: Optional[str] = None
    items: list[Warehouse]


class ClaimBlock(BaseModel):
    type: Literal["claim"] = "claim"
    confirmation: ClaimConfirmation


class ProofOfDeliveryBlock(BaseModel):
    type: Literal["proof_of_delivery"] = "proof_of_delivery"
    tracking_number: str
    service: str
    origin_city: str
    destination_city: str
    pod: ProofOfDelivery


class EtaBlock(BaseModel):
    type: Literal["eta"] = "eta"
    result: EtaResult


class CustomsBlock(BaseModel):
    type: Literal["customs"] = "customs"
    breakdown: CustomsBreakdown


class AddressBookBlock(BaseModel):
    type: Literal["address_book"] = "address_book"
    title: Optional[str] = None
    items: list[Address]


MessageBlock = (
    TextBlock | DisclaimerBlock | ProhibitedAlertBlock | ShipmentTrackingBlock
    | ShipmentListBlock | RouteMapBlock | QuoteBlock | ServiceOptionsBlock
    | PickupBlock | FleetBlock | WarehouseBlock | ClaimBlock
    | ProofOfDeliveryBlock | EtaBlock | CustomsBlock | AddressBookBlock
)


# ─── Response ──────────────────────────────────────────────
class ChatResponse(BaseModel):
    session_id: str
    intent: str
    confidence: float
    blocks: list[MessageBlock]
    suggestions: list[str] = []
    safety_flag: Optional[str] = None  # None | "prohibited" | "privacy" | "social_engineering"
