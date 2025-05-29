import numpy as np
from functools import lru_cache

# Card drawing probabilities (infinite deck assumption)
CARD_PROBS = {i: 1/13 for i in range(1, 10)}
CARD_PROBS[10] = 4/13  # 10, J, Q, K all count as 10

# Possible player sums and dealer upcards
PLAYER_SUMS = list(range(12, 22))        # effective states where choice matters
DEALER_UPCARDS = list(range(1, 11))      # 1=Ace, 2-9 face value, 10=10/J/Q/K
USABLE_ACE = [False, True]

# Default hyperparameters (tunable)
DEFAULT_GAMMA = 1.0        # Discount factor
DEFAULT_THETA = 1e-6       # Convergence threshold

# State type: tuple (player_sum, dealer_upcard, usable_ace)
State = tuple[int, int, bool]


def _update_sum_and_usable(total: int, usable: bool, card: int) -> tuple[int, bool]:
    """
    Given current sum and usable-ace flag, draw a card and return new (sum, usable)
    Handles counting Ace as 11 or 1 and converting usable ace to 1 if bust.
    """
    if card == 1:
        if total + 11 <= 21:
            total += 11
            usable = True
        else:
            total += 1
    else:
        total += card
    if total > 21 and usable:
        total -= 10
        usable = False
    return total, usable


@lru_cache(maxsize=None)
def dealer_final_distribution(total: int, usable: bool) -> dict[int, float]:
    if total >= 17:
        return {total: 1.0}
    dist: dict[int, float] = {}
    for card, p_card in CARD_PROBS.items():
        new_total, new_usable = _update_sum_and_usable(total, usable, card)
        sub_dist = dealer_final_distribution(new_total, new_usable)
        for final_sum, p_sub in sub_dist.items():
            dist[final_sum] = dist.get(final_sum, 0.0) + p_card * p_sub
    return dist


def compute_stay_value(player_sum: int, dealer_card: int, gamma: float = DEFAULT_GAMMA) -> float:
    total_value = 0.0
    for hidden, p_hidden in CARD_PROBS.items():
        dealer_sum, dealer_usable = _update_sum_and_usable(dealer_card, False, hidden)
        final_dist = dealer_final_distribution(dealer_sum, dealer_usable)
        for final_sum, p_final in final_dist.items():
            p = p_hidden * p_final
            if final_sum > 21 or final_sum < player_sum:
                reward = 1.0
            elif final_sum == player_sum:
                reward = 0.0
            else:
                reward = -1.0
            total_value += p * reward
    return total_value

compute_stick_value = compute_stay_value


@lru_cache(maxsize=None)
def compute_hit_transitions(state: State) -> dict[State, float]:
    player_sum, dealer_up, usable = state
    dist: dict[State, float] = {}
    for card, p_card in CARD_PROBS.items():
        new_sum, new_usable = _update_sum_and_usable(player_sum, usable, card)
        if new_sum > 21:
            next_state = ('bust', 0, False)
        else:
            next_state = (new_sum, dealer_up, new_usable)
        dist[next_state] = dist.get(next_state, 0.0) + p_card
    return dist


def value_iteration(
    gamma: float = DEFAULT_GAMMA,
    theta: float = DEFAULT_THETA,
    return_stats: bool = False
) -> tuple:
    """
    Perform Value Iteration on the Blackjack MDP.
    If return_stats=True, also return a dict with 'deltas' and 'mean_values' lists per iteration.
    Returns:
      V, policy[, stats]
    """
    V = { (ps, du, ua): 0.0
          for ps in PLAYER_SUMS
          for du in DEALER_UPCARDS
          for ua in USABLE_ACE }
    policy = { (ps, du, ua): 0
               for ps in PLAYER_SUMS
               for du in DEALER_UPCARDS
               for ua in USABLE_ACE }
    stats = {'deltas': [], 'mean_values': []} if return_stats else None

    while True:
        delta = 0.0
        for state in V:
            ps, du, ua = state
            q_stay = compute_stay_value(ps, du, gamma)
            q_hit = 0.0
            for next_state, p in compute_hit_transitions(state).items():
                if next_state[0] == 'bust':
                    q_hit += p * (-1.0)
                else:
                    q_hit += p * (0.0 + gamma * V[next_state])
            best_q = max(q_stay, q_hit)
            delta = max(delta, abs(best_q - V[state]))
            V[state] = best_q
            policy[state] = 0 if q_stay >= q_hit else 1
        if return_stats:
            stats['deltas'].append(delta)
            stats['mean_values'].append(np.mean(list(V.values())))
        if delta < theta:
            break
    if return_stats:
        return V, policy, stats
    return V, policy


def policy_iteration(
    gamma: float = DEFAULT_GAMMA,
    theta: float = DEFAULT_THETA,
    return_stats: bool = False
) -> tuple:
    """
    Perform Policy Iteration on the Blackjack MDP.
    If return_stats=True, also return a dict with 'policy_iterations'.
    Returns V, policy[, stats]
    """
    policy = { (ps, du, ua): 0
           for ps in PLAYER_SUMS
           for du in DEALER_UPCARDS
           for ua in USABLE_ACE }
    V = { state: 0.0 for state in policy }
    stats = {'policy_iterations': 0} if return_stats else None

    stable = False
    while not stable:
        stats['policy_iterations'] += 1 if return_stats else None
        # Policy Evaluation
        while True:
            delta = 0.0
            for state, action in policy.items():
                if action == 0:
                    v_new = compute_stay_value(state[0], state[1], gamma)
                else:
                    v_hit = 0.0
                    for ns, p in compute_hit_transitions(state).items():
                        if ns[0] == 'bust':
                            v_hit += p * (-1.0)
                        else:
                            v_hit += p * (0.0 + gamma * V[ns])
                    v_new = v_hit
                delta = max(delta, abs(v_new - V[state]))
                V[state] = v_new
            if delta < theta:
                break
        # Policy Improvement
        stable = True
        for state in policy:
            old_action = policy[state]
            q_stay = compute_stay_value(state[0], state[1], gamma)
            q_hit = sum(
                p * (-1.0 if ns[0]=='bust' else gamma * V[ns])
                for ns, p in compute_hit_transitions(state).items()
            )
            best_action = 0 if q_stay >= q_hit else 1
            policy[state] = best_action
            if best_action != old_action:
                stable = False
    if return_stats:
        return V, policy, stats
    return V, policy


if __name__ == "__main__":
    # Example usage
    V_vi, pi_vi, vi_stats = value_iteration(gamma=0.9, theta=1e-5, return_stats=True)
    print("VI iterations:", len(vi_stats['deltas']))
    V_pi, pi_pi, pi_stats = policy_iteration(gamma=0.9, theta=1e-5, return_stats=True)
    print("PI policy iterations:", pi_stats['policy_iterations'])
