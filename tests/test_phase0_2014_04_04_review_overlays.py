"""Synthetic presentation-only overlay checks; no original research TIFFs required.

Tests verify pixel alignment, source-independent masks, outline color/geometry,
invalid-detector visualization and refusal of changed source mask hashes.
NumPy, scipy, Pillow and matplotlib are optional in lightweight GitHub CI;
run on the native compatible scientific environment for PASS evidence.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

DEPS = all(importlib.util.find_spec(k) for k in ("numpy", "scipy", "PIL", "matplotlib", "tifffile"))
SRC = Path(__file__).resolve().parents[1] / "Python_code" / "phase0_2014_04_04_review_overlays.py"


@unittest.skipUnless(DEPS, "Optional native image libraries not installed")
class SourceLockedOverlayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import numpy as np
        from PIL import Image
        cls.np, cls.Image = np, Image
        spec=importlib.util.spec_from_file_location("review_overlays_source_locked_test_module",SRC)
        cls.mod=importlib.util.module_from_spec(spec)
        sys.modules[spec.name]=cls.mod
        spec.loader.exec_module(cls.mod)

    def test_one_pixel_boundary_on_3x3_region(self):
        a=self.np.zeros((9,9),dtype=bool)
        a[2:5,3:6]=True
        b=self.mod.outline(a)
        self.assertEqual(int(b.sum()),8)
        self.assertFalse(b[3,4])
        self.assertTrue(b[2,3])
        self.assertFalse(b[0,0])

    def test_paint_preserves_background_and_input_masks(self):
        np=self.np
        background=np.full((18,24,3),100,dtype=np.uint8)
        pos=np.zeros((18,24),bool);pos[2:8,2:9]=True
        neg=np.zeros((18,24),bool);neg[9:16,12:20]=True
        originals=(background.copy(),pos.copy(),neg.copy())
        overlays=self.mod.paint(background,{"positive":pos,"negative":neg},
                                positive=True,negative=True,filled=False)
        self.assertEqual(overlays.shape,background.shape)
        self.assertTrue(np.array_equal(overlays[0,0],background[0,0]))
        self.assertTrue(np.array_equal(overlays[2,2],self.mod.COLOR_POS.astype(np.uint8)))
        self.assertTrue(np.array_equal(overlays[9,12],self.mod.COLOR_NEG.astype(np.uint8)))
        self.assertTrue(np.array_equal(overlays[4,5],background[4,5]))
        self.assertTrue(np.array_equal(background,originals[0]))
        self.assertTrue(np.array_equal(pos,originals[1]))
        self.assertTrue(np.array_equal(neg,originals[2]))

    def test_fill_alpha_applies_only_interior_and_outlines_on_top(self):
        np=self.np
        image=np.full((24,26,3),100,dtype=np.uint8)
        p=np.zeros((24,26),bool);p[2:12,2:12]=True
        n=np.zeros((24,26),bool);n[13:23,14:24]=True
        y=self.mod.paint(image,{"positive":p,"negative":n},
                         positive=True,negative=True,filled=True)
        expected_pos=((1-self.mod.ALPHA)*image[6,6] +
                      self.mod.ALPHA*self.mod.COLOR_POS).astype(np.uint8)
        self.assertTrue(np.array_equal(y[6,6],expected_pos))
        self.assertTrue(np.array_equal(y[2,2],self.mod.COLOR_POS.astype(np.uint8)))
        self.assertTrue(np.array_equal(y[13,14],self.mod.COLOR_NEG.astype(np.uint8)))
        self.assertTrue(np.array_equal(y[0,0],image[0,0]))

    def test_invalid_detector_pixels_are_distinct(self):
        np=self.np
        p=np.zeros((5,7),float)
        v=np.ones((5,7),bool);v[2,3]=False
        rgb=self.mod.make_heat(p,v)
        self.assertEqual(rgb.shape,(5,7,3))
        self.assertTrue(np.array_equal(rgb[2,3],[30,32,38]))
        self.assertFalse(np.array_equal(rgb[1,1],[30,32,38]))

    def test_source_mask_checksum_and_geometry_required(self):
        np=self.np
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"m.png"
            mask=np.zeros(self.mod.SHAPE,dtype=np.uint8)
            mask[120:150,180:210]=255
            self.Image.fromarray(mask).save(p)
            checksum=self.mod.digest(p)
            actual=self.mod.load_mask(p,checksum)
            self.assertEqual(int(actual.sum()),30*30)
            with self.assertRaisesRegex(ValueError,"checksum"):
                self.mod.load_mask(p,"0"*64)
            self.Image.fromarray(mask[:20,:30]).save(p)
            with self.assertRaisesRegex(ValueError,"geometry"):
                self.mod.load_mask(p,self.mod.digest(p))

    def test_original_pixel_geometry_and_constants_are_unchanged(self):
        self.assertEqual(self.mod.SHAPE,(426,761))
        self.assertEqual(self.mod.ROI,(120,412,155,690))
        self.assertEqual(self.mod.SELECTED,(
            ("main",119),("main",480),("main",639),
            ("main",1200),("main",3147),("end",297)))
        self.assertEqual(self.mod.CASE_SHA,
           "77fac9a38a9cdaa41ee5ec9c9562acb7149ee1cee8f0246a80c2b267928f2510")


if __name__=="__main__":
    unittest.main()
