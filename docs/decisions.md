# Decisions and requirements to clarify

## Accepted boundaries

- Separate Git repository for autonomous motion; controller/protection stay in dmotor.
- Every daemon consumer uses dmotor_client. Hardware testing remains paused pending
  assembled monitor and motor boards.
- dmotor D01 commissioning-first scope remains unchanged. Live recovery is not
  implemented: recovery status is unavailable and admission is closed.
- Start with architecture and offline simulation. Numeric prototype values carry
  no physical authority.

## Proposals, awaiting vehicle details

| Question | Provisional simulation choice | Required confirmation |
|---|---|---|
| Geometry | Ideal differential/skid-steer abstraction | Tracks vs wheels; steering layout; wheel radius, track width, gearing; encoder scale; four-motor side mapping and signs |
| First behavior | Relative move, turn, dwell and cancel | Actual first task; accuracy, speed and deadline requirements |
| Sensors | Synthetic wheel motion and separate ground truth | Encoders, IMU, GNSS, camera/lidar/range sensors; rates, coverage, latency and validity |
| Compute | Executor on Zynq PS proposed | Mission/navigation/perception placement, available CPU/RAM, external host and links |
| Environment | Unspecified | Indoor/outdoor, surface/slope, obstacles/people, operating area and uncertainty policy |
| Stop/rearm | Explicit per-motion lifecycle | Measured stopping distance/settling, approved admission API and sequence |

The initial plant uses two effective side speeds, not an approved four-motor map.
Its effective track width is not a calibrated skid-steer model. No waypoint or
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
