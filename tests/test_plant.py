import math
import unittest
from simulation.plant import Parameters, Plant


class PlantTests(unittest.TestCase):
    def test_straight_acceleration_and_stop_distance(self):
        p = Plant()
        p.command(0.4, 0.4)
        p.step(1.0)
        self.assertAlmostEqual(p.truth.x_m, 0.32)
        p.stop()
        p.step(1.0)
        self.assertAlmostEqual(p.truth.x_m, 0.4)
        self.assertEqual(p.speeds, (0.0, 0.0))
        self.assertEqual(p.time_s, 2.0)

    def test_turn_sign_and_no_translation(self):
        p = Plant()
        p.command(-0.4, 0.4)
        p.step(1.0)
        self.assertAlmostEqual(p.truth.yaw_rad, 1.28)
        self.assertAlmostEqual(p.truth.x_m, 0.0)
        self.assertAlmostEqual(p.truth.y_m, 0.0)

    def test_slip_separates_odometry_from_truth(self):
        p = Plant()
        p.command(0.4, 0.4)
        p.step(1.0, (0.5, 0.5))
        self.assertAlmostEqual(p.odometry.x_m, 0.32)
        self.assertAlmostEqual(p.truth.x_m, 0.16)

    def test_saturation_preserves_ratio(self):
        p = Plant()
        p.command(-2.0, 1.0)
        self.assertEqual(p.targets, (-0.8, 0.4))

    def test_straight_subdivision_agrees(self):
        a, b = Plant(), Plant()
        for p in (a, b):
            p.command(0.4, 0.4)
        a.step(1)
        for _ in range(100):
            b.step(0.01)
        self.assertAlmostEqual(a.truth.x_m, b.truth.x_m)

    def test_invalid_input_does_not_advance(self):
        p = Plant()
        for dt in (0, -1, math.nan, math.inf):
            with self.assertRaises(ValueError):
                p.step(dt)
        with self.assertRaises(ValueError):
            p.step(1, (1, 2))
        with self.assertRaises(ValueError):
            p.command(math.nan, 0)
        with self.assertRaises(ValueError):
            Parameters(track_width_m=0)
        self.assertEqual(p.time_s, 0)


if __name__ == '__main__':
    unittest.main()
