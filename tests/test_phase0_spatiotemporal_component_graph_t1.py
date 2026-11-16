"""Synthetic, source-order independent tests for T1. No private radiographs needed."""
import importlib.util
import sys
import unittest
from pathlib import Path

HAS_SCIENCE=bool(importlib.util.find_spec("numpy") and importlib.util.find_spec("scipy"))
if HAS_SCIENCE:
    import numpy as np
    P=Path(__file__).resolve().parents[1]/"Python_code"/"phase0_spatiotemporal_component_graph_t1.py"
    spec=importlib.util.spec_from_file_location("phase0_t1_test_model",P)
    model=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=model
    spec.loader.exec_module(model)

@unittest.skipUnless(HAS_SCIENCE,"NumPy and SciPy required for native T1")
class ComponentGraphTests(unittest.TestCase):
    def make(self,ordinal,time,blobs,group=1,role="main",zone_rect=(35,80,0,100)):
        mask=np.zeros((80,100),bool)
        for y0,y1,x0,x1 in blobs:mask[y0:y1,x0:x1]=True
        zone=np.zeros_like(mask)
        if zone_rect is not None:
            y0,y1,x0,x1=zone_rect;zone[y0:y1,x0:x1]=True
        p=np.full(mask.shape,0.0)
        p[mask]=-0.06
        return model.FrameObservation(role,ordinal,time,group,mask,zone,
                                      np.ones_like(mask),p)
    def test_exact_area_and_zone_gate(self):
        f=self.make(0,0,[(20,30,20,30),(50,60,20,30)])
        cs=model.components(f)
        self.assertEqual(len(cs),2)
        self.assertEqual(sum(x.area for x in cs),200)
        self.assertEqual([x.spatial_supported for x in cs],[False,True])
    def test_no_mask_mutation(self):
        f=self.make(0,0,[(30,50,20,40)])
        m=f.negative.copy();z=f.zone.copy()
        model.components(f)
        self.assertTrue(np.array_equal(f.negative,m))
        self.assertTrue(np.array_equal(f.zone,z))
    def test_motion_links_and_preserves_split(self):
        a=self.make(0,0,[(38,52,20,45)])
        b=self.make(1,1000,[(38,52,20,30),(38,52,36,46)])
        r=model.graph([a,b])
        self.assertEqual(r["component_nodes"],3)
        self.assertEqual(r["edges"],2)
        self.assertEqual(sum(x["following_associations"]==2 for x in r["components"]),1)
    def test_merge_two_components(self):
        a=self.make(0,0,[(38,52,20,31),(38,52,39,50)])
        b=self.make(1,1000,[(38,52,19,51)])
        r=model.graph([a,b])
        self.assertEqual(r["edges"],2)
        self.assertEqual(max(x["preceding_associations"] for x in r["components"]),2)
    def test_stationary_upper_artifact_not_promoted(self):
        a=self.make(0,0,[(10,22,25,37)])
        b=self.make(1,1000,[(10,22,25,37)])
        c=self.make(2,2000,[(10,22,25,37)])
        r=model.graph([a,b,c])
        self.assertEqual(r["edges"],2)
        self.assertTrue(all(not x["retained_by_T1_exploratory"] for x in r["components"]))
        self.assertTrue(all(x["decision"]!="spatial_supported" for x in r["components"]))
    def test_no_cross_gap_link(self):
        a=self.make(918,918000,[(38,52,20,40)],group=1)
        b=self.make(919,922360,[(38,52,20,40)],group=2)
        r=model.graph([a,b])
        self.assertEqual(r["edges"],0)
        self.assertEqual(len(r["discontinuities"]),1)
    def test_no_end_stream_link(self):
        a=self.make(3147,3147000,[(38,52,20,40)],group=4)
        b=self.make(0,3148000,[(38,52,20,40)],group=5,role="end")
        r=model.graph([a,b])
        self.assertEqual(r["edges"],0)
    def test_nonadjacent_frame_no_edge(self):
        a=self.make(10,10000,[(40,52,20,38)])
        b=self.make(12,12000,[(40,52,20,38)])
        r=model.graph([a,b])
        self.assertEqual(r["edges"],0)
    def test_reject_corrupt_source_validity(self):
        f=self.make(0,0,[(40,52,20,38)])
        f.valid[:]=False
        with self.assertRaisesRegex(ValueError,"invalid detector"):
            model.components(f)
    def test_reject_duplicate_frame(self):
        a=self.make(0,0,[(40,52,20,38)])
        with self.assertRaises(ValueError):
            model.graph([a,a])
    def test_graph_uncertainty_is_not_physical_probability(self):
        a=self.make(0,0,[(10,22,20,34)])
        b=self.make(1,1000,[(12,24,22,36)])
        r=model.graph([a,b])
        self.assertEqual(len(r["associations"]),1)
        self.assertTrue(all(x["decision"]=="uncertain_temporal_evidence_only" for x in r["components"]))
        self.assertFalse(r["physical_channel_rooting_verified"])
if __name__=="__main__":unittest.main()
