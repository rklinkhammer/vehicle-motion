"""Fictional four-wheel mecanum plant, SI units and explicit time; not a controller model."""
from dataclasses import dataclass
from math import cos, sin, isfinite


@dataclass(frozen=True)
class Parameters:
    half_wheelbase_m: float = 0.25
    half_track_m: float = 0.25
    max_wheel_speed_mps: float = 0.8
    acceleration_mps2: float = 1.0

    def __post_init__(self):
        if not all(isfinite(v) and v > 0 for v in vars(self).values()):
            raise ValueError('plant parameters must be finite and positive')


@dataclass(frozen=True)
class Pose:
    x_m: float = 0.0
    y_m: float = 0.0
    yaw_rad: float = 0.0


def wheel_speeds(vx, vy, omega, parameters):
    """Ideal 45-degree rollers; FL, FR, RL, RR. See docs/geometry.md."""
    if not all(isfinite(v) for v in (vx, vy, omega)):
        raise ValueError('body twist must be finite')
    k = parameters.half_wheelbase_m + parameters.half_track_m
    return (vx - vy - k * omega, vx + vy + k * omega,
            vx + vy - k * omega, vx - vy + k * omega)


def body_twist(wheels, parameters):
    fl, fr, rl, rr = wheels
    k = parameters.half_wheelbase_m + parameters.half_track_m
    return ((fl + fr + rl + rr) / 4, (-fl + fr + rl - rr) / 4,
            (-fl + fr - rl + rr) / (4 * k))


def integrate(pose, wheels, parameters, dt):
    vx, vy, omega = body_twist(wheels, parameters)
    angle = omega * dt
    if abs(angle) < 1e-8:
        a, b = dt * (1 - angle * angle / 6), dt * angle / 2
    else:
        a, b = sin(angle) / omega, (1 - cos(angle)) / omega
    dx, dy = a * vx - b * vy, b * vx + a * vy
    c, s = cos(pose.yaw_rad), sin(pose.yaw_rad)
    return Pose(pose.x_m + c * dx - s * dy,
                pose.y_m + s * dx + c * dy, pose.yaw_rad + angle)


class Plant:
    def __init__(self, parameters=None):
        self.parameters = parameters or Parameters()
        self.time_s = 0.0
        self.odometry = Pose()
        self.truth = Pose()
        self.speeds = (0.0, 0.0, 0.0, 0.0)
        self.targets = (0.0, 0.0, 0.0, 0.0)

    def command(self, vx_mps, vy_mps, omega_radps):
        """Body twist to four wheel inputs, uniformly scaled to wheel limits."""
        requested = wheel_speeds(vx_mps, vy_mps, omega_radps, self.parameters)
        scale = max(1.0, max(abs(v) for v in requested) /
                    self.parameters.max_wheel_speed_mps)
        self.targets = tuple(v / scale for v in requested)

    def stop(self):
        """Zero plant targets with finite deceleration; NOT daemon STOP/rearm."""
        self.targets = (0.0, 0.0, 0.0, 0.0)

    def step(self, dt_s, traction=(1.0, 1.0, 1.0, 1.0)):
        """Advance fake time; traction affects truth, never wheel odometry.

        Uses mean wheel speeds over the step. Curved acceleration is a numerical
        approximation; use small steps. No model of braking, permits or recovery.
        """
        if not isfinite(dt_s) or dt_s <= 0:
            raise ValueError('time step must be finite and positive')
        if len(traction) != 4 or not all(isfinite(v) and 0 <= v <= 1 for v in traction):
            raise ValueError('four traction factors in [0, 1] required')
        acceleration = self.parameters.acceleration_mps2
        means, following = [], []
        for old, target in zip(self.speeds, self.targets):
            delta = target - old
            ramp_s = min(dt_s, abs(delta) / acceleration)
            new = old + (1 if delta >= 0 else -1) * acceleration * ramp_s
            # Include time spent at target if acceleration finishes within a step.
            means.append(((old + new) * ramp_s / 2 + new * (dt_s - ramp_s)) / dt_s)
            following.append(new)
        self.odometry = integrate(self.odometry, means, self.parameters, dt_s)
        effective = tuple(v * t for v, t in zip(means, traction))
        self.truth = integrate(self.truth, effective, self.parameters, dt_s)
        self.speeds = tuple(following)
        self.time_s += dt_s
