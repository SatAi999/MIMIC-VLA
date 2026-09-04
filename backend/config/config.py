import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"

if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

class SystemConfig(BaseModel):
    app_name: str = "MIMIC-VLA"
    version: str = "1.0.0"
    debug: bool = True
    
    # Provider options: "gemini", "openai", "fallback"
    vlm_provider: str = os.getenv("VLM_PROVIDER", "gemini")
    vlm_model: str = os.getenv("VLM_MODEL", "gemini-1.5-flash")
    
    # Perception
    detector_confidence_threshold: float = 0.5
    
    # Predictive planner weights
    lambda_risk: float = 10.0
    lambda_distance: float = 0.1
    lambda_collision: float = 20.0
    
    # Server & Telemetry
    host: str = "0.0.0.0"
    port: int = 8000
    
config = SystemConfig()
