from __future__ import annotations

from pydantic import BaseModel
from pydantic.dataclasses import dataclass

from typing import List, Any


@dataclass
class GoogleEmailSignin:
    kind: str
    localId: str
    email: str
    displayName: str
    idToken: str
    registered: str
    refreshToken: str
    expiresIn: str

    def __init__(self, kind, localId, email, displayName, idToken, registered, refreshToken, expiresIn):
        self.kind = kind
        self.localId = localId
        self.displayName = displayName
        self.registered = registered
        self.refreshToken = refreshToken
        self.expiresIn = expiresIn
        self.idToken = idToken
        self.email = email


class GoogleEmailRequest(BaseModel):
    email: str = "ias.topalidis@gmail.com"
    password: str = "mao2mao2mao"
    returnSecureToken: bool = True



