from typing import Dict, Any, List
from backend.world_model.state import WorldState, Entity
from backend.prediction.predictive_planner import PredictivePlanner

class DynamicReplanner:
    def __init__(self, world_state: WorldState):
        self.world_state = world_state
        self.predictive_planner = PredictivePlanner(world_state)

    def trigger_replan(self, current_route_name: str, obstacle_info: str, goal_pos: List[float]) -> Dict[str, Any]:
        """
        Computes dynamic replan when active route is invalidated by dynamic obstacle insertion.
        """
        # Add dynamic blocking obstacle into world model state
        obstacle_entity = Entity(
            id="debris_corridor_B",
            type="debris",
            position=[0.0, 4.0, 0.0],
            confidence=0.99,
            properties={"blocking": True, "size": 1.0},
            source="replan_trigger"
        )
        self.world_state.add_entity(obstacle_entity)
        self.world_state.add_relation("debris_corridor_B", "blocking", "corridor_B")

        # Step 1: Invalidate active route
        invalidation_event = {
            "old_route": current_route_name,
            "reason": obstacle_info,
            "status": "INVALIDATED"
        }

        # Step 2: Regenerate candidates avoiding blocked route
        candidates = [
            {
                "id": "route_B",
                "name": "Route B (Corridor B)",
                "waypoints": [[-4.0, -4.0], [-2.0, 3.0], [0.0, 4.0], [4.0, 4.0]]
            },
            {
                "id": "route_C",
                "name": "Route C (Alternative Detour)",
                "waypoints": [[-4.0, -4.0], [-4.0, 0.0], [0.0, -3.0], [4.0, 0.0], [4.0, 4.0]]
            }
        ]

        # Step 3: Run predictive scoring on candidates
        eval_result = self.predictive_planner.evaluate_candidates(candidates, goal_pos)

        return {
            "invalidation": invalidation_event,
            "evaluated_candidates": eval_result["evaluated_candidates"],
            "new_selected_route": eval_result["selected_route"],
            "replan_status": "SUCCESS" if eval_result["selected_route"] else "FAILED"
        }
