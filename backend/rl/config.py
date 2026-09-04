import os
from pydantic import BaseModel

class RLConfig(BaseModel):
    rl_enabled: bool = os.getenv("RL_ENABLED", "true").lower() in ["true", "1", "yes"]
    rl_training_enabled: bool = os.getenv("RL_TRAINING_ENABLED", "false").lower() in ["true", "1", "yes"]
    rl_policy_path: str = os.getenv("RL_POLICY_PATH", "models/rl_policy/ppo_v1.zip")
    rl_confidence_threshold: float = float(os.getenv("RL_CONFIDENCE_THRESHOLD", "0.65"))
    rl_blend_weight: float = float(os.getenv("RL_BLEND_WEIGHT", "0.30"))
    rl_max_action_risk: float = float(os.getenv("RL_MAX_ACTION_RISK", "0.25"))
    rl_fallback_to_planner: bool = os.getenv("RL_FALLBACK_TO_PLANNER", "true").lower() in ["true", "1", "yes"]
    rl_seed: int = int(os.getenv("RL_SEED", "42"))

rl_config = RLConfig()
