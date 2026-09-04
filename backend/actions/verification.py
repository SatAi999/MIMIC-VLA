from typing import Dict, Any
from backend.world_model.state import WorldState

class ActionVerifier:
    def __init__(self, world_state: WorldState):
        self.world_state = world_state

    def verify_action(self, action_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifies expected vs actual physical observation after action execution.
        """
        if action_type == "DELIVER":
            item_id = params.get("item_id", "medical_kit_01")
            target_id = params.get("target_id", "victim_01")
            
            item = self.world_state.get_entity(item_id)
            target = self.world_state.get_entity(target_id)
            robot = self.world_state.robot
            
            if not item or not target:
                return {
                    "verified": False,
                    "reason": "Entities not found in world state",
                    "checks": {"entities_exist": False}
                }
                
            dist_item_target = ((item.position[0] - target.position[0])**2 + (item.position[1] - target.position[1])**2)**0.5
            gripper_empty = (robot.gripper_holding is None or robot.gripper_holding != item_id)
            target_reached = dist_item_target <= 1.5
            
            success = gripper_empty and target_reached
            
            return {
                "verified": success,
                "reason": "Delivery successfully verified" if success else "Item position mismatch",
                "checks": {
                    "item_near_target": target_reached,
                    "distance_meters": round(dist_item_target, 2),
                    "gripper_empty": gripper_empty
                }
            }
        elif action_type == "PICK":
            item_id = params.get("item_id")
            robot = self.world_state.robot
            holding = robot.gripper_holding == item_id
            return {
                "verified": holding,
                "reason": "Pickup verified" if holding else "Item not held in gripper",
                "checks": {"gripper_holding": holding}
            }
            
        return {"verified": True, "reason": "Default verification passed", "checks": {}}
