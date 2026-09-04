import numpy as np

class CameraSensor:
    def __init__(self, width: int = 640, height: int = 480):
        self.width = width
        self.height = height

    def capture_frame(self, robot_pos: list, robot_yaw: float, objects: dict) -> np.ndarray:
        """
        Generates simulated RGB frame from camera perspective mounted on robot.
        Draws visual representations of robot view scene.
        """
        # Create dark background image (RGB)
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        frame[:] = (15, 20, 28) # Futuristic dark theme base color
        
        # Grid visualizer lines
        for x in range(0, self.width, 40):
            frame[:, x] = (25, 35, 48)
        for y in range(0, self.height, 40):
            frame[y, :] = (25, 35, 48)

        # Draw detected object overlays synthetic visual representation
        # Draw camera center reticle
        cx, cy = self.width // 2, self.height // 2
        frame[cy-10:cy+10, cx] = (0, 220, 255)
        frame[cy, cx-10:cx+10] = (0, 220, 255)

        return frame
