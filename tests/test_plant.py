import math
import unittest
from simulation.plant import Parameters, Plant, Pose, body_twist, wheel_speeds, integrate


class PlantTests(unittest.TestCase):
    def test_straight_acceleration_and_stop_distance(self):
        p = Plant()
        p.command(0.4, 0, 0)
        p.step(1.0)
        self.assertAlmostEqual(p.truth.x_m, 0.32)
        p.stop()
        p.step(1.0)
        self.assertAlmostEqual(p.truth.x_m, 0.4)
        self.assertEqual(p.speeds, (0.0,) * 4)
        self.assertEqual(p.time_s, 2.0)

    def test_turn_sign_and_no_translation(self):
        p = Plant()
        p.command(0, 0, 0.8)
        p.step(1.0)
        self.assertAlmostEqual(p.truth.yaw_rad, 0.64)
        self.assertAlmostEqual(p.truth.x_m, 0.0)
        self.assertAlmostEqual(p.truth.y_m, 0.0)

    def test_slip_separates_odometry_from_truth(self):
        p = Plant()
        p.command(0.4, 0, 0)
        p.step(1.0, (0.5,) * 4)
        self.assertAlmostEqual(p.odometry.x_m, 0.32)
        self.assertAlmostEqual(p.truth.x_m, 0.16)

    def test_saturation_preserves_ratio(self):
        p = Plant()
        p.command(1.0, 0.5, 0)
        self.assertAlmostEqual(max(p.targets), 0.8)
        self.assertAlmostEqual(p.targets[0] / p.targets[1], 1 / 3)

    def test_straight_subdivision_agrees(self):
        a, b = Plant(), Plant()
        for p in (a, b):
            p.command(0.4, 0, 0)
        a.step(1)
        for _ in range(100):
            b.step(0.01)
        self.assertAlmostEqual(a.truth.x_m, b.truth.x_m)

    def test_left_strafe(self):
        p = Plant()
        p.command(0, 0.4, 0)
        self.assertEqual(p.targets, (-0.4, 0.4, 0.4, -0.4))
        p.step(1)
        self.assertAlmostEqual(p.truth.x_m, 0)
        self.assertAlmostEqual(p.truth.y_m, 0.32)
        self.assertAlmostEqual(p.truth.yaw_rad, 0)

    def test_combined_twist_roundtrip(self):
        params = Parameters()
        for twist in ((0.2, -0.3, 0.4), (-0.1, 0.2, -0.5)):
            recovered = body_twist(wheel_speeds(*twist, params), params)
            for expected, actual in zip(twist, recovered):
                self.assertAlmostEqual(expected, actual)

    def test_diagonal(self):
        p = Plant()
        p.command(0.2, 0.2, 0)
        self.assertEqual(p.targets, (0, 0.4, 0.4, 0))
        p.step(1)
        self.assertAlmostEqual(p.truth.x_m, 0.16)
        self.assertAlmostEqual(p.truth.y_m, 0.16)

    def test_body_translation_rotates_into_world(self):
        params = Parameters()
        pose = integrate(Pose(yaw_rad=math.pi / 2),
                         wheel_speeds(1, 0, 0, params), params, 1)
        self.assertAlmostEqual(pose.x_m, 0)
        self.assertAlmostEqual(pose.y_m, 1)

    def test_invalid_input_does_not_advance(self):
        p = Plant()
        for dt in (0, -1, math.nan, math.inf):
            with self.assertRaises(ValueError):
                p.step(dt)
        with self.assertRaises(ValueError):
            p.step(1, (1, 2))
        with self.assertRaises(ValueError):
            p.command(math.nan, 0, 0)
        with self.assertRaises(ValueError):
            Parameters(half_track_m=0)
        self.assertEqual(p.time_s, 0)


if __name__ == '__main__':
    unittest.main()
