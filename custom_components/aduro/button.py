"""Button platform for Aduro Hybrid Stove."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AduroDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Aduro buttons from config entry."""
    coordinator: AduroDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        AduroRefilledButton(coordinator),
        AduroCleanedButton(coordinator),
        AduroToggleModeButton(coordinator),
    ])


class AduroRefilledButton(CoordinatorEntity[AduroDataUpdateCoordinator], ButtonEntity):
    """Button to mark stove as refilled."""

    def __init__(self, coordinator: AduroDataUpdateCoordinator) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_name = "Aduro Stove Refilled"
        self._attr_unique_id = f"{coordinator.stove_serial}_refilled"
        self._attr_icon = "mdi:sack"

    async def async_press(self) -> None:
        """Handle the button press."""
        # Reset consumption counter
        # This would typically be implemented via a service call or helper entity
        _LOGGER.info("Stove marked as refilled")


class AduroCleanedButton(CoordinatorEntity[AduroDataUpdateCoordinator], ButtonEntity):
    """Button to mark stove as cleaned."""

    def __init__(self, coordinator: AduroDataUpdateCoordinator) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_name = "Aduro Stove Cleaned"
        self._attr_unique_id = f"{coordinator.stove_serial}_cleaned"
        self._attr_icon = "mdi:broom"

    async def async_press(self) -> None:
        """Handle the button press."""
        # Reset refill counter
        _LOGGER.info("Stove marked as cleaned")


class AduroToggleModeButton(CoordinatorEntity[AduroDataUpdateCoordinator], ButtonEntity):
    """Button to toggle between heat level and temperature mode."""

    def __init__(self, coordinator: AduroDataUpdateCoordinator) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_name = "Aduro Toggle Heat Target"
        self._attr_unique_id = f"{coordinator.stove_serial}_toggle_mode"

    @property
    def icon(self) -> str:
        """Return the icon based on current mode."""
        if self.coordinator.data and "status" in self.coordinator.data:
            mode = self.coordinator.data["status"].get("regulation.operation_mode", 0)
            if mode == 0:
                return "mdi:fire"
            elif mode == 1:
                return "mdi:thermometer"
            else:
                return "mdi:campfire"
        return "mdi:help-circle"

    async def async_press(self) -> None:
        """Handle the button press - toggle between modes."""
        if self.coordinator.data and "status" in self.coordinator.data:
            current_mode = self.coordinator.data["status"].get("regulation.operation_mode", 0)
            # Toggle between heat level (0) and temperature (1) modes
            new_mode = 1 if current_mode == 0 else 0
            await self.coordinator.async_set_operation_mode(new_mode)
