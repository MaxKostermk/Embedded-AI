import os
from requests import get
import datetime

GENERALURL = "http://217.63.23.225:8123/api/states/"

TOKEN = ""
 # home assistant token

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}



def read_valve(url):
    """
    Eurotronic Comet Zigbee
    """
    response = get(url, headers=HEADERS).json()['state'] # edit to the right value that shows valve feedback in HA
    return response

def read_occ(url):
    """
    Aqara Aanwezigheidssensor PS-S02D
    Read presence sensor function
    Does not work with Zigbee, only Wi-Fi/BLE
    """
    response = get(url, headers=HEADERS).json()['state'] # edit to the right value that shows occupancy in HA
    if response == 'on':
        response = 1
    elif response == 'off':
        response = 0

    return response

def read_temp(url):
    """
    Aqara Temperatuursensor en luchtvochtigheidssensor TH-S02D
    """
    response = get(url, headers=HEADERS).json()['state'] # edit to the right value that shows temperature in HA

    return response
