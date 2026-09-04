import os
import json
import random
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib

def generate_synthetic_trajectory_dataset(n_samples: int = 500, seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)

    X = []
    y = []

    for _ in range(n_samples):
        route_length = random.uniform(5.0, 25.0)
        obstacle_density = random.uniform(0.0, 1.0)
        min_obstacle_dist = random.uniform(0.2, 5.0)
        hazard_dist = random.uniform(0.1, 6.0)
        n_turns = random.randint(1, 6)
        corridor_width = random.uniform(1.0, 4.0)

        # Physics-based collision ground truth determination
        collision_prob = 0.0
        if min_obstacle_dist < 1.0 or hazard_dist < 1.5 or obstacle_density > 0.7:
            collision = 1
        else:
            collision = 0 if random.random() > 0.1 else 1

        features = [route_length, obstacle_density, min_obstacle_dist, hazard_dist, n_turns, corridor_width]
        X.append(features)
        y.append(collision)

    return np.array(X), np.array(y)

def train_and_save_risk_model():
    model_dir = Path("models/risk_predictor")
    model_dir.mkdir(parents=True, exist_ok=True)

    X, y = generate_synthetic_trajectory_dataset(n_samples=500, seed=42)
    split_idx = int(0.8 * len(X))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    acc = round(float(accuracy_score(y_test, y_pred)), 4)
    prec = round(float(precision_score(y_test, y_pred)), 4)
    rec = round(float(recall_score(y_test, y_pred)), 4)
    f1 = round(float(f1_score(y_test, y_pred)), 4)
    cm = confusion_matrix(y_test, y_pred).tolist()

    metrics = {
        "model_type": "RandomForestClassifier",
        "n_samples": 500,
        "n_estimators": 50,
        "test_accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "confusion_matrix": cm,
        "feature_names": ["route_length", "obstacle_density", "min_obstacle_dist", "hazard_dist", "n_turns", "corridor_width"]
    }

    joblib.dump(model, model_dir / "risk_model.joblib")

    with open(model_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print("Learned Risk Model Trained Successfully!")
    print(f"Metrics: Acc: {acc*100:.1f}%, Prec: {prec*100:.1f}%, Rec: {rec*100:.1f}%, F1: {f1:.4f}")
    return metrics

if __name__ == "__main__":
    train_and_save_risk_model()
