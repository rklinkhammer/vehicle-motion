# Mecanum geometry and conventions

Confirmed: four-wheel-drive mecanum platform. Dimensions, roller installation,
motor channels, polarity, gear ratios and encoder scales remain TBD. The user
provided [this product reference](https://www.amazon.com/dp/B09VZT7DRY); no listing
dimension is adopted as a measured wheel-center spacing.

Simulation convention: +x forward, +y left, positive yaw counterclockwise about
+z. Wheels are ordered front-left (FL), front-right (FR), rear-left (RL), rear-right
(RR). Positive wheel speed means its forward rolling direction; it is not motor
wiring polarity. Assume ideal 45-degree rollers with the sign pattern below;
confirm the physical arrangement before introducing a hardware mapping.

Let L be half the longitudinal wheel-center spacing, W half the lateral spacing,
and k = L + W. Wheel circumferential velocities in m/s are:

```text
FL = vx - vy - k*wz
FR = vx + vy + k*wz
RL = vx + vy - k*wz
RR = vx - vy + k*wz

vx = ( FL + FR + RL + RR) / 4
vy = (-FL + FR + RL - RR) / 4
wz = (-FL + FR - RL + RR) / (4*k)
```

This follows the conventional independent-wheel kinematic structure described in
[WPILib's mecanum kinematics documentation](https://docs.wpilib.org/en/stable/docs/software/kinematics-and-odometry/mecanum-drive-kinematics.html).
WPILib is a reference, not a selected dependency. Uniform scaling to the largest
wheel limit preserves the requested body-twist proportions at steady state.
Independent acceleration ramps can change transient proportions; the prototype
is not a trajectory tracker.

A future adapter converts circumferential speed to wheel RPM using measured radius,
then to motor milliRPM with verified gearing and polarity. Do not assume daemon
channel order matches logical wheel order. No such adapter exists yet.

| Required vehicle fact | Status |
|---|---|
| Loaded rolling radius and wheel-center L/W | TBD |
| Roller angle and handedness at each corner | TBD |
| FL/FR/RL/RR → daemon channels 0–3 and signs | TBD |
| Motor/encoder location, gearing, counts per revolution | TBD |
| Body footprint, sensor extrinsics and ground clearance | TBD |
| Direction-dependent slip, speed/acceleration and stopping limits | TBD |

First behavior remains a proposal: local forward, lateral and diagonal translations,
turn, dwell and cancel, each bounded and independently stopped. Lateral motion
requires lateral obstacle coverage; a forward-looking camera alone is not an
assumed all-direction clearance source. Map navigation and tolerances remain open.
