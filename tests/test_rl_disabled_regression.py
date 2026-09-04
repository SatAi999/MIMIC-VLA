import os
import pytest
from backend.rl.config import rl_config
from backend.world_model.state import WorldState, Hazard
from backend.prediction.predictive_planner import PredictivePlanner
from backend.intelligence.decision_fusion import DecisionFusionEngine

def test_rl_disabled_regression():
    """
    Verifies that when RL_ENABLED is false or RL confidence is low, baseline planner decision is strictly preserved.
    """
    ws = WorldState()
    ws.hazards.append(Hazard(id="fire_01", type="fire", position=[0.0, 1.0, 0.0], radius=1.5, severity=0.9))
    planner = PredictivePlanner(ws)

    candidates = [
        {"id": "route_A", "name": "Route A", "waypoints": [[-4.0, -4.0], [0.0, 1.0], [4.0, 4.0]]},
        {"id": "route_B", "name": "Route B", "waypoints": [[-4.0, -4.0], [-2.0, 3.0], [0.0, 4.0], [4.0, 4.0]]}
    ]
    
    eval_res = planner.evaluate_candidates(candidates, [4.0, 4.0])
    selected = eval_res["selected_route"]
    assert selected["id"] == "route_B"

    # Test Decision Fusion with RL disabled or zero confidence
    fusion = DecisionFusionEngine()
    rl_rec = {"action": 0, "action_name": "CONTINUE", "confidence": 0.0}
    fused = fusion.fuse_decisions(selected, rl_rec, 0.02, 0.0)

    assert fused["selected_action"] == selected["name"]
    assert fused["used_rl"] is False
