"""Data update coordinator for the Dreame AC (tolerant of flaky cloud RPC)."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import DreameCloud, DreameCommandError
from .const import (
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PROP_CURRENT_TEMP,
    PROP_FAN_SPEED,
    PROP_MODE,
    PROP_NIGHT,
    PROP_POWER,
    PROP_SWING,
    PROP_TARGET_TEMP,
)

_LOGGER = logging.getLogger(__name__)

_POLL_PROPS = [
    PROP_POWER,
    PROP_MODE,
    PROP_TARGET_TEMP,
    PROP_FAN_SPEED,
    PROP_NIGHT,
    PROP_SWING,
    PROP_CURRENT_TEMP,
]


class DreameACCoordinator(DataUpdateCoordinator):
    """Polls the AC; keeps last good values when the device times out."""

    def __init__(self, hass: HomeAssistant, cloud: DreameCloud, did: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.cloud = cloud
        self.did = did
        self._last: dict[tuple[int, int], object] = {}

    async def _async_update_data(self) -> dict[tuple[int, int], object]:
        try:
            data = await self.cloud.async_get_properties(self.did, _POLL_PROPS)
            if data:
                self._last.update(data)
        except DreameCommandError as err:
            _LOGGER.debug("Dreame AC poll skipped (%s)", err)
        return dict(self._last)
