# Decisions and requirements to clarify

## Accepted boundaries

- Separate Git repository for autonomous motion; controller/protection stay in dmotor.
- Every daemon consumer uses dmotor_client. Hardware testing remains paused pending
  assembled monitor and motor boards.
- dmotor D01 commissioning-first scope remains unchanged. Live recovery is not
  implemented: recovery status is unavailable and admission is closed.
- Start with architecture and offline simulation. Numeric prototype values carry
  no physical authority.

## User decisions — 2026-11-06 follow-up

- Platform is four-wheel-drive mecanum, identified by the user with
  [Amazon ASIN B09VZT7DRY](https://www.amazon.com/dp/B09VZT7DRY).
  This supersedes the initial skid-steer assumption. The listing was accessed,
  but no dimensions, encoder configuration or roller arrangement were verified.
- Navigation runs on the Zynq PS. The intended Zynq platform has 1 GB RAM;
  usable application memory and exact board/device remain to be established.
- Consider PL support for MIPI camera, GPS and other sensors, including
  ultrasonic, radar and advanced camera processing. These are candidates, not
  selected sensors or implemented interfaces.
- A Jetson Nano for AI/CUDA processing is possible, not committed hardware.

## Proposals, awaiting vehicle details

| Question | Provisional simulation choice | Required confirmation |
|---|---|---|
| Geometry | Four-wheel mecanum; ideal 45-degree roller model | Wheel radius, wheelbase/track center spacing, roller arrangement, gearing, encoder scale; FL/FR/RL/RR channel mapping and signs |
| First behavior | Relative forward/strafe/diagonal move, turn, dwell and cancel | Actual first task; accuracy, speed and deadline requirements |
| Sensors | Synthetic wheel motion and separate ground truth | Encoders, IMU, GNSS, camera/lidar/range sensors; rates, coverage, latency and validity |
| Compute | Navigation and executor on Zynq PS; intended 1 GB RAM | Exact board/device, usable memory, mission placement, sensor interfaces, optional Jetson and link |
| Environment | Unspecified | Indoor/outdoor, surface/slope, obstacles/people, operating area and uncertainty policy |
| Stop/rearm | Explicit per-motion lifecycle | Measured stopping distance/settling, approved admission API and sequence |

The plant now models four logical wheels, not an approved daemon channel map.
Its dimensions and traction are not a calibrated physical mecanum model. No waypoint or
collision-avoidance capability is claimed. Answers should replace proposals with
dated decisions, not silently turn simulation defaults into requirements.

## Source context

Read from the sibling dmotor working tree on 2026-11-06:

- [Autonomous motion proposal](../../dmotor/docs/autonomous_motion_architecture.md)
- [Active decisions](../../dmotor/docs/decisions.md)
- [Client contract](../../dmotor/software/CLIENT.md)
- Public header `software/include/dmotor_sw/client.hpp` checked for API names.

Observed dmotor HEAD: `67cb5dad1cdfeaf27eed65bb435150134d818f29`.
The working tree had existing edits and an untracked architecture proposal; that
commit alone does not reproduce all source context. No dmotor files were changed.
