import sys
import uvicorn
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Add project root to python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.config.config import config
from backend.api.server import app

# Mount static frontend files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def read_root():
    return FileResponse("frontend/index.html")

if __name__ == "__main__":
    print("================================================================")
    print("   MIMIC-VLA — Predictive Embodied AI Control Center")
    print("   Server running at: http://localhost:8000")
    print("================================================================")
    uvicorn.run("main:app", host=config.host, port=config.port, reload=False)
