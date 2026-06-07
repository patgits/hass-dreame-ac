"""Climate platform for Dreame AC (dreame.aircon.tbl2528)."""
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
    MAX_TEMP,
    MIN_TEMP,
    MODE_TO_HVAC,
    PROP_CURRENT_TEMP,
    PROP_MODE,
    PROP_POWER,
    PROP_SWING,
    PROP_TARGET_TEMP,
    TEMP_SCALE,
)
from .coordinator import DreameACCoordinator

_HVAC_TO_MODE = {v: k for k, v in MODE_TO_HVAC.items()}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: DreameACCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DreameACClimate(coordinator, entry)])


class DreameACClimate(CoordinatorEntity[DreameACCoordinator], ClimateEntity):
    """Dreame portable air conditioner (cooling/dry/fan, no heat)."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 1
    _attr_min_temp = MIN_TEMP
    _attr_max_temp = MAX_TEMP
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.COOL, HVACMode.DRY, HVACMode.FAN_ONLY]
    _attr_swing_modes = ["off", "on"]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.SWING_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(self, coordinator: DreameACCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = entry.unique_id
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.unique_id)},
            "name": entry.title,
            "manufacturer": "Dreame",
            "model": entry.data.get(CONF_MODEL, "dreame.aircon.tbl2528"),
        }

    def _val(self, prop):
        return (self.coordinator.data or {}).get(prop)

    @property
    def hvac_mode(self) -> HVACMode:
        if not self._val(PROP_POWER):
            return HVACMode.OFF
        return HVACMode(MODE_TO_HVAC.get(self._val(PROP_MODE), "cool"))

    @property
    def current_temperature(self):
        raw = self._val(PROP_CURRENT_TEMP)
        return raw / TEMP_SCALE if raw is not None else None

    @property
    def target_temperature(self):
        raw = self._val(PROP_TARGET_TEMP)
        return raw / TEMP_SCALE if raw is not None else None

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
        if hvac_mode.value in _HVAC_TO_MODE:
            await self._set(PROP_MODE, _HVAC_TO_MODE[hvac_mode.value])

    async def async_turn_on(self) -> None:
        await self._set(PROP_POWER, True)

    async def async_turn_off(self) -> None:
        await self._set(PROP_POWER, False)

    async def async_set_temperature(self, **kwargs) -> None:
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is not None:
            await self._set(PROP_TARGET_TEMP, int(round(temp * TEMP_SCALE)))

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        await self._set(PROP_SWING, swing_mode == "on")
