import os
import sqlite3
from requests import get
import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), 'database', 'feedback.db')

GENERALURL = "http://localhost:8123/api/states/"

TOKEN = "" # home assistant token

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",  
    "Content-Type": "application/json",
}

def init_db():
    """Create the sensor reading table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sensor (
        timestamp TIMESTAMP NOT NULL,
        value TEXT NOT NULL,
        device_id TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()

def read_valve(url):
    """
    Eurotronic Comet Zigbee
    """

    response = get(url, headers=HEADERS).json()['temperature'] # edit to the right value that shows valve feedback in HA
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO sensor (timestamp, value, device_id) VALUES (?, ?, ?)", (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), response, "valve" ))
    conn.commit()
    conn.close()

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
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO sensor (timestamp, value, device_id) VALUES (?, ?, ?)", (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), response, "occ" ))
    conn.commit()
    conn.close()

    return response

def read_temp(url):
    """
    Aqara Temperatuursensor en luchtvochtigheidssensor TH-S02D
    """
    response = get(url, headers=HEADERS).json()['state'] # edit to the right value that shows temperature in HA
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO sensor (timestamp, value, device_id) VALUES (?, ?, ?)", (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), response, "temp" ))
    conn.commit()
    conn.close()
    return response

