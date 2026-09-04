import heapq
import math
from typing import List, Tuple, Optional, Set

class AStarPlanner:
    def __init__(self, grid_size: Tuple[int, int] = (40, 40), resolution: float = 0.5, origin: Tuple[float, float] = (-10.0, -10.0)):
        self.width, self.height = grid_size
        self.resolution = resolution
        self.origin_x, self.origin_y = origin
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]

    def world_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        gx = int(round((x - self.origin_x) / self.resolution))
        gy = int(round((y - self.origin_y) / self.resolution))
        gx = max(0, min(self.width - 1, gx))
        gy = max(0, min(self.height - 1, gy))
        return gx, gy

    def grid_to_world(self, gx: int, gy: int) -> Tuple[float, float]:
        wx = self.origin_x + gx * self.resolution
        wy = self.origin_y + gy * self.resolution
        return wx, wy

    def set_obstacle(self, x: float, y: float, radius: float = 0.5, cost: int = 1):
        gx, gy = self.world_to_grid(x, y)
        r_grid = max(1, int(round(radius / self.resolution)))
        for dx in range(-r_grid, r_grid + 1):
            for dy in range(-r_grid, r_grid + 1):
                nx, ny = gx + dx, gy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    self.grid[ny][nx] = max(self.grid[ny][nx], cost)

    def plan(self, start: Tuple[float, float], goal: Tuple[float, float]) -> Optional[List[Tuple[float, float]]]:
        sx, sy = self.world_to_grid(start[0], start[1])
        gx, gy = self.world_to_grid(goal[0], goal[1])

        if self.grid[gy][gx] == 100: # Blocked goal cell fallback
            # Find nearest free cell near goal
            found = False
            for r in range(1, 5):
                for dx in range(-r, r+1):
                    for dy in range(-r, r+1):
                        nx, ny = gx + dx, gy + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height and self.grid[ny][nx] < 100:
                            gx, gy = nx, ny
                            found = True
                            break
                    if found: break
                if found: break

        open_set = []
        heapq.heappush(open_set, (0, (sx, sy)))
        came_from = {}
        g_score = {(sx, sy): 0.0}
        f_score = {(sx, sy): math.hypot(gx - sx, gy - sy)}

        # 8-directional movement
        neighbors = [
            (0, 1, 1.0), (1, 0, 1.0), (0, -1, 1.0), (-1, 0, 1.0),
            (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)
        ]

        visited: Set[Tuple[int, int]] = set()

        while open_set:
            _, current = heapq.heappop(open_set)
            if current in visited:
                continue
            visited.add(current)

            if current == (gx, gy):
                # Reconstruct path
                path = []
                curr = current
                while curr in came_from:
                    wx, wy = self.grid_to_world(curr[0], curr[1])
                    path.append((wx, wy))
                    curr = came_from[curr]
                path.append(start)
                path.reverse()
                return path

            for dx, dy, cost in neighbors:
                nx, ny = current[0] + dx, current[1] + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    cell_val = self.grid[ny][nx]
                    if cell_val >= 100: # Solid obstacle
                        continue
                    
                    # Extra cost penalty for high-risk zones
                    cost_penalty = cell_val * 5.0
                    tentative_g = g_score[current] + cost + cost_penalty
                    
                    if (nx, ny) not in g_score or tentative_g < g_score[(nx, ny)]:
                        came_from[(nx, ny)] = current
                        g_score[(nx, ny)] = tentative_g
                        h = math.hypot(gx - nx, gy - ny)
                        f_score[(nx, ny)] = tentative_g + h
                        heapq.heappush(open_set, (f_score[(nx, ny)], (nx, ny)))

        return None
