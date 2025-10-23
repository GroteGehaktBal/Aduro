"""Constants for the Aduro Hybrid Stove integration."""
from datetime import timedelta

DOMAIN = "aduro"
PLATFORMS = ["sensor", "switch", "number", "button"]

# Configuration keys
CONF_STOVE_SERIAL = "stove_serial"
CONF_STOVE_PIN = "stove_pin"
CONF_MQTT_HOST = "mqtt_host"
CONF_MQTT_PORT = "mqtt_port"
CONF_MQTT_USERNAME = "mqtt_username"
CONF_MQTT_PASSWORD = "mqtt_password"
CONF_MQTT_BASE_PATH = "mqtt_base_path"

# Defaults
DEFAULT_MQTT_PORT = 1883
DEFAULT_MQTT_BASE_PATH = "aduro_h2/"
DEFAULT_SCAN_INTERVAL = timedelta(seconds=20)
DEFAULT_CAPACITY_PELLETS = 9.5
DEFAULT_NOTIFICATION_LEVEL = 10
DEFAULT_SHUTDOWN_LEVEL = 5

# State mappings
STATE_NAMES = {
    "0": "Operating {heatlevel}",
    "2": "Operating {heatlevel}",
    "4": "Operating {heatlevel}",
    "5": "Operating {heatlevel}",
    "6": "Stopped",
    "9": "Off",
    "13": "Stopped",
    "14": "Off",
    "20": "Stopped",
    "28": "Stopped",
    "32": "Operating III",
    "34": "Stopped",
}

SUBSTATE_NAMES = {
    "0": "Waiting",
    "2": "Ignition 1",
    "4": "Ignition 2",
    "5": "Normal",
    "6": "Room temperature reached",
    "9": "Wood burning",
    "13": "Failed ignition - Open door and check burner for pellet accumulation",
    "14_0": "By button",
    "14_1": "Wood burning?",
    "20": "No fuel",
    "28": "Unknown",
    "32": "Heating up",
    "34": "Check burn cup",
}

# Startup states
STARTUP_STATES = ["0", "2", "4", "5", "32"]
SHUTDOWN_STATES = ["6", "9", "13", "14", "20", "28", "34"]

# Heat level mappings
HEAT_LEVEL_POWER_MAP = {
    10: 1,
    50: 2,
    100: 3,
}

POWER_HEAT_LEVEL_MAP = {
    1: 10,
    2: 50,
    3: 100,
}

# Timer durations
TIMER_STARTUP_1 = 870  # 14:30 minutes in seconds
TIMER_STARTUP_2 = 870  # 14:30 minutes in seconds

# Service names
SERVICE_SET_HEATLEVEL = "set_heatlevel"
SERVICE_SET_TEMPERATURE = "set_temperature"
SERVICE_SET_OPERATION_MODE = "set_operation_mode"
SERVICE_START_STOVE = "start_stove"
SERVICE_STOP_STOVE = "stop_stove"
