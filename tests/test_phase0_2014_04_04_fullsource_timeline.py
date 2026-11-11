"""Synthetic source/CRC/flat-field timeline tests, no real research data in CI.

Native scientific dependencies NumPy and tifffile must exist for PASS; otherwise
tests are SKIP, not evidence of a successful experimental preflight.
"""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zlib

HAS_DEPS = bool(importlib.util.find_spec("numpy") and
                importlib.util.find_spec("tifffile"))
SRC = Path(__file__).resolve().parents[1] / "Python_code" / "phase0_2014_04_04_fullsource_timeline.py"


@unittest.skipUnless(HAS_DEPS, "Optional image science dependencies missing")
class FullSourceTimelineTests(unittest.TestCase):
    def setUp(self):
        import numpy as np
        import tifffile
        spec = importlib.util.spec_from_file_location("full_source_timeline", SRC)
        self.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)
        self.np = np
        self.tifffile = tifffile
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.flat = self.root / "flat"
        self.exp = self.root / "exp"
        self.flat.mkdir()
        self.exp.mkdir()
        self.inv = {
            "schema": "ga-in-archive-inventory/v1",
            "case_id": "2014-04-04",
            "archive_sha256_verified": True,
            "archive_sha256": "a" * 64,
            "flat_field_role_confirmed": True,
            "reference_recording_role": "flat_field_correction_owner_confirmed",
            "streams": {
                "reference": {"count": 4},
                "main": {"count": 3},
                "end": {"count": 2},
            },
            "filename_candidate_frame_records": {
                "reference": [], "main": [], "end": []
            }
        }
        for role, dir_, vals, times in (
            ("reference", self.flat, [30000,30010,30020,30030],
             [1000,2000,3000,4000]),
            ("main", self.exp, [29800,29400,29000],
             [10000,11000,15000]),
            ("end", self.exp, [28700,28500], [20000,21000]),
        ):
            for j,(val,t) in enumerate(zip(vals,times)):
                name=f"{role}_{j:03d}.tif"
                array=np.full((4,5),val,dtype=np.uint16)
                array[0,0]=65535
                self._write(dir_,role,j,name,t,array)

    def _write(self, directory, role, j, name, t, arr):
        p=directory/name
        self.tifffile.imwrite(p,arr,compression=None)
        self.inv["filename_candidate_frame_records"][role].append({
            "candidate_ordinal_id_zero_based": j,
            "filename": name, "filename_clock_ms": t,
            "member_size_bytes": p.stat().st_size,
            "member_crc32_header_unverified": f"{zlib.crc32(p.read_bytes()) & 0xffffffff:08X}",
        })

    def trace(self):
        return self.m.build_trace(self.inv,self.flat,self.exp,
                                  expected_shape_yx=(4,5),
                                  flat_field_train_n=2)

    def test_verified_counts_breaks_and_no_composition(self):
        result, rows=self.trace()
        self.assertEqual(result["flat_field_source_frames_crc_checked"],4)
        self.assertEqual(result["experiment_source_frames_crc_checked"],5)
        self.assertEqual(len(result["contiguous_candidate_segments"]),3)
        self.assertEqual([x["count"] for x in result["contiguous_candidate_segments"]],[2,1,2])
        self.assertEqual([x["candidate_filename_dt_s"] for x in result["timestamp_discontinuities"]],[4,5])
        self.assertTrue(rows[0]["break_before"])
        self.assertTrue(rows[2]["break_before"])
        self.assertTrue(rows[3]["break_before"])
        self.assertTrue(all(x["detector_jointly_valid_fraction"]==19/20 for x in rows))
        self.assertFalse(result["filename_clock_is_verified_camera_time"])
        self.assertFalse(result["physical_cell_or_liquid_roi_admitted"])
        self.assertFalse(result["separate_homogeneous_25wtpct_sample_baseline_admitted"])
        self.assertFalse(result["composition_wt_pct_admitted"])
        self.assertFalse(result["original_v25_mil_reproduced_by_this_code"])
        self.assertEqual(result["flat_field_role"],
                         "owner_confirmed_detector_flat_field_recording")

    def test_flat_field_identity_mandatory(self):
        self.inv["flat_field_role_confirmed"]=False
        with self.assertRaisesRegex(self.m.AdmissionError, "confirmed flat-field"):
            self.trace()

    def test_archive_hash_status_mandatory(self):
        self.inv["archive_sha256_verified"]=False
        with self.assertRaisesRegex(self.m.AdmissionError, "SHA-verified"):
            self.trace()

    def test_reject_modified_extracted_image_crc(self):
        p=self.exp/"main_001.tif"
        a=self.tifffile.imread(p)
        a[1,1]+=1
        self.tifffile.imwrite(p,a,compression=None)
        with self.assertRaisesRegex(self.m.AdmissionError, "CRC"):
            self.trace()

    def test_reject_missing_member(self):
        (self.exp/"end_001.tif").unlink()
        with self.assertRaisesRegex(self.m.AdmissionError, "Extracted TIFF set"):
            self.trace()

    def test_reject_unknown_extra_tiff(self):
        self.tifffile.imwrite(self.exp/"unregistered.tif",
                              self.np.ones((4,5),dtype=self.np.uint16))
        with self.assertRaisesRegex(self.m.AdmissionError, "Extracted TIFF set"):
            self.trace()

    def test_reject_clock_reversal(self):
        self.inv["filename_candidate_frame_records"]["main"][1]["filename_clock_ms"]=9000
        with self.assertRaisesRegex(self.m.AdmissionError, "nonmonotonic"):
            self.trace()

    def test_reject_duplicate_member_name(self):
        self.inv["filename_candidate_frame_records"]["end"][0]["filename"]="main_000.tif"
        with self.assertRaisesRegex(self.m.AdmissionError, "repeated"):
            self.trace()

    def test_reject_image_geometry_after_crc_update(self):
        p=self.exp/"main_001.tif"
        self.tifffile.imwrite(p,self.np.ones((3,5),dtype=self.np.uint16))
        r=self.inv["filename_candidate_frame_records"]["main"][1]
        r["member_size_bytes"]=p.stat().st_size
        r["member_crc32_header_unverified"]=f"{zlib.crc32(p.read_bytes()) & 0xffffffff:08X}"
        with self.assertRaisesRegex(self.m.AdmissionError, "shape/type"):
            self.trace()

    def test_reject_invalid_training_split(self):
        with self.assertRaisesRegex(self.m.AdmissionError, "separate flat-field"):
            self.m.build_trace(self.inv,self.flat,self.exp,
                               expected_shape_yx=(4,5),flat_field_train_n=4)


if __name__ == "__main__":
    unittest.main()
