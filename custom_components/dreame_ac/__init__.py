"""The Dreame AC integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DreameAuthError, DreameCloud
from .const import (
    CONF_DID,
    CONF_HOST_PREFIX,
    CONF_PASSWORD,
    CONF_REGION,
    CONF_USERNAME,
    DOMAIN,
)
from .coordinator import DreameACCoordinator

PLATFORMS = ["climate"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    cloud = DreameCloud(
        session,
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
        entry.data[CONF_REGION],
        entry.data[CONF_HOST_PREFIX],
    )
    try:
        await cloud.async_login()
    except DreameAuthError as err:
        raise ConfigEntryAuthFailed(str(err)) from err
    except Exception as err:  # noqa: BLE001
        raise ConfigEntryNotReady(str(err)) from err

    coordinator = DreameACCoordinator(hass, cloud, entry.data[CONF_DID])
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded
