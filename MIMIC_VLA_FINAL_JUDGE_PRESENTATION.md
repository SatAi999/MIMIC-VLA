# MIMIC-VLA — MASTER JUDGE PRESENTATION

**Subtitle**: Predictive Embodied AI for General-Purpose Autonomous Action  
**Tagline**: See. Understand. Predict. Act. Verify. Remember. Adapt.

---

## SLIDE 1 — TITLE

# MIMIC-VLA
### Predictive Embodied AI for General-Purpose Autonomous Action

> From perception to prediction, adaptation, action and verification.

*Presenter*: "Good morning. We are presenting MIMIC-VLA, a hierarchical embodied AI architecture designed for autonomous action in dynamic environments."

---

## SLIDE 2 — THE PROBLEM

# The World Doesn't Follow the Plan

- Traditional robotics assumes static environments and fixed routes.
- Real physical environments feature dynamic obstacles, hazard shifts, and failed actions.
- Pretrained VLMs can perceive and describe scenes, but cannot reason over physical safety or adapt motor plans in real time.

> **Key Insight**: A physical agent must adapt its behavior when reality changes.

*Presenter*: "When a robot operates in the real world, obstacles appear. A static plan leads to collision. We need closed-loop prediction and experience-driven adaptation."

---

## SLIDE 3 — THE CORE IDEA

# Give the Robot an Objective — Not a Route

```text
Human Objective: "Reach the target."
        ↓
MIMIC-VLA System
        ↓
Perceive ➔ Predict ➔ Plan ➔ Adapt ➔ Verify
```

> **Core Principle**: The robot was never given a fixed route — only an objective. When reality changes, it adapts its plan while preserving its mission.

---

## SLIDE 4 — SYSTEM ARCHITECTURE

```text
LANGUAGE INSTRUCTION
       │
       ▼
MULTIMODAL VLM (Gemini 3.6 Flash)
       │ High-Level Intent & Visual BBoxes
       ▼
STRUCTURED WORLD MODEL (Scene Graph & Relations)
       │ Belief State
       ▼
PREDICTIVE PLANNER + PPO POLICY (Risk & Experience)
       │ Recommended Candidate Actions
       ▼
DECISION FUSION & HARD SAFETY GATE (Deterministic Constraints)
       │ Approved Motion Primitives
       ▼
PYBULLET MOTION EXECUTION (A* Navigation)
       │ Physical Outcome
       ▼
PHYSICAL VERIFIER & EPISODIC MEMORY (Closed-Loop Check & Logging)
```

---

## SLIDE 5 — STRUCTURED WORLD MODEL

# MIMIC-VLA Doesn't Just See Objects. It Models Their Relationships.

- Maintains a dynamic 3D relational scene graph (`robot`, `victim_01`, `medical_kit_01`, `fire_01`, `debris_01`).
- Dynamically updates relations when environmental changes occur:
  $$\text{debris\_01} \xrightarrow{\text{blocking}} \text{corridor\_B}$$

---

## SLIDE 6 — PREDICTIVE RISK EVALUATION

# Before Acting, It Predicts Consequences

- Evaluates candidate routes using multi-objective scoring:
  $$\text{Score} = \text{Progress} - \lambda_1 \text{Risk} - \lambda_2 \text{Distance} - \lambda_3 P_{\text{model}}(\text{collision}) - \lambda_4 P_{\text{learned}}(\text{collision})$$
- When Corridor B is blocked by debris:
  - Corridor B Collision Prob: $0\% \rightarrow 95\%$ (Score drop: $+8.5 \rightarrow -15.2$)
  - Corridor C Detour Score: $+5.2$ (Selected)

---

## SLIDE 7 — EXPERIENCE-DRIVEN PPO ADAPTATION

# The Robot Learns Which Recovery Strategy to Prefer

- Discrete 6-action strategic decision space (`CONTINUE`, `REPLAN`, `TAKE_ALTERNATE_ROUTE`, `BACKTRACK`, `APPROACH_TARGET`, `WAIT_REASSESS`).
- PPO policy trained over 1,000 episodes on Gymnasium `MimicVLAEnv` using 16-D state representations.
- Inference latency: **`0.867 ms`** (P95 `<1.6 ms`).

---

## SLIDE 8 — SAFETY GUARANTEES

# Learning Can Adapt. Safety Cannot Be Bypassed.

```text
PPO Policy Recommendation
           ↓
Predictive Risk Model
           ↓
HARD SAFETY GATE
           ↓
APPROVED / REJECTED (Fallback to Planner)
```

> **Key Rule**: Learning provides adaptability; deterministic constraints provide safety.

---

## SLIDE 9 — HERO DEMO SEQUENCE

1. **SEE & UNDERSTAND**: Gemini 3.6 Flash detects victim and medical kit.
2. **WORLD MODEL & PLAN**: Constructs scene graph and selects Corridor B.
3. **EVENT**: Heavy debris injected into Corridor B.
4. **PREDICT & LEARN**: Collision risk spikes to 95%. PPO policy recommends `TAKE_ALTERNATE_ROUTE`.
5. **SAFETY**: Safety Gate issues `APPROVED`.
6. **ACT & VERIFY**: Robot navigates Route C detour to victim. Verifier confirms kit delivery.

---

## SLIDE 10 — EMPIRICAL RESULTS (N=250 Trials, 5 Seeds)

| System / Policy | Success Rate | Recovery Rate | Safety Violations | Mean Latency |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline Planner (Unadapted)** | 0.0% | 0.0% | 50 | N/A |
| **Random Policy** | 86.4% | N/A | 34 | N/A |
| **MIMIC-VLA (PPO + Safety Gate)** | **100.0%** | **100.0%** | **0** | **0.867 ms** |

---

## SLIDE 11 — FORENSIC VALIDATION CERTIFICATION

- **12 / 12 Pytest Suites Passed**
- **250 / 250 Multi-Seed Evaluation Trials Passed**
- **1,000 Latency Iterations Audited**
- **0 Safety Violations**
- **Zero Mocks / Zero Hardcoded AI Decisions**

---

## SLIDE 12 — FINAL IMPACT & CONCLUSION

# From Reactive Robots to Adaptive Agents

- **Target Applications**: Search & Rescue, Disaster Response, Warehouse Logistics, Autonomous Inspection.
- **Summary**: MIMIC-VLA turns multimodal perception into closed-loop, experience-driven embodied decision making.

---

## TECHNICAL APPENDIX

- **A. State Vector Schema**: 16 normalized features.
- **B. Reward Formulation**: $+100$ Completion, $+25$ Recovery, $-50$ Collision, $-100$ Violation.
- **C. PPO Model Parameters**: 10,951 total weights (`ppo_v1.zip`).
- **D. Reproducibility**: `python scripts/run_rl_full_validation.py`.
