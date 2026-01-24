from multiagent_trading.agents.base import BaseAgent
import numpy as np
import random

class RLAgent(BaseAgent):
    """
    Agente que implementa reforço de aprendizagem.
    Suporta Q-Learning e estrutura base para Deep Q-Learning (DQN).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_dqn = self.config.get("use_dqn", False)
        self.q_table = {}
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.2
        self.actions = ["BUY", "SELL", "HOLD"]
        self.last_state = None
        self.last_action = None

    async def on_market_update(self, data):
        await super().on_market_update(data)
        state = self._get_state(data)

        # Atribuir recompensa baseada no PnL se houver uma ação anterior
        if self.last_state is not None:
            reward = self._calculate_reward()
            self._update_q_table(self.last_state, self.last_action, reward, state)

        # Escolher nova ação
        if random.random() < self.epsilon:
            action = random.choice(self.actions)
        else:
            action = self._get_best_action(state)

        self.last_state = state
        self.last_action = action

        if action != "HOLD":
            opp = {"symbol": data.get("symbol"), "side": action, "agent": self.name}
            await self.event_bus.publish("opportunity_found", opp)

    def _get_state(self, data):
        # Discretização simples do estado (apenas valores numéricos para compatibilidade DQN)
        rsi = data.get("rsi", 50)
        regime_map = {"BULL": 1, "BEAR": -1, "NEUTRAL": 0}
        regime_val = regime_map.get(self.context.regime, 0)
        return (int(rsi / 10), regime_val)

    def _calculate_reward(self):
        # Recompensa baseada na mudança percentual do valor do portfólio
        if not hasattr(self.context, "portfolio") or not hasattr(self, "last_portfolio_value"):
            self.last_portfolio_value = getattr(self.context.portfolio, "total_value", 10000)
            return 0

        current_value = self.context.portfolio.total_value
        reward = (current_value - self.last_portfolio_value) / self.last_portfolio_value
        self.last_portfolio_value = current_value
        return reward

    def _update_q_table(self, state, action, reward, next_state):
        current_q = self.q_table.get((state, action), 0.0)
        max_next_q = max([self.q_table.get((next_state, a), 0.0) for a in self.actions])

        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[(state, action)] = new_q

    def _get_best_action(self, state):
        if self.use_dqn:
            # Estrutura lógica para Deep Q-Learning
            # Em produção, usaria PyTorch ou TensorFlow
            state_tensor = np.array(state).reshape(1, -1)

            # Simulação de pesos de uma rede neuronal simples
            weights = np.random.randn(len(state), len(self.actions))
            q_values = np.dot(state_tensor, weights)[0]

            self.logger.debug(f"DQN Q-Values para {state}: {q_values}")
            return self.actions[np.argmax(q_values)]

        q_values = [self.q_table.get((state, a), 0.0) for a in self.actions]
        return self.actions[np.argmax(q_values)]
