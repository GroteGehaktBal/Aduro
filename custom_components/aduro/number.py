"""Number platform for Aduro Hybrid Stove."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DEFAULT_CAPACITY_PELLETS,
    DEFAULT_NOTIFICATION_LEVEL,
    DEFAULT_SHUTDOWN_LEVEL,
    DOMAIN,
)
from .coordinator import AduroDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Aduro number entities from config entry."""
    coordinator: AduroDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        AduroHeatLevelNumber(coordinator),
        AduroBoilerRefNumber(coordinator),
        AduroCapacityPelletsNumber(coordinator),
        AduroNotificationLevelNumber(coordinator),
        AduroShutdownLevelNumber(coordinator),
    ])


class AduroHeatLevelNumber(CoordinatorEntity[AduroDataUpdateCoordinator], NumberEntity):
    """Number entity for heat level control."""

    def __init__(self, coordinator: AduroDataUpdateCoordinator) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_name = "Aduro Heat Level"
        self._attr_unique_id = f"{coordinator.stove_serial}_heatlevel"
        self._attr_icon = "mdi:fire"
        self._attr_native_min_value = 1
        self._attr_native_max_value = 3
        self._attr_native_step = 1
        self._attr_mode = NumberMode.SLIDER

    @property
    def native_value(self) -> float | None:
        """Return the current heat level."""
        if self.coordinator.data and "status" in self.coordinator.data:
            from .const import HEAT_LEVEL_POWER_MAP
            power = self.coordinator.data["status"].get("regulation.fixed_power", 50)
            return HEAT_LEVEL_POWER_MAP.get(int(power), 2)
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the heat level."""
        await self.coordinator.async_set_heatlevel(int(value))


class AduroBoilerRefNumber(CoordinatorEntity[AduroDataUpdateCoordinator], NumberEntity):
    """Number entity for boiler reference temperature."""

    def __init__(self, coordinator: AduroDataUpdateCoordinator) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_name = "Aduro Target Temperature"
        self._attr_unique_id = f"{coordinator.stove_serial}_boiler_ref"
        self._attr_icon = "mdi:thermometer"
        self._attr_native_min_value = 5
        self._attr_native_max_value = 35
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = "°C"
        self._attr_mode = NumberMode.SLIDER

    @property
    def native_value(self) -> float | None:
        """Return the current boiler reference temperature."""
        if self.coordinator.data and "status" in self.coordinator.data:
            return self.coordinator.data["status"].get("boiler.temp", 20)
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the boiler reference temperature."""
        await self.coordinator.async_set_temperature(int(value))


class AduroCapacityPelletsNumber(CoordinatorEntity[AduroDataUpdateCoordinator], NumberEntity):
    """Number entity for pellet capacity setting."""

    def __init__(self, coordinator: AduroDataUpdateCoordinator) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_name = "Aduro Pellet Capacity"
        self._attr_unique_id = f"{coordinator.stove_serial}_capacity_pellets"
        self._attr_icon = "mdi:sack"
        self._attr_native_min_value = 9
        self._attr_native_max_value = 10
        self._attr_native_step = 0.1
        self._attr_native_unit_of_measurement = "kg"
        self._attr_mode = NumberMode.BOX
        self._value = DEFAULT_CAPACITY_PELLETS

    @property
    def native_value(self) -> float:
        """Return the pellet capacity."""
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        """Set the pellet capacity."""
        self._value = value
        self.async_write_ha_state()


class AduroNotificationLevelNumber(CoordinatorEntity[AduroDataUpdateCoordinator], NumberEntity):
    """Number entity for notification pellet level."""

    def __init__(self, coordinator: AduroDataUpdateCoordinator) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_name = "Aduro Notification Pellet Level"
        self._attr_unique_id = f"{coordinator.stove_serial}_notification_level"
        self._attr_icon = "mdi:bell"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 20
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = "%"
        self._attr_mode = NumberMode.BOX
        self._value = DEFAULT_NOTIFICATION_LEVEL

    @property
    def native_value(self) -> float:
        """Return the notification level."""
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        """Set the notification level."""
        self._value = value
        self.async_write_ha_state()


class AduroShutdownLevelNumber(CoordinatorEntity[AduroDataUpdateCoordinator], NumberEntity):
    """Number entity for shutdown pellet level."""

    def __init__(self, coordinator: AduroDataUpdateCoordinator) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._attr_name = "Aduro Shutdown Pellet Level"
        self._attr_unique_id = f"{coordinator.stove_serial}_shutdown_level"
        self._attr_icon = "mdi:alert"
        self._attr_native_min_value = -10
        self._attr_native_max_value = 15
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = "%"
        self._attr_mode = NumberMode.BOX
        self._value = DEFAULT_SHUTDOWN_LEVEL

    @property
    def native_value(self) -> float:
        """Return the shutdown level."""
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        """Set the shutdown level."""
        self._value = value
        self.async_write_ha_state()
