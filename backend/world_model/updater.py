import time
from typing import Dict, Any, List, Tuple
from backend.world_model.state import WorldState, Entity, Hazard

class WorldModelUpdater:
    def __init__(self, world_state: WorldState):
        self.world_state = world_state

    def update_from_detections(self, detections: List[Dict[str, Any]]) -> List[str]:
        """
        Updates entities based on visual detection frames.
        Returns a list of change alert descriptions if environment changes are detected.
        """
        changes = []
        now = time.time()
        
        for det in detections:
            entity_id = det.get("id") or f"{det['class']}_01"
            obj_type = det.get("class", "unknown")
            pos = det.get("position", [0.0, 0.0, 0.0])
            conf = det.get("confidence", 0.9)
            
            existing = self.world_state.get_entity(entity_id)
            if existing:
                dist_moved = ((existing.position[0] - pos[0])**2 + (existing.position[1] - pos[1])**2)**0.5
                if dist_moved > 0.8:
                    changes.append(f"Entity {entity_id} position shifted by {dist_moved:.2f}m")
                    existing.position = pos
                existing.confidence = conf
                existing.last_seen = now
            else:
                new_entity = Entity(
                    id=entity_id,
                    type=obj_type,
                    position=pos,
                    confidence=conf,
                    last_seen=now,
                    source="perception"
                )
                self.world_state.add_entity(new_entity)
                changes.append(f"New entity detected: {entity_id} ({obj_type})")
                
        self.world_state.last_updated = now
        return changes

    def add_dynamic_obstacle(self, obstacle_id: str, position: List[float], size: float = 1.0) -> str:
        """
        Simulates dynamic obstacle injection into the world model.
        """
        entity = Entity(
            id=obstacle_id,
            type="debris",
            position=position,
            confidence=0.99,
            properties={"blocking": True, "size": size},
            source="manual_injection"
        )
        self.world_state.add_entity(entity)
        self.world_state.add_relation(obstacle_id, "blocking", "corridor_B")
        change_msg = f"DYNAMIC OBSTACLE DETECTED: {obstacle_id} at ({position[0]:.1f}, {position[1]:.1f})"
        return change_msg

    def remove_obstacle(self, obstacle_id: str) -> str:
        """
        Removes dynamic obstacle entity and updates relations.
        """
        if obstacle_id in self.world_state.entities:
            del self.world_state.entities[obstacle_id]
        self.world_state.relations = [r for r in self.world_state.relations if r.subject_id != obstacle_id]
        self.world_state.last_updated = time.time()
        return f"REMOVED OBSTACLE: {obstacle_id} and cleared blocking relations"
