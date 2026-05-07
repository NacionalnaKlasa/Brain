"""
Verbatim copy of graph/laneSnapper.py — no pygame, no Floyd imports.
Uses GraphLocal instead of Graph (same .nodes / .graph interface).
"""
import math
from collections import deque

_POSITION_KEY        = "pos"
CORRECTION_FACTOR    = 0.20
INTERSECTION_RADIUS_PX = 60
MIN_VALID_COS        = -0.5


def _project_to_segment(px, py, A, B):
    ax, ay = A
    bx, by = B
    dx, dy = bx - ax, by - ay
    len_sq = dx * dx + dy * dy
    if len_sq < 1e-9:
        return 0.0, math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / len_sq
    t = max(0.0, min(1.0, t))
    return t, math.hypot(px - (ax + t * dx), py - (ay + t * dy))


class LaneSnapperLocal:
    TIMEOUT_S        = 1.0
    MAX_EDGE_DIST_PX = 120

    def __init__(self, graph, screen_scale: float):
        self.graph        = graph
        self.screen_scale = screen_scale
        self._active      = False
        self._current_edge = None
        self._time_without_signal = 0.0
        self.nav_queue: deque[str] = deque()

    # ── Public API ────────────────────────────────────────────────────

    def push_nav_command(self, cmd: str):
        cmd = cmd.upper().strip()
        if cmd in ("STRAIGHT", "LEFT", "RIGHT"):
            self.nav_queue.append(cmd)

    def on_lane_signal(self, car_sx: float, car_sy: float, car_angle_rad=None):
        self._time_without_signal = 0.0
        if not self._active:
            self._snap_to_nearest_edge(car_sx, car_sy, car_angle_rad)

    def update(self, car_sx: float, car_sy: float, dt: float, car_angle_rad=None):
        """
        Returns (world_x, world_y, angle_rad) if active, else None.
        car_sx/sy are in virtual screen pixels (car.X * screen_scale).
        """
        if not self._active:
            return None

        self._time_without_signal += dt
        if self._time_without_signal > self.TIMEOUT_S:
            self._active = False
            return None

        if self._near_intersection(car_sx, car_sy):
            return None

        u, v = self._current_edge
        A = self.graph.nodes[u][_POSITION_KEY]
        B = self.graph.nodes[v][_POSITION_KEY]
        t, dist = _project_to_segment(car_sx, car_sy, A, B)

        if dist > self.MAX_EDGE_DIST_PX:
            if not self._snap_to_nearest_edge(car_sx, car_sy, car_angle_rad):
                return None
            u, v = self._current_edge
            A = self.graph.nodes[u][_POSITION_KEY]
            B = self.graph.nodes[v][_POSITION_KEY]
            t, _ = _project_to_segment(car_sx, car_sy, A, B)

        if t >= 0.99:
            next_v = self._best_next_node(u, v)
            if next_v:
                self._current_edge = (v, next_v)
                A = self.graph.nodes[v][_POSITION_KEY]
                B = self.graph.nodes[next_v][_POSITION_KEY]
                t, _ = _project_to_segment(car_sx, car_sy, A, B)

        proj_x = A[0] + t * (B[0] - A[0])
        proj_y = A[1] + t * (B[1] - A[1])

        corrected_x = car_sx + CORRECTION_FACTOR * (proj_x - car_sx)
        corrected_y = car_sy + CORRECTION_FACTOR * (proj_y - car_sy)
        angle       = math.atan2(B[1] - A[1], B[0] - A[0])

        return corrected_x / self.screen_scale, corrected_y / self.screen_scale, angle

    # ── Intersection helpers ──────────────────────────────────────────

    def _near_intersection(self, sx, sy):
        for node in self.graph.nodes:
            if self.graph.graph.out_degree(node) <= 1:
                continue
            nx, ny = self.graph.nodes[node][_POSITION_KEY]
            if math.hypot(sx - nx, sy - ny) <= INTERSECTION_RADIUS_PX:
                return True
        return False

    # ── Edge snapping ─────────────────────────────────────────────────

    def _snap_to_nearest_edge(self, sx, sy, car_angle_rad=None):
        best_edge, min_dist = None, float('inf')
        for u, v in self.graph.graph.edges():
            if u not in self.graph.nodes or v not in self.graph.nodes:
                continue
            A = self.graph.nodes[u][_POSITION_KEY]
            B = self.graph.nodes[v][_POSITION_KEY]
            if car_angle_rad is not None:
                dx, dy = B[0] - A[0], B[1] - A[1]
                le = math.hypot(dx, dy)
                if le > 1e-9:
                    cos_a = (math.cos(car_angle_rad) * dx + math.sin(car_angle_rad) * dy) / le
                    if cos_a < MIN_VALID_COS:
                        continue
            _, dist = _project_to_segment(sx, sy, A, B)
            if dist < min_dist:
                min_dist, best_edge = dist, (u, v)

        if best_edge is None and car_angle_rad is not None:
            return self._snap_to_nearest_edge(sx, sy, car_angle_rad=None)
        if best_edge:
            self._current_edge = best_edge
            self._active = True
            return True
        return False

    # ── Next-node selection ───────────────────────────────────────────

    def _best_next_node(self, from_node, current_node):
        successors = list(self.graph.graph.successors(current_node))
        if not successors:
            return None
        if len(successors) == 1:
            return successors[0]
        valid = self._filter_valid_successors(from_node, current_node, successors)
        if not valid:
            valid = successors
        if len(valid) == 1:
            return valid[0]
        cmd = self.nav_queue.popleft() if self.nav_queue else None
        return self._choose_direction(from_node, current_node, valid, cmd)

    def _filter_valid_successors(self, from_node, current_node, successors):
        if from_node not in self.graph.nodes or current_node not in self.graph.nodes:
            return successors
        A  = self.graph.nodes[from_node][_POSITION_KEY]
        B  = self.graph.nodes[current_node][_POSITION_KEY]
        dx, dy = B[0] - A[0], B[1] - A[1]
        lab = math.hypot(dx, dy)
        if lab < 1e-9:
            return successors
        valid = []
        for s in successors:
            if s not in self.graph.nodes:
                continue
            C  = self.graph.nodes[s][_POSITION_KEY]
            ex, ey = C[0] - B[0], C[1] - B[1]
            le = math.hypot(ex, ey)
            if le < 1e-9:
                continue
            if (dx * ex + dy * ey) / (lab * le) > MIN_VALID_COS:
                valid.append(s)
        return valid

    def _choose_direction(self, from_node, current_node, candidates, cmd):
        if not candidates:
            return None
        A  = self.graph.nodes[from_node][_POSITION_KEY]
        B  = self.graph.nodes[current_node][_POSITION_KEY]
        dx, dy = B[0] - A[0], B[1] - A[1]
        lab = math.hypot(dx, dy)
        if lab < 1e-9:
            return candidates[0]
        best_node, best_score = None, float('-inf')
        for s in candidates:
            if s not in self.graph.nodes:
                continue
            C  = self.graph.nodes[s][_POSITION_KEY]
            ex, ey = C[0] - B[0], C[1] - B[1]
            le = math.hypot(ex, ey)
            if le < 1e-9:
                continue
            dot   = (dx * ex + dy * ey) / (lab * le)
            cross = (dx * ey - dy * ex) / (lab * le)
            score = cross if cmd == "RIGHT" else (-cross if cmd == "LEFT" else dot)
            if score > best_score:
                best_score, best_node = score, s
        return best_node
