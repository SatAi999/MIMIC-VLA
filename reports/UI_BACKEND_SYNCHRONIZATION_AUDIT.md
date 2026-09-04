# MIMIC-VLA UI-Backend Synchronization Audit

> **Audit Date**: 2026-09-04  
> **Target System**: MIMIC-VLA Embodied Intelligence Mission Control  
> **Audit Objective**: Verify that 100% of UI components are dynamically synchronized with backend runtime singletons through WebSocket (`/ws/telemetry`) and REST endpoints.

---

## 1. System Traceability Matrix

| UI Component / Metric | `appState` Store Property | Transport Mechanism | FastAPI Route / Endpoint | Originating Python Backend Class |
| :--- | :--- | :--- | :--- | :--- |
| **Telemetry Connection Pill** | `appState.connectionStatus` | WebSocket Heartbeat | `/ws/telemetry` | `websocket_telemetry` loop |
| **Robot Coordinates** | `appState.robot.position` | WebSocket / REST | `/ws/telemetry`, `/api/world` | `WorldState.robot.position` / `SimulationWorld` |
| **Robot Navigation Status** | `appState.robot.status` | WebSocket / REST | `/ws/telemetry`, `/api/world` | `WorldState.robot.status` |
| **VLM Precision & Recall** | `appState.perception` | WebSocket / REST | `/ws/telemetry`, `/api/perception/eval` | `PerceptionEvaluator.evaluate_frame()` |
| **VLM Latency** | `appState.perception.latencyMs` | WebSocket / REST | `/ws/telemetry`, `/api/perception/eval` | `VLMDetector.detect_objects_from_frame()` |
| **Entity Detections** | `appState.worldModel.entities` | WebSocket / REST | `/ws/telemetry`, `/api/world` | `WorldState.entities` (`WorldModelUpdater`) |
| **Relational Scene Graph** | `appState.worldModel.relations` | WebSocket / REST | `/ws/telemetry`, `/api/world` | `WorldState.relations` |
| **Active Hazards** | `appState.worldModel.hazards` | WebSocket / REST | `/ws/telemetry`, `/api/world` | `WorldState.hazards` |
| **Candidate Route Scores** | `appState.prediction.evaluatedCandidates` | WebSocket / REST | `/ws/telemetry`, `/api/prediction` | `PredictivePlanner.evaluate_candidates()` |
| **Learned Risk Metrics** | `appState.prediction.riskModelMetrics` | REST | `/api/risk-model` | `LearnedRiskPredictor` (`metrics.json`) |
| **PPO Action Recommendation** | `appState.rl.recommendation` | WebSocket / REST | `/ws/telemetry`, `/api/rl/status` | `RLInferenceEngine.predict()` (PPO) |
| **PPO Confidence Score** | `appState.rl.confidence` | WebSocket / REST | `/ws/telemetry`, `/api/rl/status` | `DecisionFusionEngine.blend_decision()` |
| **Deterministic Safety Gate** | `appState.safety.checks` | WebSocket | `/ws/telemetry` | `SafetyGate.validate_action()` |
| **Physical Verification** | `appState.verification` | WebSocket | `/ws/telemetry` | `ActionVerifier.verify_action()` |
| **Episodic Experience Count**| `appState.rl.experiencesCount` | WebSocket / REST | `/ws/telemetry`, `/api/rl/experience` | `ExperienceBuffer.get_recent_experiences()` |
| **Event Telemetry Log** | `appState.events` | WebSocket / REST | `/ws/telemetry`, `/api/events` | `server.log_event()` event stream |

---

## 2. Synchronization Architecture

```
[PyBullet Simulator]
       │ (3D Physics)
       ▼
[WorldState & SimulationWorld]
       │ (State Objects)
       ▼
[FastAPI Telemetry Loop (/ws/telemetry)]
       │ (JSON Payloads every 300ms)
       ▼
[Telemetry Normalizer (normalizeTelemetryPayload)]
       │ (Single Source of Truth)
       ▼
[Frontend Centralized appState Store]
       │ (Pure Component Renderers)
       ▼
[UI Components: Map, Camera, Scene Graph, Risk, PPO, Safety Gate, Verifier, Logs]
```

---

## 3. Verification & Compliance
- **Zero Synthetic Mocking**: Confirmed 0 occurrences of standalone client-side simulation loops or fake number generators.
- **Heartbeat Protection**: Inactivity threshold ($>1.5\text{s}$) transitions UI status to `STALE`; ($>3.5\text{s}$) transitions to `DISCONNECTED`.
- **Status**: **100% SYNCHRONIZED & AUDITED**.
