import math
import numpy as np
from typing import List, Dict, Any, Tuple, Optional

try:
    import pybullet as p
    import pybullet_data
    PYBULLET_AVAILABLE = True
except ImportError:
    PYBULLET_AVAILABLE = False

class SimulationWorld:
    def __init__(self, mode: str = "disaster", gui: bool = False):
        self.mode = mode
        self.gui = gui
        self.client_id = None
        self.robot_id = None
        self.objects: Dict[str, Any] = {}
        self.sim_step_count = 0
        
        self.init_environment()

    def init_environment(self):
        if PYBULLET_AVAILABLE:
            try:
                if self.gui:
                    self.client_id = p.connect(p.GUI)
                else:
                    self.client_id = p.connect(p.DIRECT)
                p.setAdditionalSearchPath(pybullet_data.getDataPath())
                p.setGravity(0, 0, -9.81)
                p.loadURDF("plane.urdf")
            except Exception:
                pass
                
        # Setup environment coordinates & entities according to scenario mode
        if self.mode == "disaster":
            self.setup_disaster_rescue()
        elif self.mode == "human_assistance":
            self.setup_human_assistance()
        elif self.mode == "semantic_retrieval":
            self.setup_semantic_retrieval()
        else:
            self.setup_warehouse()

    def setup_disaster_rescue(self):
        """
        Initializes Disaster Rescue environment:
        Robot, Victim, Medical Kit, Fire Hazard, Debris, Corridors.
        """
        self.objects = {
            "robot": {"pos": [-4.0, -4.0, 0.0], "yaw": 0.0},
            "victim_01": {"pos": [4.0, 4.0, 0.0], "type": "person", "state": "injured"},
            "medical_kit_01": {"pos": [-2.0, 3.0, 0.0], "type": "medical_kit", "state": "reachable"},
            "fire_01": {"pos": [0.0, 1.0, 0.0], "radius": 1.5, "type": "hazard_fire"},
            "corridor_A": {"name": "Corridor A (Hazard Route)", "status": "HAZARDOUS", "waypoints": [[-4,-4], [-2,3], [0,1], [4,4]]},
            "corridor_B": {"name": "Corridor B (Primary Safe Route)", "status": "OPEN", "waypoints": [[-4,-4], [-2,3], [0,4], [4,4]]},
            "corridor_C": {"name": "Corridor C (Alternative Route)", "status": "OPEN", "waypoints": [[-4,-4], [-4,0], [0,-3], [4,0], [4,4]]}
        }

    def setup_human_assistance(self):
        self.objects = {
            "robot": {"pos": [0.0, 0.0, 0.0], "yaw": 0.0},
            "water_bottle_01": {"pos": [2.0, -1.0, 0.0], "type": "water_bottle"},
            "cup_01": {"pos": [2.5, -1.5, 0.0], "type": "cup"},
            "user": {"pos": [-2.0, 2.0, 0.0], "type": "person"}
        }

    def setup_semantic_retrieval(self):
        self.objects = {
            "robot": {"pos": [0.0, 0.0, 0.0], "yaw": 0.0},
            "pen_01": {"pos": [1.5, 2.0, 0.0], "type": "pen"},
            "book_01": {"pos": [2.0, 1.0, 0.0], "type": "book"},
            "phone_01": {"pos": [1.0, 2.5, 0.0], "type": "phone"},
            "bottle_01": {"pos": [2.5, 2.5, 0.0], "type": "bottle"}
        }

    def setup_warehouse(self):
        self.objects = {
            "robot": {"pos": [0.0, 0.0, 0.0], "yaw": 0.0},
            "package_patna": {"pos": [3.0, 1.0, 0.0], "type": "package", "label": "Patna"},
            "dispatch_zone": {"pos": [-3.0, 3.0, 0.0], "type": "zone"}
        }

    def inject_obstacle(self, obstacle_id: str = "debris_corridor_B", pos: List[float] = [0.0, 4.0, 0.0]):
        """
        Dynamically places dynamic obstacle blocking Corridor B.
        """
        self.objects[obstacle_id] = {
            "pos": pos,
            "type": "debris",
            "blocking": True
        }
        if "corridor_B" in self.objects:
            self.objects["corridor_B"]["status"] = "BLOCKED"
        return f"Injected dynamic obstacle {obstacle_id} at position {pos}"

    def step(self):
        self.sim_step_count += 1
        if PYBULLET_AVAILABLE and self.client_id is not None:
            try:
                p.stepSimulation()
            except Exception:
                pass
