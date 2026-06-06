"""Data update coordinator with runtime property discovery."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DreameCloud, DreameCommandError
from .const import (
    DEFAULT_SCAN_INTERVAL,
    DISCOVERY_PIIDS,
    DISCOVERY_SIIDS,
    DOMAIN,
    PROP_CURRENT_TEMP,
    PROP_FAN_LEVEL,
    PROP_MODE,
    PROP_POWER,
    PROP_SWING,
    PROP_TARGET_TEMP,
)

_LOGGER = logging.getLogger(__name__)

# Properties the climate entity needs each cycle.
_POLL_PROPS = [
    PROP_POWER,
    PROP_MODE,
    PROP_TARGET_TEMP,
    PROP_CURRENT_TEMP,
    PROP_FAN_LEVEL,
    PROP_SWING,
]


class DreameACCoordinator(DataUpdateCoordinator):
    """Polls the AC and performs one-time property discovery."""

    def __init__(self, hass: HomeAssistant, cloud: DreameCloud, did: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.cloud = cloud
        self.did = did
        self.discovered: dict[tuple[int, int], object] | None = None
        self.cloud_control_ok: bool | None = None

    async def async_discover(self) -> dict[tuple[int, int], object]:
        """Probe a siid/piid grid once to learn the device's real layout.

        Result is logged so we can confirm the climate mapping (or detect that
        the device only answers over MQTT, in which case every read times out).
        """
        grid = [(s, p) for s in DISCOVERY_SIIDS for p in DISCOVERY_PIIDS]
        try:
            found = await self.cloud.async_get_properties(self.did, grid)
        except DreameCommandError as err:
            self.cloud_control_ok = False
            _LOGGER.warning(
                "Dreame AC %s: property discovery failed (%s). The device is "
                "not answering the cloud RPC — it likely requires the MQTT "
                "transport used by the app.",
                self.did, err,
            )
            return {}
        self.cloud_control_ok = bool(found)
        self.discovered = found
        _LOGGER.info(
            "Dreame AC %s discovery: %s",
            self.did,
            {f"{s}.{p}": v for (s, p), v in sorted(found.items())},
        )
        return found

    async def _async_update_data(self) -> dict[tuple[int, int], object]:
        if self.discovered is None:
            await self.async_discover()
        try:
            return await self.cloud.async_get_properties(self.did, _POLL_PROPS)
        except DreameCommandError as err:
            raise UpdateFailed(str(err)) from err
