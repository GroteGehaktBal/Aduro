"""Data update coordinator for Aduro Hybrid Stove."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from pyduro.actions import discover, get, set, raw
import paho.mqtt.client as mqtt

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import asyncio
import json

from .const import (
    CONF_MQTT_BASE_PATH,
    CONF_MQTT_HOST,
    CONF_MQTT_PASSWORD,
    CONF_MQTT_PORT,
    CONF_MQTT_USERNAME,
    CONF_STOVE_PIN,
    CONF_STOVE_SERIAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    HEAT_LEVEL_POWER_MAP,
)

_LOGGER = logging.getLogger(__name__)


class AduroDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Aduro stove data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.stove_serial = entry.data[CONF_STOVE_SERIAL]
        self.stove_pin = entry.data[CONF_STOVE_PIN]
        self.mqtt_host = entry.data[CONF_MQTT_HOST]
        self.mqtt_port = entry.data[CONF_MQTT_PORT]
        self.mqtt_username = entry.data.get(CONF_MQTT_USERNAME)
        self.mqtt_password = entry.data.get(CONF_MQTT_PASSWORD)
        self.mqtt_base_path = entry.data.get(CONF_MQTT_BASE_PATH, "aduro_h2/")
        
        self.stove_ip = None
        self.mqtt_client = None
        self._mqtt_data = {}
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the stove."""
        try:
            # Discover stove if we don't have IP yet
            if not self.stove_ip:
                await self._async_discover_stove()
            
            # Get status data
            status_data = await self._async_get_status()
            
            # Get consumption data
            consumption_data = await self._async_get_consumption()
            
            return {
                "status": status_data,
                "consumption": consumption_data,
                "ip": self.stove_ip,
                "serial": self.stove_serial,
            }
        except Exception as err:
            _LOGGER.error("Error fetching Aduro data: %s", err)
            raise UpdateFailed(f"Error communicating with stove: {err}")

    async def _async_discover_stove(self) -> None:
        """Discover the stove on the network."""
        def discover_stove():
            try:
                response = discover.run()
                data = response.parse_payload()
                ip = data.get("IP", "apprelay20.stokercloud.dk")
                
                # Fallback to cloud if local IP is invalid
                if "0.0.0.0" in ip:
                    ip = "apprelay20.stokercloud.dk"
                
                return ip
            except Exception as e:
                _LOGGER.warning("Discovery failed, using cloud address: %s", e)
                return "apprelay20.stokercloud.dk"
        
        self.stove_ip = await self.hass.async_add_executor_job(discover_stove)
        _LOGGER.debug("Discovered stove at: %s", self.stove_ip)

    async def _async_get_status(self) -> dict[str, Any]:
        """Get status data from the stove."""
        def get_status():
            try:
                response = get.run(
                    burner_address=self.stove_ip,
                    serial=self.stove_serial,
                    pin_code=self.stove_pin,
                )
                return response.parse_payload()
            except Exception as e:
                _LOGGER.error("Failed to get status: %s", e)
                return {}
        
        return await self.hass.async_add_executor_job(get_status)

    async def _async_get_consumption(self) -> dict[str, Any]:
        """Get consumption data from the stove."""
        def get_consumption():
            try:
                from datetime import date, timedelta
                
                # Get daily consumption
                response = raw.run(
                    burner_address=self.stove_ip,
                    serial=self.stove_serial,
                    pin_code=self.stove_pin,
                    payload="total_days"
                )
                
                data = response.payload.split(',')
                data[0] = data[0][11:]  # Remove "total_days" prefix
                
                today = date.today().day
                yesterday = (date.today() - timedelta(1)).day
                
                consumption_today = float(data[today - 1])
                consumption_yesterday = float(data[yesterday - 1])
                
                # Get monthly consumption
                response = raw.run(
                    burner_address=self.stove_ip,
                    serial=self.stove_serial,
                    pin_code=self.stove_pin,
                    payload="total_months"
                )
                
                data = response.payload.split(',')
                data[0] = data[0][13:]  # Remove "total_months" prefix
                month = date.today().month
                consumption_month = float(data[month - 1])
                
                # Get yearly consumption
                response = raw.run(
                    burner_address=self.stove_ip,
                    serial=self.stove_serial,
                    pin_code=self.stove_pin,
                    payload="total_years"
                )
                
                data = response.payload.split(',')
                data[0] = data[0][12:]  # Remove "total_years" prefix
                year = date.today().year
                data_position = year - (year - (len(data) - 1))
                consumption_year = float(data[data_position])
                
                return {
                    "day": consumption_today,
                    "yesterday": consumption_yesterday,
                    "month": consumption_month,
                    "year": consumption_year,
                }
            except Exception as e:
                _LOGGER.error("Failed to get consumption data: %s", e)
                return {}
        
        return await self.hass.async_add_executor_job(get_consumption)

    async def async_set_heatlevel(self, level: int) -> None:
        """Set the heat level."""
        def set_level():
            try:
                response = set.run(
                    burner_address=self.stove_ip,
                    serial=self.stove_serial,
                    pin_code=self.stove_pin,
                    path="regulation.fixed_power",
                    value=HEAT_LEVEL_POWER_MAP.get(level, 50),
                )
                return response.parse_payload()
            except Exception as e:
                _LOGGER.error("Failed to set heat level: %s", e)
                raise
        
        await self.hass.async_add_executor_job(set_level)
        await self.async_request_refresh()

    async def async_set_temperature(self, temperature: int) -> None:
        """Set the target temperature."""
        def set_temp():
            try:
                response = set.run(
                    burner_address=self.stove_ip,
                    serial=self.stove_serial,
                    pin_code=self.stove_pin,
                    path="boiler.temp",
                    value=temperature,
                )
                return response.parse_payload()
            except Exception as e:
                _LOGGER.error("Failed to set temperature: %s", e)
                raise
        
        await self.hass.async_add_executor_job(set_temp)
        await self.async_request_refresh()

    async def async_set_operation_mode(self, mode: int) -> None:
        """Set the operation mode."""
        def set_mode():
            try:
                response = set.run(
                    burner_address=self.stove_ip,
                    serial=self.stove_serial,
                    pin_code=self.stove_pin,
                    path="regulation.operation_mode",
                    value=mode,
                )
                return response.parse_payload()
            except Exception as e:
                _LOGGER.error("Failed to set operation mode: %s", e)
                raise
        
        await self.hass.async_add_executor_job(set_mode)
        await self.async_request_refresh()

    async def async_start_stove(self) -> None:
        """Start the stove."""
        def start():
            try:
                response = set.run(
                    burner_address=self.stove_ip,
                    serial=self.stove_serial,
                    pin_code=self.stove_pin,
                    path="start_stop",
                    value="start",
                )
                return response.parse_payload()
            except Exception as e:
                _LOGGER.error("Failed to start stove: %s", e)
                raise
        
        await self.hass.async_add_executor_job(start)
        await self.async_request_refresh()

    async def async_stop_stove(self) -> None:
        """Stop the stove."""
        def stop():
            try:
                response = set.run(
                    burner_address=self.stove_ip,
                    serial=self.stove_serial,
                    pin_code=self.stove_pin,
                    path="start_stop",
                    value="stop",
                )
                return response.parse_payload()
            except Exception as e:
                _LOGGER.error("Failed to stop stove: %s", e)
                raise
        
        await self.hass.async_add_executor_job(stop)
        await self.async_request_refresh()
