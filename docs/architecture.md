# Architecture proposal

Status: discussion and offline prototype, 2026-11-06.

## Responsibility and placement

| Component | Responsibility | Proposed placement / owner |
|---|---|---|
| Mission | Identified goals, sequence, cancellation | vehicle-motion; compute TBD |
| Navigation | Localization, obstacle representation, local path generation | vehicle-motion; Zynq PS, planned 1 GB RAM |
| Perception | Sensor processing and optional AI inference | PS baseline; PL and optional Jetson acceleration under evaluation |
| Vehicle executor | Own active trajectory; feedback tracking; geometry and limits | vehicle-motion; Zynq PS |
| Client boundary | Serialized operations through dmotor_client | PS, one normal owner |
| Daemon/runtime | Admission, deadlines, coordinated motor publication | dmotor |
| Velocity control | Deterministic motor regulation and watchdog response | dmotor, Zynq PL |
| Electrical protection | Permits, ARM/STOP, monitor/recovery participation | dmotor, ESP32; operational gaps remain |

No middleware, sensor suite or external computer is selected. An optional Jetson Nano may supply timestamped perception results to the PS; it
must never open a second daemon connection or own motion targets. See
[compute and sensors](compute_and_sensors.md) for the proposed partition. Maintenance handover
requires stopped/inhibited state and explicit ownership transfer.

## Proposed contracts (not implemented)

A goal contains an ID, relative action (planar translation, turn, dwell), frame, tolerances,
deadline and cancellation identity. A trajectory contains its goal ID, generation,
time-indexed local references, validity interval and limits. Motor targets are
short-lived coordinated four-channel milliRPM values derived by the executor.
New motor batch numbers do not prove fresh planner intent.

Proposed frames: body +x forward, +y left, +z up; positive yaw counterclockwise.
Local relative goals anchor to a captured start pose and reset identity. `odom`
is continuous wheel-derived motion, not externally corrected truth. `map` is
reserved until localization and transform/jump policies are specified.
Observations need units, frame, source and receipt times, validity, uncertainty
and reset identity. Never integrate counter reset as displacement. Preserve
fractional encoder conversion. No encoder count scale, gearing or motor polarity
is yet selected. Wheel odometry cannot prove vehicle displacement under slip.

Proposed lifecycle: idle → accepted → executing → stopping → terminal.
Terminal results distinguish succeeded, cancelled, failed and stop-unconfirmed.
Success requires measured tolerance and settling after stopping, not an accepted
command. Cancellation invalidates queued work before requesting controlled STOP.
STOP requires rearm in the current runtime; a subsequent goal does not automatically
prepare/enable. Faults use existing HALT/protection semantics, without claiming a
successful transport call proves physical stopping. Restart or ARM never resumes
an old goal. Simulation initialization is not an implementation of physical rearm.

Independent validity checks cover upstream intent, planner progress, pose age and
actuator delivery. Exact budgets await requirements and commissioning measurements.
Loss of planner/pose/ownership defaults to stopping; do not refresh abandoned intent.
A transport failure leaves the operation outcome unknown. Record that uncertainty;
do not replay. Physical collision avoidance needs sensor coverage, freshness and
measured stopping capability beyond electrical protection.

## Staged work

1. Confirm mecanum dimensions/mapping, first behavior, sensors, exact Zynq board
   and operating envelope. Navigation placement on the PS is selected.
2. Review goal/result and observation contracts plus stop/rearm policy.
3. Add a fake-clock executor and failure scenarios against an in-process actuator
   fake. This fake will not speak the daemon wire protocol.
4. Build a C++14 adapter through the installed dmotor_client SDK; exercise it with
   a test daemon using dmotor's supported test facilities. No raw socket peer here.
5. Revisit physical work only after the board pause ends and dmotor gate evidence
   permits it. U1/G2 remain dmotor procedures; physical vehicle claims await G6/GV.

This repository's simulations do not accept BV/GV or change dmotor motion admission.

## Mecanum vehicle

The user confirmed four independently driven mecanum wheels. Use a planar
body twist `(vx, vy, yaw_rate)`, including lateral motion. See
[geometry and conventions](geometry.md). The former two-side skid-steer model
is superseded. Wheel roller arrangement, dimensions and channel mapping remain
unconfirmed; the simulator uses an explicitly provisional ideal arrangement.
