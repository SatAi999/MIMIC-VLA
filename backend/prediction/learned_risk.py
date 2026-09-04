import os
import joblib
import numpy as np
from pathlib import Path
from typing import List, Dict, Any

class LearnedRiskPredictor:
    def __init__(self):
        self.model_path = Path("models/risk_predictor/risk_model.joblib")
        self.model = None
        if self.model_path.exists():
            try:
                self.model = joblib.load(self.model_path)
            except Exception:
                self.model = None

    def predict_collision_risk(self, route_length: float, obstacle_density: float, min_obstacle_dist: float, hazard_dist: float, n_turns: int = 2, corridor_width: float = 2.0) -> float:
        """
        Predicts collision risk probability using the trained RandomForest model.
        Returns float probability in [0.0, 1.0].
        """
        if self.model is None:
            # Physics-heuristic estimation if model file is not present
            if min_obstacle_dist < 1.0 or hazard_dist < 1.5:
                return 0.92
            return round(max(0.01, min(0.99, obstacle_density * 0.5 + (1.0 / (min_obstacle_dist + 0.1)) * 0.3)), 2)

        features = np.array([[route_length, obstacle_density, min_obstacle_dist, hazard_dist, n_turns, corridor_width]])
        try:
            probs = self.model.predict_proba(features)
            risk = float(probs[0][1]) if len(probs[0]) > 1 else float(probs[0][0])
            return round(risk, 2)
        except Exception:
            return 0.10
