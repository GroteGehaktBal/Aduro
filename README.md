# Aduro Hybrid Stove Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/GroteGehaktBal/Aduro.svg)](https://github.com/GroteGehaktBal/Aduro/releases)

Control and monitor your **Aduro Hybrid pellet stove** directly from Home Assistant! 🔥

This custom integration provides a complete Home Assistant integration for Aduro Hybrid stoves, based on excellent work from [SpaceTeddy](https://github.com/SpaceTeddy/homeassistant_aduro_stove_control_python_scripts) and [clementprevot](https://github.com/clementprevot/pyduro).

## ✨ Features

- 🔥 **Start/Stop Control** - Turn your stove on and off remotely
- 🌡️ **Temperature Monitoring** - Track smoke, shaft, and boiler temperatures in real-time
- ⚙️ **Heat Level Control** - Easily set heat levels (I, II, III)
- 📊 **Consumption Tracking** - Monitor pellet usage (daily, monthly, yearly)
- 🎯 **Dual Operation Modes** - Switch between heat level and temperature control modes
- 🔔 **Smart Notifications** - Get alerts for low pellets, errors, and state changes
- 📱 **Beautiful UI** - Fully compatible with Mushroom cards and Lovelace
- 🔌 **Easy Installation** - Install via HACS with just a few clicks!

## 📸 Screenshots
1. Temperature mode
![Screenshot UI](https://github.com/NewImproved/Aduro/blob/main/UI_2.jpg)

2. Mode change to temperature mode
![Screenshot UI mode change](https://github.com/NewImproved/Aduro/blob/main/UI_3.jpg)

## 🚀 Installation

### Via HACS (Recommended)

1. **Add Custom Repository**
   - Open HACS in Home Assistant
   - Click on **Integrations**
   - Click the **⋮** menu (top right) and select **Custom repositories**
   - Add this repository: `https://github.com/GroteGehaktBal/Aduro`
   - Select category: **Integration**
   - Click **Add**

2. **Install Integration**
   - Find **"Aduro Hybrid Stove"** in HACS
   - Click **Download**
   - Restart Home Assistant

3. **Configure Integration**
   - Go to **Settings** → **Devices & Services**
   - Click **+ Add Integration**
   - Search for **"Aduro Hybrid Stove"**
   - Enter your configuration:
     - **Stove Serial Number** (found in your Aduro app or on the stove)
     - **Stove PIN Code** (4-digit PIN for your stove)
     - **MQTT Broker Host** (e.g., `192.168.1.100` or `localhost`)
     - **MQTT Port** (default: `1883`)
     - **MQTT Username** (optional)
     - **MQTT Password** (optional)
   - Click **Submit**

✅ **Done!** Your Aduro stove is now integrated into Home Assistant!

### Manual Installation (Advanced)

1. Copy the `custom_components/aduro` directory to your Home Assistant `custom_components` folder
2. Restart Home Assistant
3. Follow step 3 from the HACS installation above

## 📋 Prerequisites

Before installing this integration, make sure you have:

- ✅ **Aduro Hybrid pellet stove** with network connectivity
- ✅ **MQTT Broker** installed and running (e.g., [Mosquitto](https://github.com/home-assistant/addons/tree/master/mosquitto))
- ✅ **Home Assistant** 2024.1.0 or newer
- ✅ Your stove's **serial number** and **PIN code**

## 🎛️ What You Get

### 🔘 Entities Created

#### Sensors
- **Temperature Sensors**
  - Smoke temperature
  - Shaft temperature
  - Boiler/room temperature
- **State Sensors**
  - Current stove state (operating, stopped, error, etc.)
  - Sub-state details
  - Operation mode (Heat Level / Temperature / Wood)
- **Consumption Sensors**
  - Daily pellet consumption
  - Yesterday's consumption
  - Monthly consumption
  - Yearly consumption
- **Pellet Level Sensors**
  - Remaining pellets (kg)
  - Pellet percentage (%)
- **Other Sensors**
  - Power output (kW)
  - Oxygen level (ppm)
  - Stove IP address

#### Controls
- **Switch**: Turn stove on/off
- **Number Entities**:
  - Heat level (1-3)
  - Target temperature (5-35°C)
  - Pellet capacity setting
  - Notification threshold
  - Auto-shutdown threshold
- **Buttons**:
  - Mark as refilled
  - Mark as cleaned
  - Toggle operation mode

### 🔧 Services

The integration provides these services for automation:

```yaml
# Set heat level (1-3)
service: aduro.set_heatlevel
data:
  heatlevel: 2

# Set target temperature
service: aduro.set_temperature
data:
  temperature: 22

# Set operation mode (0=Heat Level, 1=Temperature, 2=Wood)
service: aduro.set_operation_mode
data:
  mode: 1

# Start the stove
service: aduro.start_stove

# Stop the stove
service: aduro.stop_stove
```

## 💡 Usage Examples

### Simple Automation - Start stove when cold

```yaml
automation:
  - alias: "Start stove when cold"
    trigger:
      - platform: numeric_state
        entity_id: sensor.aduro_boiler_temperature
        below: 18
    condition:
      - condition: time
        after: "06:00:00"
        before: "22:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.aduro_stove_power
```

### Low Pellet Notification

```yaml
automation:
  - alias: "Notify when pellets low"
    trigger:
      - platform: numeric_state
        entity_id: sensor.aduro_pellet_percentage
        below: 20
    action:
      - service: notify.mobile_app
        data:
          title: "Aduro Stove"
          message: "Pellet level is {{ states('sensor.aduro_pellet_percentage') }}%"
```

## 🎨 Dashboard Example

Use Mushroom cards for a beautiful interface:

```yaml
type: vertical-stack
cards:
  - type: custom:mushroom-entity-card
    entity: switch.aduro_stove_power
    icon: mdi:fireplace
    name: Aduro Stove
    
  - type: custom:mushroom-number-card
    entity: number.aduro_heat_level
    icon: mdi:fire
    name: Heat Level
    
  - type: custom:mushroom-chips-card
    chips:
      - type: entity
        entity: sensor.aduro_boiler_temperature
      - type: entity
        entity: sensor.aduro_pellet_percentage
      - type: entity
        entity: sensor.aduro_power
```

## 🔄 Migration from Old Setup

If you're using the old manual YAML configuration:

1. **Backup your configuration**
2. **Install this integration via HACS** (see installation above)
3. **Configure the integration** through the UI
4. **Remove old YAML configuration**:
   - Remove `aduro.yaml` includes from `configuration.yaml`
   - Remove `pyduro_scripts.yaml` includes
   - Remove `mqtt_devices.yaml` includes
   - Remove old `python_scripts/pyduro_*.py` files
5. **Restart Home Assistant**
6. **Update your Lovelace dashboards** to use the new entity names

The new integration uses cleaner entity IDs like:
- `sensor.aduro_smoke_temperature` (was `sensor.aduro_h2_smoke_temperature`)
- `switch.aduro_stove_power` (was `input_boolean.aduro_start_stop`)
- `number.aduro_heat_level` (was `input_number.aduro_heatlevel`)

## 🐛 Troubleshooting

### Integration not found
- Make sure you've restarted Home Assistant after installation
- Check that the `custom_components/aduro` folder exists

### Cannot connect to stove
- Verify your stove serial number and PIN are correct
- Check that your MQTT broker is running
- Ensure your stove is connected to your network
- Try the cloud address if local discovery fails (integration does this automatically)

### Entities not updating
- Check your MQTT broker logs
- Verify the pyduro and paho-mqtt dependencies installed correctly
- Enable debug logging (see below)

### Enable Debug Logging

Add to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.aduro: debug
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 Credits

This integration builds upon the excellent work of:
- [SpaceTeddy](https://github.com/SpaceTeddy/homeassistant_aduro_stove_control_python_scripts) - Original Home Assistant scripts
- [clementprevot](https://github.com/clementprevot/pyduro) - pyduro Python library

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This is an unofficial integration and is not affiliated with or endorsed by Aduro. Use at your own risk.

---

## 🗂️ Legacy Documentation (Old Manual Setup)

The sections below are kept for reference but are **no longer needed** with the new integration.

<details>
<summary>Click to expand old documentation</summary>

### Old Entity Types (No longer needed - now created automatically)

**Utility Meter**: Tracks the amount of pellets consumed (aduro_consumed_amount_of_pellets).

**Counters**: Tracks the number of times the stove has been refilled without being cleaned (aduro_pellets_refill_counter).

**Input Booleans**: Toggles for starting/stopping the stove, toggling heat targets, and shutting down at specific pellet levels.

**Input Numbers**: Configurable values for heat levels, boiler reference temperature, pellet capacity, and notification thresholds.

**Input Buttons**: Buttons for marking the stove as refilled or cleaned.

### Old Manual Installation (Deprecated)

1. You will need a MQTT-broker. I use Mosquitto broker.
2. Follow instruction in https://github.com/SpaceTeddy/homeassistant_aduro_stove_control_python_scripts. Which includes installation of:
   * PythonScriptsPro (https://github.com/AlexxIT/PythonScriptsPro) for HA
   * pyduro (https://github.com/clementprevot/pyduro) as standard python library to get connection to the stove.
   * paho-mqtt (https://github.com/eclipse/paho.mqtt.python) library is required for python mqtt connectivity.  
3. I use Mushroom cards for the UI.
4. Update your configuration with the files and/or lines in the files.

**Note**: The above steps are no longer required! Just install via HACS as described in the installation section above.

</details>

