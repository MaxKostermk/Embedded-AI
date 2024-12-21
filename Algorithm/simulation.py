import numpy as np

class ContextualBandit:
    def __init__(self, n_actions, n_contexts, epsilon=0.1):
        self.n_actions = n_actions
        self.n_contexts = n_contexts
        self.epsilon = epsilon
        self.q_values = np.zeros((n_contexts, n_actions))       # Estimated reward
        self.action_counts = np.zeros((n_contexts, n_actions))  # Action counts
        
    def select_action(self, context):
        if np.random.rand() < self.epsilon:
            # Explore a random action
            return np.random.choice(self.n_actions)
        else:
            # Exploit the best action
            return np.argmax(self.q_values[context])
        
    def update(self, context, action, reward):
        self.action_counts[context, action] += 1
        self.q_values[context, action] += (reward - self.q_values[context, action]) / self.action_counts[context, action]
        
def get_context(temperature, humdity, occupancy):
    max_temp, max_hum, max_occ = 30, 100, 5
    normalized_temp = int((temperature / max_temp) * (n_contexts // 3))
    normalized_hum = int((humdity / max_hum) * (n_contexts // 3))
    normalize_occ = int((occupancy / max_occ) * (n_contexts // 3))
    return normalized_temp + normalized_hum + normalize_occ

def get_feedback():
    feedback = ['comfortable', 'warm', 'cold']
    return np.random.choice(feedback)

def get_reward(feedback):
    if feedback == 'comfortable':
        return 1.0
    elif feedback == 'warm':
        return 0.5
    elif feedback == 'cold':
        return 0.5
        
n_actions = 21
n_contexts = 330
actions_taken = []

"""
n_actions: range of thermostat
Temperature: 15-25 | 11
Humidity: 30, 40, 50, 60, 70 | 5
Occupancy: 0-5 | 6
n_contexts = 11 * 5 * 6 = 330
"""

bandit = ContextualBandit(n_actions, n_contexts, epsilon=0.1)

for _ in range(100):
    temperature = np.random.randint(15, 26)
    humidity = np.random.choice([30, 40, 50, 60, 70])
    occupancy = np.random.randint(0, 6)
    context = get_context(temperature, humidity, occupancy)
    
    action = bandit.select_action(context)
    actions_taken.append(action)
    
    feedback = get_feedback()
    reward = get_reward(feedback)
    bandit.update(context, action, reward)
    
    print(f"C: {context}, A: {action}, F: {feedback}, R: {reward}")
    print(f"Q-values: {bandit.q_values[context]}")
    
print(f"Actions taken: {actions_taken}")
count = np.bincount(actions_taken)
print(f"Action counts: {count}")