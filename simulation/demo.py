"""Run with python3 -m simulation.demo; no wall-clock waits or I/O to devices."""
from dataclasses import asdict
import json
from .plant import Plant


def scenario(traction, twist=(0.4, 0.0, 0.0)):
    plant = Plant()
    plant.command(*twist)
    for _ in range(100):
        plant.step(0.01, traction)
    stop_start = (plant.truth.x_m, plant.truth.y_m)
    plant.stop()
    for _ in range(100):
        plant.step(0.01, traction)
    return dict(time_s=plant.time_s, odometry=asdict(plant.odometry),
                truth=asdict(plant.truth), stop_travel_m=((plant.truth.x_m - stop_start[0]) ** 2 +
                              (plant.truth.y_m - stop_start[1]) ** 2) ** 0.5,
                final_wheel_speeds_mps=plant.speeds)


if __name__ == '__main__':
    print(json.dumps({'scope': 'FICTIONAL OFFLINE PLANT ONLY',
                      'ideal': scenario((1.0,) * 4),
                      'half_traction': scenario((0.5,) * 4),
                      'strafe_left': scenario((1.0,) * 4, (0.0, 0.4, 0.0))}, indent=2))
