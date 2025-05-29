import random
from collections import defaultdict
from typing import Tuple, Union, Dict, List

# State is a 4-tuple: (player_sum:int, dealer_up:int, usable_ace:bool, count_bin:str)
State = Tuple[int, int, bool, str]

class QLearningAgent:
    def __init__(
        self,
        action_count: int,
        initial_alpha: float = 0.1,
        final_alpha: float = 1e-3,
        alpha_decay: float = 1e-5,
        alpha_decay_type: str = 'linear',  # 'linear' or 'exponential'
        gamma: float = 1.0,
        initial_epsilon: float = 1.0,
        final_epsilon: float = 0.01,
        epsilon_decay: float = 1e-5,
        decay_type: str = 'linear',         # 'linear' or 'exponential'
        seed: int = None
    ):
        """
        Tabular Q-Learning agent for Blackjack, keyed on 4-tuple state:
           (player_sum, dealer_upcard, usable_ace, count_bin).

        Schedules for both α and ε can be linear or exponential.
        """
        self.action_count = action_count

        # α schedule
        self.alpha            = initial_alpha
        self.initial_alpha    = initial_alpha
        self.final_alpha      = final_alpha
        self.alpha_decay      = alpha_decay
        self.alpha_decay_type = alpha_decay_type

        # discount
        self.gamma = gamma

        # ε schedule
        self.epsilon       = initial_epsilon
        self.initial_epsilon = initial_epsilon
        self.final_epsilon   = final_epsilon
        self.epsilon_decay   = epsilon_decay
        self.decay_type      = decay_type

        # Q-table: State → [Q_a0, Q_a1, …]
        self.q_values = defaultdict(lambda: [0.0] * action_count)

        if seed is not None:
            random.seed(seed)


    def select_action(self, state: State, greedy: bool = False) -> int:
        """
        Epsilon-greedy selection over the Q-table.
        If greedy=True, ε is ignored and the best action is chosen.
        """
        if not greedy and random.random() < self.epsilon:
            return random.randrange(self.action_count)
        q_list = self.q_values[state]
        max_q  = max(q_list)
        # break ties randomly
        bests  = [i for i, q in enumerate(q_list) if q == max_q]
        return random.choice(bests)

    def update(
        self,
        state:      State,
        action:     int,
        reward:     float,
        next_state: State,
        done:       bool
    ):
        """
        Perform standard Q-learning update:
          Q(s,a) ← Q(s,a) + α [r + γ max_a' Q(s',a') − Q(s,a)].
        At terminal (done=True), we bootstrap only on the reward.
        """
        current_q = self.q_values[state][action]
        if done:
            target = reward
        else:
            target = reward + self.gamma * max(self.q_values[next_state])
        self.q_values[state][action] = current_q + self.alpha * (target - current_q)

    def decay_epsilon(self):
        """Lower ε per schedule: linear or exponential down to final_epsilon."""
        if self.decay_type == 'linear':
            self.epsilon = max(self.final_epsilon, self.epsilon - self.epsilon_decay)
        else:  # exponential
            self.epsilon = max(self.final_epsilon, self.epsilon * self.epsilon_decay)

    def decay_alpha(self):
        """Lower α per schedule: linear or exponential down to final_alpha."""
        if self.alpha_decay_type == 'linear':
            self.alpha = max(self.final_alpha, self.alpha - self.alpha_decay)
        else:
            self.alpha = max(self.final_alpha, self.alpha * self.alpha_decay)

    def reset(self):
        """Reset α and ε back to their initial values (for fresh runs)."""
        self.alpha   = self.initial_alpha
        self.epsilon = self.initial_epsilon

    def get_policy(self) -> Dict[State,int]:
        """
        Extract the greedy policy mapping from each seen state
        to argmax_a Q(state)[a].
        """
        return {s: vals.index(max(vals)) for s, vals in self.q_values.items()}

    def get_q_values(self) -> Dict[State,List[float]]:
        """Return the entire Q-table as a normal dict."""
        return dict(self.q_values)