import io
from typing import List, Dict, Any, Tuple
import numpy as np
from PIL import Image, ImageDraw

class PyBulletCameraAdapter:
    def __init__(self, width: int = 640, height: int = 480):
        self.width = width
        self.height = height

    def render_robot_view(self, robot_pos: List[float], sim_objects: Dict[str, Any], hazards: List[Any]) -> Tuple[np.ndarray, bytes]:
        """
        Renders an RGB frame from the robot camera perspective and encodes it as JPEG bytes for VLM analysis.
        """
        # Base background image (Dark cyber theme)
        img = Image.new("RGB", (self.width, self.height), (15, 20, 28))
        draw = ImageDraw.Draw(img)

        # Draw floor grid lines
        for x in range(0, self.width, 40):
            draw.line([(x, 0), (x, self.height)], fill=(25, 35, 48), width=1)
        for y in range(0, self.height, 40):
            draw.line([(0, y), (self.width, y)], fill=(25, 35, 48), width=1)

        rx, ry = robot_pos[0], robot_pos[1]

        # Draw hazards
        for hz in hazards:
            h_pos = hz.position if hasattr(hz, "position") else hz.get("position", [0.0, 0.0, 0.0])
            sx = int(320 + (h_pos[0] - rx) * 35)
            sy = int(240 - (h_pos[1] - ry) * 35)
            draw.ellipse([sx - 25, sy - 25, sx + 25, sy + 25], fill=(255, 51, 102, 100), outline=(255, 51, 102), width=2)
            draw.text((sx - 30, sy - 5), "FIRE HAZARD", fill=(255, 51, 102))

        # Draw objects
        for obj_id, obj_data in sim_objects.items():
            if not isinstance(obj_data, dict):
                continue
            obj_type = obj_data.get("type", "object")
            pos = obj_data.get("pos", [0.0, 0.0, 0.0])
            sx = int(320 + (pos[0] - rx) * 35)
            sy = int(240 - (pos[1] - ry) * 35)

            if obj_type == "person":
                draw.ellipse([sx - 15, sy - 15, sx + 15, sy + 15], fill=(0, 255, 136), outline=(0, 255, 136))
                draw.text((sx - 20, sy - 25), "INJURED VICTIM", fill=(0, 255, 136))
            elif obj_type == "medical_kit":
                draw.rectangle([sx - 12, sy - 12, sx + 12, sy + 12], fill=(0, 119, 255), outline=(255, 255, 255))
                draw.text((sx - 22, sy - 22), "MEDICAL KIT", fill=(0, 119, 255))
            elif obj_type == "debris":
                draw.rectangle([sx - 15, sy - 15, sx + 15, sy + 15], fill=(255, 170, 0), outline=(255, 170, 0))
                draw.text((sx - 25, sy - 25), "BLOCKED DEBRIS", fill=(255, 170, 0))
            elif obj_type == "pen":
                draw.line([(sx - 10, sy), (sx + 10, sy)], fill=(138, 43, 226), width=4)
                draw.text((sx - 15, sy - 15), "WRITING PEN", fill=(138, 43, 226))

        # Draw crosshair reticle
        cx, cy = self.width // 2, self.height // 2
        draw.line([(cx - 12, cy), (cx + 12, cy)], fill=(0, 240, 255), width=1)
        draw.line([(cx, cy - 12), (cx, cy + 12)], fill=(0, 240, 255), width=1)

        # Convert to numpy array & JPEG bytes
        img_np = np.array(img)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=90)
        jpeg_bytes = buffer.getvalue()

        return img_np, jpeg_bytes
