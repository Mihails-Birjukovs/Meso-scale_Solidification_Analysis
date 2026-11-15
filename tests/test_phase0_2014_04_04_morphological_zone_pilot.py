"""Synthetic refusal and topology tests for unverified solid-zone envelope pilot.

Do not treat pixelwise results as physically validated solid/liquid segmentation.
"""
from pathlib import Path
import importlib.util,sys,unittest
DEPS=bool(importlib.util.find_spec("numpy") and importlib.util.find_spec("scipy"))
SCRIPT=Path(__file__).resolve().parents[1]/"Python_code"/"phase0_2014_04_04_morphological_zone_pilot.py"
if DEPS:
    import numpy as np
    spec=importlib.util.spec_from_file_location("phase0_morphological_zone_synthetic",SCRIPT)
    m=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=m
    spec.loader.exec_module(m)
@unittest.skipUnless(DEPS,"NumPy and SciPy scientific deps required for native morphology test")
class MorphologicalZoneTests(unittest.TestCase):
    def fixture_positive(self):
        pos=np.zeros((426,761),bool)
        y0,y1,x0,x1=m.ROI
        pos[260:y1-2,x0+5:x1-5]=True
        pos[260:y1-2,355:380]=False # liquid channel gap across the dendritic zone
        return pos
    def test_early_no_solid_seeds_refuses_front(self):
        zone,front,status=m.envelope(np.zeros((426,761),bool))
        self.assertIsNone(front)
        self.assertFalse(zone.any())
        self.assertTrue(status["reason_if_rejected"])
    def test_invalid_source_shape_refused(self):
        with self.assertRaisesRegex(ValueError,"geometry"):
            m.envelope(np.zeros((10,20),bool))
    def test_bottom_connected_solid_area_produces_geometry_hypothesis(self):
        zone,front,status=m.envelope(self.fixture_positive(),radius=4,margin=8)
        self.assertIsNotNone(front)
        self.assertGreater(status["supported_column_fraction"],.75)
        self.assertTrue(zone[350,300])
        self.assertFalse(zone[180,300])
        self.assertFalse(zone[:120].any())
        self.assertEqual(zone.shape,(426,761))
    def test_floating_upper_false_positive_does_not_shift_front(self):
        pos=self.fixture_positive()
        _,front0,_=m.envelope(pos,radius=4,margin=8)
        pos[155:182,275:312]=True
        _,front1,_=m.envelope(pos,radius=4,margin=8)
        self.assertLess(float(np.max(np.abs(front1-front0))),1.0)
    def test_keep_entire_connected_plume_above_front_and_reject_floating(self):
        pos=self.fixture_positive()
        zone,front,_=m.envelope(pos,radius=4,margin=8)
        self.assertIsNotNone(front)
        neg=np.zeros((426,761),bool)
        neg[215:355,360:367]=True   # vertical plume penetrates zone at bottom
        neg[155:164,230:237]=True   # isolated upper false candidate
        kept,metric=m.keep_connected_negative(neg,zone,min_overlap=10)
        self.assertTrue(kept[220,362])
        self.assertTrue(kept[320,362])
        self.assertFalse(kept[160,232])
        self.assertEqual(metric["component_count_original"],2)
        self.assertEqual(metric["retained_component_count"],1)
    def test_isolated_negative_above_front_not_kept_even_if_large(self):
        zone,_,_=m.envelope(self.fixture_positive(),radius=4,margin=0)
        neg=np.zeros((426,761),bool)
        neg[170:210,480:510]=True
        kept,metric=m.keep_connected_negative(neg,zone)
        self.assertFalse(kept.any())
        self.assertEqual(metric["rejected_pixels"],int(neg.sum()))
    def test_nonguessed_negative_mask_no_mutation(self):
        zone,_,_=m.envelope(self.fixture_positive(),radius=4,margin=8)
        neg=np.zeros((426,761),bool);neg[245:370,365:370]=True
        before=neg.copy();zbefore=zone.copy()
        kept,_=m.keep_connected_negative(neg,zone,min_overlap=10)
        self.assertTrue(np.array_equal(neg,before))
        self.assertTrue(np.array_equal(zone,zbefore))
        self.assertTrue(np.all(kept<=neg))
if __name__=="__main__":unittest.main()
