from typing import Dict, Any

class RLRewardCalculator:
    def __init__(self):
        pass

    def compute_reward(self, action: int, outcome: Dict[str, Any]) -> float:
        """
        Calculates scalar reward based on action choice and physical verification outcome.
        """
        reward = -0.5 # Step cost penalty

        success = outcome.get("success", False)
        collision = outcome.get("collision", False)
        safety_violation = outcome.get("safety_violation", False)
        recovery = outcome.get("recovery", False)
        progress = outcome.get("progress", 0.0)

        if success:
            reward += 100.0
        if recovery:
            reward += 25.0
        if progress > 0:
            reward += progress * 10.0

        if collision:
            reward -= 50.0
        if safety_violation:
            reward -= 100.0

        # Action specific heuristics
        if action == 2 and recovery: # TAKE_ALTERNATE_ROUTE when corridor blocked
            reward += 15.0
        elif action == 1 and not recovery: # Unnecessary replan
            reward -= 5.0

        return float(reward)
