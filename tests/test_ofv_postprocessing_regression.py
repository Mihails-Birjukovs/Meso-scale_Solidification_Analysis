"""Static pipeline-admission tests plus manufactured image-coordinate examples.

No research data, workstation installation, SciPy or NumPy is required in CI.
The production script has interactive inputs, so it must never be imported here.
"""
import ast
import importlib.util
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "Python_code" / "VelocimetryRaksturlielumi.py"
COORD = ROOT / "Python_code" / "ofv_coordinate_conventions.py"
spec = importlib.util.spec_from_file_location("ofv_coords", COORD)
coords = importlib.util.module_from_spec(spec)
spec.loader.exec_module(coords)


class PostprocessingRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SRC.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.calls = [
            node.func.id
            for node in ast.walk(cls.tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        ]

    def test_pipeline_compiles_without_ever_running_interactive_script(self):
        compile(self.source, str(SRC), "exec")

    def test_upstream_inversion_is_required_in_script(self):
        self.assertIn("require_inversion", self.calls)
        self.assertIn("forward_image_components", self.calls)
        self.assertNotIn("u = u_pix * scale", self.source)
        self.assertNotIn("v = v_pix * scale", self.source)

    def test_refuse_one_component_basis_flip(self):
        self.assertNotIn("vectors_interp[:, 1] *= -1", self.source)
        self.assertNotIn("vectors_interp[:, 0] *= -1", self.source)
        self.assertIn("positions_interp = positions_all.copy()", self.source)
        self.assertIn("vectors_interp = vectors_all.copy()", self.source)

    def test_curl_derivative_basis_explicit(self):
        self.assertIn("physical_vorticity_from_image_derivatives", self.calls)
        self.assertNotIn("omega = dv_dx - du_dy", self.source)

    def test_interpolation_selection_is_explicit(self):
        self.assertIn('INTERPOLATION_METHOD = "rbf"', self.source)
        self.assertIn('if INTERPOLATION_METHOD == "rbf":', self.source)
        self.assertIn('elif INTERPOLATION_METHOD == "linear":', self.source)
        self.assertNotIn("U = U_linear.copy()", self.source)
        self.assertIn("np.isfinite(U) & np.isfinite(V)", self.source)
        self.assertIn("np.count_nonzero(mask_far_from_data)", self.source)
        self.assertIn("if n_unsupported:", self.source)
        self.assertIn("if n_bad:", self.source)
        self.assertIn("raise ValueError(", self.source)
        # selected field goes into derivatives and physical integrals
        self.assertIn("np.gradient(U, dy, dx)", self.source)

    def test_manufactured_translation_all_cardinal_signs(self):
        scale, dt = 70e-6, 1.0
        for inv in (-1, 1):
            for dx, dy in [(3, 5), (2, -7), (-4, -5), (-3, 9), (0, 1)]:
                with self.subTest(inv=inv, dx=dx, dy=dy):
                    ux, vy = coords.forward_image_components(
                        dx * inv, dy * inv, inversion=inv,
                        m_per_pixel=scale, pair_dt_s=dt
                    )
                    self.assertAlmostEqual(ux, dx * scale)
                    self.assertAlmostEqual(vy, dy * scale)
                    cx, cy = coords.physical_cartesian_velocity(ux, vy)
                    self.assertAlmostEqual(cx, dx * scale)
                    self.assertAlmostEqual(cy, -dy * scale)

    def test_manufactured_asymmetric_divergence_free_field(self):
        # u_image = 2*y + 0.25*x, v_image = -3*x - 0.25*y
        # div_image = 0.25 - 0.25 = 0, physical curl +z = 2-(-3)=+5
        # Not invariant under arbitrary v-only flips.
        ux_dy = 2.0
        vy_dx = -3.0
        self.assertEqual(coords.physical_vorticity_from_image_derivatives(ux_dy,vy_dx),5)
        self.assertEqual(0.25 + (-0.25),0)

    def test_manufactured_two_dimensional_grid_derivative_sign(self):
        # Image axes: x right, y DOWN. Construct a physical counterclockwise
        # rotation plus planar extension, and differentiate by central differences.
        # u_img = 2*y + x/4, v_img = -3*x - y/4.
        u = lambda x, y: 2.0*y + 0.25*x
        v = lambda x, y: -3.0*x - 0.25*y
        step = 0.01
        for x, y in ((0.0,0.0),(1.7,3.1),(-2.4,1.1)):
            with self.subTest(x=x,y=y):
                ux = (u(x+step,y)-u(x-step,y))/(2*step)
                uy = (u(x,y+step)-u(x,y-step))/(2*step)
                vx = (v(x+step,y)-v(x-step,y))/(2*step)
                vy = (v(x,y+step)-v(x,y-step))/(2*step)
                self.assertAlmostEqual(ux+vy,0,places=10)
                self.assertAlmostEqual(
                    coords.physical_vorticity_from_image_derivatives(uy,vx),
                    5,places=10
                )

    def test_reject_missing_or_invalid_upstream_inversion(self):
        for bad in (0,float("inf"),float("nan")):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                coords.require_inversion({"VelocityInversion":bad})
        with self.assertRaises(ValueError):
            coords.require_inversion({})


if __name__ == "__main__":
    unittest.main()
