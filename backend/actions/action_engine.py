import time
from typing import Dict, Any, List, Optional
from backend.simulation.world import SimulationWorld
from backend.simulation.robot import RobotController
from backend.world_model.state import WorldState
from backend.safety.checker import SafetyGate
from backend.actions.verification import ActionVerifier

class ActionEngine:
    def __init__(self, sim_world: SimulationWorld, world_state: WorldState):
        self.sim_world = sim_world
        self.world_state = world_state
        self.robot_controller = RobotController()
        self.safety_gate = SafetyGate(world_state)
        self.verifier = ActionVerifier(world_state)

    def execute_primitive(self, action_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a single high-level action primitive through Safety Gate and Verifier.
        """
        # 1. Pre-execution Safety Check
        safety_result = self.safety_gate.check_action(action_type, params)
        if safety_result["decision"] == "BLOCK":
            return {
                "success": False,
                "stage": "SAFETY_GATE",
                "message": safety_result["reason"],
                "safety_gate": safety_result
            }

        # 2. Simulation Execution
        if action_type == "NAVIGATE":
            target_pos = params.get("target_pos", [0.0, 0.0])
            self.robot_controller.position[0] = target_pos[0]
            self.robot_controller.position[1] = target_pos[1]
            self.world_state.robot.position = [target_pos[0], target_pos[1], 0.0]
            self.world_state.robot.status = "NAVIGATING"
            msg = f"Navigated to position ({target_pos[0]:.1f}, {target_pos[1]:.1f})"
            
        elif action_type == "PICK":
            target_id = params.get("target_id", "medical_kit_01")
            self.robot_controller.attach_item(target_id)
            self.world_state.robot.gripper_holding = target_id
            entity = self.world_state.get_entity(target_id)
            if entity:
                entity.state = "CARRIED"
            self.world_state.add_relation("robot", "carrying", target_id)
            msg = f"Picked up item {target_id}"

        elif action_type == "DELIVER":
            item_id = params.get("item_id", "medical_kit_01")
            target_id = params.get("target_id", "victim_01")
            self.robot_controller.release_item()
            self.world_state.robot.gripper_holding = None
            
            target_entity = self.world_state.get_entity(target_id)
            item_entity = self.world_state.get_entity(item_id)
            if target_entity and item_entity:
                item_entity.position = [target_entity.position[0] + 0.5, target_entity.position[1], 0.0]
                item_entity.state = "DELIVERED"
            msg = f"Delivered item {item_id} to target {target_id}"
        else:
            msg = f"Executed generic primitive {action_type}"

        # 3. Post-action Verification
        verification = self.verifier.verify_action(action_type, params)
        
        return {
            "success": verification["verified"],
            "stage": "EXECUTION",
            "message": msg,
            "safety_gate": safety_result,
            "verification": verification
        }
