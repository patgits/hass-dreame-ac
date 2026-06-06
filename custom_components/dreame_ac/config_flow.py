"""Config flow for Dreame AC."""
from __future__ import annotations

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
    """Email + password login, then auto-select the air-conditioner."""

    VERSION = 1

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
                acs = [d for d in devices if "aircon" in (d.get("model") or "")]
                if not acs:
                    errors["base"] = "no_aircon"
                else:
                    dev = acs[0]
                    await self.async_set_unique_id(str(dev["did"]))
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=dev.get("customName") or "Dreame AC",
                        data={
                            CONF_USERNAME: user_input[CONF_USERNAME],
                            CONF_PASSWORD: user_input[CONF_PASSWORD],
                            CONF_REGION: user_input[CONF_REGION],
                            CONF_HOST_PREFIX: DEFAULT_HOST_PREFIX,
                            CONF_DID: str(dev["did"]),
                            CONF_MODEL: dev.get("model"),
                        },
                    )

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
