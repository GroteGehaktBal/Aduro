"""Config flow for Aduro Hybrid Stove integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.const import CONF_NAME

from .const import (
    CONF_MQTT_BASE_PATH,
    CONF_MQTT_HOST,
    CONF_MQTT_PASSWORD,
    CONF_MQTT_PORT,
    CONF_MQTT_USERNAME,
    CONF_STOVE_PIN,
    CONF_STOVE_SERIAL,
    DEFAULT_MQTT_BASE_PATH,
    DEFAULT_MQTT_PORT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_STOVE_SERIAL): str,
        vol.Required(CONF_STOVE_PIN): str,
        vol.Required(CONF_MQTT_HOST): str,
        vol.Optional(CONF_MQTT_PORT, default=DEFAULT_MQTT_PORT): int,
        vol.Optional(CONF_MQTT_USERNAME): str,
        vol.Optional(CONF_MQTT_PASSWORD): str,
        vol.Optional(CONF_MQTT_BASE_PATH, default=DEFAULT_MQTT_BASE_PATH): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.
    
    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # Test connection by trying to discover the stove
    try:
        from pyduro.actions import discover
        
        def test_discover():
            response = discover.run()
            return response.parse_payload()
        
        result = await hass.async_add_executor_job(test_discover)
        
        if not result:
            raise CannotConnect
        
    except Exception as e:
        _LOGGER.error("Failed to validate connection: %s", e)
        raise CannotConnect
    
    # Return info to be stored in the config entry
    return {"title": f"Aduro Stove {data[CONF_STOVE_SERIAL]}"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Aduro Hybrid Stove."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Create a unique ID based on the stove serial
                await self.async_set_unique_id(user_input[CONF_STOVE_SERIAL])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Aduro integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_MQTT_HOST,
                        default=self.config_entry.data.get(CONF_MQTT_HOST),
                    ): str,
                    vol.Optional(
                        CONF_MQTT_PORT,
                        default=self.config_entry.data.get(CONF_MQTT_PORT, DEFAULT_MQTT_PORT),
                    ): int,
                    vol.Optional(
                        CONF_MQTT_USERNAME,
                        default=self.config_entry.data.get(CONF_MQTT_USERNAME, ""),
                    ): str,
                    vol.Optional(
                        CONF_MQTT_PASSWORD,
                        default=self.config_entry.data.get(CONF_MQTT_PASSWORD, ""),
                    ): str,
                    vol.Optional(
                        CONF_MQTT_BASE_PATH,
                        default=self.config_entry.data.get(CONF_MQTT_BASE_PATH, DEFAULT_MQTT_BASE_PATH),
                    ): str,
                }
            ),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
