import math

WHEEL_DISTANCE = 0.265  # rear-to-front axle [m]

class CarModel:
    """Bicycle kinematic model — pure Python, no pygame."""

    def __init__(self, x=0.0, y=0.0, angle_deg=0.0):
        self.X     = x
        self.Y     = y
        self.angle = math.radians(angle_deg)
        self.speed = 0.0
        self._angular_speed = 0.0

    def setSpeed(self, speed_mps: float):
        self.speed = speed_mps
        # Recompute angular speed so it stays consistent with current wheel angle
        # (wheel angle is cached implicitly via _angular_speed/speed ratio)

    def setWheelAngle(self, angle_rad: float):
        if abs(angle_rad) < 1e-6:
            self._angular_speed = 0.0
        else:
            self._angular_speed = self.speed / WHEEL_DISTANCE * math.tan(angle_rad)

    def teleport(self, x: float, y: float, angle_deg: float):
        self.X     = x
        self.Y     = y
        self.angle = math.radians(angle_deg)

    def update(self, dt: float):
        self.X     += self.speed * dt * math.cos(self.angle)
        self.Y     += self.speed * dt * math.sin(self.angle)
        self.angle  = (self.angle + self._angular_speed * dt) % (2 * math.pi)
