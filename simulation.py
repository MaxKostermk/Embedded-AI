import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox

class LinUCB:
    def __init__(self, n_actions, context_dim, alpha):
        self.n_actions = n_actions
        self.context_dim = context_dim
        self.alpha = alpha

        # Initialize A (d x d identity matrix) and b (d-dimensional zero vector) for each action
        self.A = [np.eye(context_dim) for _ in range(n_actions)]
        self.b = [np.zeros((context_dim, 1)) for _ in range(n_actions)]

    def select_action(self, context):
        context = context.reshape(-1, 1)  # Ensure context is a column vector
        ucb_values = []

        for a in range(self.n_actions):
            A_inv = np.linalg.inv(self.A[a])
            theta = A_inv @ self.b[a]
            # Compute UCB for each action
            estimated_reward = theta.T @ context
            confidence = self.alpha * np.sqrt(context.T @ A_inv @ context)
            ucb = estimated_reward + confidence
            ucb_values.append(ucb)

        # Choose action with the highest UCB
        return np.argmax(ucb_values)

    # def update(self, action, context, reward):
    #     context = context.reshape(-1, 1)  # Ensure context is a column vector
    #     self.A[action] += context @ context.T
    #     self.b[action] += reward * context
    def update(self, action, context, reward, decay=0.99):
        context = context.reshape(-1, 1)
        self.A[action] = decay * self.A[action] + context @ context.T
        self.b[action] = decay * self.b[action] + reward * context


def simulate_temperature(current_temp, temperature_setpoint, outside_temp, k_heating, k_cooling, time_step):
    if temperature_setpoint < outside_temp:
        temperature_setpoint = outside_temp

    if current_temp < temperature_setpoint:
        k = k_heating
    else:
        k = k_cooling
    dT = -k * (current_temp - temperature_setpoint) * time_step
    return current_temp + dT

# Initialize cumulative_time at the start
cumulative_time = 0  # This should be done outside the function
total =0
def temperature_through_occupancy(occupancy, room_volume, t):
    global cumulative_time, total # Referencing the global variable
    if occupancy == 0:
        cumulative_time = 0  # Reset cumulative_time when occupancy is 0
        return 0
    else:
        time = t # Convert time to seconds
        cumulative_time += time  # Accumulate time properly
        specific_heat_air = 1005  # J/(kg*K)
        air_density = 1.225  # kg/m^3
        mass_air = air_density * room_volume  # kg
        energy = 70 * occupancy * cumulative_time # Energy based on occupancy
        temperature_change = energy / (mass_air * specific_heat_air)
        total += temperature_change# Calculate temperature change
        return temperature_change


# Parameters for LinUCB
n_actions = 21
context_dim = 3  # [temperature, humidity, occupancy]
alpha = 2.0

# Initialize LinUCB
linucb = LinUCB(n_actions, context_dim, alpha)
auto_button = False
# Simulation parameters
outside_temperature = 5.0
k_heating = 0.2
k_cooling = 0.05
time_step = 1.0
tolerance = 0.1
delay_after_reach = 0.2  # seconds
room_volume = 100  # m^3
occupancy = 0

# Initialize variables
times = []
temperatures = []
setpoints = []
current_temperature = outside_temperature
temperature_setpoint = outside_temperature
t = 0
context = np.array([current_temperature, 50, occupancy])
action = linucb.select_action(context)

# GUI setup
fig, ax = plt.subplots(figsize=(10, 6))
plt.subplots_adjust(bottom=0.3)  # Make space for buttons and text input

line, = ax.plot([], [], label="Room Temperature", color="blue", linewidth=2)
setpoint_line, = ax.plot([], [], 'r--', label="Setpoint Temperature")
ax.set_xlim(0, 100)
ax.set_ylim(0, 30)
ax.set_title("CMAB", fontsize=14)
ax.set_xlabel("Time", fontsize=12)
ax.set_ylabel("Temperature (°C)", fontsize=12)
ax.legend()
ax.grid(True)

# # Functions for buttons
# def update_plot():
#     global t, current_temperature, temperature_setpoint, context, action, delta_t
#     current_temperature = simulate_temperature(
#         current_temperature, temperature_setpoint, outside_temperature, k_heating, k_cooling, time_step
#     )
    
#     delta_t = temperature_through_occupancy(occupancy, room_volume, time_step)

#     times.append(t)
#     temperatures.append(current_temperature)
#     setpoints.append(temperature_setpoint)

#     line.set_data(times, temperatures)
#     setpoint_line.set_data(times, setpoints)
#     ax.set_xlim(0, max(100, t))
#     plt.draw()

#     t += time_step
#     # Check if the setpoint has been reached
#     if abs (current_temperature - temperature_setpoint) <= tolerance:
#         print(f"Reached setpoint: {temperature_setpoint}°C. Waiting for feedback...")
#         if auto_button and current_temperature < lower_temperature:
#             on_feedback("cold")
#         elif auto_button and current_temperature > upper_temperature:
#             on_feedback("hot")
#         elif auto_button: 
#             on_feedback("just_right")
#         return True
#     return False
window_size = 1700  # Number of points to display

def update_plot():
    global t, current_temperature, temperature_setpoint, context, action, delta_t
    current_temperature = simulate_temperature(
        current_temperature, temperature_setpoint, outside_temperature, k_heating, k_cooling, time_step
    )
    
    delta_t = temperature_through_occupancy(occupancy, room_volume, time_step)

    # Update the data lists
    times.append(t)
    temperatures.append(current_temperature)
    setpoints.append(temperature_setpoint)

    # Apply windowing: Keep only the last `window_size` points
    if len(times) > window_size:
        times.pop(0)
        temperatures.pop(0)
        setpoints.pop(0)

    # Update the plot lines
    line.set_data(times, temperatures)
    setpoint_line.set_data(times, setpoints)
    ax.set_xlim(max(0, t - window_size), t)  # Adjust x-axis to show only the windowed data
    plt.draw()

    t += time_step
    # Check if the setpoint has been reached
    if abs(current_temperature - temperature_setpoint) <= tolerance:
        print(f"Reached setpoint: {temperature_setpoint}°C. Waiting for feedback...")
        if auto_button and current_temperature < lower_temperature:
            on_feedback("cold")
        elif auto_button and current_temperature > upper_temperature:
            on_feedback("hot")
        elif auto_button: 
            on_feedback("just_right")
        return True
    return False

def on_feedback(feedback):
    global current_temperature, temperature_setpoint, context, action, occupancy

    # Map feedback to reward
    if feedback == "hot":
        reward = -1
    elif feedback == "cold":
        reward = -1
    elif feedback == "just_right":
        reward = 1
    else:
        reward = 0

    # Update LinUCB with the reward
    linucb.update(action, context, reward)

    # Select new action and setpoint
    context = np.array([current_temperature, 50, (occupancy/5)])  # Update context
    action = linucb.select_action(context)
    temperature_setpoint = action + 8

    print(f"New setpoint: {temperature_setpoint}°C")


def hot_callback(event):
    global auto_button
    auto_button = False
    on_feedback("hot")


def cold_callback(event):
    global auto_button
    auto_button = False
    on_feedback("cold")


def just_right_callback(event):
    global auto_button
    auto_button = False
    on_feedback("just_right")

def automatic_feedback(event):
    global auto_button 
    auto_button = True
    # if current_temperature < lower_temperature:
    #     return "cold"
    # elif current_temperature > upper_temperature:
    #     on_feedback("hot")
    # else:
    #     on_feedback("just_right")

def set_lower_temperature(text):
    global lower_temperature
    try:
        lower_temperature = float(text)
        print(f"Lower temperature set to: {lower_temperature}°C")
    except ValueError:
        print("Invalid input. Please enter a number.")

def set_upper_temperature(text):
    global upper_temperature
    try:
        upper_temperature = float(text)
        print(f"Upper temperature set to: {upper_temperature}°C")
    except ValueError:
        print("Invalid input. Please enter a number.")

def set_occupancy(text):
    global occupancy
    try:
        occupancy = int(text)
        print(f"Occupancy set to: {occupancy}")
    except ValueError:
        print("Invalid input. Please enter a number.")

# GUI widgets
ax_hot = plt.axes([0.1, 0.15, 0.2, 0.075])
ax_cold = plt.axes([0.4, 0.15, 0.2, 0.075])
ax_just_right = plt.axes([0.7, 0.15, 0.2, 0.075])
button_hot = Button(ax_hot, "Too Hot")
button_cold = Button(ax_cold, "Too Cold")
button_just_right = Button(ax_just_right, "Just Right")

ax_auto = plt.axes([0.1, 0.05, 0.125, 0.075])
button_auto = Button(ax_auto, "Auto")
ax_lower = plt.axes([0.325, 0.05, 0.125, 0.075])
ax_higher = plt.axes([0.550, 0.05, 0.125, 0.075])
textbox_lower = TextBox(ax_lower, "Lower:")
textbox_upper = TextBox(ax_higher, "Upper:")
ax_occupancy = plt.axes([0.775, 0.05, 0.125, 0.075])  # Adjusted position to upper left corner
textbox_occupancy = TextBox(ax_occupancy, "Occupancy:", initial=0)
# ax_text = plt.axes([0.3, 0.15, 0.4, 0.075])
# text_box = TextBox(ax_text, "Start Temp:", initial="20")

# Button events
button_hot.on_clicked(hot_callback)
button_cold.on_clicked(cold_callback)
button_just_right.on_clicked(just_right_callback)
button_auto.on_clicked(automatic_feedback)
textbox_lower.on_submit(set_lower_temperature)
textbox_upper.on_submit(set_upper_temperature)
textbox_occupancy.on_submit(set_occupancy)
# text_box.on_submit(set_initial_temperature)

# Simulation loop
def main_loop():
    try:
        while True:
            if update_plot():
                plt.pause(delay_after_reach)
            else:
                plt.pause(0.1)
    except KeyboardInterrupt:
        print("Simulation interrupted.")
        plt.ioff()
        plt.show()

# Start the simulation
main_loop()
