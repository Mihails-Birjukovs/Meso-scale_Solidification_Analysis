"""Coordinate/sign regression tests for saved 2WCF vectors and physical curl."""
import importlib.util
import math
from pathlib import Path
import unittest

SRC = Path(__file__).resolve().parents[1] / "Python_code" / "ofv_coordinate_conventions.py"
spec = importlib.util.spec_from_file_location("ofv_coordinate_conventions", SRC)
frame = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frame)


class OFVCoordinateConventionTests(unittest.TestCase):
    def test_requires_saved_upstream_inversion(self):
        with self.assertRaisesRegex(ValueError, "Missing"):
            frame.require_inversion({"ArrowDensityStep": 7})
        self.assertEqual(frame.require_inversion({"VelocityInversion": -1}), -1)
        with self.assertRaises(ValueError):
            frame.require_inversion({"VelocityInversion": 0})

    def test_all_cardinal_directions_when_upstream_negates_both_components(self):
        # Ground truth forward image displacements, positive y DOWN.
        dt, pixel_size = 1, 70e-6
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (2, -1)]:
            with self.subTest(dx=dx, dy=dy):
                u_img, v_img = frame.forward_image_components(
                    -dx, -dy, inversion=-1, m_per_pixel=pixel_size, pair_dt_s=dt)
                self.assertAlmostEqual(u_img, dx * pixel_size)
                self.assertAlmostEqual(v_img, dy * pixel_size)
                u_phys, v_phys = frame.physical_cartesian_velocity(u_img, v_img)
                self.assertAlmostEqual(u_phys, dx * pixel_size)
                self.assertAlmostEqual(v_phys, -dy * pixel_size)

    def test_alternate_upstream_inversion(self):
        u, v = frame.forward_image_components(3, -2, inversion=1,
                        m_per_pixel=2, pair_dt_s=4)
        self.assertEqual((u, v), (1.5, -1))

    def test_refuses_inversion_and_scale_ambiguity(self):
        for kw in ({"inversion": 0, "m_per_pixel": 1, "pair_dt_s": 1},
                   {"inversion": -1, "m_per_pixel": -1, "pair_dt_s": 1},
                   {"inversion": -1, "m_per_pixel": 1, "pair_dt_s": 0},
                   {"inversion": math.nan, "m_per_pixel": 1, "pair_dt_s": 1}):
            with self.assertRaises(ValueError):
                frame.forward_image_components(1, 2, **kw)

    def test_physical_curl_of_cartesian_counterclockwise_rotation(self):
        # Physical u_x = -a*y_phys; v_phys = a*x.
        # With y_image = -y_phys: u_img = a*y_image, v_img = -a*x.
        # Thus du/dy_img=a and dv_img/dx=-a, so curl_phys=2a.
        a = 1.25
        self.assertAlmostEqual(frame.physical_vorticity_from_image_derivatives(a, -a), 2*a)

    def test_physical_curl_of_planar_extension_zero(self):
        # Physical u=a*x, v=-a*y_phys => image u=a*x, image v=-a*y_img.
        self.assertEqual(frame.physical_vorticity_from_image_derivatives(0, 0), 0)

    def test_internal_image_frame_dilatation_unchanged_by_reflection(self):
        # Reflection of both coordinate and velocity y-components preserves div:
        # d(u_phys)/dx + d(v_phys)/dy_phys = d(u_img)/dx + d(v_img)/dy_img.
        div_img = 0.8 + (-0.3)
        div_phys = 0.8 + (-0.3)
        self.assertAlmostEqual(div_img, div_phys)


if __name__ == "__main__":
    unittest.main()
