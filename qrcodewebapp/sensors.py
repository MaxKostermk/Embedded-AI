import os
import sqlite3
from requests import get

DB_FILE = os.path.join(os.path.dirname(__file__), 'database', 'feedback.db')


headers = {
    "Authorization": "Bearer TOKEN",
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
        device_identifier TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()

def read_valve():
    """
    Eurotronic Comet Zigbee
    """
    url = "http://localhost:8123/api/valve" # URL from home assistant
    response = get(url, headers=headers)
    


def read_occ():
    """
    Aqara Aanwezigheidssensor PS-S02D 
    Read presence sensor function
    Does not work with Zigbee, only Wi-Fi/BLE
    """
    url = "http://localhost:8123/api/presence" # URL from home assistant
    response = get(url, headers=headers)
    

def read_temp():
    """
    Aqara Temperatuursensor en luchtvochtigheidssensor TH-S02D
    """
    url = "http://localhost:8123/api/temp" # URL from home assistant
    response = get(url, headers=headers)

