import pytest
from backend.intelligence.decision_fusion import DecisionFusionEngine
from backend.rl.action_space import RLAction

def test_rl_low_confidence_fallback():
    fusion = DecisionFusionEngine()
    planner_cand = {"name": "Route B (Corridor B)"}
    low_conf_rl = {"action": RLAction.TAKE_ALTERNATE_ROUTE, "action_name": "TAKE_ALTERNATE_ROUTE", "confidence": 0.45, "source": "PPO-v1"}

    res = fusion.fuse_decisions(planner_cand, low_conf_rl, 0.05, 0.0)
    assert res["used_rl"] is False
    assert res["selected_action"] == "Route B (Corridor B)"

def test_rl_safety_gate_rejection():
    fusion = DecisionFusionEngine()
    planner_cand = {"name": "Route B (Corridor B)"}
    high_conf_rl = {"action": RLAction.TAKE_ALTERNATE_ROUTE, "action_name": "TAKE_ALTERNATE_ROUTE", "confidence": 0.92, "source": "PPO-v1"}

    # Mock safety check function evaluating action as UNSAFE
    def mock_safety_check(action_name):
        return False

    res = fusion.fuse_decisions(planner_cand, high_conf_rl, 0.05, 0.0, safety_check_fn=mock_safety_check)
    assert res["used_rl"] is False
    assert res["safety_status"] == "REJECTED_BY_SAFETY_GATE"
    assert res["selected_action"] == "Route B (Corridor B)"
