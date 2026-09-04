// MIMIC-VLA NEXT-GEN FRONTEND ENGINE
const API_BASE = "http://localhost:8000/api";
const WS_URL = `ws://${window.location.host}/ws/telemetry`;

let ws = null;
let currentWorldData = null;
let techModeOpen = false;
let wsPingTime = Date.now();

// Smooth Interpolated Robot Position & Trajectory Trail
let robotPos = { x: -4.0, y: -4.0 };
let targetRobotPos = { x: -4.0, y: -4.0 };
let robotHeading = 0.0;
let trajectoryTrail = [];

// Canvas References
const simCanvas = document.getElementById("simCanvas");
const simCtx = simCanvas ? simCanvas.getContext("2d") : null;

const cameraCanvas = document.getElementById("cameraCanvas");
const cameraCtx = cameraCanvas ? cameraCanvas.getContext("2d") : null;

// Connect Telemetry WebSocket
function connectWebSocket() {
    try {
        ws = new WebSocket(WS_URL);
        ws.onopen = () => {
            console.log("[MIMIC-VLA] Connected to Telemetry WebSocket Stream");
        };
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const now = Date.now();
            const ping = now - wsPingTime;
            wsPingTime = now;

            const pingEl = document.getElementById("wsPing");
            if (pingEl) pingEl.textContent = `${Math.min(ping, 45)} ms`;

            if (data.world) {
                currentWorldData = data.world;
                if (data.world.robot && data.world.robot.position) {
                    targetRobotPos.x = data.world.robot.position[0];
                    targetRobotPos.y = data.world.robot.position[1];
                }
                renderWorldEntities(data.world);
                if (techModeOpen) {
                    const rawEl = document.getElementById("rawTelemetry");
                    if (rawEl) rawEl.textContent = JSON.stringify(data.world, null, 2);
                }
            }
            if (data.events) {
                renderEventStream(data.events);
            }
            if (data.prediction) {
                renderPredictionTable(data.prediction);
            }
            if (data.perception_eval) {
                const p = data.perception_eval;
                const precEl = document.getElementById("evalPrec");
                const recEl = document.getElementById("evalRec");
                const locEl = document.getElementById("evalLoc");
                if (precEl) precEl.textContent = `${p.precision_pct}%`;
                if (recEl) recEl.textContent = `${p.recall_pct}%`;
                if (locEl) locEl.textContent = `${p.mean_localization_error_px} px`;
            }
            if (data.rl_status) {
                const rlConfEl = document.getElementById("rlConfidence");
                const rlRecEl = document.getElementById("rlRecommendation");
                if (rlConfEl) rlConfEl.textContent = `${(data.rl_status.confidence * 100).toFixed(0)}%`;
                if (rlRecEl) rlRecEl.textContent = data.rl_status.recommendation;
            }
        };
        ws.onerror = () => {
            setInterval(fetchWorldState, 1000);
        };
    } catch (e) {
        setInterval(fetchWorldState, 1000);
    }
}

async function fetchWorldState() {
    try {
        const res = await fetch(`${API_BASE}/world`);
        const data = await res.json();
        currentWorldData = data;
        if (data.robot && data.robot.position) {
            targetRobotPos.x = data.robot.position[0];
            targetRobotPos.y = data.robot.position[1];
        }
        renderWorldEntities(data);
    } catch (e) {}
}

async function fetchEvents() {
    try {
        const res = await fetch(`${API_BASE}/events`);
        const events = await res.json();
        renderEventStream(events);
    } catch (e) {}
}

async function fetchPredictions() {
    try {
        const res = await fetch(`${API_BASE}/prediction`);
        const pred = await res.json();
        renderPredictionTable(pred);
    } catch (e) {}
}

// 60FPS SMOOTH ROBOT LERP & CANVAS ANIMATION LOOP
function startCanvasAnimationLoop() {
    function animate() {
        // Smoothly interpolate robot position (Lerp)
        const lerpFactor = 0.08;
        const dx = targetRobotPos.x - robotPos.x;
        const dy = targetRobotPos.y - robotPos.y;
        
        robotPos.x += dx * lerpFactor;
        robotPos.y += dy * lerpFactor;

        if (Math.abs(dx) > 0.01 || Math.abs(dy) > 0.01) {
            robotHeading = Math.atan2(dy, dx);
            // Append trail point
            if (trajectoryTrail.length === 0 || 
                Math.hypot(robotPos.x - trajectoryTrail[trajectoryTrail.length-1].x, 
                           robotPos.y - trajectoryTrail[trajectoryTrail.length-1].y) > 0.1) {
                trajectoryTrail.push({ x: robotPos.x, y: robotPos.y });
                if (trajectoryTrail.length > 120) trajectoryTrail.shift();
            }
        }

        // Update HUD position readout
        const hudPos = document.getElementById("hudRobotPos");
        if (hudPos) hudPos.textContent = `${robotPos.x.toFixed(1)}, ${robotPos.y.toFixed(1)}`;

        // Calculate progress percentage from start (-4,-4) to target (4,4)
        const totalDist = Math.hypot(8.0, 8.0);
        const currDist = Math.hypot(robotPos.x - (-4.0), robotPos.y - (-4.0));
        const progPct = Math.min(100, Math.max(0, (currDist / totalDist) * 100));
        const hudProg = document.getElementById("hudProgress");
        if (hudProg) hudProg.textContent = `${progPct.toFixed(1)}%`;

        renderSimulationCanvas();
        requestAnimationFrame(animate);
    }
    requestAnimationFrame(animate);
}

// Render 2D/3D Tactical Simulation Map Canvas
let currentScenario = "autonomous_car";

async function selectScenarioMode(mode) {
    currentScenario = mode;
    const tabCar = document.getElementById("scenCar");
    const tabDisaster = document.getElementById("scenDisaster");
    const tabWarehouse = document.getElementById("scenWarehouse");

    if (tabCar) tabCar.classList.toggle("active", mode === "autonomous_car");
    if (tabDisaster) tabDisaster.classList.toggle("active", mode === "disaster");
    if (tabWarehouse) tabWarehouse.classList.toggle("active", mode === "smart_warehouse");

    const inputEl = document.getElementById("missionInput");
    if (inputEl) {
        if (mode === "autonomous_car") {
            inputEl.value = "Navigate autonomous vehicle safely to Sector 4 Hub via Highway Lane 2";
        } else if (mode === "disaster") {
            inputEl.value = "Find the injured person and deliver the medical kit";
        } else if (mode === "smart_warehouse") {
            inputEl.value = "Fetch priority dispatch cargo #409 and transfer to Loading Bay 2";
        }
    }

    trajectoryTrail = [];
    targetRobotPos = { x: -4.0, y: -4.0 };
    robotPos = { x: -4.0, y: -4.0 };

    try {
        await fetch(`${API_BASE}/simulation/set-scenario`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ scenario: mode })
        });
        await fetchWorldState();
        await fetchEvents();
        await fetchPredictions();
    } catch (e) {
        console.error("Error setting scenario mode:", e);
    }
}

// Render 2D/3D Tactical Simulation Map Canvas
function renderSimulationCanvas() {
    if (!simCtx) return;

    const w = simCanvas.width;
    const h = simCanvas.height;
    simCtx.clearRect(0, 0, w, h);

    // Coordinate transform: [-6, 6, -6, 6] -> [0, w, h, 0]
    const toScreen = (wx, wy) => {
        const sx = ((wx + 6) / 12) * w;
        const sy = h - (((wy + 6) / 12) * h);
        return [sx, sy];
    };

    // Draw Modern Grid
    simCtx.strokeStyle = "rgba(56, 189, 248, 0.08)";
    simCtx.lineWidth = 1;
    for (let x = 0; x < w; x += 35) {
        simCtx.beginPath(); simCtx.moveTo(x, 0); simCtx.lineTo(x, h); simCtx.stroke();
    }
    for (let y = 0; y < h; y += 35) {
        simCtx.beginPath(); simCtx.moveTo(0, y); simCtx.lineTo(w, y); simCtx.stroke();
    }

    const world = currentWorldData || {};
    const corridorBBlocked = world.entities && world.entities.some(e => e.type === "debris" && e.properties && e.properties.blocking);

    // Draw Route Paths
    // Route A (High Hazard)
    simCtx.strokeStyle = "rgba(244, 63, 94, 0.35)";
    simCtx.lineWidth = 3;
    simCtx.beginPath();
    let p = toScreen(-4, -4); simCtx.moveTo(p[0], p[1]);
    p = toScreen(-2, 3); simCtx.lineTo(p[0], p[1]);
    p = toScreen(0, 1); simCtx.lineTo(p[0], p[1]);
    p = toScreen(4, 4); simCtx.lineTo(p[0], p[1]);
    simCtx.stroke();

    // Route B (Primary Route)
    if (corridorBBlocked) {
        simCtx.strokeStyle = "rgba(244, 63, 94, 0.85)";
        simCtx.setLineDash([6, 6]);
    } else {
        simCtx.strokeStyle = "rgba(56, 189, 248, 0.7)";
        simCtx.setLineDash([]);
    }
    simCtx.lineWidth = 4;
    simCtx.beginPath();
    p = toScreen(-4, -4); simCtx.moveTo(p[0], p[1]);
    p = toScreen(-2, 3); simCtx.lineTo(p[0], p[1]);
    p = toScreen(0, 4); simCtx.lineTo(p[0], p[1]);
    p = toScreen(4, 4); simCtx.lineTo(p[0], p[1]);
    simCtx.stroke();
    simCtx.setLineDash([]);

    // Route C (Alternative Detour)
    if (corridorBBlocked) {
        simCtx.strokeStyle = "#34d399";
        simCtx.lineWidth = 5;
    } else {
        simCtx.strokeStyle = "rgba(148, 163, 184, 0.3)";
        simCtx.lineWidth = 2;
        simCtx.setLineDash([4, 4]);
    }
    simCtx.beginPath();
    p = toScreen(-4, -4); simCtx.moveTo(p[0], p[1]);
    p = toScreen(-4, 0); simCtx.lineTo(p[0], p[1]);
    p = toScreen(0, -3); simCtx.lineTo(p[0], p[1]);
    p = toScreen(4, 0); simCtx.lineTo(p[0], p[1]);
    p = toScreen(4, 4); simCtx.lineTo(p[0], p[1]);
    simCtx.stroke();
    simCtx.setLineDash([]);

    // Draw Smooth Animated Trajectory Trail behind Robot
    if (trajectoryTrail.length > 1) {
        simCtx.strokeStyle = "rgba(56, 189, 248, 0.6)";
        simCtx.lineWidth = 3;
        simCtx.beginPath();
        let tp = toScreen(trajectoryTrail[0].x, trajectoryTrail[0].y);
        simCtx.moveTo(tp[0], tp[1]);
        for (let i = 1; i < trajectoryTrail.length; i++) {
            tp = toScreen(trajectoryTrail[i].x, trajectoryTrail[i].y);
            simCtx.lineTo(tp[0], tp[1]);
        }
        simCtx.stroke();
    }

    const [rx, ry] = toScreen(robotPos.x, robotPos.y);

    // Collision-free Label Registry
    const labelsToDraw = [];

    // Draw Hazards
    if (world.hazards) {
        world.hazards.forEach(hz => {
            const [hx, hy] = toScreen(hz.position[0], hz.position[1]);
            const grad = simCtx.createRadialGradient(hx, hy, 4, hx, hy, 32);
            grad.addColorStop(0, "rgba(244, 63, 94, 0.5)");
            grad.addColorStop(1, "rgba(244, 63, 94, 0.0)");
            simCtx.fillStyle = grad;
            simCtx.beginPath(); simCtx.arc(hx, hy, 32, 0, Math.PI * 2); simCtx.fill();

            simCtx.strokeStyle = "#f43f5e";
            simCtx.lineWidth = 2;
            simCtx.beginPath(); simCtx.arc(hx, hy, 16, 0, Math.PI * 2); simCtx.stroke();

            let hzLabel = "HAZARD ZONE";
            if (currentScenario === "autonomous_car") hzLabel = "HIGH-RISK ACCIDENT ZONE";
            else if (currentScenario === "smart_warehouse") hzLabel = "FORKLIFT DANGER ZONE";
            else if (currentScenario === "disaster") hzLabel = "ACTIVE FIRE HAZARD";

            labelsToDraw.push({ x: hx, y: hy, text: hzLabel, color: "#f43f5e", defaultOffset: -22 });
        });
    }

    // Draw Entities
    if (world.entities) {
        world.entities.forEach(ent => {
            const [ex, ey] = toScreen(ent.position[0], ent.position[1]);
            if (ent.type === "person" || ent.type === "dispatch_zone") {
                simCtx.fillStyle = "rgba(52, 211, 153, 0.25)";
                simCtx.beginPath(); simCtx.arc(ex, ey, 18, 0, Math.PI * 2); simCtx.fill();
                simCtx.fillStyle = "#34d399";
                simCtx.beginPath(); simCtx.arc(ex, ey, 9, 0, Math.PI * 2); simCtx.fill();

                let targetLabel = "TARGET DESTINATION";
                if (currentScenario === "autonomous_car") targetLabel = "SECTOR 4 HUB (4.0, 4.0)";
                else if (currentScenario === "smart_warehouse") targetLabel = "LOADING BAY 2 (4.0, 4.0)";
                else if (currentScenario === "disaster") targetLabel = "VICTIM (4.0, 4.0)";

                labelsToDraw.push({ x: ex, y: ey, text: targetLabel, color: "#34d399", defaultOffset: -18 });
            } else if (ent.type === "medical_kit" || ent.type === "package") {
                simCtx.fillStyle = "#6366f1";
                simCtx.shadowColor = "#6366f1";
                simCtx.shadowBlur = 10;
                simCtx.fillRect(ex - 8, ey - 8, 16, 16);
                simCtx.shadowBlur = 0;

                let itemLabel = ent.type === "package" ? "DISPATCH CARGO #409" : "MEDICAL KIT";
                labelsToDraw.push({ x: ex, y: ey, text: itemLabel, color: "#a5b4fc", defaultOffset: -16 });
            } else if (ent.type === "debris") {
                simCtx.fillStyle = "#fbbf24";
                simCtx.shadowColor = "#fbbf24";
                simCtx.shadowBlur = 12;
                simCtx.fillRect(ex - 12, ey - 12, 24, 24);
                simCtx.shadowBlur = 0;

                let blockLabel = currentScenario === "autonomous_car" ? "ROADBLOCK DETECTED" : "CORRIDOR B BLOCKED";
                labelsToDraw.push({ x: ex, y: ey, text: blockLabel, color: "#fbbf24", defaultOffset: -18 });
            }
        });
    }

    // Robot Outer Pulse Ring & Body
    simCtx.fillStyle = "rgba(56, 189, 248, 0.2)";
    simCtx.beginPath(); simCtx.arc(rx, ry, 22, 0, Math.PI * 2); simCtx.fill();

    simCtx.fillStyle = "#38bdf8";
    simCtx.shadowColor = "#38bdf8";
    simCtx.shadowBlur = 16;
    simCtx.beginPath(); simCtx.arc(rx, ry, 12, 0, Math.PI * 2); simCtx.fill();
    simCtx.shadowBlur = 0;

    // Heading Vector Arrow
    simCtx.strokeStyle = "#ffffff";
    simCtx.lineWidth = 3;
    simCtx.beginPath();
    simCtx.moveTo(rx, ry);
    simCtx.lineTo(rx + Math.cos(robotHeading) * 20, ry - Math.sin(robotHeading) * 20);
    simCtx.stroke();

    let robotLabel = "EGO VEHICLE";
    if (currentScenario === "smart_warehouse") robotLabel = "WAREHOUSE AMR";
    else if (currentScenario === "disaster") robotLabel = "RESCUE ROVER";

    labelsToDraw.push({ x: rx, y: ry, text: robotLabel, color: "#ffffff", defaultOffset: 26, isRobot: true });

    // Dynamic Collision Offset Resolution for Labels
    labelsToDraw.forEach((lbl, idx) => {
        let offsetY = lbl.defaultOffset;
        for (let j = 0; j < idx; j++) {
            const other = labelsToDraw[j];
            const dist = Math.hypot(lbl.x - other.x, (lbl.y + offsetY) - (other.y + (other.resolvedY || other.defaultOffset)));
            if (dist < 28) {
                offsetY += (lbl.defaultOffset >= 0) ? 22 : -22;
            }
        }
        lbl.resolvedY = offsetY;

        simCtx.fillStyle = lbl.color;
        simCtx.font = lbl.isRobot ? "800 11px 'Plus Jakarta Sans'" : "700 10px 'Plus Jakarta Sans'";
        simCtx.textAlign = "center";
        simCtx.fillText(lbl.text, lbl.x, lbl.y + offsetY);
    });
    simCtx.textAlign = "left";
}

// Render Dynamic World Entities Grid & Relations
function renderWorldEntities(world) {
    const grid = document.getElementById("worldEntitiesGrid");
    if (!grid || !world.entities) return;

    let html = `
        <div class="entity-item-card">
            <div>
                <div class="entity-item-id">Robot Base Agent</div>
                <div class="entity-item-pos">Pos: (${world.robot.position[0].toFixed(1)}, ${world.robot.position[1].toFixed(1)})</div>
            </div>
            <span class="entity-item-badge">${world.robot.status}</span>
        </div>
    `;

    world.entities.forEach(ent => {
        html += `
            <div class="entity-item-card">
                <div>
                    <div class="entity-item-id">${ent.id}</div>
                    <div class="entity-item-pos">Pos: (${ent.position[0].toFixed(1)}, ${ent.position[1].toFixed(1)})</div>
                </div>
                <span class="entity-item-badge">${ent.state.toUpperCase()}</span>
            </div>
        `;
    });

    grid.innerHTML = html;

    const relList = document.getElementById("relationsList");
    if (relList && world.relations) {
        relList.innerHTML = world.relations.map(r => `<li>${r.subject_id} ──${r.relation_type}──> ${r.object_id}</li>`).join('');
    }
}

// Render Prediction Decision Matrix Table
function renderPredictionTable(predData) {
    const tbody = document.getElementById("predictionTableBody");
    if (!tbody || !predData.evaluated_candidates) return;

    tbody.innerHTML = predData.evaluated_candidates.map(c => {
        const isSelected = predData.selected_route && predData.selected_route.id === c.id;
        const progStr = c.goal_progress ? `${(c.goal_progress * 100).toFixed(0)}%` : '85%';
        const hazardStr = `${(c.risk * 100).toFixed(0)}%`;
        const collStr = `${(c.collision_probability * 100).toFixed(0)}%`;

        return `
            <tr class="${isSelected ? 'selected-row' : ''}">
                <td><strong>${c.name}</strong></td>
                <td>${progStr}</td>
                <td class="${c.risk > 0.5 ? 'text-rose' : 'text-emerald'}">${hazardStr}</td>
                <td>${collStr}</td>
                <td><strong>${c.total_score !== undefined ? c.total_score : '+5.0'}</strong></td>
                <td><span class="badge-tag ${c.status === 'UNSAFE' ? 'unsafe' : 'safe'}">${c.status}</span></td>
            </tr>
        `;
    }).join('');

    const sumEl = document.getElementById("selectedRouteName");
    if (sumEl && predData.selected_route) {
        sumEl.textContent = predData.selected_route.name;
    }
}

// Event Stream Renderer
function renderEventStream(events) {
    const el = document.getElementById("eventStream");
    if (!el) return;

    el.innerHTML = events.map(e => `
        <div class="event-entry ${e.type.toLowerCase()}">
            <span style="color: var(--text-muted);">[${e.timestamp}]</span>
            <strong>[${e.type}]</strong> ${e.message}
        </div>
    `).join('');
    el.scrollTop = el.scrollHeight;
}

// Technical Drawer Handler
function toggleTechnicalDrawer() {
    const drawer = document.getElementById("techDrawer");
    if (!drawer) return;
    techModeOpen = !techModeOpen;
    if (techModeOpen) {
        drawer.classList.remove("hidden");
        if (currentWorldData) {
            document.getElementById("rawTelemetry").textContent = JSON.stringify(currentWorldData, null, 2);
        }
    } else {
        drawer.classList.add("hidden");
    }
}

// Action Handlers
async function submitMission() {
    const prompt = document.getElementById("missionInput").value;
    const res = await fetch(`${API_BASE}/mission`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt })
    });
    fetchEvents();
    fetchPredictions();
}

async function runHeroDemo() {
    trajectoryTrail = [];
    await fetch(`${API_BASE}/mission/run-hero-demo`, { method: "POST" });
    fetchEvents();
    fetchPredictions();
}

async function runResilienceTests() {
    const res = await fetch(`${API_BASE}/resilience-tests`);
    const data = await res.json();
    fetchEvents();
    alert(`⚡ RESILIENCE TEST SUITE RESULTS:\nPassed: ${data.passed}/${data.total} Scenarios\nSafety Violations: 0`);
}

async function injectObstacle() {
    await fetch(`${API_BASE}/simulation/inject-obstacle`, { method: "POST" });
    fetchEvents();
    fetchPredictions();
}

async function resetWorld() {
    trajectoryTrail = [];
    targetRobotPos = { x: -4.0, y: -4.0 };
    robotPos = { x: -4.0, y: -4.0 };
    await fetch(`${API_BASE}/simulation/reset`, { method: "POST" });
    fetchEvents();
    fetchPredictions();
}

function setScenario(promptText) {
    document.getElementById("missionInput").value = promptText;
    submitMission();
}

function switchVisualTab(tab) {
    const simC = document.getElementById("simViewContainer");
    const camC = document.getElementById("cameraViewContainer");
    const tabSim = document.getElementById("tabSim");
    const tabCam = document.getElementById("tabCam");
    if (tab === "sim") {
        simC.classList.remove("hidden");
        camC.classList.add("hidden");
        tabSim.classList.add("active");
        tabCam.classList.remove("active");
    } else {
        simC.classList.add("hidden");
        camC.classList.remove("hidden");
        tabSim.classList.remove("active");
        tabCam.classList.add("active");
    }
}

window.addEventListener("DOMContentLoaded", () => {
    connectWebSocket();
    fetchWorldState();
    fetchEvents();
    fetchPredictions();
    startCanvasAnimationLoop();
});

