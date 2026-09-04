from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import time

class Entity(BaseModel):
    id: str
    type: str
    position: List[float]  # [x, y, z] or [x, y]
    state: str = "detected" # reachable, carried, delivered, injured, active, blocked
    confidence: float = 1.0
    properties: Dict[str, Any] = Field(default_factory=dict)
    last_seen: float = Field(default_factory=time.time)
    source: str = "perception"

class Relation(BaseModel):
    subject_id: str
    relation_type: str # blocking, near, inside, carrying
    object_id: str
    confidence: float = 1.0

class Hazard(BaseModel):
    id: str
    type: str # fire, debris, oil, high_risk_zone
    position: List[float]
    radius: float = 1.0
    severity: float = 0.9 # 0.0 to 1.0

class RobotState(BaseModel):
    position: List[float] = [0.0, 0.0, 0.0]
    orientation: float = 0.0 # yaw angle in radians
    status: str = "IDLE" # IDLE, NAVIGATING, PICKING, DELIVERING, REPLANNING, ERROR
    gripper_holding: Optional[str] = None
    target_position: Optional[List[float]] = None

class WorldState(BaseModel):
    robot: RobotState = Field(default_factory=RobotState)
    entities: Dict[str, Entity] = Field(default_factory=dict)
    relations: List[Relation] = Field(default_factory=list)
    hazards: List[Hazard] = Field(default_factory=list)
    occupancy_grid: List[List[int]] = Field(default_factory=list)
    grid_bounds: List[float] = [-10.0, 10.0, -10.0, 10.0] # [min_x, max_x, min_y, max_y]
    grid_resolution: float = 0.5
    current_goal: Optional[str] = None
    current_plan: List[str] = Field(default_factory=list)
    last_updated: float = Field(default_factory=time.time)

    def add_entity(self, entity: Entity):
        self.entities[entity.id] = entity
        self.last_updated = time.time()

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        return self.entities.get(entity_id)

    def add_relation(self, subject: str, rel: str, obj: str, confidence: float = 1.0):
        # Remove existing relation between subject and object if present
        self.relations = [r for r in self.relations if not (r.subject_id == subject and r.object_id == obj and r.relation_type == rel)]
        self.relations.append(Relation(subject_id=subject, relation_type=rel, object_id=obj, confidence=confidence))
        self.last_updated = time.time()

    def query_relations(self, subject_id: Optional[str] = None, rel_type: Optional[str] = None, object_id: Optional[str] = None) -> List[Relation]:
        results = self.relations
        if subject_id:
            results = [r for r in results if r.subject_id == subject_id]
        if rel_type:
            results = [r for r in results if r.relation_type == rel_type]
        if object_id:
            results = [r for r in results if r.object_id == object_id]
        return results
