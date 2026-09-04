import time
from typing import List, Dict, Any

class EpisodicMemory:
    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def record_mission(self, mission_id: str, prompt: str, outcome: str, route_taken: str, replans: int, details: Dict[str, Any]):
        entry = {
            "mission_id": mission_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "prompt": prompt,
            "outcome": outcome,
            "route_taken": route_taken,
            "replans_count": replans,
            "details": details
        }
        self.history.append(entry)

    def get_all_experiences(self) -> List[Dict[str, Any]]:
        return self.history

    def get_summary(self) -> Dict[str, Any]:
        total = len(self.history)
        successful = sum(1 for m in self.history if m["outcome"] == "SUCCESS")
        total_replans = sum(m.get("replans_count", 0) for m in self.history)
        return {
            "total_missions": total,
            "successful_missions": successful,
            "success_rate": (successful / total * 100) if total > 0 else 100.0,
            "total_replans_executed": total_replans
        }
