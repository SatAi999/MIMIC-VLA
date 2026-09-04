import json
import random
import argparse
from pathlib import Path
from typing import Dict, Any, List

from backend.rl.environment import MimicVLAEnv
from backend.rl.inference import RLInferenceEngine
from backend.rl.config import rl_config

def evaluate_baseline_vs_rl(runs: int = 50, seed: int = 42) -> Dict[str, Any]:
    random.seed(seed)
    env = MimicVLAEnv(seed=seed)
    rl_engine = RLInferenceEngine()

    baseline_success = 0
    baseline_recoveries = 0
    baseline_steps = []

    rl_success = 0
    rl_recoveries = 0
    rl_steps = []

    # 1. Baseline Evaluation (No RL)
    rl_config.rl_enabled = False
    for r in range(runs):
        obs, _ = env.reset(seed=seed + r)
        done = False
        steps = 0
        while not done:
            steps += 1
            # Baseline uses Action 2 (TAKE_ALTERNATE_ROUTE) when obstacle injected
            action = 2 if env.corridor_b_blocked else 0
            obs, reward, done, _, info = env.step(action)
            if info.get("success"):
                baseline_success += 1
            if info.get("recovery"):
                baseline_recoveries += 1
        baseline_steps.append(steps)

    # 2. RL-Enhanced Evaluation (PPO RL Policy)
    rl_config.rl_enabled = True
    for r in range(runs):
        obs, _ = env.reset(seed=seed + r)
        done = False
        steps = 0
        while not done:
            steps += 1
            prediction = rl_engine.predict(obs)
            action = prediction["action"]
            obs, reward, done, _, info = env.step(action)
            if info.get("success"):
                rl_success += 1
            if info.get("recovery"):
                rl_recoveries += 1
        rl_steps.append(steps)

    results = {
        "runs_per_condition": runs,
        "seed": seed,
        "baseline_planner": {
            "success_rate_pct": round((baseline_success / runs) * 100.0, 1),
            "recovery_rate_pct": round((baseline_recoveries / runs) * 100.0, 1),
            "mean_steps": round(sum(baseline_steps) / len(baseline_steps), 2)
        },
        "rl_enhanced_mimic_vla": {
            "success_rate_pct": round((rl_success / runs) * 100.0, 1),
            "recovery_rate_pct": round((rl_recoveries / runs) * 100.0, 1),
            "mean_steps": round(sum(rl_steps) / len(rl_steps), 2),
            "policy": "PPO-v1 (Stable-Baselines3)"
        }
    }

    out_dir = Path("reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "RL_ABLATION_RESULTS.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n================================================================")
    print("  RL COMPARATIVE EVALUATION RESULTS SUMMARY")
    print("================================================================")
    print(f"Baseline Planner: Success Rate {results['baseline_planner']['success_rate_pct']}%, Recovery Rate {results['baseline_planner']['recovery_rate_pct']}%")
    print(f"MIMIC-VLA + RL:   Success Rate {results['rl_enhanced_mimic_vla']['success_rate_pct']}%, Recovery Rate {results['rl_enhanced_mimic_vla']['recovery_rate_pct']}%")
    print("================================================================\n")

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    evaluate_baseline_vs_rl(runs=args.runs, seed=args.seed)
