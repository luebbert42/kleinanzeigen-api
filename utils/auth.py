import base64
import binascii
import os
import secrets
from dataclasses import dataclass
from typing import Awaitable, Callable

from fastapi import Request
from fastapi.responses import JSONResponse, Response


@dataclass(frozen=True)
class BasicAuthSettings:
    username: str | None
    password: str | None

    @property
    def enabled(self) -> bool:
        return bool(self.username and self.password)

    @classmethod
    def from_env(cls) -> "BasicAuthSettings":
        username = os.getenv("BASIC_AUTH_USERNAME")
        password = os.getenv("BASIC_AUTH_PASSWORD")

        if bool(username) != bool(password):
            raise RuntimeError(
                "Basic Auth requires both BASIC_AUTH_USERNAME and "
                "BASIC_AUTH_PASSWORD, or neither of them."
            )

        return cls(username=username, password=password)


def create_basic_auth_middleware(
    settings: BasicAuthSettings,
) -> Callable[[Request, Callable[[Request], Awaitable[Response]]], Awaitable[Response]]:
    async def basic_auth_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if not settings.enabled:
            return await call_next(request)

        authorization = request.headers.get("Authorization")
        if not authorization:
            return _unauthorized_response()

        scheme, _, encoded_credentials = authorization.partition(" ")
        if scheme.lower() != "basic" or not encoded_credentials:
            return _unauthorized_response()

        credentials = _decode_basic_auth_credentials(encoded_credentials)
        if credentials is None:
            return _unauthorized_response()

        username, password = credentials
        if not (
            secrets.compare_digest(username, settings.username or "")
            and secrets.compare_digest(password, settings.password or "")
        ):
            return _unauthorized_response()

        return await call_next(request)

    return basic_auth_middleware


def _decode_basic_auth_credentials(encoded_credentials: str) -> tuple[str, str] | None:
    try:
        decoded = base64.b64decode(encoded_credentials, validate=True).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        return None

    username, separator, password = decoded.partition(":")
    if not separator:
        return None

    return username, password


def _unauthorized_response() -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"detail": "Unauthorized"},
        headers={"WWW-Authenticate": 'Basic realm="Kleinanzeigen API"'},
    )
