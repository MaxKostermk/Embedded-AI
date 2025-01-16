from Algorithm.simulation import ContextualBandit, get_context
from qrcodewebapp.sensors import read_temp, read_occ, read_valve, init_db, GENERALURL, TOKEN          
import sqlite3
from datetime import datetime, timedelta
import requests
import time
import os

# Paths and constants
DB_FILE = os.path.join(os.path.dirname(__file__), 'database', 'feedback.db')

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",  
    "Content-Type": "application/json",
}

n_actions = 21  
n_contexts = 330  
bandit = ContextualBandit(n_actions, n_contexts, epsilon=0.1)
last_valve_state = None

def get_feedback():
    """Retrieve recent feedback from the database."""

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT feedback_type, MAX(timestamp) FROM feedback WHERE timestamp > ?", (datetime.now() - timedelta(minutes=10),))
    row = cursor.fetchone()
    conn.close()

    if row and row[0]:  # Check if feedback exists
        return row[0]  # Return feedback type ("too hot", "too cold")
    return None  

def map_feedback_to_reward(feedback, action, temp, valve_adjustment):
    """Map user feedback to reward values."""

    reward = 0.0

    if feedback == "too hot" and action > temp:
        reward += 0.5  # Penalize if thermostat setting is too high
    elif feedback == "too cold" and action < temp:
        reward += 0.5  # Penalize if thermostat setting is too low
    elif feedback:
        reward += 1.0  # Positive reward for matching feedback
    if valve_adjustment == "increase" and action < temp + 1:
        reward += 0.5  # Reward for increasing the thermostat when the valve suggests it
    elif valve_adjustment == "decrease" and action > temp - 1:
        reward += 0.5  # Reward for decreasing the thermostat when the valve suggests it
    return reward


def detect_valve_adjustment(current_valve_state):
    """Detect if the valve has been adjusted since the last state."""
    global last_valve_state
    adjustment = None

    if last_valve_state is not None:
        if current_valve_state > last_valve_state:
            adjustment = "increase"  # User turned the valve up
        elif current_valve_state < last_valve_state:
            adjustment = "decrease"  # User turned the valve down
    last_valve_state = current_valve_state
    return adjustment

def update_valve_temperature(ideal_temperature):
    """Send the calculated ideal temperature to the valve."""
    payload = {"entity_id": "climate.sonoff_trvzb_thermostat", "temperature": ideal_temperature}
    try:
        response = requests.post("http://localhost:8123/api/services/climate/set_temperature", headers=HEADERS, json=payload) # be sure to change "valve" to actual URL that home assistant shows.
        response.raise_for_status()
        print(f"Valve updated to: {ideal_temperature}°C")
    except requests.RequestException as e:
        print(f"Failed to update valve: {e}")

def get_from_db(type, rows):
    """Simple function to get data from historical database"""

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    if type == feedback:
        cursor.execute("SELECT feedback_type, MAX(timestamp) FROM feedback WHERE timestamp > ?", (datetime.now() - timedelta(minutes=10),))
    else:
        cursor.execute("SELECT  FROM sensor WHERE timestamp > ?", (datetime.now() - timedelta(minutes=10),))
    row = cursor.fetchone()
    conn.close()

init_db()

for _ in range(100):  #100 iterations
    temperature = read_temp(GENERALURL + "sensor.lumi_lumi_sensor_ht_agl02_temperature")
    occupancy = read_occ(GENERALURL + "binary_sensor.presence_sensor_fp2_a6a8_presence_sensor_1")
    valve_state = read_valve(GENERALURL + "climate.eurotronic_spzb0001_thermostat")

    # Derive context
    context = get_context(temperature, 50, occupancy)  # Assuming fixed humidity for simplicity

    # Bandit selects an action
    action = bandit.select_action(context)
    ideal_temperature = 15 + action  # Map action (0–20) back to the temperature range (15–35°C)

    # Detect valve adjustments
    valve_adjustment = detect_valve_adjustment(valve_state)

    # Get user feedback
    feedback = get_feedback()

    # Map feedback (user and valve) to reward
    reward = map_feedback_to_reward(feedback, ideal_temperature, temperature, valve_adjustment)

    # Update bandit with feedback
    if reward > 0.0:  # Update only if there is feedback or valve adjustment
        bandit.update(context, action, reward)

    # Report the calculated ideal temperature to the valve
    update_valve_temperature(ideal_temperature)
    time.sleep(10)

