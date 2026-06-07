"""Config flow for Dreame AC."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DreameAuthError, DreameCloud
from .const import (
    CONF_DID,
    CONF_HOST_PREFIX,
    CONF_MODEL,
    CONF_PASSWORD,
    CONF_REGION,
    CONF_USERNAME,
    DEFAULT_HOST_PREFIX,
    DEFAULT_REGION,
    DOMAIN,
    REGIONS,
)


class DreameACConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Email + password login, then pick the air-conditioner."""

    VERSION = 1

    def __init__(self) -> None:
        self._creds: dict[str, str] = {}
        self._acs: list[dict[str, Any]] = []

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            cloud = DreameCloud(
                session,
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
                user_input[CONF_REGION],
                DEFAULT_HOST_PREFIX,
            )
            try:
                await cloud.async_login()
                devices = await cloud.async_list_devices()
            except DreameAuthError:
                errors["base"] = "invalid_auth"
            except Exception:  # noqa: BLE001
                errors["base"] = "cannot_connect"
            else:
                self._acs = [d for d in devices if "aircon" in (d.get("model") or "")]
                if not self._acs:
                    errors["base"] = "no_aircon"
                else:
                    self._creds = {
                        CONF_USERNAME: user_input[CONF_USERNAME],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                        CONF_REGION: user_input[CONF_REGION],
                    }
                    if len(self._acs) == 1:
                        return await self._create_for(self._acs[0])
                    return await self.async_step_select()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(CONF_REGION, default=DEFAULT_REGION): vol.In(REGIONS),
                }
            ),
            errors=errors,
        )

    async def async_step_select(self, user_input=None) -> FlowResult:
        """Let the user pick one of several air conditioners on the account."""
        if user_input is not None:
            did = user_input[CONF_DID]
            dev = next(d for d in self._acs if str(d["did"]) == did)
            return await self._create_for(dev)

        choices = {
            str(d["did"]): (d.get("customName") or d.get("model") or str(d["did"]))
            for d in self._acs
        }
        return self.async_show_form(
            step_id="select",
            data_schema=vol.Schema({vol.Required(CONF_DID): vol.In(choices)}),
        )

    async def _create_for(self, dev: dict[str, Any]) -> FlowResult:
        await self.async_set_unique_id(str(dev["did"]))
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title=dev.get("customName") or "Dreame AC",
            data={
                **self._creds,
                CONF_HOST_PREFIX: DEFAULT_HOST_PREFIX,
                CONF_DID: str(dev["did"]),
                CONF_MODEL: dev.get("model"),
            },
        )
