import math
import time

from src.templates.threadwithstop import ThreadWithStop
from src.utils.messages.allMessages import (SpeedMotor, SteerMotor, signDetection, laneDetection)
from src.utils.messages.messageHandlerSubscriber import messageHandlerSubscriber
from src.statemachine.FSM.src.states import OBJECT_CLASSES, States
from src.statemachine.FSM.src.callback.callback_intersection import navigation, counter, counterModuo

from .config import (
    SERVER_IP, SERVER_PORT,
    WORLD_SIZE_X,
    GRAPH_FILE, GRAPH_COORD_SPACE, FLIP_Y,
    VIRTUAL_WIDTH, VIRTUAL_HEIGHT, SCREEN_SCALE,
    CAR_START_X, CAR_START_Y, CAR_START_ANG,
    STEER_OFFSET, STEER_MAX_POS, STEER_MAX_NEG,
    STEER_LIMIT, STEER_HYSTERESIS_DEG,
)
from .src.carModel      import CarModel
from .src.graphLocal    import GraphLocal
from .src.laneSnapperLocal import LaneSnapperLocal
from .src.localServer   import LocalServer


class threadlocal(ThreadWithStop):
    """
    Runs car kinematics + LaneSnapper on RPi and streams
    {"type": "position", "x": ..., "y": ..., "angle": ...} to PC.
    PC only renders — it no longer runs its own simulation physics.
    """

    def __init__(self, queueList, logging, debugging=False):
        self.queuesList = queueList
        self.logging    = logging
        self.debugging  = debugging
        self.subscribe()
        super().__init__()

        # ── Car model ─────────────────────────────────────────────────
        self.car = CarModel(CAR_START_X, CAR_START_Y, CAR_START_ANG)

        # ── Graph + LaneSnapper ───────────────────────────────────────
        self.graph   = GraphLocal(GRAPH_FILE, SCREEN_SCALE, VIRTUAL_HEIGHT, FLIP_Y)
        self.snapper = LaneSnapperLocal(self.graph, SCREEN_SCALE)
        print(f"[threadlocal] Graph loaded — {len(self.graph.nodes)} nodes")

        # ── TCP connection to PC (optional — localization runs regardless) ──
        self.server = LocalServer(SERVER_IP, SERVER_PORT)
        self._pc_connected = self.server.start()
        if not self._pc_connected:
            print("[threadlocal] PC not reachable — running localization locally, retrying in background.")
        self._reconnect_interval = 5.0   # seconds between reconnect attempts
        self._last_reconnect_t   = time.time()

        # ── Servo hysteresis state ────────────────────────────────────
        self._servo_actual = 0.0

        # ── Timing ───────────────────────────────────────────────────
        self._last_t = time.time()

    # ── Subscribe ────────────────────────────────────────────────────

    def subscribe(self):
        self.speedRx = messageHandlerSubscriber(self.queuesList, SpeedMotor,    "lastOnly", True)
        self.steerRx = messageHandlerSubscriber(self.queuesList, SteerMotor,    "lastOnly", True)
        self.signRx  = messageHandlerSubscriber(self.queuesList, signDetection, "lastOnly", True)
        self.laneRx  = messageHandlerSubscriber(self.queuesList, laneDetection, "lastOnly", True)

    def state_change_handler(self):
        pass

    # ── Main loop ─────────────────────────────────────────────────────

    def thread_work(self):
        now = time.time()
        dt  = min(now - self._last_t, 0.1)   # cap dt to avoid big jumps
        self._last_t = now

        # ── 1. Read sensors ───────────────────────────────────────────
        raw_speed = self.speedRx.receive()
        raw_steer = self.steerRx.receive()
        lane_rec  = self.laneRx.receive()
        sign_rec  = self.signRx.receive()

        # ── 2. Map speed (mm/s → m/s, clamp ±0.5) ────────────────────
        if raw_speed is not None:
            sim_speed = float(raw_speed) / 1000.0
            sim_speed = max(-0.5, min(0.5, sim_speed))
            self.car.setSpeed(sim_speed)

        # ── 3. Map steer (raw units → degrees, hysteresis) ────────────
        if raw_steer is not None:
            steer = float(raw_steer)
            if steer >= 0:
                deg = steer * (STEER_LIMIT + STEER_OFFSET) / STEER_MAX_POS - STEER_OFFSET
            else:
                deg = steer * (STEER_LIMIT - STEER_OFFSET) / STEER_MAX_NEG - STEER_OFFSET
            deg = max(-STEER_LIMIT, min(STEER_LIMIT, deg))

            delta = deg - self._servo_actual
            if abs(delta) > STEER_HYSTERESIS_DEG:
                self._servo_actual = deg - math.copysign(STEER_HYSTERESIS_DEG, delta)

            self.car.setWheelAngle(math.radians(self._servo_actual))

        # ── 4. Dead-reckoning update ──────────────────────────────────
        self.car.update(dt)

        # ── 5. Lane snap ──────────────────────────────────────────────
        car_sx = self.car.X * SCREEN_SCALE
        car_sy = self.car.Y * SCREEN_SCALE

        if lane_rec:
            self.snapper.on_lane_signal(car_sx, car_sy, self.car.angle)

        snap = self.snapper.update(car_sx, car_sy, dt, self.car.angle)
        if snap:
            wx, wy, angle_rad = snap
            self.car.teleport(wx, wy, math.degrees(angle_rad))

        # ── 6. Navigation commands ────────────────────────────────────
        next_state = navigation[counter % counterModuo]
        if next_state == States.INTERSECTION_STRAIGHT:
            self.snapper.push_nav_command("STRAIGHT")
        elif next_state == States.INTERSECTION_RIGHT:
            self.snapper.push_nav_command("RIGHT")
        elif next_state == States.INTERSECTION_LEFT:
            self.snapper.push_nav_command("LEFT")

        # ── 7. Checkpoint detection ───────────────────────────────────
        if sign_rec is not None:
            detected = str(sign_rec).split()[0]
            if detected in (OBJECT_CLASSES.get(States.STOP_LINE, ""),
                            OBJECT_CLASSES.get(States.CROSSWALK, ""),
                            OBJECT_CLASSES.get(States.PARKING, "")):
                self.server.send_checkpoint(detected)

        # ── 8. Reconnect to PC if not connected ───────────────────────
        if not self._pc_connected:
            if now - self._last_reconnect_t >= self._reconnect_interval:
                self._last_reconnect_t = now
                self._pc_connected = self.server.start()
                if self._pc_connected:
                    print("[threadlocal] PC connected.")

        # ── 9. Send position to PC ────────────────────────────────────
        self.server.send_position(self.car.X, self.car.Y, self.car.angle)

        # ── 10. Print position
        print(self.car.X, self.car.Y, self.car.angle)