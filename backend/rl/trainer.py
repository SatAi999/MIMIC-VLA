import os
import argparse
import json
from pathlib import Path
from stable_baselines3 import PPO
from backend.rl.environment import MimicVLAEnv

def train_ppo_policy(episodes: int = 1000, seed: int = 42, save_dir: str = "models/rl_policy"):
    model_dir = Path(save_dir)
    model_dir.mkdir(parents=True, exist_ok=True)

    print(f"Initializing PPO Training with {episodes} episodes (Seed: {seed})...")
    env = MimicVLAEnv(seed=seed)

    # Train PPO agent on CPU for maximum MLP speed
    model = PPO(
        "MlpPolicy",
        env,
        learning_rate=0.0003,
        n_steps=64,
        batch_size=32,
        n_epochs=10,
        gamma=0.99,
        verbose=0,
        seed=seed,
        device="cpu"
    )

    total_timesteps = episodes * 10
    model.learn(total_timesteps=total_timesteps)

    policy_file = model_dir / "ppo_v1.zip"
    model.save(str(policy_file))

    meta = {
        "algorithm": "PPO",
        "library": "Stable-Baselines3",
        "policy_architecture": "MlpPolicy",
        "episodes": episodes,
        "total_timesteps": total_timesteps,
        "seed": seed,
        "save_path": str(policy_file),
        "feature_dim": 16,
        "action_dim": 6
    }

    with open(model_dir / "training_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"\nPPO Policy Successfully Trained and Saved to: {policy_file}")
    return meta

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train MIMIC-VLA PPO Policy")
    parser.add_argument("--episodes", type=int, default=1000, help="Number of training episodes")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    train_ppo_policy(episodes=args.episodes, seed=args.seed)
