"""Switch platform for Dreame AC — Nachtmodus (night mode)."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, PROP_NIGHT
from .coordinator import DreameACCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: DreameACCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DreameNightSwitch(coordinator, entry)])


class DreameNightSwitch(CoordinatorEntity[DreameACCoordinator], SwitchEntity):
    """Night mode (Nachtmodus) as an on/off switch with a moon icon."""

    _attr_has_entity_name = True
    _attr_name = "Nachtmodus"
    _attr_icon = "mdi:weather-night"

    def __init__(self, coordinator: DreameACCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.unique_id}_night"
        self._attr_device_info = {"identifiers": {(DOMAIN, entry.unique_id)}}

    @property
    def is_on(self) -> bool:
        return bool((self.coordinator.data or {}).get(PROP_NIGHT))

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.cloud.async_set_property(
            self.coordinator.did, PROP_NIGHT[0], PROP_NIGHT[1], True
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.cloud.async_set_property(
            self.coordinator.did, PROP_NIGHT[0], PROP_NIGHT[1], False
        )
        await self.coordinator.async_request_refresh()
