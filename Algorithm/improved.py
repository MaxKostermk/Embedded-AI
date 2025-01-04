import numpy as np
import matplotlib.pyplot as plt

class ContextualBandit:
    def __init__(self, n_actions, n_contexts, epsilon):
        self.n_actions = n_actions
        self.n_contexts = n_contexts
        self.epsilon = epsilon
        self.q_values = np.full((n_contexts, n_actions), 1.0)  # Optimistic initialization
        self.action_counts = np.zeros((n_contexts, n_actions))  # Count of actions per context

    def select_action(self, context):
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.n_actions)  # Explore
        else:
            max_value = np.max(self.q_values[context])
            best_actions = np.where(self.q_values[context] == max_value)[0]
            return np.random.choice(best_actions)  # Exploit

    def update(self, context, action, reward):
        self.action_counts[context, action] += 1
        self.q_values[context, action] += (
            (reward - self.q_values[context, action]) / self.action_counts[context, action]
        )

def get_context(temperature, humidity, occupancy, n_contexts):
    max_temp, max_hum, max_occ = 30, 100, 5
    temp_bin = int((temperature / max_temp) * (n_contexts // 3))
    hum_bin = int((humidity / max_hum) * (n_contexts // 3))
    occ_bin = int((occupancy / max_occ) * (n_contexts // 3))
    return min(temp_bin + hum_bin + occ_bin, n_contexts - 1)

def get_feedback(action):
    if (action + 15) < 19:
        return 'cold'
    elif (action + 15) > 22:
        return 'warm'
    else:
        return 'comfortable'

def get_reward(feedback):
    reward_map = {'comfortable': 1.0, 'warm': 0.4, 'cold': 0.4}
    return reward_map.get(feedback, 0.0)

n_actions = 21  
n_contexts = 330 
initial_epsilon = 1.0  # Start with full exploration
epsilon_decay = 0.4 # Decay factor for exploration
min_epsilon = 0.1  # Minimum exploration rate
iterations = 1000  # Number of iterations
old_environment = {'temperature': 20, 'humidity': 50, 'occupancy': 2}

bandit = ContextualBandit(n_actions, n_contexts, initial_epsilon)
actions_taken = []
contexts_encountered = []

for iteration in range(iterations):
    # Gradually decay epsilon
    bandit.epsilon = max(min_epsilon, bandit.epsilon * epsilon_decay)

    # Simulate environment state
    environment = {
        'temperature': old_environment['temperature'] + np.random.choice([-1, 1]),
        'humidity': 50,
        'occupancy': np.random.randint(0, 6),
    }
    context = get_context(
        environment['temperature'], 
        environment['humidity'], 
        environment['occupancy'], 
        n_contexts
    )
    contexts_encountered.append(context)

    # Select action and log it
    action = bandit.select_action(context)
    actions_taken.append(action)

    # Simulate feedback based on action
    feedback = get_feedback(action)
    reward = get_reward(feedback)

    # Update bandit with observed reward
    bandit.update(context, action, reward)
    old_environment = environment

    print(f"Iteration {iteration+1}")
    print(f"Context: {context}, Action: {action}, Feedback: {feedback}, Reward: {reward}")
    print(f"Q-values for context {context}: {bandit.q_values[context]}\n")

action_counts = np.bincount(actions_taken, minlength=n_actions)
print(f"Action counts: {action_counts}")

plt.figure(figsize=(10, 5))
plt.bar(range(n_actions), action_counts, color='skyblue')
plt.title("Action Frequency Distribution")
plt.xlabel("Actions (mapped to thermostat settings)")
plt.ylabel("Frequency")
plt.show()

