from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Dict


@dataclass
class ReviewerRole:
    username: str
    password: str
    role: str


class SimpleAuth:
    def __init__(self) -> None:
        self._users: Dict[str, ReviewerRole] = {
            "hr": ReviewerRole("hr", "hr123", "hr"),
            "manager": ReviewerRole("manager", "mgr123", "manager"),
            "reviewer": ReviewerRole("reviewer", "rev123", "reviewer"),
        }
        self._sessions: Dict[str, str] = {}

    def authenticate(self, username: str, password: str) -> ReviewerRole | None:
        user = self._users.get(username.lower())
        if user and user.password == password:
            return user
        return None

    def create_session(self, user: ReviewerRole) -> str:
        token = secrets.token_urlsafe(20)
        self._sessions[token] = user.role
        return token

    def validate_session(self, token: str | None) -> str | None:
        if not token:
            return None
        return self._sessions.get(token)

    def role_can_approve(self, role: str) -> bool:
        return role in {"hr", "manager"}
