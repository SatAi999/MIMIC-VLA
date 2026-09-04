import numpy as np
from typing import Dict, Any, List

class StateEncoder:
    def __init__(self, observation_dim: int = 16):
        self.observation_dim = observation_dim

    def encode(self, world_state: Any, target_pos: List[float], eval_candidates: List[Dict[str, Any]], learned_risk: float = 0.0, historical_failure_rate: float = 0.0, obstacle_injected: bool = False) -> np.ndarray:
        """
        Encodes WorldState and planner candidate evaluations into a 16-dimensional normalized observation vector.
        """
        obs = np.zeros(self.observation_dim, dtype=np.float32)

        rx = world_state.robot.position[0] if hasattr(world_state, "robot") else -4.0
        ry = world_state.robot.position[1] if hasattr(world_state, "robot") else -4.0

        dist_to_target = ((rx - target_pos[0])**2 + (ry - target_pos[1])**2)**0.5
        mission_progress = max(0.0, min(1.0, 1.0 - (dist_to_target / 15.0)))

        # Corridor blocking checks
        corridor_b_blocked = 0.0
        if hasattr(world_state, "entities"):
            for ent in world_state.entities.values():
                if getattr(ent, "properties", {}).get("blocking"):
                    corridor_b_blocked = 1.0

        scores = [c.get("total_score", 0.0) for c in eval_candidates] if eval_candidates else [5.0, 0.0]
        scores.sort(reverse=True)
        best_score = scores[0] if len(scores) > 0 else 5.0
        second_score = scores[1] if len(scores) > 1 else 0.0

        model_collision = max([c.get("collision_probability", 0.0) for c in eval_candidates]) if eval_candidates else 0.0

        obs[0] = np.float32(mission_progress)
        obs[1] = np.float32((rx + 6.0) / 12.0)
        obs[2] = np.float32((ry + 6.0) / 12.0)
        obs[3] = np.float32(min(1.0, dist_to_target / 15.0))
        obs[4] = np.float32(0.8 if corridor_b_blocked else 0.1)
        obs[5] = np.float32(0.1 if corridor_b_blocked else 1.0)
        obs[6] = np.float32(corridor_b_blocked)
        obs[7] = np.float32(1.0) # Corridor C available
        obs[8] = np.float32(max(-1.0, min(1.0, best_score / 10.0)))
        obs[9] = np.float32(max(-1.0, min(1.0, second_score / 10.0)))
        obs[10] = np.float32(max(0.0, (best_score - second_score) / 10.0))
        obs[11] = np.float32(model_collision)
        obs[12] = np.float32(learned_risk)
        obs[13] = np.float32(historical_failure_rate)
        obs[14] = np.float32(1.0 if corridor_b_blocked else 0.0)
        obs[15] = np.float32(1.0 if obstacle_injected else 0.0)

        return obs
