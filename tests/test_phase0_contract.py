"""Offline Phase-0 regression tests: no private image data or 2WCF code needed."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "Python_code" / "phase0_contract.py"
spec = importlib.util.spec_from_file_location("phase0_contract", MODULE_PATH)
phase0 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(phase0)


class PhaseZeroContractTests(unittest.TestCase):
    def test_timing_binned_frames_and_midpoint(self):
        kw = {"raw_dt_s": 0.2, "bin_size": 5, "source_start_index": 0}
        self.assertAlmostEqual(phase0.bin_center_time(0, **kw), 0.4)
        self.assertAlmostEqual(phase0.bin_center_time(1, **kw), 1.4)
        self.assertAlmostEqual(phase0.pair_center_time(0, **kw), 0.9)

    def test_crop_start_frame_and_absolute_clock(self):
        self.assertAlmostEqual(phase0.bin_center_time(0, raw_dt_s=.2,
            bin_size=5, source_start_index=10, acquisition_t0_s=100), 102.4)

    def test_bad_time_parameters_rejected(self):
        for dt, bins in [(0, 5), (-0.1, 5), (0.2, 0)]:
            with self.subTest(dt=dt, bins=bins):
                with self.assertRaises(ValueError):
                    phase0.bin_center_time(0, raw_dt_s=dt, bin_size=bins)

    def test_cartesian_transform_with_upstream_negative_inversion(self):
        # Forward pixel displacement right +2, down +3; saved by upstream as -2,-3.
        v = phase0.to_physical(4, 6, -2, -3, image_height_px=20,
                               pixel_size_m=70e-6, pair_dt_s=1,
                               velocity_inversion=-1)
        self.assertAlmostEqual(v["x_m"], 4 * 70e-6)
        self.assertAlmostEqual(v["y_m"], 13 * 70e-6)
        self.assertAlmostEqual(v["u_m_s"], 2 * 70e-6)
        self.assertAlmostEqual(v["v_m_s"], -3 * 70e-6)

    def test_cartesian_transform_with_positive_inversion(self):
        v = phase0.to_physical(0, 0, 2, -3, image_height_px=20,
                               pixel_size_m=1, pair_dt_s=2,
                               velocity_inversion=1)
        self.assertEqual((v["u_m_s"], v["v_m_s"]), (1, 1.5))

    def test_zero_velocity_inversion_rejected(self):
        with self.assertRaises(ValueError):
            phase0.to_physical(0, 0, 1, 2, image_height_px=10,
                               pixel_size_m=1, pair_dt_s=1, velocity_inversion=0)

    def test_frame_scan_and_staged_byte_integrity(self):
        with tempfile.TemporaryDirectory() as temp:
            origin = Path(temp) / "raw"
            origin.mkdir()
            data = b"II\x2a\x00" + b"\x00" * 48
            (origin / "filtered3D_00000.tif").write_bytes(data)
            (origin / "filtered3D_00001.tif").write_bytes(data + b"\x01")
            (origin / "notes.txt").write_text("ignore")
            images = phase0.indexed_files(origin, phase0.IMAGE_PATTERN)
            self.assertEqual([i for i, _ in images], [0, 1])
            dest = Path(temp) / "for_2wcf"
            rec = phase0.stage_tiff(images, dest)
            self.assertEqual([Path(x["staged"]).suffix for x in rec], [".tiff", ".tiff"])
            self.assertEqual((dest / "filtered3D_00001.tiff").read_bytes(), data + b"\x01")
            with self.assertRaises(ValueError):
                phase0.stage_tiff(images, dest)

    def test_gaps_and_duplicate_ids_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            for name in ["filtered3D_00000.tif", "filtered3D_00002.tif"]:
                (folder / name).write_bytes(b"II\x2a\x00")
            with self.assertRaises(ValueError):
                phase0.indexed_files(folder, phase0.IMAGE_PATTERN)
            (folder / "filtered3D_00001.tif").write_bytes(b"II\x2a\x00")
            (folder / "filtered3D_00001.tiff").write_bytes(b"II\x2a\x00")
            with self.assertRaises(ValueError):
                phase0.indexed_files(folder, phase0.IMAGE_PATTERN)

    def test_manifest_pairing_and_no_pickle_execution(self):
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            for i in range(3):
                (d / f"filtered3D_{i:05d}.tif").write_bytes(b"II\x2a\x00")
                (d / f"Conc_In_{i:05d}.tif").write_bytes(b"II\x2a\x00")
            for i in range(2):
                # Intentionally invalid pickle bytes: contract checker MUST NOT load them.
                (d / f"velocity_field_{i:05d}.pkl").write_text("not a pickle")
            imgs = phase0.indexed_files(d, phase0.IMAGE_PATTERN)
            conc = phase0.indexed_files(d, phase0.CONCENTRATION_PATTERN)
            fields = phase0.indexed_files(d, phase0.VECTOR_PATTERN)
            m = phase0.make_manifest(imgs, concentration=conc, vectors=fields,
                raw_dt_s=.2, bin_size=5, source_start_index=0,
                acquisition_t0_s=0, pixel_size_m=70e-6,
                velocity_inversion=-1, ofv_parameters={"VelocityInversion": -1})
            self.assertEqual(len(m["frame_pairs"]), 2)
            self.assertAlmostEqual(m["frame_pairs"][0]["velocity_center_s"], .9)
            self.assertEqual(m["frame_pairs"][0]["vector_file"], "velocity_field_00000.pkl")
            self.assertFalse(m["validation"]["physical_wall_boundary_verified"])
            json.dumps(m)

    def test_manifest_rejects_incomplete_pair_list(self):
        imgs = [(i, Path(f"filtered3D_{i:05d}.tif")) for i in range(3)]
        with self.assertRaises(ValueError):
            phase0.make_manifest(imgs, vectors=[(0, Path("velocity_field_00000.pkl"))],
                raw_dt_s=.2, bin_size=5, source_start_index=0,
                acquisition_t0_s=0, pixel_size_m=70e-6, velocity_inversion=-1)

    def test_manifest_rejects_inversion_mismatch(self):
        imgs = [(i, Path(f"filtered3D_{i:05d}.tif")) for i in range(2)]
        with self.assertRaises(ValueError):
            phase0.make_manifest(imgs, raw_dt_s=.2, bin_size=5, source_start_index=0,
                acquisition_t0_s=0, pixel_size_m=70e-6,
                velocity_inversion=1, ofv_parameters={"VelocityInversion": -1})


if __name__ == "__main__":
    unittest.main()
