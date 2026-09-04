import pytest
from backend.planning.astar import AStarPlanner

def test_astar_pathfinding():
    planner = AStarPlanner(grid_size=(20, 20), resolution=0.5, origin=(-5.0, -5.0))
    start = (-4.0, -4.0)
    goal = (4.0, 4.0)
    
    path = planner.plan(start, goal)
    assert path is not None
    assert len(path) > 1
    assert path[0] == start

def test_astar_obstacle_avoidance():
    planner = AStarPlanner(grid_size=(20, 20), resolution=0.5, origin=(-5.0, -5.0))
    # Block direct line
    planner.set_obstacle(0.0, 0.0, radius=1.0, cost=100)
    
    start = (-4.0, -4.0)
    goal = (4.0, 4.0)
    path = planner.plan(start, goal)
    assert path is not None
    # Verify no waypoint passes directly through (0,0)
    for p in path:
        dist = (p[0]**2 + p[1]**2)**0.5
        assert dist > 0.4
