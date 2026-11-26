"""Synthetic safety/geometry/contrast tests for 2014-04-04 candidate masks.

No user TIFFs in GitHub or unit fixtures. All assertions test numerical
behavior and refusal contracts, NOT scientific phase accuracy.
"""
import importlib.util
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

DEPS=all(importlib.util.find_spec(n) for n in ("numpy","scipy","tifffile","PIL"))
SRC=Path(__file__).resolve().parents[1]/"Python_code"/"phase0_2014_04_04_mil_candidate_benchmark.py"


@unittest.skipUnless(DEPS,"NumPy SciPy tifffile Pillow required; optional native scientific tests SKIP in CI")
class CandidateBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import numpy as np
        import tifffile
        cls.np=np
        cls.tifffile=tifffile
        spec=importlib.util.spec_from_file_location("source_relative_candidate_benchmark_v1",SRC)
        cls.m=importlib.util.module_from_spec(spec)
        sys.modules[spec.name]=cls.m
        spec.loader.exec_module(cls.m)

    def test_exact_unchanged_image_null_across_all_options(self):
        np,m=self.np,self.m
        J0=np.full((18,22),40000.0)
        raw=J0.copy()
        p,valid=m.candidate_log_ratio(raw,J0,np.ones(J0.shape,bool))
        self.assertTrue(np.allclose(p,0))
        for filt in m.FILTERS:
            field,v=m.filter_field(p,valid,filt)
            for threshold in m.THRESHOLDS:
                for polarity in m.POLARITIES:
                    mask=m.generate_mask(field,v,threshold,polarity,(0,18,0,22),min_area=1)
                    self.assertFalse(mask.any())

    def test_polality_separates_attenuation_signs(self):
        np,m=self.np,self.m
        frame=np.full((20,20),40000.0)
        J0=np.full((20,20),40000.0)
        frame[1:7,1:7]=35000   # >0.04 positive log
        frame[12:18,12:18]=45000 # < -0.04 negative log
        p,v=m.candidate_log_ratio(frame,J0,np.ones((20,20),bool))
        plus=m.generate_mask(p,v,0.04,"positive",(0,20,0,20),1)
        minus=m.generate_mask(p,v,0.04,"negative",(0,20,0,20),1)
        both=m.generate_mask(p,v,0.04,"absolute",(0,20,0,20),1)
        self.assertEqual(int(plus.sum()),36)
        self.assertEqual(int(minus.sum()),36)
        self.assertTrue(np.array_equal(plus|minus,both))
        self.assertFalse((plus&minus).any())

    def test_min_component_removes_isolated_noise_and_uses_four_connectivity(self):
        np,m=self.np,self.m
        a=np.zeros((15,15),float)
        a[1,1]=0.2
        a[3:9,4:10]=0.2
        a[12,12]=0.2;a[13,13]=0.2
        v=np.ones_like(a,dtype=bool)
        mask=m.generate_mask(a,v,0.04,"positive",(0,15,0,15),min_area=25)
        self.assertEqual(int(mask.sum()),36)
        self.assertEqual(m.mask_metrics(mask,v,(0,15,0,15))["component_count_4connect"],1)

    def test_roi_is_explicit_not_whole_detector(self):
        np,m=self.np,self.m
        p=np.full((10,10),0.2)
        mask=m.generate_mask(p,np.ones((10,10),bool),0.04,"absolute",(2,7,3,9),min_area=1)
        self.assertEqual(int(mask.sum()),30)
        self.assertFalse(mask[:2].any())
        self.assertFalse(mask[:,0].any())
        self.assertAlmostEqual(m.mask_metrics(mask,np.ones((10,10),bool),(2,7,3,9))["candidate_fraction_valid_roi"],1)

    def test_invalid_saturated_or_zero_original_pixels_never_masked(self):
        np,m=self.np,self.m
        im=np.full((9,9),31000)
        j=np.full((9,9),40000)
        validflat=np.ones((9,9),bool);validflat[0,0]=False
        im[1,1]=0;im[2,2]=65535
        j[3,3]=65535
        p,valid=m.candidate_log_ratio(im,j,validflat)
        for i in ((0,0),(1,1),(2,2),(3,3)):
            self.assertFalse(valid[i])
            self.assertEqual(p[i],0)
        mask=m.generate_mask(p,valid,0.04,"positive",(0,9,0,9),1)
        for i in ((0,0),(1,1),(2,2),(3,3)):
            self.assertFalse(mask[i])

    def test_gaussian_invalid_neighbourhood_not_smeared_into_confident_mask(self):
        np,m=self.np,self.m
        p=np.full((25,25),0.2)
        p[12,12]=-100.0
        v=np.ones((25,25),bool);v[12,12]=False
        field,usable=m.filter_field(p,v,"gaussian_1px")
        self.assertFalse(usable[12,12])
        self.assertFalse(usable[12,13])  # normalized Gaussian weight <0.999
        self.assertAlmostEqual(field[0,0],0.2)
        self.assertTrue(np.isfinite(field).all())

    def test_median_invalid_neighbourhood_excluded(self):
        np,m=self.np,self.m
        p=np.full((17,17),0.1)
        v=np.ones((17,17),bool);v[8,8]=False
        field,usable=m.filter_field(p,v,"median_3px")
        self.assertFalse(usable[8,8])
        self.assertFalse(usable[8,9])
        self.assertAlmostEqual(field[0,0],0.1)

    def test_jaccard_undefined_for_two_empty_masks_not_perfect_accuracy(self):
        np,m=self.np,self.m
        a=np.zeros((9,9),bool)
        self.assertIsNone(m.jaccard(a,a))
        b=a.copy();b[2:5,2:5]=True
        self.assertEqual(m.jaccard(a,b),0.0)
        self.assertEqual(m.jaccard(b,b),1.0)

    def test_reject_unknown_filter_threshold_polarity_and_bad_roi(self):
        np,m=self.np,self.m
        arr=np.zeros((10,10))
        v=np.ones_like(arr,dtype=bool)
        with self.assertRaises(m.GateError):m.filter_field(arr,v,"blur_that_looks_nice")
        with self.assertRaises(m.GateError):m.generate_mask(arr,v,0,"positive",(0,10,0,10))
        with self.assertRaises(m.GateError):m.generate_mask(arr,v,0.01,"solid",(0,10,0,10))
        with self.assertRaises(m.GateError):m.generate_mask(arr,v,0.01,"positive",(0,11,0,10))

    def test_reject_unverified_archive_and_misclassified_reference(self):
        m=self.m
        manifest={"schema":"ga-in-archive-inventory/v1","case_id":"2014-04-04",
                  "archive_sha256":m.EXPECTED_ARCHIVE_SHA,"archive_sha256_verified":False,
                  "reference_recording_role":"flat_field_correction_owner_confirmed",
                  "flat_field_role_confirmed":True}
        with self.assertRaisesRegex(m.GateError,"SHA"):m.validate_inventory(manifest)
        manifest["archive_sha256_verified"]=True
        manifest["reference_recording_role"]="specimen J0"
        with self.assertRaisesRegex(m.GateError,"NOT specimen"):m.validate_inventory(manifest)

    def test_member_crc_and_shape_checks_with_synthetic_tiff(self):
        import numpy as np
        m=self.m
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"example.tif"
            self.tifffile.imwrite(p,np.full(m.SHAPE,30000,dtype=np.uint16),compression=None)
            record={"filename":p.name,"member_size_bytes":p.stat().st_size,
                "member_crc32_header_unverified":f"{zlib.crc32(p.read_bytes())&0xffffffff:08X}"}
            image=m.read_source(p,record)
            self.assertEqual(image.shape,m.SHAPE)
            record["member_crc32_header_unverified"]="00000000"
            with self.assertRaisesRegex(m.GateError,"CRC32"):
                m.read_source(p,record)

if __name__=="__main__":
    unittest.main()