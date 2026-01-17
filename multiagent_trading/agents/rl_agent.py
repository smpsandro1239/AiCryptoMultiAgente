import numpy as np
import random
from multiagent_trading.agents.base import BaseAgent

class RLAgent(BaseAgent):
    """
    A basic Q-learning agent that learns to signal BUY/SELL based on PnL rewards.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.q_table = {} # (state) -> [q_buy, q_hold, q_sell]
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.2 # Exploration rate
        self.last_state = None
        self.last_action = None
        self.logger.info(f"{self.name} RL Agent (Q-Learning) initialized.")

    async def on_market_update(self, data_batch):
        if not data_batch: return

        symbol = next(iter(data_batch))
        state = self.get_state(data_batch[symbol])

        # 1. Update Q-table based on reward from last action
        reward = self.get_reward()
        if self.last_state is not None:
            self.update_q_table(self.last_state, self.last_action, reward, state)

        # 2. Select action using epsilon-greedy
        if random.random() < self.epsilon:
            action = random.randint(0, 2) # Explore
        else:
            action = self.select_best_action(state) # Exploit

        # 3. Execute action
        if action == 0: # BUY
             await self.event_bus.publish("opportunity_found", {"symbol": symbol, "side": "BUY", "reason": "RL Q-Learning Signal"})
        elif action == 2: # SELL
             await self.event_bus.publish("opportunity_found", {"symbol": symbol, "side": "SELL", "reason": "RL Q-Learning Signal"})

        self.last_state = state
        self.last_action = action

    def get_state(self, tick):
        # Discretize close price into a simple state (e.g., modulo 10)
        price = tick.get("close", 100)
        return int(price // 10) % 100

    def select_best_action(self, state):
        if state not in self.q_table:
            self.q_table[state] = [0.0, 0.0, 0.0]
        return np.argmax(self.q_table[state])

    def update_q_table(self, state, action, reward, next_state):
        if state not in self.q_table: self.q_table[state] = [0.0, 0.0, 0.0]
        if next_state not in self.q_table: self.q_table[next_state] = [0.0, 0.0, 0.0]

        old_value = self.q_table[state][action]
        next_max = np.max(self.q_table[next_state])

        # Q-Learning Formula
        new_value = old_value + self.learning_rate * (reward + self.discount_factor * next_max - old_value)
        self.q_table[state][action] = new_value

    def get_reward(self):
        # Get latest PnL from memory as reward
        executions = self.context.memory.get_by_key("execution")
        if not executions:
            return 0.0
        # Positive reward if the last execution was profitable (simulated)
        last_exec = executions[-1]["value"]
        return last_exec.get("pnl", 0.0)
