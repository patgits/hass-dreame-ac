"""Dreame Cloud API client (async, aiohttp)."""
from __future__ import annotations

import hashlib
import logging
import time
from typing import Any

import aiohttp

from .const import (
    AUTH_URL_TEMPLATE,
    BASIC_AUTH,
    DEVICE_LIST_URL_TEMPLATE,
    DREAME_META,
    PASSWORD_SALT,
    SEND_COMMAND_URL_TEMPLATE,
    TENANT_ID,
    TOKEN_REFRESH_MARGIN,
    USER_AGENT,
)

_LOGGER = logging.getLogger(__name__)


class DreameAuthError(Exception):
    """Authentication failed (bad credentials)."""


class DreameCommandError(Exception):
    """A device command failed or timed out."""


class DreameCloud:
    """Minimal client for the Dreame (Alibaba-backed) cloud."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        username: str,
        password: str,
        region: str,
        host_prefix: str,
    ) -> None:
        self._session = session
        self._username = username
        self._password = password
        self._region = region
        self._host_prefix = host_prefix

        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._expires_at: float = 0.0
        self._req_id = 0

    # ---- auth -------------------------------------------------------------
    @property
    def _pwd_hash(self) -> str:
        return hashlib.md5((self._password + PASSWORD_SALT).encode("utf-8")).hexdigest()

    async def async_login(self) -> dict[str, Any]:
        """Password-grant login. Returns the raw token payload."""
        url = AUTH_URL_TEMPLATE.format(region=self._region)
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": USER_AGENT,
            "Authorization": BASIC_AUTH,
            "Tenant-Id": TENANT_ID,
        }
        data = {
            "platform": "IOS",
            "scope": "all",
            "grant_type": "password",
            "username": self._username,
            "password": self._pwd_hash,
            "type": "account",
        }
        async with self._session.post(
            url, headers=headers, data=data, timeout=aiohttp.ClientTimeout(total=20)
        ) as resp:
            payload = await resp.json(content_type=None)
        if "access_token" not in payload:
            raise DreameAuthError(payload.get("error_description") or str(payload))
        self._store_tokens(payload)
        return payload

    async def async_refresh(self) -> None:
        """Refresh the access token, falling back to a full login."""
        if not self._refresh_token:
            await self.async_login()
            return
        url = AUTH_URL_TEMPLATE.format(region=self._region)
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": USER_AGENT,
            "Authorization": BASIC_AUTH,
            "Tenant-Id": TENANT_ID,
        }
        data = {"grant_type": "refresh_token", "refresh_token": self._refresh_token}
        try:
            async with self._session.post(
                url, headers=headers, data=data,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as resp:
                payload = await resp.json(content_type=None)
            if "access_token" not in payload:
                raise DreameAuthError("refresh rejected")
            self._store_tokens(payload)
        except DreameAuthError:
            await self.async_login()

    def _store_tokens(self, payload: dict[str, Any]) -> None:
        self._access_token = payload["access_token"]
        self._refresh_token = payload.get("refresh_token", self._refresh_token)
        self._expires_at = time.time() + int(payload.get("expires_in", 7200))

    async def _ensure_token(self) -> None:
        if not self._access_token:
            await self.async_login()
        elif time.time() >= self._expires_at - TOKEN_REFRESH_MARGIN:
            await self.async_refresh()

    @property
    def _api_headers(self) -> dict[str, str]:
        return {
            "Accept": "*/*",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
            "Authorization": f"Bearer {self._access_token}",
            "dreame-auth": self._access_token or "",
            "Tenant-Id": TENANT_ID,
            "dreame-meta": DREAME_META,
        }

    # ---- devices ----------------------------------------------------------
    async def async_list_devices(self) -> list[dict[str, Any]]:
        await self._ensure_token()
        url = DEVICE_LIST_URL_TEMPLATE.format(region=self._region)
        async with self._session.post(
            url, headers=self._api_headers, json={},
            timeout=aiohttp.ClientTimeout(total=20),
        ) as resp:
            payload = await resp.json(content_type=None)
        page = (payload.get("data") or {}).get("page") or {}
        return page.get("records") or []

    # ---- device RPC -------------------------------------------------------
    def _next_id(self) -> int:
        self._req_id += 1
        return self._req_id

    async def _send_command(self, did: str, method: str, params: Any) -> Any:
        await self._ensure_token()
        rid = self._next_id()
        url = SEND_COMMAND_URL_TEMPLATE.format(
            region=self._region, host_prefix=self._host_prefix
        )
        body = {
            "did": did,
            "id": rid,
            "data": {"did": did, "id": rid, "method": method, "params": params},
        }
        async with self._session.post(
            url, headers=self._api_headers, json=body,
            timeout=aiohttp.ClientTimeout(total=25),
        ) as resp:
            payload = await resp.json(content_type=None)
        code = payload.get("code")
        if code not in (0, None):
            raise DreameCommandError(f"code={code} msg={payload.get('msg')}")
        return payload.get("data")

    async def async_get_properties(
        self, did: str, props: list[tuple[int, int]]
    ) -> dict[tuple[int, int], Any]:
        params = [{"did": did, "siid": s, "piid": p} for s, p in props]
        data = await self._send_command(did, "get_properties", params)
        result: dict[tuple[int, int], Any] = {}
        for item in data or []:
            if item.get("code") == 0:
                result[(item["siid"], item["piid"])] = item.get("value")
        return result

    async def async_set_property(
        self, did: str, siid: int, piid: int, value: Any
    ) -> None:
        params = [{"did": did, "siid": siid, "piid": piid, "value": value}]
        await self._send_command(did, "set_properties", params)
