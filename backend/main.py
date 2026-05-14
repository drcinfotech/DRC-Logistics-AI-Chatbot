"""
FastAPI entry point for the Logistics & Transportation AI Chatbot.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.catalog import catalog
from app.chatbot import engine
from app.models import ChatRequest, ChatResponse
from app.sessions import store

app = FastAPI(
    title="Logistics AI Chatbot",
    description=(
        "A demo conversational AI for logistics, transportation, and supply-chain operations. "
        "Includes intent classification, prohibited-goods and shipment-privacy guardrails, and rich "
        "response blocks for shipment tracking, quotes, pickups, fleet, warehouses, claims, and customs. "
        "NOT a production shipping system — all data is fictional."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status":     "ok",
        "shipments":  len(catalog.shipments()),
        "fleet":      len(catalog.fleet()),
        "warehouses": len(catalog.warehouses()),
        "services":   len(catalog.services()),
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session = store.get_or_create(req.session_id)
    return engine.respond(req.message, session)


@app.get("/shipments")
def list_shipments():
    return catalog.shipments()


@app.get("/shipments/{tracking_number}")
def get_shipment(tracking_number: str):
    s = catalog.shipment_by_tracking(tracking_number)
    return s or {"error": "not found", "tracking_number": tracking_number}


@app.get("/fleet")
def list_fleet():
    return catalog.fleet()


@app.get("/warehouses")
def list_warehouses():
    return catalog.warehouses()


@app.get("/services")
def list_services():
    return catalog.services()


@app.get("/prohibited-items")
def list_prohibited():
    return catalog.prohibited_items()


@app.get("/addresses")
def list_addresses():
    return catalog.addresses()


@app.get("/")
def root():
    return {
        "name":       "Logistics AI Chatbot",
        "version":    app.version,
        "docs":       "/docs",
        "disclaimer": "Demo only. All shipments, fleet, and warehouse data are fictional.",
    }
