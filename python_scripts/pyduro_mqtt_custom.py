#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------

#---import
from pyduro.actions import FUNCTIONS, STATUS_PARAMS, discover, get, set, raw
import paho.mqtt.client as mqtt
import asyncio

import json
import time
from datetime import date, timedelta

# ------------------------------------------------------------------------------
# Get data from Home Assistant

MQTT_SERVER_IP   = data.get('MQTT_SERVER_IP')
MQTT_SERVER_PORT = data.get('MQTT_SERVER_PORT')
MQTT_BASE_PATH   = data.get('MQTT_BASE_PATH')
MQTT_USERNAME    = data.get('MQTT_USERNAME')
MQTT_PASSWORD    = data.get('MQTT_PASSWORD')
STOVE_SERIAL     = data.get('STOVE_SERIAL')
STOVE_PIN        = data.get('STOVE_PIN')
MODE             = data.get('MODE')
STOVE_BOIL_REF   = data.get('STOVE_BOIL_REF')
STOVE_OPERATION_MODE = data.get('STOVE_OPERATION_MODE')
STOVE_PATH       = data.get('STOVE_PATH')
STOVE_VALUE      = data.get('STOVE_VALUE')


#-------------------------------------------------------------------------------
#MQTT stuff
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    dummy_block_statement = 0
    #print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #MQTT_BASE_PATH = "aduro_h2" + "/"
    #client.subscribe(MQTT_BASE_PATH)

# The callback when the client disconnects from server
async def on_disconnect(client, userdata,rc=0):
    #logging.debug("DisConnected result code "+str(rc))
    await client.loop_stop()

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    # more callbacks, etc
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Get Stove Discovery data
def get_discovery_data(aduro_cloud_backup_address = "apprelay20.stokercloud.dk"):
    from pyduro.actions import FUNCTIONS, STATUS_PARAMS, discover, get, set, raw
    import json

    result          = 0
    serial          = " "
    ip              = "no connection"
    device_type     = " "
    version         = " "
    build           = " "
    lang            = " "
    mqtt_json_data  = " "
    discovery_json  = " "

    try:
        response = discover.run()
        response = response.parse_payload()
    except:
        result = -1
        discovery_json = {"DISCOVERY": {"StoveSerial": serial, "StoveIP": ip, "NBE_Type": device_type, "StoveSWVersion": version, "StoveSWBuild": build, "StoveLanguage": lang}} 
        mqtt_json_data = json.dumps(discovery_json)
        return result, ip, serial, mqtt_json_data

    response = json.dumps(response)

    # JSON in ein Python-Dictionary umwandeln
    data = json.loads(response)

    # Variablen extrahieren
    serial      = data['Serial']
    ip          = data['IP']
    device_type = data['Type']
    version     = data['Ver']
    build       = data['Build']
    lang        = data['Lang']

    # check if IP is valid. fallback to Stove Cloud address if not valid    
    if "0.0.0.0" in ip:
        ip = aduro_cloud_backup_address

    if response:
        discovery_json = {"DISCOVERY": {"StoveSerial": serial, "StoveIP": ip, "NBE_Type": device_type, "StoveSWVersion": version, "StoveSWBuild": build, "StoveLanguage": lang}} 
        mqtt_json_data = json.dumps(discovery_json)
        result = 0
        #print(mqtt_json_data)
        return result, ip, serial, mqtt_json_data
    else:
        result = -1
        #print('no connection to stove')
        return result, ip, serial, mqtt_json_data
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Set boiler_ref
def set_boiler_ref(ip, STOVE_SERIAL, STOVE_PIN, set_ref_temp):
    from pyduro.actions import FUNCTIONS, STATUS_PARAMS, discover, get, set, raw
    import json

    response = set.run( burner_address=str(ip),
                        serial=str(STOVE_SERIAL),
                        pin_code=str(STOVE_PIN),
                        path="boiler.temp",
                        value=set_ref_temp
                        )
    data = response.parse_payload()
    #print(data)
    if data == "":
        result = 0
    else:
        result = -1
        return result
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Set operation_mode
def set_operation_mode_ref(ip, STOVE_SERIAL, STOVE_PIN, set_ref_operation_mode):
    from pyduro.actions import FUNCTIONS, STATUS_PARAMS, discover, get, set, raw
    import json

    response = set.run( burner_address=str(ip),
                        serial=str(STOVE_SERIAL),
                        pin_code=str(STOVE_PIN),
                        path="regulation.operation_mode",
                        value=set_ref_operation_mode
                        )
    data = response.parse_payload()
    #print(data)
    if data == "":
        result = 0
    else:
        result = -1
        return result
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# Set custom
def set_custom(ip, STOVE_SERIAL, STOVE_PIN, custom_path, custom_value):
    from pyduro.actions import FUNCTIONS, STATUS_PARAMS, discover, get, set, raw
    import json

    response = set.run( burner_address=str(ip),
                        serial=str(STOVE_SERIAL),
                        pin_code=str(STOVE_PIN),
                        path=custom_path,
                        value=custom_value
                        )
    data = response.parse_payload()
    #print(data)
    if data == "":
        result = 0
    else:
        result = -1
        return result
#-------------------------------------------------------------------------------


#--------------------------------[MAIN]-----------------------------------------
#logger.info(f"starting Pyduro script!")

#init Mqtt stuff if script shall send mqtt data
if MQTT_SERVER_IP != None:
    client = mqtt.Client()
    client.on_connect == on_connect
    client.on_message = on_message
    client.username_pw_set(username=MQTT_USERNAME,password=MQTT_PASSWORD)
    client.connect(MQTT_SERVER_IP, MQTT_SERVER_PORT, 60)
    client.subscribe(MQTT_BASE_PATH)
    client.loop_start()
#-------------------------------------------------------------------------------

# get previous discovered stove IP from Home Assistant
ip = hass.states.get('sensor.aduro_h2_stove_ip').state
#logger.info(f"IP from HA:{ ip}")

# check if IP is valid. fallback to Stove Cloud address if not valid
aduro_cloud_backup_address = "apprelay20.stokercloud.dk"

# workaround if stove lost router ipv4 -> switch to cloud server address 
if "0.0.0.0" in ip or ip == "unknown" or ip == "no connection" or ip == aduro_cloud_backup_address:
    try:
        result, ip, serial, mqtt_json_discover_data = get_discovery_data()
        if "0.0.0.0" in ip:
            ip = aduro_cloud_backup_address

        discovery_json = json.loads(mqtt_json_discover_data)
        discovery_json['DISCOVERY']['StoveIP'] = ip
        discovery_json['DISCOVERY']['StoveSerial'] = serial
        mqtt_json_discover_data = json.dumps(discovery_json)

        if MQTT_SERVER_IP != None:
            client.publish(MQTT_BASE_PATH + "discovery", str(mqtt_json_discover_data))
            time.sleep(0.2)
    except:
        #logger.info(f"Discovery Exeption!")
        if MQTT_SERVER_IP != None:
            client.disconnect()
        exit()
#-------------------------------------------------------------------------------


#-------------------------------------------------------------------------------
# Set boiler_ref
if MODE == "set_temp":
    try:
        result = set_boiler_ref(ip, serial, STOVE_PIN, STOVE_BOIL_REF)
    except:
        #retries 3 times
        for x in range(0, 3):
            time.sleep(1)
            result, ip, serial, mqtt_json_discover_data = get_discovery_data()
            result = set_boiler_ref(ip, serial, STOVE_PIN, STOVE_BOIL_REF)
            if result != -1:
                break
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Set operation_mode_ref
if MODE == "set_operation_mode":
    try:
        result = set_operation_mode_ref(ip, serial, STOVE_PIN, STOVE_OPERATION_MODE)
    except:
        #retries 3 times
        for x in range(0, 3):
            time.sleep(1)
            result, ip, serial, mqtt_json_discover_data = get_discovery_data()
            result = set_operation_mode_ref(ip, serial, STOVE_PIN, STOVE_OPERATION_MODE)
            if result != -1:
                break
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# Set custom
if MODE == "set_custom":
    try:
        result = set_custom(ip, serial, STOVE_PIN, STOVE_PATH, STOVE_VALUE)
    except:
        #retries 3 times
        for x in range(0, 3):
            time.sleep(1)
            result, ip, serial, mqtt_json_discover_data = get_discovery_data()
            result = set_custom(ip, serial, STOVE_PIN, STOVE_PATH, STOVE_VALUE)
            if result != -1:
                break
# ------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
if MQTT_SERVER_IP != None:
    client.disconnect()

