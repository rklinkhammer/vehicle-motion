"""Fictional two-side plant, SI units and explicit time; not a controller model."""
from dataclasses import dataclass
from math import cos, sin, isfinite


@dataclass(frozen=True)
class Parameters:
    track_width_m: float = 0.5
    max_side_speed_mps: float = 0.8
    acceleration_mps2: float = 1.0

    def __post_init__(self):
        if not all(isfinite(v) and v > 0 for v in vars(self).values()):
            raise ValueError('plant parameters must be finite and positive')


@dataclass(frozen=True)
class Pose:
    x_m: float = 0.0
    y_m: float = 0.0
    yaw_rad: float = 0.0


def integrate(pose, left, right, width, dt):
    speed = (left + right) / 2
    omega = (right - left) / width
    angle = omega * dt
    if abs(omega) < 1e-12:
        dx, dy = speed * dt * cos(pose.yaw_rad), speed * dt * sin(pose.yaw_rad)
    else:
        radius = speed / omega
        dx = radius * (sin(pose.yaw_rad + angle) - sin(pose.yaw_rad))
        dy = radius * (cos(pose.yaw_rad) - cos(pose.yaw_rad + angle))
    return Pose(pose.x_m + dx, pose.y_m + dy, pose.yaw_rad + angle)


class Plant:
    def __init__(self, parameters=None):
        self.parameters = parameters or Parameters()
        self.time_s = 0.0
        self.odometry = Pose()
        self.truth = Pose()
        self.speeds = (0.0, 0.0)
        self.targets = (0.0, 0.0)

    def command(self, left_mps, right_mps):
        """Curvature-preserving saturation of fictional plant side inputs."""
        if not all(isfinite(v) for v in (left_mps, right_mps)):
            raise ValueError('speeds must be finite')
        scale = max(1.0, abs(left_mps) / self.parameters.max_side_speed_mps,
                    abs(right_mps) / self.parameters.max_side_speed_mps)
        self.targets = (left_mps / scale, right_mps / scale)

    def stop(self):
        """Zero plant targets with finite deceleration; NOT daemon STOP/rearm."""
        self.targets = (0.0, 0.0)

    def step(self, dt_s, traction=(1.0, 1.0)):
        """Advance fake time; traction affects truth, never wheel odometry.

        Uses mean side speeds over the step. Curved acceleration is a numerical
        approximation; use small steps. No model of braking, permits or recovery.
        """
        if not isfinite(dt_s) or dt_s <= 0:
            raise ValueError('time step must be finite and positive')
        if len(traction) != 2 or not all(isfinite(v) and 0 <= v <= 1 for v in traction):
            raise ValueError('two traction factors in [0, 1] required')
        acceleration = self.parameters.acceleration_mps2
        means, following = [], []
        for old, target in zip(self.speeds, self.targets):
            delta = target - old
            ramp_s = min(dt_s, abs(delta) / acceleration)
            new = old + (1 if delta >= 0 else -1) * acceleration * ramp_s
            # Include time spent at target if acceleration finishes within a step.
            means.append(((old + new) * ramp_s / 2 + new * (dt_s - ramp_s)) / dt_s)
            following.append(new)
        self.odometry = integrate(self.odometry, *means, self.parameters.track_width_m, dt_s)
        self.truth = integrate(self.truth, means[0] * traction[0], means[1] * traction[1],
                               self.parameters.track_width_m, dt_s)
        self.speeds = tuple(following)
        self.time_s += dt_s
