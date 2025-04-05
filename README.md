# Aduro hybrid
The provided components in the directory defines various entities, sensors, automations, and scripts to manage and monitor the operation of an Aduro Hybrid stove in Home Assistant. Based out of work from [SpaceTeddy](https://github.com/SpaceTeddy/homeassistant_aduro_stove_control_python_scripts) and [clementprevot](https://github.com/clementprevot/pyduro).  
Here's a breakdown of its main functionality:

## 0. Screen shot examples
1. Temperature mode
![Screenshot UI](https://github.com/NewImproved/Aduro/blob/main/UI_2.jpg)

2. Mode change to temperature mode
![Screenshot UI mode change](https://github.com/NewImproved/Aduro/blob/main/UI_3.jpg)

## 1. Entities
The configuration defines several types of entities to interact with the Aduro stove:

### Utility Meter:

Tracks the amount of pellets consumed (aduro_consumed_amount_of_pellets).
### Counters:

Tracks the number of times the stove has been refilled without being cleaned (aduro_pellets_refill_counter).
### Input Booleans:

Toggles for starting/stopping the stove, toggling heat targets, and shutting down at specific pellet levels (shuting down at specific level requires my actionable notification script to work without modification).
### Input Numbers:

Configurable values for heat levels, boiler reference temperature, pellet capacity, and notification thresholds (Notifications requires my actionable notification script to work without modification).
### Input Buttons:

Buttons for marking the stove as refilled or cleaned.
## 2. Sensors
The configuration defines multiple template sensors to calculate and monitor stove states:

### Pellet Levels:

Calculates the remaining amount and percentage of pellets in the stove.
### Boolean Checks:

Verifies if the current heat level, boiler temperature, or operation mode matches the target values.
### Operation Mode:

Tracks the stove's operation mode and transitions between heat level and temperature modes.
### Display Formatting:

Formats the display text for the current operation mode, heat level, or temperature.
### State Tracking:

Tracks the stove's main and sub-states (e.g., startup, normal operation, errors).
## 3. Automations
The automations handle various events and actions related to the stove:

### State-Based Automations:

Automatically turns the stove input_boolean on/off based on the stoves state.
Updates input values (e.g., heat level, boiler reference) when the stove's state changes (i.e. when aduros application is used).
### Mode Transitions:

Manages and displays transitions between heat level and temperature modes.
Updates sensors and triggers actions when mode changes occur.
### Notifications:

Sends notifications for low pellet levels, errors, or state changes.
Includes actionable notifications for shutting down the stove when pellet levels are critically low.
Requires my actionable notification script to work without modification.
### Fallbacks:

Handles fallback actions if changes (e.g., mode transitions) are not completed within a certain time.
## 4. Scripts
The configuration references scripts (e.g., pyduro_set_heatlevel, pyduro_set_temp) to interact with the stove. These scripts likely send commands to the stove via MQTT or another protocol.

## 5. Notifications
The configuration includes actionable notifications to alert users about:

Low pellet levels.  
Stove errors or warnings.  
State changes (mostly related to involuntary shutdown shutdown).  
Notifications requires my actionable notification script to work without modification, to work without modification.

## 6. MQTT Integration
The configuration includes automations to trigger MQTT calls to synchronize the stove's state with Home Assistant.

## 7. Error Handling
The configuration includes mechanisms to handle errors or unexpected states:

Automatically resets toggles and timers.
Sends notifications for specific error states (e.g., no fuel, failed ignition).
## 8. Development needed

The conversion between the different states/sub states are not done. Many states are not yet defined. The common ones (at least for me) are defined. The states that are defined are written in swedish in the code. These are not translated because I don't want the wording to be wrong.

My aim is to calculate an aproximate time when the stove is going to run out of pellets, but this will probably have to wait until next winter.
## 9. Installation/usage
1. You will need a MQTT-broker. I use Mosquitto broker.
2. Follow instruction in https://github.com/SpaceTeddy/homeassistant_aduro_stove_control_python_scripts. Which includes installation of:
   * PythonScriptsPro (https://github.com/AlexxIT/PythonScriptsPro) for HA
   * pyduro (https://github.com/clementprevot/pyduro) as standard python library to get connection to the stove.
   * paho-mqtt (https://github.com/eclipse/paho.mqtt.python) library is required for python mqtt connectifity.  
3. I use Mushroom cards for the UI.
4. Update your configuration with the files and/or lines in the files. I have included all my Aduro related files in this repository, some will be duplicates from the installations in first step. Some will have the same name, but with additional code. Some of the files will add to the original installation.
5. If your setup differs from mine, you might have to change references in the scripts/files.
6. For notifications/auto shutdown etc. to work without modification, use my actionable notification script (https://github.com/NewImproved/Actionable-notifications-script). If you want to modify the script, all notification automations are located all the way down in aduro.yaml

## 10. Summary
This YAML file is a comprehensive configuration for managing an Aduro stove in Home Assistant. It provides:

* Real-time monitoring of the stove's state, pellet levels, and operation mode.
* Automation of common tasks (e.g., starting/stopping the stove, switching modes).
* Notifications for critical events (e.g., low pellets, errors).
* Integration with MQTT for communication with the stove.

This setup ensures efficient and automated control of the Aduro stove while keeping the user informed of its status.
