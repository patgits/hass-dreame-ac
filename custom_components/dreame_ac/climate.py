"""Climate platform for Dreame AC."""
from __future__ import annotations

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_MODEL,
    DOMAIN,
    FAN_TO_HA,
    MODE_TO_HVAC,
    PROP_CURRENT_TEMP,
    PROP_FAN_LEVEL,
    PROP_MODE,
    PROP_POWER,
    PROP_SWING,
    PROP_TARGET_TEMP,
)
from .coordinator import DreameACCoordinator

_HVAC_TO_MODE = {v: k for k, v in MODE_TO_HVAC.items()}
_HA_TO_FAN = {v: k for k, v in FAN_TO_HA.items()}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: DreameACCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DreameACClimate(coordinator, entry)])


class DreameACClimate(CoordinatorEntity[DreameACCoordinator], ClimateEntity):
    """A Dreame air conditioner exposed as an HA climate entity."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 1
    _attr_min_temp = 16
    _attr_max_temp = 30
    _attr_hvac_modes = [
        HVACMode.OFF,
        HVACMode.COOL,
        HVACMode.HEAT,
        HVACMode.AUTO,
        HVACMode.DRY,
        HVACMode.FAN_ONLY,
    ]
    _attr_fan_modes = ["auto", "low", "medium", "high"]
    _attr_swing_modes = ["off", "on"]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.SWING_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(self, coordinator: DreameACCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = entry.unique_id
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.unique_id)},
            "name": entry.title,
            "manufacturer": "Dreame",
            "model": entry.data.get(CONF_MODEL, "dreame.aircon"),
        }

    def _val(self, prop):
        return (self.coordinator.data or {}).get(prop)

    @property
    def hvac_mode(self) -> HVACMode:
        if not self._val(PROP_POWER):
            return HVACMode.OFF
        return HVACMode(MODE_TO_HVAC.get(self._val(PROP_MODE), "auto"))

    @property
    def current_temperature(self):
        return self._val(PROP_CURRENT_TEMP)

    @property
    def target_temperature(self):
        return self._val(PROP_TARGET_TEMP)

    @property
    def fan_mode(self):
        return FAN_TO_HA.get(self._val(PROP_FAN_LEVEL), "auto")

    @property
    def swing_mode(self):
        return "on" if self._val(PROP_SWING) else "off"

    async def _set(self, prop, value) -> None:
        await self.coordinator.cloud.async_set_property(
            self.coordinator.did, prop[0], prop[1], value
        )
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            await self._set(PROP_POWER, False)
            return
        if not self._val(PROP_POWER):
            await self._set(PROP_POWER, True)
        await self._set(PROP_MODE, _HVAC_TO_MODE[hvac_mode.value])

    async def async_turn_on(self) -> None:
        await self._set(PROP_POWER, True)

    async def async_turn_off(self) -> None:
        await self._set(PROP_POWER, False)

    async def async_set_temperature(self, **kwargs) -> None:
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is not None:
            await self._set(PROP_TARGET_TEMP, int(temp))

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        await self._set(PROP_FAN_LEVEL, _HA_TO_FAN[fan_mode])

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        await self._set(PROP_SWING, swing_mode == "on")
