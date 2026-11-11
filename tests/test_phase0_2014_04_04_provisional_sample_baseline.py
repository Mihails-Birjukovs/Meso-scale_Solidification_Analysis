"""Source-hashed synthetic original-TIFF tests for provisional J0 diagnostic.

Optional NumPy+tifffile: scientific tests SKIP cleanly in lightweight CI;
run natively for acceptance evidence.
"""
import importlib.util,sys
from pathlib import Path
import tempfile,unittest,zlib

DEPS=bool(importlib.util.find_spec("numpy") and importlib.util.find_spec("tifffile"))
SRC=Path(__file__).resolve().parents[1]/"Python_code"/"phase0_2014_04_04_provisional_sample_baseline.py"


@unittest.skipUnless(DEPS,"NumPy and tifffile optional: native scientific test skipped")
class ProvisionalSampleBaselineTests(unittest.TestCase):
    def setUp(self):
        import numpy as np,tifffile
        spec=importlib.util.spec_from_file_location("provisional_j0_test",SRC)
        self.m=importlib.util.module_from_spec(spec)
        sys.modules[spec.name]=self.m
        spec.loader.exec_module(self.m)
        self.np=np;self.tf=tifffile
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.inv={"schema":"ga-in-archive-inventory/v1","case_id":"2014-04-04",
                  "archive_sha256_verified":True,"archive_sha256":"a"*64,
                  "flat_field_role_confirmed":True,
                  "reference_recording_role":"flat_field_correction_owner_confirmed",
                  "filename_candidate_frame_records":{"main":[]}}
        for i in range(7):
            arr=np.full((3,4),40000+(0 if i<3 else 20 if i<5 else -1000),dtype=np.uint16)
            p=self.root/f"frame_{i:03d}.tif"
            tifffile.imwrite(p,arr,compression=None)
            self.inv["filename_candidate_frame_records"]["main"].append({
                "filename":p.name,
                "candidate_ordinal_id_zero_based":i,
                "filename_clock_ms":1000*(i+1),
                "member_size_bytes":p.stat().st_size,
                "member_crc32_header_unverified":f"{zlib.crc32(p.read_bytes())&0xffffffff:08X}"})

    def probe(self):
        return self.m.probe(self.inv,self.root,shape_yx=(3,4),region_yx=(0,3,0,4),
                            train_n=3,heldout_n=2,sample_ordinals=(0,3,4,6))

    def test_heldout_and_evolving_signal_not_physical_acceptance(self):
        r=self.probe()
        self.assertEqual(r["raw_source_crc_checked_selected_count"],6)
        self.assertEqual(r["train_source_frames"],3)
        self.assertEqual(r["heldout_source_frames"],2)
        self.assertAlmostEqual(r["max_absolute_holdout_frame_median_P"],abs(-self.np.log((40020)/40000)))
        self.assertEqual(r["status"],"CANDIDATE_SPECIMEN_BASELINE_NOT_EXPERT_ACCEPTED")
        self.assertFalse(r["independent_expert_phase_and_ROI_review"])
        self.assertFalse(r["initial_25wtpct_composition_verified"])
        self.assertFalse(r["chemical_concentration_calibration_admitted"])
        self.assertEqual(r["role_Reference"],"detector_flat_field_R_not_J0")

    def test_no_dark_claim(self):
        r=self.probe()
        self.assertFalse(r["dark_detector_offset_admitted"])
        self.assertEqual(r["mode"],"flat_only")

    def test_unchecked_archive_rejected(self):
        self.inv["archive_sha256_verified"]=False
        with self.assertRaisesRegex(self.m.BaselineGateError,"provenance-checked"):
            self.probe()

    def test_reference_role_must_be_flat_field(self):
        self.inv["reference_recording_role"]="unknown"
        with self.assertRaisesRegex(self.m.BaselineGateError,"flat-field"):
            self.probe()

    def test_crc_corruption_rejected(self):
        p=self.root/"frame_003.tif"
        a=self.tf.imread(p);a[0,0]+=3
        self.tf.imwrite(p,a,compression=None)
        with self.assertRaisesRegex(self.m.BaselineGateError,"CRC"):
            self.probe()

    def test_gap_in_first_train_holdout_rejected(self):
        self.inv["filename_candidate_frame_records"]["main"][4]["filename_clock_ms"]=6000
        with self.assertRaisesRegex(self.m.BaselineGateError,"noncontiguous"):
            self.probe()

    def test_geometry_out_of_bounds_rejected(self):
        with self.assertRaisesRegex(self.m.BaselineGateError,"ROI"):
            self.m.probe(self.inv,self.root,shape_yx=(3,4),region_yx=(0,5,0,4),
                          train_n=3,heldout_n=2,sample_ordinals=(0,3,4,6))


if __name__=="__main__":
    unittest.main()
