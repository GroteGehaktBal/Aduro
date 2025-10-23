"""The Aduro Hybrid Stove integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import (
    CONF_MQTT_BASE_PATH,
    CONF_MQTT_HOST,
    CONF_MQTT_PASSWORD,
    CONF_MQTT_PORT,
    CONF_MQTT_USERNAME,
    CONF_STOVE_PIN,
    CONF_STOVE_SERIAL,
    DOMAIN,
    PLATFORMS,
    SERVICE_SET_HEATLEVEL,
    SERVICE_SET_OPERATION_MODE,
    SERVICE_SET_TEMPERATURE,
    SERVICE_START_STOVE,
    SERVICE_STOP_STOVE,
)
from .coordinator import AduroDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the Aduro Hybrid Stove component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Aduro Hybrid Stove from a config entry."""
    coordinator = AduroDataUpdateCoordinator(hass, entry)
    
    await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Forward setup to platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register services
    await _async_register_services(hass, coordinator)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


async def _async_register_services(
    hass: HomeAssistant, coordinator: AduroDataUpdateCoordinator
) -> None:
    """Register services for the integration."""
    
    async def handle_set_heatlevel(call: ServiceCall) -> None:
        """Handle the set heatlevel service."""
        heatlevel = call.data.get("heatlevel")
        await coordinator.async_set_heatlevel(heatlevel)
    
    async def handle_set_temperature(call: ServiceCall) -> None:
        """Handle the set temperature service."""
        temperature = call.data.get("temperature")
        await coordinator.async_set_temperature(temperature)
    
    async def handle_set_operation_mode(call: ServiceCall) -> None:
        """Handle the set operation mode service."""
        mode = call.data.get("mode")
        await coordinator.async_set_operation_mode(mode)
    
    async def handle_start_stove(call: ServiceCall) -> None:
        """Handle the start stove service."""
        await coordinator.async_start_stove()
    
    async def handle_stop_stove(call: ServiceCall) -> None:
        """Handle the stop stove service."""
        await coordinator.async_stop_stove()
    
    # Register service schemas
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_HEATLEVEL,
        handle_set_heatlevel,
        schema=vol.Schema({vol.Required("heatlevel"): vol.In([1, 2, 3])}),
    )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_TEMPERATURE,
        handle_set_temperature,
        schema=vol.Schema({
            vol.Required("temperature"): vol.All(vol.Coerce(int), vol.Range(min=5, max=35))
        }),
    )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_OPERATION_MODE,
        handle_set_operation_mode,
        schema=vol.Schema({vol.Required("mode"): vol.In([0, 1, 2])}),
    )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_START_STOVE,
        handle_start_stove,
    )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_STOP_STOVE,
        handle_stop_stove,
    )
