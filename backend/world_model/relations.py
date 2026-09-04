from typing import List, Optional
from backend.world_model.state import WorldState, Entity

class SceneGraphManager:
    def __init__(self, world_state: WorldState):
        self.world_state = world_state

    def find_blocking_objects(self, target_id: str) -> List[Entity]:
        relations = self.world_state.query_relations(rel_type="blocking", object_id=target_id)
        blocking_entities = []
        for r in relations:
            entity = self.world_state.get_entity(r.subject_id)
            if entity:
                blocking_entities.append(entity)
        return blocking_entities

    def get_nearby_hazards(self, position: List[float], max_distance: float = 3.0):
        hazards = []
        for h in self.world_state.hazards:
            dist = ((position[0] - h.position[0])**2 + (position[1] - h.position[1])**2)**0.5
            if dist <= max_distance:
                hazards.append(h)
        return hazards

    def find_entities_by_type(self, entity_type: str) -> List[Entity]:
        return [e for e in self.world_state.entities.values() if e.type.lower() == entity_type.lower()]
