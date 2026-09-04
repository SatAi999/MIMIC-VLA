from typing import Dict, Any, List
from backend.world_model.state import WorldState

class SafetyGate:
    def __init__(self, world_state: WorldState):
        self.world_state = world_state

    def check_action(self, action_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates proposed high-level or motion primitive action against hard safety rules.
        """
        # Rule 1: Navigation path safety check
        if action_type == "NAVIGATE":
            waypoints = params.get("waypoints", [])
            for wp in waypoints:
                # Check fire hazards
                for hazard in self.world_state.hazards:
                    dist = ((wp[0] - hazard.position[0])**2 + (wp[1] - hazard.position[1])**2)**0.5
                    if dist < hazard.radius:
                        return {
                            "decision": "BLOCK",
                            "reason": f"Route crosses critical hazard zone {hazard.id} ({hazard.type}) at position ({wp[0]:.1f}, {wp[1]:.1f})",
                            "hazard_id": hazard.id
                        }
                # Check solid obstacle collision
                for entity in self.world_state.entities.values():
                    if entity.properties.get("blocking"):
                        dist = ((wp[0] - entity.position[0])**2 + (wp[1] - entity.position[1])**2)**0.5
                        if dist < 0.6:
                            return {
                                "decision": "BLOCK",
                                "reason": f"Direct collision predicted with obstacle {entity.id} at ({entity.position[0]:.1f}, {entity.position[1]:.1f})",
                                "entity_id": entity.id
                            }
                            
        # Rule 2: Pickup safety check
        elif action_type == "PICK":
            target_id = params.get("target_id")
            entity = self.world_state.get_entity(target_id)
            if not entity:
                return {"decision": "BLOCK", "reason": f"Target object {target_id} not present in world model"}
            if entity.properties.get("hazardous"):
                return {"decision": "BLOCK", "reason": f"Target object {target_id} is classified as unsafe to handle"}

        return {"decision": "ALLOW", "reason": "All hard safety constraints passed successfully"}
