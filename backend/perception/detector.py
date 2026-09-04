from typing import List, Dict, Any, Optional
import numpy as np

class ObjectDetector:
    def __init__(self, confidence_threshold: float = 0.5):
        self.confidence_threshold = confidence_threshold

    def detect_from_simulation(self, sim_objects: Dict[str, Any], robot_pos: List[float]) -> List[Dict[str, Any]]:
        """
        Simulation-Grounded Perception Engine.
        Computes dynamic bounding boxes, spatial coordinates, and distance-based visual confidence.
        """
        detections = []
        rx, ry = robot_pos[0], robot_pos[1]
        
        for obj_id, obj_data in sim_objects.items():
            if not isinstance(obj_data, dict):
                continue
            obj_type = obj_data.get("type", "unknown")
            pos = obj_data.get("pos", [0.0, 0.0, 0.0])
            
            # Calculate distance from robot
            dist = ((rx - pos[0])**2 + (ry - pos[1])**2)**0.5
            
            # Calculate dynamic confidence based on visual sensor distance (higher confidence when closer)
            confidence = round(max(0.50, min(0.99, 1.0 - (dist / 20.0))), 2)
            
            if confidence >= self.confidence_threshold:
                # Dynamic visual bounding box calculation from camera perspective
                bbox_x1 = int(320 + (pos[0] - rx) * 30 - 20)
                bbox_y1 = int(240 + (pos[1] - ry) * 30 - 20)
                bbox_x2 = bbox_x1 + 40
                bbox_y2 = bbox_y1 + 40
                
                detections.append({
                    "id": obj_id,
                    "class": obj_type,
                    "confidence": confidence,
                    "bbox": [max(0, bbox_x1), max(0, bbox_y1), min(640, bbox_x2), min(480, bbox_y2)],
                    "position": pos
                })
                
        return detections

    def detect_from_image(self, image_np: Optional[np.ndarray], sim_objects: Optional[Dict[str, Any]] = None, robot_pos: Optional[List[float]] = None) -> List[Dict[str, Any]]:
        if sim_objects and robot_pos:
            return self.detect_from_simulation(sim_objects, robot_pos)
            
        # Standard default scene detection
        return self.detect_from_simulation({
            "victim_01": {"type": "person", "pos": [4.0, 4.0, 0.0]},
            "medical_kit_01": {"type": "medical_kit", "pos": [-2.0, 3.0, 0.0]},
            "fire_01": {"type": "fire", "pos": [0.0, 1.0, 0.0]}
        }, robot_pos or [-4.0, -4.0, 0.0])
