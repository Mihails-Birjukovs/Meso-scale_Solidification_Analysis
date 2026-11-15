"""Synthetic topology admission tests: candidate corridor is not physical liquid."""
import importlib.util,sys,unittest
from pathlib import Path
HAS=bool(importlib.util.find_spec("numpy") and importlib.util.find_spec("scipy"))
if HAS:
    import numpy as np
    P=Path(__file__).resolve().parents[1]/"Python_code"/"phase0_t1_tentative_liquid_corridor.py"
    spec=importlib.util.spec_from_file_location("t1_tentative_corridor",P)
    m=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=m
    spec.loader.exec_module(m)

@unittest.skipUnless(HAS,"NumPy+SciPy needed for native path admission tests")
class TentativeCorridorTests(unittest.TestCase):
    ROI=(10,70,10,90)
    def setup_case(self,gap=(48,57)):
        valid=np.ones((80,100),bool)
        pos=np.zeros_like(valid)
        pos[31:35,10:90]=True
        if gap is not None:
            pos[31:35,gap[0]:gap[1]]=False
        negative=np.zeros_like(pos)
        negative[38:52,47:58]=True
        zone=np.zeros_like(pos)
        zone[28:70,10:90]=True
        front=np.full(80,31.0)
        return pos,valid,negative,zone,front
    def test_open_channel_bulk_to_subfront(self):
        pos,valid,neg,zone,front=self.setup_case()
        c=m.candidate_corridor(pos,valid,front,roi=self.ROI,neck_radius=1)
        self.assertGreater(c.metadata["seed_pixels"],0)
        self.assertTrue(c.below_front_connected[42,50])
        rows=m.component_root_diagnostics(neg,c,zone)
        self.assertEqual(len(rows),1)
        self.assertTrue(rows[0]["proposed_candidate_corridor_supported"])
        self.assertFalse(rows[0]["physical_liquid_channel_verified"])
    def test_blocked_wall_refuses_below_front_root(self):
        pos,valid,neg,zone,front=self.setup_case(gap=None)
        c=m.candidate_corridor(pos,valid,front,roi=self.ROI,neck_radius=0)
        self.assertEqual(int(c.below_front_connected.sum()),0)
        rows=m.component_root_diagnostics(neg,c,zone)
        self.assertTrue(rows[0]["baseline_spatial_supported"])
        self.assertFalse(rows[0]["proposed_candidate_corridor_supported"])
    def test_narrow_neck_fails_when_opening_is_stricter(self):
        pos,valid,neg,zone,front=self.setup_case(gap=(50,51))
        loose=m.candidate_corridor(pos,valid,front,roi=self.ROI,neck_radius=0)
        restrictive=m.candidate_corridor(pos,valid,front,roi=self.ROI,neck_radius=2)
        self.assertTrue(loose.below_front_connected[42,50])
        self.assertFalse(restrictive.below_front_connected[42,50])
    def test_invalid_pixel_can_block_path(self):
        pos,valid,neg,zone,front=self.setup_case(gap=(50,51))
        valid[31:35,50]=False
        c=m.candidate_corridor(pos,valid,front,roi=self.ROI,neck_radius=0)
        self.assertEqual(int(c.below_front_connected.sum()),0)
    def test_unknown_front_refuses_inference(self):
        pos,valid,neg,zone,front=self.setup_case()
        c=m.candidate_corridor(pos,valid,None,roi=self.ROI,neck_radius=0)
        self.assertEqual(c.metadata["status"],"NO_FRONT_NO_TOPOLOGICAL_CLAIM")
        self.assertFalse(c.source_bulk_connected.any())
    def test_fails_bad_source_shape_and_front(self):
        pos,valid,neg,zone,front=self.setup_case()
        with self.assertRaises(ValueError):m.candidate_corridor(pos,valid[:2],front,roi=self.ROI)
        with self.assertRaises(ValueError):m.candidate_corridor(pos,valid,front[:-1],roi=self.ROI)
        with self.assertRaises(ValueError):m.candidate_corridor(pos,valid,np.full(80,9.),roi=self.ROI)
    def test_no_source_pixel_mutation(self):
        pos,valid,neg,zone,front=self.setup_case()
        before=[x.copy() for x in (pos,valid,neg,zone,front)]
        m.corridor_comparison(pos,pos.copy(),valid,front,neg,zone,roi=self.ROI,neck_radii=(0,1))
        for a,b in zip((pos,valid,neg,zone,front),before):
            self.assertTrue(np.array_equal(a,b))
    def test_more_positive_obstacles_cannot_create_extra_path_at_radius_zero(self):
        pos,valid,neg,zone,front=self.setup_case()
        broad=pos.copy()
        broad[30:40,60:65]=True
        result=m.corridor_comparison(pos,broad,valid,front,neg,zone,roi=self.ROI,neck_radii=(0,))
        a,b=result["hypotheses"]
        self.assertLessEqual(b["corridor"]["bulk_connected_candidate_pixels"],a["corridor"]["bulk_connected_candidate_pixels"])
    def test_positives_cannot_overlap_invalids(self):
        pos,valid,neg,zone,front=self.setup_case()
        valid[31,20]=False
        with self.assertRaisesRegex(ValueError,"invalid detector"):
            m.candidate_corridor(pos,valid,front,roi=self.ROI)
    def test_component_diagnostic_never_changes_baseline_retention(self):
        pos,valid,neg,zone,front=self.setup_case(gap=None)
        r=m.corridor_comparison(pos,pos.copy(),valid,front,neg,zone,roi=self.ROI,neck_radii=(0,))
        self.assertFalse(r["original_masks_changed"])
        self.assertFalse(r["physical_channel_path_admitted"])
        for x in r["hypotheses"]:
            self.assertEqual(x["spatial_retained_components"],1)
            self.assertEqual(x["spatial_retained_with_candidate_root"],0)
if __name__=="__main__":unittest.main()
