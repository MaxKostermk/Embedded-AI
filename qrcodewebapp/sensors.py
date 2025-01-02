import os
import sqlite3
from requests import get
import datetime
from main import GENERALURL

DB_FILE = os.path.join(os.path.dirname(__file__), 'database', 'feedback.db')

headers = {
    "Authorization": "Bearer TOKEN", #replace TOKEN with Home Assistant token.
    "content-type": "application/json"
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

def read_valve():
    """
    Eurotronic Comet Zigbee
    """
    url = GENERALURL + "valve" # URL from home assistant (replace with actual URL)
    response = get(url, headers=headers).json()['state'] # edit to the right value that shows valve feedback in HA
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO sensor (timestamp, value, device_id) VALUES (?, ?, ?)", (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), response, "valve" ))
    conn.commit()
    conn.close()
    return float(response)

def read_occ():
    """
    Aqara Aanwezigheidssensor PS-S02D 
    Read presence sensor function
    Does not work with Zigbee, only Wi-Fi/BLE
    """
    url = GENERALURL + "presencesensor" # URL from home assistant (replace with actual URL)
    response = get(url, headers=headers).json()['state'] # edit to the right value that shows occupancy in HA
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO sensor (timestamp, value, device_id) VALUES (?, ?, ?)", (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), response, "occ" ))
    conn.commit()
    conn.close()
    return int(response)

def read_temp():
    """
    Aqara Temperatuursensor en luchtvochtigheidssensor TH-S02D
    """
    url = GENERALURL + "tempsensor" # URL from home assistant (replace with actual URL)
    response = get(url, headers=headers).json()['temperature'] # edit to the right value that shows temperature in HA

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO sensor (timestamp, value, device_id) VALUES (?, ?, ?)", (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), response, "temp" ))
    conn.commit()
    conn.close()
    return float(response)

# WIP - loop where readings are taken, functions are called.

