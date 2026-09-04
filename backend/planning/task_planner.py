from typing import List, Dict, Any, Optional

class TaskPlanner:
    def __init__(self):
        self.tasks: List[Dict[str, Any]] = []
        self.current_task_idx: int = 0
        self.status: str = "IDLE" # IDLE, RUNNING, REPLANNING, PAUSED, COMPLETED, FAILED

    def load_plan(self, task_list: List[Dict[str, Any]]):
        self.tasks = task_list
        self.current_task_idx = 0
        self.status = "RUNNING"
        for t in self.tasks:
            t["status"] = "PENDING"

    def get_current_task(self) -> Optional[Dict[str, Any]]:
        if 0 <= self.current_task_idx < len(self.tasks):
            return self.tasks[self.current_task_idx]
        return None

    def mark_current_completed(self):
        if 0 <= self.current_task_idx < len(self.tasks):
            self.tasks[self.current_task_idx]["status"] = "COMPLETED"
            self.current_task_idx += 1
            if self.current_task_idx >= len(self.tasks):
                self.status = "COMPLETED"

    def mark_current_failed(self, reason: str):
        if 0 <= self.current_task_idx < len(self.tasks):
            self.tasks[self.current_task_idx]["status"] = "FAILED"
            self.tasks[self.current_task_idx]["error"] = reason
            self.status = "REPLANNING"

    def get_plan_summary(self) -> List[Dict[str, Any]]:
        return self.tasks
