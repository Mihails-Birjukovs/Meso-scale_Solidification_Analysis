"""Synthetic image/CRC tests for the optional scientific TIFF reference diagnostic.

CI without numpy+tifffile+Pillow reports SKIP, not scientific acceptance.
Run on the native lab Python 3.10 environment for real PASS evidence.
"""
from __future__ import annotations

import importlib.util
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

HAS_SCIENCE = all(importlib.util.find_spec(name) for name in ("numpy", "tifffile", "PIL"))
SOURCE = Path(__file__).resolve().parents[1] / "Python_code" / "phase0_2014_04_04_reference_probe.py"


@unittest.skipUnless(HAS_SCIENCE, "numpy/tifffile/Pillow not installed: optional native science test")
class ReferenceProbeTests(unittest.TestCase):
    def setUp(self):
        import numpy as np
        import tifffile
        spec = importlib.util.spec_from_file_location("reference_probe", SOURCE)
        self.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)
        self.np, self.tifffile = np, tifffile
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.refs = self.root / "Reference"
        self.refs.mkdir()
        self.samples = self.root / "Samples"
        self.samples.mkdir()
        self.inventory = {
            "schema": "ga-in-archive-inventory/v1",
            "case_id": "2014-04-04",
            "archive_sha256_verified": True,
            "archive_sha256": "a" * 64,
            "filename_candidate_frame_records": {"reference": [], "main": [], "end": []},
        }
        self.reference_names = []
        for idx in range(5):
            name = f"ga-25in-ref1_2014-04-04_10-07-{43+idx:02d}-889.tif"
            a = np.full((4, 5), 200 + idx, dtype=np.uint16)
            a[0,0] = 65535
            self._store(self.refs / name, a, "reference", idx)
            self.reference_names.append(name)
        self.sample_name = "ga-25in-1_2014-04-04_10-25-47-069.tif"
        a = np.full((4,5), 195, dtype=np.uint16)
        a[0,0] = 65535
        self._store(self.samples / self.sample_name, a, "main", 0)

    def _store(self, path, array, role, idx):
        self.tifffile.imwrite(path, array, compression=None)
        actual_crc = zlib.crc32(path.read_bytes()) & 0xffffffff
        self.inventory["filename_candidate_frame_records"][role].append({
            "filename": path.name,
            "candidate_ordinal_id_zero_based": idx,
            "member_crc32_header_unverified": f"{actual_crc:08X}",
            "member_size_bytes": path.stat().st_size,
        })

    def test_counts_drift_crc_and_refusal(self):
        result, rows = self.m.examine(
            self.refs, self.inventory, expected_n=5,
            reference_train_n=3, sample_dir=self.samples)
        self.assertEqual(result["reference_count"], 5)
        self.assertEqual(len(rows), 5)
        self.assertEqual(result["reference_heldout_frames"], 2)
        self.assertEqual(result["source_tiff_metadata"]["shape_yx"], [4,5])
        self.assertAlmostEqual(result["stable_nonmax_pixel_fraction"], 19/20)
        self.assertTrue(result["verified_extracted_member_crc32"])
        self.assertEqual(len(result["independent_decoder_reference_checks"]), 3)
        self.assertEqual(len(result["experimental_samples"]), 1)
        self.assertFalse(result["reference_is_homogeneous_liquid_admitted"])
        self.assertEqual(result["reference_acquisition_role"], "flat_field_recording_owner_confirmed")
        self.assertTrue(result["flat_field_source_role_confirmed"])
        self.assertFalse(result["separate_initial_homogeneous_sample_baseline_identified"])
        self.assertFalse(result["reference_is_sample_composition_baseline"])
        self.assertIn("median_flat_field_log_ratio", result["experimental_samples"][0])
        self.assertFalse(result["concentration_wt_pct_admitted"])
        self.assertFalse(result["camera_clock_admitted"])

    def test_crc_rejects_corrupted_extracted_member(self):
        path = self.refs / self.reference_names[2]
        a = self.tifffile.imread(path)
        a[1,1] += 1
        self.tifffile.imwrite(path, a, compression=None)
        with self.assertRaisesRegex(self.m.DiagnosticError, "CRC"):
            self.m.examine(self.refs, self.inventory, expected_n=5,
                           reference_train_n=3)

    def test_image_geometry_mismatch_rejected_after_valid_crc(self):
        path = self.refs / self.reference_names[2]
        a = self.np.full((5,5), 201, dtype=self.np.uint16)
        self._store_replacement(path, a)
        with self.assertRaisesRegex(self.m.DiagnosticError, "geometry"):
            self.m.examine(self.refs, self.inventory, expected_n=5,
                           reference_train_n=3)

    def _store_replacement(self, path, a):
        self.tifffile.imwrite(path, a, compression=None)
        row = next(x for x in self.inventory["filename_candidate_frame_records"]["reference"]
                   if x["filename"] == path.name)
        row["member_size_bytes"] = path.stat().st_size
        row["member_crc32_header_unverified"] = f"{zlib.crc32(path.read_bytes()) & 0xffffffff:08X}"

    def test_requires_sha_verified_inventory(self):
        self.inventory["archive_sha256_verified"] = False
        with self.assertRaisesRegex(self.m.DiagnosticError, "SHA-checked"):
            self.m.examine(self.refs, self.inventory, expected_n=5,
                           reference_train_n=3)

    def test_bad_reference_filename_refused(self):
        self.refs.joinpath(self.reference_names[0]).rename(self.refs/"frame001.tif")
        with self.assertRaisesRegex(self.m.DiagnosticError, "filenames"):
            self.m.examine(self.refs, self.inventory, expected_n=5,
                           reference_train_n=3)

    def test_unverified_sample_file_rejected(self):
        self.tifffile.imwrite(self.samples/"unregistered.tif",
                              self.np.full((4,5), 200, dtype=self.np.uint16))
        with self.assertRaisesRegex(self.m.DiagnosticError, "not in same archive"):
            self.m.examine(self.refs, self.inventory, expected_n=5,
                           reference_train_n=3, sample_dir=self.samples)


if __name__ == "__main__":
    unittest.main()
