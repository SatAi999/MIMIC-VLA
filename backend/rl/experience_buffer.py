import json
import time
from pathlib import Path
from typing import Dict, Any, List

class ExperienceBuffer:
    def __init__(self):
        self.log_dir = Path("data/rl/experiences")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = self.log_dir / "experiences.jsonl"

    def record_transition(self, transition_data: Dict[str, Any]):
        """
        Appends a complete physical transition trace to data/rl/experiences/experiences.jsonl.
        """
        entry = {
            "timestamp": time.time(),
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            **transition_data
        }
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def get_recent_experiences(self, limit: int = 50) -> List[Dict[str, Any]]:
        if not self.file_path.exists():
            return []
        experiences = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        experiences.append(json.loads(line))
                    except Exception:
                        pass
        return experiences[-limit:]
