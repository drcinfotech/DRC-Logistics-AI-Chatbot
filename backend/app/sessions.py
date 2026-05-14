"""
Lightweight in-memory session store for the logistics chatbot.
"""
from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class Session:
    session_id: str
    last_intent: str = ""
    last_tracking_number: str | None = None
    history: list[dict] = field(default_factory=list)


class SessionStore:
    def __init__(self):
        self._sessions: dict[str, Session] = {}
        self._lock = Lock()

    def get_or_create(self, session_id: str | None) -> Session:
        with self._lock:
            if session_id and session_id in self._sessions:
                return self._sessions[session_id]
            new_id = session_id or secrets.token_urlsafe(12)
            s = Session(session_id=new_id)
            self._sessions[new_id] = s
            return s

    def get(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)


store = SessionStore()
