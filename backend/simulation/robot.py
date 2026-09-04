import math
from typing import List, Optional, Tuple

class RobotController:
    def __init__(self, start_pos: List[float] = [-4.0, -4.0, 0.0], start_yaw: float = 0.0):
        self.position = list(start_pos)
        self.yaw = start_yaw
        self.linear_velocity = 0.0
        self.angular_velocity = 0.0
        self.gripper_attached_item: Optional[str] = None
        self.target_waypoint: Optional[Tuple[float, float]] = None

    def set_velocity(self, v: float, w: float):
        self.linear_velocity = v
        self.angular_velocity = w

    def step(self, dt: float = 0.1):
        """
        Updates robot kinematics step.
        """
        self.yaw += self.angular_velocity * dt
        self.position[0] += self.linear_velocity * math.cos(self.yaw) * dt
        self.position[1] += self.linear_velocity * math.sin(self.yaw) * dt

    def move_towards(self, target: Tuple[float, float], speed: float = 1.0, dt: float = 0.1) -> bool:
        """
        Steers robot towards target position. Returns True if reached within 0.3m.
        """
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        dist = math.hypot(dx, dy)
        
        if dist < 0.3:
            self.linear_velocity = 0.0
            self.angular_velocity = 0.0
            return True
            
        target_yaw = math.atan2(dy, dx)
        yaw_diff = target_yaw - self.yaw
        
        # Normalize yaw diff to [-pi, pi]
        while yaw_diff > math.pi: yaw_diff -= 2 * math.pi
        while yaw_diff < -math.pi: yaw_diff += 2 * math.pi
        
        self.angular_velocity = 2.0 * yaw_diff
        self.linear_velocity = min(speed, dist * 1.5)
        
        self.step(dt)
        return False

    def attach_item(self, item_id: str):
        self.gripper_attached_item = item_id

    def release_item(self) -> Optional[str]:
        item = self.gripper_attached_item
        self.gripper_attached_item = None
        return item
