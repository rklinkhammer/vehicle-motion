# Compute and sensor architecture

## Selected baseline

The user selected navigation on the Zynq PS with 1 GB RAM on the intended platform.
The vehicle executor also remains on PS and is the sole normal dmotor_client
owner. Mission placement remains open. No middleware or sensor model is selected.
A Jetson Nano is an optional AI/CUDA coprocessor, not a prerequisite or motion owner.

Proposed data path:

```text
Sensors → PS drivers / optional PL capture and preprocessing → PS state estimation
Optional Jetson perception results ──────────────────────────→ PS obstacle model
PS navigation → PS vehicle executor → dmotor_client → dmotor daemon → PL control
```

Sensor acceleration must preserve dmotor's deterministic control/protection
resources and timing. This document allocates no PL pins, clocks, DMA channels,
interrupts or memory bandwidth. Changes to controller/protection remain in dmotor;
board/build integration stays with its existing owning repositories.

## Sensor candidates, not commitments

| Candidate | Proposed role | Questions before selecting an interface |
|---|---|---|
| MIPI camera | Image input; optional PL capture/preprocessing | Exact camera and Zynq part/board; connector, electrical/PHY compatibility, lane count/rate, CSI receiver support, drivers, pixel format, DMA and buffering |
| GPS/GNSS | Outdoor absolute position; optional timing reference | Receiver interface, antenna/environment, accuracy, update rate, PPS availability, time association and loss behavior |
| Ultrasonic | Short-range clearance input | Coverage including strafing, trigger/echo or serial interface, voltage levels, timing capture, interference and minimum range |
| Radar | Range/velocity or object observations | Module output (objects vs raw data), bus, bandwidth, processing location, calibration and latency |
| Advanced camera processing | Features, depth or AI-derived objects | Algorithm, input size/rate, accuracy, compute/memory cost; PS vs PL vs optional Jetson placement |
| IMU (additional proposal) | Heading-rate/inertial observations | Availability, bias calibration, sample timing, mounting and fusion policy |

PL is a candidate for timing-sensitive capture, timestamps and bounded streaming
preprocessing; feasibility is unverified until the actual interfaces and resource
budget are known. GPS and other sensors need not pass through PL when a suitable
PS interface suffices. Camera connectivity does not imply available MIPI support.
No sensor is assumed to establish pose validity or collision coverage by itself.

## Memory and scheduling plan

Treat 1 GB as total platform RAM, not an application budget. First inventory OS,
drivers, DMA reservations, daemon and other services; then assign measured budgets
for localization, local maps, planning, camera buffers and optional inference.
Bound map extent, queue depth and image buffers; avoid unbounded history. Record
peak resident memory, allocation failures, CPU load, sensor-to-plan latency and
executor scheduling jitter under simultaneous workloads before selecting a stack.
For planning, image storage is width × height × bytes/pixel × buffer count; account
separately for copies and intermediate images. No resolution/rate is approved yet.

Keep perception and slow planning work outside the serialized motor-client event
loop. Freshness and bounded queues matter more than retaining every frame. Dropped
or late sensor data must be visible to the validity policy, not hidden by lease
refresh. Sensor DMA/resource contention requires later target measurements.

## Optional Jetson boundary

Propose timestamped perception observations over a bounded PS–Jetson link (transport
TBD). Each result includes source/frame identity, capture and receipt times, clock
mapping uncertainty, calibration version, validity and appropriate uncertainty.
PS owns fusion, navigation, trajectory admission and motor commands. Jetson restart
or reconnect does not resume motion. Loss/staleness of required perception requests
stopping; no degraded continuation is authorized by this proposal. Jetson model,
power/thermal budget, camera attachment and link bandwidth remain open.

## Next clarifications

1. Exact Zynq board/device and available camera/sensor connectors.
2. Physical wheel dimensions, roller arrangement and motor/encoder mapping.
3. First autonomous task and environment: local motion sequence or waypoint task;
   required accuracy, speed and obstacle coverage.
4. Actual sensors available now versus desired later, and whether Jetson is needed
   for a concrete perception workload.

These are architecture tasks. Hardware testing remains paused, and no PL sensor
implementation or live recovery capability is claimed.
