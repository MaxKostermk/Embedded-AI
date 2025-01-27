import appdaemon.plugins.hass.hassapi as hass
from Algorithm.bandit import ContextualBandit, LinUCB, get_context
from qrcodewebapp.sensors import read_temp, read_occ, read_valve, GENERALURL, TOKEN
from datetime import datetime, timedelta
import requests
import time
import os
import numpy as np
GENERALURL = "http://localhost:8123/api/states/"

class optimal_temperature(hass.Hass):
    def initialize(self):
    # Paths and constants
        self.log("starting")
        self.HEADERS = {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        }

        self.n_actions = 21
        self.n_contexts = 330
        self.initial_epsilon = 1.0  # Start with full exploration
        self.epsilon_decay = 0.4  # Decay factor for exploration
        self.min_epsilon = 0.1  # Minimum exploration rate
        self.bandit = ContextualBandit(self.n_actions, self.n_contexts, epsilon=0.1)
        self.last_valve_state = None
        self.old_environment = {'temperature': 20, 'humidity': 50, 'occupancy': 2}
        self.log("running")
        self.run_every(self.run, "now", 3*10*60)

    def run(self, kwargs):
        try:
            occupancy = read_occ(GENERALURL + "binary_sensor.presence_sensor_fp2_a6a8_presence_sensor_1")
            self.log("1")
            temperature =float(read_temp(GENERALURL + "sensor.lumi_lumi_sensor_ht_agl02_temperature"))
            self.log("2")

            self.bandit.epsilon = max(self.min_epsilon, self.bandit.epsilon * self.epsilon_decay)
            environment = {
                "temperature": float(temperature),
                'humidity': 50,  # Assuming fixed humidity for simplicity
                "occupancy": occupancy
            }

            context = get_context(environment['temperature'], environment['humidity'], environment['occupancy'], self.n_contexts)
            action = self.bandit.select_action(context)

            feedback = self.get_feedback(action)
            reward = self.get_reward(feedback)
            context = get_context(temperature, 50, occupancy, self.n_contexts)  # Assuming fixed humidity for simplicity
            action = self.bandit.select_action(context)
            self.log(action + 8)
            if temperature > (action + 8):
                ideal_temperature = 4
            elif temperature < (action + 8):
                ideal_temperature = 35
            elif temperature == (action + 8):
                ideal_temperature = 20

            self.bandit.update(context, action, reward)
            self.old_environment = environment
            self.log("temperature: ", temperature)
            self.log(ideal_temperature)
            self.update_valve_temperature(ideal_temperature)
        except Exception as e:
            print(f"Error: {e}")

    def get_feedback(self, action):
        if (action + 8) < 19:
            return 'too cold'
        elif (action + 8) > 24:
            return 'too warm'
        else:
            return 'comfortable'


    def map_feedback_to_reward(self, feedback, action, temp, valve_adjustment):
        """Map user feedback to reward values."""

        reward = 0.0

        if feedback == "too hot" and action > temp:
            reward += 0.5  # Penalize if thermostat setting is too high
        elif feedback == "too cold" and action < temp:
            reward += 0.5  # Penalize if thermostat setting is too low
        elif feedback == "comfortable":
            reward += 1.0  # Positive reward for matching feedback
        return reward

    def get_reward(self,feedback):
        reward_map = {'comfortable': 1.0, 'too warm': 0.4, 'too cold': 0.4}
        return reward_map.get(feedback, 0.0)

    def detect_valve_adjustment(self, current_valve_state):
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

    def update_valve_temperature(self, ideal_temperature):
        """Send the calculated ideal temperature to the valve."""
        payload = {"entity_id": "climate.sonoff_trvzb_thermostat", "temperature": ideal_temperature}
        try:
            response = requests.post("http://localhost:8123/api/services/climate/set_temperature", headers=self.HEADERS, json=payload) # be sure to change to actual URL that home assistant shows.
            response.raise_for_status()
            print(f"Valve updated to: {ideal_temperature}°C")
        except requests.RequestException as e:
            print(f"Failed to update valve: {e}")
