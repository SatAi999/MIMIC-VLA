# MIMIC-VLA — RAW BENCHMARK EVIDENCE REPORT

**Execution Date**: September 3, 2026  
**Trial Seed**: 42  
**Trials per Architecture**: 50  
**Total Monte-Carlo Simulations**: 300  
**Raw Data File**: `data/benchmark_results.json`  

---

## 1. Summary Metrics Table

| Architecture / Controlled Ablation | Trials ($N$) | Success Count | Success Rate | Recovery Rate | Safety Violations | Verifier Accuracy | Path Efficiency ($L_{opt}/L_{act}$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Ablation 1: Rule-Based (Static Policy)** | 50 | 0 / 50 | **0.0%** | **0.0%** | 50 | **0.0%** | 0.81 |
| **Ablation 2: Perception + Direct Action (VLM-Only)** | 50 | 0 / 50 | **0.0%** | **0.0%** | 50 | **0.0%** | 0.81 |
| **Ablation 3: VLM + Task Planner (No Safety Gate)** | 50 | 24 / 50 | **48.0%** | **53.3%** | 26 | **52.0%** | 0.61 |
| **Ablation 4: World Model + Planner (No Safety Gate)** | 50 | 50 / 50 | **100.0%** | **100.0%** | 0 | **84.0%** | 0.66 |
| **Ablation 5: World Model + Planner + Safety Gate** | 50 | 50 / 50 | **100.0%** | **100.0%** | 0 | **90.0%** | 0.66 |
| **MIMIC-VLA (Full Hierarchical Architecture)** | 50 | 50 / 50 | **100.0%** | **100.0%** | **0** | **100.0%** | **0.68** |

---

## 2. Sample Raw Trial Data Snippet

Excerpt from `data/benchmark_results.json`:

```json
{
  "metadata": {
    "timestamp": "2026-09-03 00:42:15",
    "seed": 42,
    "runs_per_architecture": 50
  },
  "raw_trials_sample": [
    {
      "trial_id": 1,
      "architecture": "MIMIC-VLA (Full Hierarchical Architecture)",
      "success": true,
      "recovery": true,
      "safety_violation": false,
      "verification_passed": true,
      "path_length": 15.2
    },
    {
      "trial_id": 1,
      "architecture": "Ablation 1: Rule-Based (Static Policy)",
      "success": false,
      "recovery": false,
      "safety_violation": true,
      "verification_passed": false,
      "path_length": 11.3
    }
  ]
}
```

---

## 3. Reproducibility Instructions

To re-run all 300 Monte-Carlo trial simulations and regenerate `data/benchmark_results.json`:

```bash
& "D:\Computer_Vision\venv\Scripts\python.exe" -m backend.evaluation.benchmark --runs 50 --seed 42
```
