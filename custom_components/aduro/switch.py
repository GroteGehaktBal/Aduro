"""Switch platform for Aduro Hybrid Stove."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, STARTUP_STATES
from .coordinator import AduroDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Aduro switch from config entry."""
    coordinator: AduroDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([AduroStoveSwitch(coordinator)])


class AduroStoveSwitch(CoordinatorEntity[AduroDataUpdateCoordinator], SwitchEntity):
    """Representation of an Aduro stove on/off switch."""

    def __init__(self, coordinator: AduroDataUpdateCoordinator) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_name = "Aduro Stove Power"
        self._attr_unique_id = f"{coordinator.stove_serial}_power"
        self._attr_icon = "mdi:fireplace"

    @property
    def is_on(self) -> bool:
        """Return true if stove is on."""
        if self.coordinator.data and "status" in self.coordinator.data:
            state = str(self.coordinator.data["status"].get("state", ""))
            return state in STARTUP_STATES
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the stove on."""
        await self.coordinator.async_start_stove()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the stove off."""
        await self.coordinator.async_stop_stove()
