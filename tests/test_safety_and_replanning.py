import pytest
from backend.world_model.state import WorldState, Hazard
from backend.safety.checker import SafetyGate
from backend.planning.replanner import DynamicReplanner

def test_safety_gate_hazard_blocking():
    state = WorldState()
    state.hazards.append(Hazard(id="fire_01", type="fire", position=[0.0, 1.0, 0.0], radius=1.5, severity=0.9))
    
    gate = SafetyGate(state)
    # Action crossing fire hazard
    result = gate.check_action("NAVIGATE", {"waypoints": [[-1.0, 1.0], [0.0, 1.0], [1.0, 1.0]]})
    assert result["decision"] == "BLOCK"
    assert "fire_01" in result["reason"]

def test_dynamic_replanner():
    state = WorldState()
    replanner = DynamicReplanner(state)
    
    res = replanner.trigger_replan("Route B", "Debris Blocking Corridor B", [4.0, 4.0])
    assert res["replan_status"] == "SUCCESS"
    assert res["new_selected_route"] is not None
    assert res["new_selected_route"]["id"] == "route_C"
