"""Sensor platform for Aduro Hybrid Stove."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfMass,
    UnitOfPower,
    UnitOfTemperature,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, STATE_NAMES, SUBSTATE_NAMES, HEAT_LEVEL_POWER_MAP
from .coordinator import AduroDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Aduro sensors from config entry."""
    coordinator: AduroDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        # Temperature sensors
        AduroTemperatureSensor(coordinator, "smoke_temp", "Smoke Temperature"),
        AduroTemperatureSensor(coordinator, "shaft_temp", "Shaft Temperature"),
        AduroTemperatureSensor(coordinator, "boiler_temp", "Boiler Temperature"),
        
        # Power sensors
        AduroPowerSensor(coordinator),
        
        # State sensors
        AduroStateSensor(coordinator),
        AduroSubstateSensor(coordinator),
        AduroOperationModeSensor(coordinator),
        
        # Consumption sensors
        AduroConsumptionSensor(coordinator, "day", "Day"),
        AduroConsumptionSensor(coordinator, "yesterday", "Yesterday"),
        AduroConsumptionSensor(coordinator, "month", "Month"),
        AduroConsumptionSensor(coordinator, "year", "Year"),
        
        # Pellet level sensors
        AduroPelletLevelSensor(coordinator),
        AduroPelletPercentageSensor(coordinator),
        
        # Additional sensors
        AduroOxygenSensor(coordinator),
        AduroHeatLevelDisplaySensor(coordinator),
        AduroStoveIPSensor(coordinator),
    ]
    
    async_add_entities(sensors)


class AduroTemperatureSensor(CoordinatorEntity[AduroDataUpdateCoordinator], SensorEntity):
    """Temperature sensor for Aduro stove."""

    def __init__(
        self,
        coordinator: AduroDataUpdateCoordinator,
        sensor_key: str,
        sensor_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._attr_name = f"Aduro {sensor_name}"
        self._attr_unique_id = f"{coordinator.stove_serial}_{sensor_key}"
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        if self.coordinator.data and "status" in self.coordinator.data:
            value = self.coordinator.data["status"].get(self._sensor_key)
            if value is not None:
                return round(float(value), 1)
        return None


class AduroPowerSensor(CoordinatorEntity[AduroDataUpdateCoordinator], SensorEntity):
    """Power sensor for Aduro stove."""

    def __init__(self, coordinator: AduroDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Aduro Power"
        self._attr_unique_id = f"{coordinator.stove_serial}_power"
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        if self.coordinator.data and "status" in self.coordinator.data:
            value = self.coordinator.data["status"].get("power_kw")
            if value is not None:
                return round(float(value), 1)
        return None


class AduroStateSensor(CoordinatorEntity[AduroDataUpdateCoordinator], SensorEntity):
    """State sensor for Aduro stove."""

    def __init__(self, coordinator: AduroDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Aduro State"
        self._attr_unique_id = f"{coordinator.stove_serial}_state"
        self._attr_icon = "mdi:information"

    @property
    def native_value(self) -> str | None:
        """Return the sensor value."""
        if self.coordinator.data and "status" in self.coordinator.data:
            state = str(self.coordinator.data["status"].get("state", ""))
            if state:
                return state
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if self.coordinator.data and "status" in self.coordinator.data:
            state = str(self.coordinator.data["status"].get("state", ""))
            heatlevel = self._get_heatlevel_display()
            state_text = STATE_NAMES.get(state, state).format(heatlevel=heatlevel)
            return {"state_text": state_text}
        return {}

    def _get_heatlevel_display(self) -> str:
        """Get heat level display."""
        if self.coordinator.data and "status" in self.coordinator.data:
            power = self.coordinator.data["status"].get("regulation.fixed_power", 50)
            level = HEAT_LEVEL_POWER_MAP.get(int(power), 2)
            return ["", "I", "II", "III"][level]
        return ""


class AduroSubstateSensor(CoordinatorEntity[AduroDataUpdateCoordinator], SensorEntity):
    """Substate sensor for Aduro stove."""

    def __init__(self, coordinator: AduroDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Aduro Substate"
        self._attr_unique_id = f"{coordinator.stove_serial}_substate"
        self._attr_icon = "mdi:information-outline"

    @property
    def native_value(self) -> str | None:
        """Return the sensor value."""
        if self.coordinator.data and "status" in self.coordinator.data:
            return str(self.coordinator.data["status"].get("substate", ""))
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if self.coordinator.data and "status" in self.coordinator.data:
            state = str(self.coordinator.data["status"].get("state", ""))
            substate = str(self.coordinator.data["status"].get("substate", ""))
            
            # Try to find specific substate text
            substate_key = f"{state}_{substate}"
            substate_text = SUBSTATE_NAMES.get(substate_key, SUBSTATE_NAMES.get(state, substate))
            
            return {"substate_text": substate_text}
        return {}


class AduroOperationModeSensor(CoordinatorEntity[AduroDataUpdateCoordinator], SensorEntity):
    """Operation mode sensor for Aduro stove."""

    def __init__(self, coordinator: AduroDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Aduro Operation Mode"
        self._attr_unique_id = f"{coordinator.stove_serial}_operation_mode"

    @property
    def native_value(self) -> str | None:
        """Return the sensor value."""
        if self.coordinator.data and "status" in self.coordinator.data:
            mode = self.coordinator.data["status"].get("regulation.operation_mode", 0)
            mode_map = {0: "Heat Level", 1: "Temperature", 2: "Wood"}
            return mode_map.get(int(mode), "Unknown")
        return None

    @property
    def icon(self) -> str:
        """Return the icon based on mode."""
        if self.coordinator.data and "status" in self.coordinator.data:
            mode = self.coordinator.data["status"].get("regulation.operation_mode", 0)
            if mode == 0:
                return "mdi:fire"
            elif mode == 1:
                return "mdi:thermometer"
            else:
                return "mdi:campfire"
        return "mdi:help-circle"


class AduroConsumptionSensor(CoordinatorEntity[AduroDataUpdateCoordinator], SensorEntity):
    """Consumption sensor for Aduro stove."""

    def __init__(
        self,
        coordinator: AduroDataUpdateCoordinator,
        period: str,
        period_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._period = period
        self._attr_name = f"Aduro Consumption {period_name}"
        self._attr_unique_id = f"{coordinator.stove_serial}_consumption_{period}"
        self._attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_icon = "mdi:fire"

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        if self.coordinator.data and "consumption" in self.coordinator.data:
            value = self.coordinator.data["consumption"].get(self._period)
            if value is not None:
                return round(float(value), 1)
        return None


class AduroPelletLevelSensor(CoordinatorEntity[AduroDataUpdateCoordinator], SensorEntity):
    """Pellet level sensor for Aduro stove."""

    def __init__(self, coordinator: AduroDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Aduro Pellet Level"
        self._attr_unique_id = f"{coordinator.stove_serial}_pellet_level"
        self._attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:sack"

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        # This would be calculated from capacity - consumption
        # Placeholder implementation
        return None


class AduroPelletPercentageSensor(CoordinatorEntity[AduroDataUpdateCoordinator], SensorEntity):
    """Pellet percentage sensor for Aduro stove."""

    def __init__(self, coordinator: AduroDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Aduro Pellet Percentage"
        self._attr_unique_id = f"{coordinator.stove_serial}_pellet_percentage"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:gauge"

    @property
    def native_value(self) -> int | None:
        """Return the sensor value."""
        # This would be calculated from pellet level / capacity * 100
        # Placeholder implementation
        return None


class AduroOxygenSensor(CoordinatorEntity[AduroDataUpdateCoordinator], SensorEntity):
    """Oxygen sensor for Aduro stove."""

    def __init__(self, coordinator: AduroDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Aduro Oxygen"
        self._attr_unique_id = f"{coordinator.stove_serial}_oxygen"
        self._attr_native_unit_of_measurement = "ppm"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:air-filter"

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""
        if self.coordinator.data and "status" in self.coordinator.data:
            value = self.coordinator.data["status"].get("oxygen")
            if value is not None:
                return round(float(value), 1)
        return None


class AduroHeatLevelDisplaySensor(CoordinatorEntity[AduroDataUpdateCoordinator], SensorEntity):
    """Heat level display sensor for Aduro stove."""

    def __init__(self, coordinator: AduroDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Aduro Heat Level Display"
        self._attr_unique_id = f"{coordinator.stove_serial}_heatlevel_display"
        self._attr_icon = "mdi:fire"

    @property
    def native_value(self) -> str | None:
        """Return the sensor value."""
        if self.coordinator.data and "status" in self.coordinator.data:
            power = self.coordinator.data["status"].get("regulation.fixed_power", 50)
            level = HEAT_LEVEL_POWER_MAP.get(int(power), 2)
            return ["", "I", "II", "III"][level]
        return None


class AduroStoveIPSensor(CoordinatorEntity[AduroDataUpdateCoordinator], SensorEntity):
    """Stove IP address sensor."""

    def __init__(self, coordinator: AduroDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Aduro Stove IP"
        self._attr_unique_id = f"{coordinator.stove_serial}_ip"
        self._attr_icon = "mdi:ip-network"

    @property
    def native_value(self) -> str | None:
        """Return the sensor value."""
        if self.coordinator.data and "ip" in self.coordinator.data:
            return self.coordinator.data["ip"]
        return self.coordinator.stove_ip
