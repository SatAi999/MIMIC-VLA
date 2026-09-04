import os
import sys
import json
import time
import random
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

PYTHON_EXE = r"D:\Computer_Vision\venv\Scripts\python.exe"

def audit_ppo_model():
    from stable_baselines3 import PPO
    model_path = BASE_DIR / "models" / "rl_policy" / "ppo_v1.zip"
    if not model_path.exists():
        return {"status": "MISSING"}
    
    file_size_bytes = model_path.stat().st_size
    model = PPO.load(str(model_path), device="cpu")
    
    params = model.policy.state_dict()
    num_tensors = len(params)
    total_params = sum(p.numel() for p in params.values())
    non_zero_params = sum((p != 0).sum().item() for p in params.values())
    param_norms = {k: float(p.norm().item()) for k, p in params.items() if "weight" in k or "bias" in k}

    return {
        "status": "VERIFIED",
        "file_path": str(model_path),
        "file_size_bytes": file_size_bytes,
        "algorithm": "PPO",
        "policy": "MlpPolicy",
        "num_tensors": num_tensors,
        "total_parameters": total_params,
        "non_zero_parameters": non_zero_params,
        "param_norms_sample": {k: round(v, 4) for k, v in list(param_norms.items())[:6]}
    }

def audit_state_sensitivity():
    from backend.rl.inference import RLInferenceEngine
    from backend.rl.state_encoder import StateEncoder
    from backend.world_model.state import WorldState, Entity
    
    engine = RLInferenceEngine()
    encoder = StateEncoder()
    ws = WorldState()
    
    # State A: Corridor B Open
    obs_open = encoder.encode(ws, [4.0, 4.0], [{"total_score": 8.5}], learned_risk=0.02, obstacle_injected=False)
    pred_open = engine.predict(obs_open)

    # State B: Corridor B Blocked
    ws.add_entity(Entity(id="debris_01", type="debris", position=[0.0, 4.0, 0.0], properties={"blocking": True}))
    obs_blocked = encoder.encode(ws, [4.0, 4.0], [{"total_score": -12.0}], learned_risk=0.95, obstacle_injected=True)
    pred_blocked = engine.predict(obs_blocked)

    # State C: Target Reached
    ws.robot.position = [4.0, 4.0, 0.0]
    obs_target = encoder.encode(ws, [4.0, 4.0], [{"total_score": 10.0}], learned_risk=0.0, obstacle_injected=False)
    pred_target = engine.predict(obs_target)

    return {
        "state_open": pred_open,
        "state_blocked": pred_blocked,
        "state_target": pred_target,
        "dynamic_response_verified": pred_open["action"] != pred_blocked["action"] or pred_open["action_name"] != pred_blocked["action_name"]
    }

def audit_multiseed_evaluation(seeds=[42, 123, 456, 789, 2026], runs_per_seed=50):
    from backend.rl.environment import MimicVLAEnv
    from backend.rl.inference import RLInferenceEngine
    from backend.rl.config import rl_config
    
    engine = RLInferenceEngine()
    seed_results = {}

    for s in seeds:
        env = MimicVLAEnv(seed=s)
        
        # 1. Random Policy
        random_success = 0
        for r in range(runs_per_seed):
            obs, _ = env.reset(seed=s + r)
            done = False
            while not done:
                action = random.randint(0, 5)
                obs, reward, done, _, info = env.step(action)
                if info.get("success"):
                    random_success += 1

        # 2. Baseline Planner (RL Disabled)
        rl_config.rl_enabled = False
        baseline_success = 0
        baseline_recoveries = 0
        for r in range(runs_per_seed):
            obs, _ = env.reset(seed=s + r)
            done = False
            while not done:
                action = 2 if env.corridor_b_blocked else 0
                obs, reward, done, _, info = env.step(action)
                if info.get("success"):
                    baseline_success += 1
                if info.get("recovery"):
                    baseline_recoveries += 1

        # 3. Trained PPO Policy (RL Enabled)
        rl_config.rl_enabled = True
        ppo_success = 0
        ppo_recoveries = 0
        for r in range(runs_per_seed):
            obs, _ = env.reset(seed=s + r)
            done = False
            while not done:
                pred = engine.predict(obs)
                action = pred["action"]
                obs, reward, done, _, info = env.step(action)
                if info.get("success"):
                    ppo_success += 1
                if info.get("recovery"):
                    ppo_recoveries += 1

        seed_results[str(s)] = {
            "random_policy_success_pct": round((random_success / runs_per_seed) * 100.0, 1),
            "baseline_planner_success_pct": round((baseline_success / runs_per_seed) * 100.0, 1),
            "ppo_policy_success_pct": round((ppo_success / runs_per_seed) * 100.0, 1),
            "ppo_recovery_rate_pct": round((ppo_recoveries / runs_per_seed) * 100.0, 1)
        }

    # Aggregate Statistics
    ppo_scores = [v["ppo_policy_success_pct"] for v in seed_results.values()]
    mean_ppo = round(float(np.mean(ppo_scores)), 1)
    std_ppo = round(float(np.std(ppo_scores)), 1)

    return {
        "seeds": seeds,
        "runs_per_seed": runs_per_seed,
        "seed_results": seed_results,
        "aggregate_ppo_success_mean_pct": mean_ppo,
        "aggregate_ppo_success_std_pct": std_ppo
    }

def audit_latency(iterations=1000):
    from backend.rl.inference import RLInferenceEngine
    from backend.rl.state_encoder import StateEncoder
    from backend.world_model.state import WorldState

    engine = RLInferenceEngine()
    encoder = StateEncoder()
    obs = encoder.encode(WorldState(), [4.0, 4.0], [{"total_score": 8.0}], learned_risk=0.02)

    latencies = []
    for _ in range(iterations):
        t0 = time.time()
        _ = engine.predict(obs)
        latencies.append((time.time() - t0) * 1000.0)

    latencies = np.array(latencies)
    return {
        "iterations": iterations,
        "mean_ms": round(float(np.mean(latencies)), 3),
        "median_ms": round(float(np.median(latencies)), 3),
        "p95_ms": round(float(np.percentile(latencies, 95)), 3),
        "p99_ms": round(float(np.percentile(latencies, 99)), 3)
    }

def main():
    print("================================================================")
    print("  MIMIC-VLA INDEPENDENT ADVERSARIAL RL FORENSIC AUDIT RUNNER")
    print("================================================================\n")

    print("[AUDIT 1/5] Auditing PPO Model Weights & Parameters...")
    ppo_meta = audit_ppo_model()

    print("[AUDIT 2/5] Auditing State Sensitivity & Dynamic Response...")
    state_meta = audit_state_sensitivity()

    print("[AUDIT 3/5] Auditing Multi-Seed Performance (5 Seeds x 50 Runs)...")
    seed_meta = audit_multiseed_evaluation()

    print("[AUDIT 4/5] Auditing Inference Latency (1,000 Iterations)...")
    latency_meta = audit_latency()

    raw_results = {
        "timestamp": time.time(),
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "ppo_model_audit": ppo_meta,
        "state_sensitivity_audit": state_meta,
        "multiseed_audit": seed_meta,
        "latency_audit": latency_meta
    }

    raw_file = REPORTS_DIR / "RL_FORENSIC_RAW_RESULTS.json"
    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(raw_results, f, indent=2)

    # Write separate specific result JSONs
    with open(REPORTS_DIR / "RL_MULTISEED_RESULTS.json", "w", encoding="utf-8") as f:
        json.dump(seed_meta, f, indent=2)

    with open(REPORTS_DIR / "RL_LATENCY_RESULTS.json", "w", encoding="utf-8") as f:
        json.dump(latency_meta, f, indent=2)

    print(f"\nAudit complete! Raw results saved to: {raw_file}")

if __name__ == "__main__":
    main()
