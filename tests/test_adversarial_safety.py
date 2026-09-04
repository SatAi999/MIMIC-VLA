import pytest
from backend.world_model.state import WorldState, Hazard, Entity
from backend.safety.checker import SafetyGate
from backend.prediction.predictive_planner import PredictivePlanner

def test_safety_gate_override_planner():
    """
    Verifies that Safety Gate decision explicitly OVERRIDES planner proposals if planner suggests an unsafe path.
    """
    ws = WorldState()
    # Add fire hazard directly on path
    ws.hazards.append(Hazard(id="fire_01", type="fire", position=[0.0, 1.0, 0.0], radius=1.5, severity=0.99))
    
    gate = SafetyGate(ws)
    # Unsafe route parameters through fire hazard
    unsafe_route_params = {"waypoints": [[-4.0, -4.0], [0.0, 1.0], [4.0, 4.0]]}
    
    check = gate.check_action("NAVIGATE", unsafe_route_params)
    assert check["decision"] == "BLOCK"
    assert "fire_01" in check["reason"]

def test_no_safe_action_available():
    """
    Verifies system behavior when ALL candidate routes are obstructed or hazardous.
    System must enter AUTONOMY PAUSED / BLOCK state rather than forcing unsafe execution.
    """
    ws = WorldState()
    # Block Corridor A with Fire Hazard
    ws.hazards.append(Hazard(id="fire_01", type="fire", position=[0.0, 1.0, 0.0], radius=2.0, severity=0.99))
    # Block Corridor B with Solid Debris
    ws.add_entity(Entity(id="debris_B", type="debris", position=[0.0, 4.0, 0.0], properties={"blocking": True}))
    # Block Corridor C with Solid Debris
    ws.add_entity(Entity(id="debris_C", type="debris", position=[0.0, -3.0, 0.0], properties={"blocking": True}))

    planner = PredictivePlanner(ws)
    candidates = [
        {"id": "route_A", "name": "Route A", "waypoints": [[-4.0, -4.0], [0.0, 1.0], [4.0, 4.0]]},
        {"id": "route_B", "name": "Route B", "waypoints": [[-4.0, -4.0], [0.0, 4.0], [4.0, 4.0]]},
        {"id": "route_C", "name": "Route C", "waypoints": [[-4.0, -4.0], [0.0, -3.0], [4.0, 4.0]]}
    ]
    
    eval_res = planner.evaluate_candidates(candidates, [4.0, 4.0])
    # Every candidate evaluated as UNSAFE
    for cand in eval_res["evaluated_candidates"]:
        assert cand["status"] == "UNSAFE"
        
    assert eval_res["selected_route"] is None
    assert "NO SAFE ACTION AVAILABLE" in eval_res["decision_reason"]
