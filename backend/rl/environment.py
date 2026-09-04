import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Tuple, Dict, Any

from backend.world_model.state import WorldState, Hazard, Entity
from backend.world_model.updater import WorldModelUpdater
from backend.prediction.predictive_planner import PredictivePlanner
from backend.rl.state_encoder import StateEncoder
from backend.rl.reward import RLRewardCalculator
from backend.rl.action_space import RLAction

class MimicVLAEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self, seed: int = 42):
        super().__init__()
        self.observation_space = spaces.Box(low=-1.0, high=1.0, shape=(16,), dtype=np.float32)
        self.action_space = spaces.Discrete(6)
        
        self.encoder = StateEncoder()
        self.reward_calc = RLRewardCalculator()
        self.step_count = 0
        self.max_steps = 20
        self.corridor_b_blocked = False

    def reset(self, seed: int = None, options: dict = None) -> Tuple[np.ndarray, dict]:
        super().reset(seed=seed)
        self.step_count = 0
        self.corridor_b_blocked = False
        
        # Build clean initial world state
        self.world_state = WorldState()
        self.world_state.robot.position = [-4.0, -4.0, 0.0]
        self.world_state.add_entity(Entity(id="victim_01", type="person", position=[4.0, 4.0, 0.0]))
        self.world_state.add_entity(Entity(id="medical_kit_01", type="medical_kit", position=[-2.0, 3.0, 0.0]))
        self.world_state.hazards.append(Hazard(id="fire_01", type="fire", position=[0.0, 1.0, 0.0], radius=1.5, severity=0.9))

        self.planner = PredictivePlanner(self.world_state)
        eval_cand = self._get_candidates()
        
        obs = self.encoder.encode(self.world_state, [4.0, 4.0], eval_cand, obstacle_injected=False)
        return obs, {}

    def _get_candidates(self):
        candidates = [
            {"id": "route_A", "name": "Route A", "waypoints": [[-4.0, -4.0], [0.0, 1.0], [4.0, 4.0]]},
            {"id": "route_B", "name": "Route B", "waypoints": [[-4.0, -4.0], [-2.0, 3.0], [0.0, 4.0], [4.0, 4.0]]},
            {"id": "route_C", "name": "Route C", "waypoints": [[-4.0, -4.0], [-4.0, 0.0], [0.0, -3.0], [4.0, 4.0]]}
        ]
        res = self.planner.evaluate_candidates(candidates, [4.0, 4.0])
        return res["evaluated_candidates"]

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, dict]:
        self.step_count += 1
        
        # Domain randomization: Inject obstacle around step 3
        if self.step_count == 3:
            self.corridor_b_blocked = True
            self.world_state.add_entity(Entity(id="debris_01", type="debris", position=[0.0, 4.0, 0.0], properties={"blocking": True}))

        eval_cand = self._get_candidates()
        
        # Determine outcome based on action choice
        success = False
        collision = False
        safety_violation = False
        recovery = False

        if action == RLAction.CONTINUE_CURRENT_ROUTE:
            if self.corridor_b_blocked:
                collision = True
            else:
                self.world_state.robot.position = [0.0, 4.0, 0.0]
        elif action == RLAction.TAKE_ALTERNATE_ROUTE or action == RLAction.REPLAN:
            if self.corridor_b_blocked:
                recovery = True
                self.world_state.robot.position = [4.0, 4.0, 0.0]
                success = True
            else:
                self.world_state.robot.position = [4.0, 4.0, 0.0]
                success = True

        done = (success or collision or self.step_count >= self.max_steps)
        outcome = {
            "success": success,
            "collision": collision,
            "safety_violation": safety_violation,
            "recovery": recovery,
            "progress": 0.5 if not done else 1.0
        }

        reward = self.reward_calc.compute_reward(action, outcome)
        obs = self.encoder.encode(self.world_state, [4.0, 4.0], eval_cand, obstacle_injected=self.corridor_b_blocked)

        return obs, reward, done, False, outcome
