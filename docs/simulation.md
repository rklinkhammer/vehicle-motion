# Offline simulation milestone

Implemented: standard-library Python plant with explicit fake time, ideal
four-wheel mecanum kinematics, uniform wheel-speed saturation, finite acceleration
and deceleration, wheel odometry and separate traction-affected ground truth.
No sleeps, networking, daemon API, device access or physical lifecycle is present.
Python is an offline exploration choice; it does not select a PS runtime stack.

All defaults are fictional: 0.25 m half-wheelbase and half-track, 0.8 m/s wheel limit,
1 m/s² acceleration/deceleration, demo speed 0.4 m/s and step 0.01 s. The model
omits motor dynamics, gearing, encoder quantization, terrain, mass, sensor noise,
latency and protection. Mean-speed integration approximates curved acceleration;
this is not a calibrated mecanum or stopping-safety model.

Run `python3 -m simulation.demo`. Ideal travel is 0.4 m after acceleration,
cruising and stopping, including 0.08 m after zero target is requested. Half
traction gives identical wheel odometry but only 0.2 m ground-truth travel.
These values illustrate model behavior, not stopping capability of the vehicle.

The demo also includes left strafe. Wheel order is FL, FR, RL, RR; see
[geometry](geometry.md) for the provisional roller convention.

Tests cover analytical straight travel/stopping, strafe, diagonal motion, turn
sign, combined-twist inversion, body/world rotation, saturation, slip,
time-step consistency for straight motion and invalid input rejection.

## Next executor scenarios (not yet implemented)

| Scenario | Required observable result |
|---|---|
| Cancel during move / turn / dwell | Goal and queue invalidated; stop requested; measured settling before cancelled |
| Upstream expiry or stalled planner | Stop; fresh batch numbers cannot extend intent |
| Stale/invalid pose | Stop; no success from stale observations |
| Encoder reset / localization jump | Discontinuity detected; no false displacement or silent goal rebase |
| Slip and insufficient progress | No false ground-truth completion; timeout/failure policy exercised |
| Ownership loss / transport timeout | No replay/reconnect; outcome uncertainty retained |
| STOP followed by another goal | No implicit rearm or automatic motion |
| Restart / recovery / physical ARM | Old goal never resumed |
| Stop overshoot beyond tolerance | Failure or reviewed correction policy, not success from command acknowledgment |

The plant's stop() only sets its fictional targets to zero; it does not emulate
Client::stop, rearm, monitor admission or confirmed HALT. Lifecycle tests belong
to the next reviewed executor milestone. A fake daemon integration test must still
route application access through dmotor_client; an in-process plant is no daemon.
