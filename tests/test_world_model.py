import pytest
from backend.world_model.state import WorldState, Entity
from backend.world_model.relations import SceneGraphManager

def test_world_state_entity_management():
    state = WorldState()
    entity = Entity(id="med_01", type="medical_kit", position=[1.0, 2.0, 0.0], confidence=0.95)
    state.add_entity(entity)
    
    retrieved = state.get_entity("med_01")
    assert retrieved is not None
    assert retrieved.type == "medical_kit"
    assert retrieved.confidence == 0.95

def test_scene_graph_relations():
    state = WorldState()
    box = Entity(id="box_01", type="box", position=[0.0, 0.0, 0.0])
    state.add_entity(box)
    state.add_relation("box_01", "blocking", "corridor_B")
    
    sg = SceneGraphManager(state)
    blocking = sg.find_blocking_objects("corridor_B")
    assert len(blocking) == 1
    assert blocking[0].id == "box_01"
