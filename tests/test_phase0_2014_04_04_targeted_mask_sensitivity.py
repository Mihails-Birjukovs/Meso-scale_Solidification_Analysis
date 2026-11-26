"""Synthetic tests for targeted 2014-04-04 post-review candidate-mask images.

Optional image dependencies may skip on lightweight GitHub CI. Use the already
validated Windows Miniconda scientific environment for native PASS evidence.
These tests verify presentation and threshold logic, not real phase labels.
"""
from __future__ import annotations
import importlib.util
import sys
import unittest
from pathlib import Path

HAS_DEPS=all(importlib.util.find_spec(n) for n in ("numpy","scipy","PIL","matplotlib","tifffile"))
SCRIPT=Path(__file__).resolve().parents[1]/"Python_code"/"phase0_2014_04_04_targeted_mask_sensitivity.py"


@unittest.skipUnless(HAS_DEPS, "Optional image-science packages unavailable")
class TargetedMaskSensitivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import numpy as np
        cls.np=np
        s=importlib.util.spec_from_file_location("targeted_sensitivity_review_tests",SCRIPT)
        cls.m=importlib.util.module_from_spec(s)
        sys.modules[s.name]=cls.m
        s.loader.exec_module(cls.m)

    def test_parameters_stay_experimental_and_source_geometry(self):
        m=self.m
        self.assertEqual(m.SHAPE,(426,761))
        self.assertEqual(m.ROI,(120,412,155,690))
        self.assertEqual(m.FRAMES,(("main",119),("main",480),("main",639),
                                   ("main",1200),("main",3147),("end",297)))
        self.assertEqual(m.POS_THRESHOLDS,(.02,.025,.03,.035,.04,.05,.06,.08))
        self.assertEqual(m.NEG_THRESHOLDS,(.04,.05,.06,.08))
        self.assertEqual(m.NEG_MIN_AREA,(25,75,150))

    def test_outline_excludes_synthetic_interior(self):
        np,m=self.np,self.m
        q=np.zeros((12,15),bool);q[2:9,3:11]=True
        e=m.edge(q)
        self.assertTrue(e[2,3])
        self.assertFalse(e[5,7])
        self.assertEqual(e.shape,q.shape)
        self.assertFalse(e[0,0])

    def test_paint_yellow_for_weak_positive_and_preserves_original(self):
        np,m=self.np,self.m
        a=np.full((18,20,3),100,dtype=np.uint8)
        base=a.copy()
        weak=np.zeros((18,20),bool)
        weak[2:11,2:12]=True
        out=m.paint(base,[(weak,"weak_positive",0)])
        self.assertTrue(np.array_equal(out[2,2],m.COLORS["weak_positive"]))
        self.assertTrue(np.array_equal(out[0,0],a[0,0]))
        self.assertTrue(np.array_equal(a,base))
        self.assertTrue(np.array_equal(base[7,6],[100,100,100]))

    def test_colormap_invalid_pixels_are_dark(self):
        np,m=self.np,self.m
        a=np.zeros((20,21),float)
        v=np.ones((20,21),bool);v[4,5]=False
        rgb=m.heatmap(a,v)
        self.assertEqual(rgb.shape,(20,21,3))
        self.assertTrue(np.array_equal(rgb[4,5],[30,32,38]))

    def test_nesting_of_positive_masks_requires_same_filter_and_roi(self):
        np=self.np
        from scipy import ndimage as ndi
        a=np.zeros((40,40))
        a[3:36,3:36]=np.linspace(.015,.085,33)[None,:]
        v=np.ones((40,40),bool)
        roi=(0,40,0,40)
        def threshold(t):
            hit=(a>t)&v
            label,n=ndi.label(hit,structure=ndi.generate_binary_structure(2,1))
            sizes=np.bincount(label.ravel())
            valid=sizes>=25
            valid[0]=False
            return valid[label]
        loose=threshold(.02);current=threshold(.04);strict=threshold(.08)
        self.assertTrue(np.all(strict<=current))
        self.assertTrue(np.all(current<=loose))
        self.assertTrue(np.any(loose&~current))

    def test_sheet_has_unscaled_source_image_pixels(self):
        m=self.m
        img=m.panel(self.np.zeros((426,761,3),dtype=self.np.uint8),"synthetic")
        self.assertEqual(img.size,(761,464))

if __name__=="__main__":
    unittest.main()
