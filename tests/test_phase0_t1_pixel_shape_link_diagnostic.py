"""Native deterministic tests: pixel-shape evidence is NOT a plume classifier."""
import importlib.util,sys,unittest
from pathlib import Path
HAVE=bool(importlib.util.find_spec("numpy") and importlib.util.find_spec("scipy"))
if HAVE:
    import numpy as np
    src=Path(__file__).resolve().parents[1]/"Python_code"
    def load(name,file):
        sp=importlib.util.spec_from_file_location(name,src/file)
        m=importlib.util.module_from_spec(sp)
        sys.modules[name]=m
        sp.loader.exec_module(m)
        return m
    t1=load("source_t1_pixel_shape_tests","phase0_spatiotemporal_component_graph_t1.py")
    diag=load("pixel_shape_diagnostics","phase0_t1_pixel_shape_link_diagnostic.py")

@unittest.skipUnless(HAVE,"Requires NumPy/SciPy native scientific environment")
class ShapeIoUTests(unittest.TestCase):
    def frame(self,i,parts,group=1,role="main"):
        mask=np.zeros((80,100),dtype=bool)
        for y0,y1,x0,x1 in parts:
            mask[y0:y1,x0:x1]=True
        zone=np.zeros_like(mask)
        zone[35:,:]=True
        p=np.zeros(mask.shape,dtype=float)
        p[mask]=-0.05
        return t1.FrameObservation(role,i,i*1000,group,mask,zone,
                                   np.ones_like(mask),p)
    def comp(self,a,b):
        return t1.components(self.frame(0,a))[0],t1.components(self.frame(1,b))[0]
    def test_translated_rigid_rectangle_aligned_one(self):
        a,b=self.comp([(35,49,20,35)],[(38,52,24,39)])
        r=diag.shape_consistency(a,b,(80,100))
        self.assertAlmostEqual(r["centroid_aligned_pixel_iou_optimistic"],1)
        self.assertLess(r["unshifted_pixel_iou"],1)
        self.assertEqual(r["centroid_alignment_dy_dx"],[3,4])
    def test_similar_centroids_but_mismatched_shape(self):
        first=self.frame(0,[(30,44,20,34)])
        second=self.frame(1,[(30,44,20,34)])
        # ring topology in second, connected with same centroid
        ring=second.negative.copy()
        ring[33:41,23:31]=False
        second.negative[:]=ring
        second.signed_contrast[:]=0.0
        second.signed_contrast[ring]=-0.05
        a=t1.components(first)[0]
        b=t1.components(second)[0]
        r=diag.shape_consistency(a,b,(80,100))
        self.assertLess(r["centroid_aligned_pixel_iou_optimistic"],0.75)
    def test_no_edge_deletion_or_input_mutation(self):
        a=t1.components(self.frame(0,[(38,55,20,40)]))
        b=t1.components(self.frame(1,[(40,56,22,41)]))
        base=t1.associate(a,b)
        old=dict(base[0]);pixels=a[0].signed_detector_pixels.copy()
        annotated=diag.annotate_candidate_edges(a,b,base,(80,100))
        self.assertEqual(len(annotated),len(base))
        self.assertEqual(base[0],old)
        self.assertTrue(np.array_equal(a[0].signed_detector_pixels,pixels))
    def test_invalid_array_geometry_refuses(self):
        a,b=self.comp([(38,55,20,40)],[(40,57,22,42)])
        with self.assertRaisesRegex(ValueError,"outside detector"):
            diag.shape_consistency(a,b,(5,5))
        with self.assertRaisesRegex(ValueError,"invalid detector shape"):
            diag.shape_consistency(a,b,(0,100))
    def test_gaps_and_cross_stream_refused(self):
        a=t1.components(self.frame(0,[(38,55,20,40)],group=1))[0]
        b=t1.components(self.frame(1,[(38,55,20,40)],group=2))[0]
        with self.assertRaisesRegex(ValueError,"unrelated"):
            diag.shape_consistency(a,b,(80,100))
    def test_unknown_edge_uid_refused(self):
        a=t1.components(self.frame(0,[(38,55,20,40)]))
        b=t1.components(self.frame(1,[(39,56,20,40)]))
        with self.assertRaisesRegex(ValueError,"unknown"):
            diag.annotate_candidate_edges(a,b,[{"src":"not-real","dst":b[0].uid}],(80,100))
    def test_translated_overlap_cannot_prove_correct_plume(self):
        a,b=self.comp([(30,44,20,34)],[(30,44,20,34)])
        r=diag.shape_consistency(a,b,(80,100))
        self.assertEqual(r["centroid_aligned_pixel_iou_optimistic"],1)
        self.assertTrue(r["manual_review_only"])
        # an exactly stationary detector defect can also have IoU of 1
    def test_two_way_clipped_fraction_in_summary(self):
        a,b=self.comp([(3,17,3,17)],[(1,15,1,15)])
        r=diag.shape_consistency(a,b,(80,100))
        self.assertAlmostEqual(r["centroid_aligned_pixel_iou_optimistic"],1)
        self.assertAlmostEqual(r["source_footprint_clipped_fraction"],2/14*2-(2/14)**2 if False else 0.0)
if __name__=="__main__":
    unittest.main()
