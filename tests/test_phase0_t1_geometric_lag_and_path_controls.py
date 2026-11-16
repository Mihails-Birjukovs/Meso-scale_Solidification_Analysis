"""T1 lagged coincidence and 2D candidate path-label controls.

Synthetic only. An admissible lag>1 geometry match must NEVER be reported as
an actual T1 source-adjacent association, or as a measured false positive.
"""
import importlib.util
import math
import sys
import unittest
from pathlib import Path

P=Path(__file__).resolve().parents[1]/"Python_code"/"phase0_t1_geometric_lag_and_path_controls.py"
spec=importlib.util.spec_from_file_location("t1_lagged_geometry",P)
m=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=m
spec.loader.exec_module(m)

def node(t,y=40,x=40,area=100,elong=2,group=1,role="main",ms=None,uid=None):
    return {"uid":uid or f"{role}:{t}:1","ordinal":t,"time_ms":t*1000 if ms is None else ms,
     "group":group,"role":role,"centroid_y":float(y),"centroid_x":float(x),
     "area":area,"elongation":float(elong)}

class LagControlsTests(unittest.TestCase):
    def test_unchanged_geometry_score_formula(self):
        a=node(0,y=50,x=50,area=100,elong=2)
        b=node(1,y=50,x=65,area=200,elong=1)
        got=m.geometric_compatibility(a,b)
        expected=math.exp(-.5*(15/30)**2)*.5**.5*.5**.25
        self.assertAlmostEqual(got,expected,places=13)

    def test_source_1001ms_rounding_preserved(self):
        a=node(0,ms=0)
        b=node(1,x=70.02,ms=1001)
        self.assertIsNotNone(m.geometric_compatibility(a,b,effective_interval_ms=1001))
        self.assertIsNone(m.geometric_compatibility(a,b,effective_interval_ms=1000))
        z=m.lagged_frame_challenge({0:[a],1:[b]},lags=(1,))
        self.assertEqual(z["lag_results"]["1"]["geometrically_admissible_pairs"],1)

    def test_historical_group_and_recording_no_crosslink(self):
        with self.assertRaises(ValueError):
            m.geometric_compatibility(node(0),node(1,group=2))
        with self.assertRaises(ValueError):
            m.geometric_compatibility(node(0),node(1,role="end"))
        got=m.lagged_frame_challenge({0:[node(0)],1:[node(1,group=2)]},lags=(1,))
        self.assertEqual(got["lag_results"]["1"]["geometrically_admissible_pairs"],0)
        self.assertEqual(got["lag_results"]["1"]["source_discontinuity_skipped_pairs"],1)

    def test_lagged_stationary_defect_does_not_prove_real_track(self):
        obs={i:[node(i,y=10,x=30)] for i in range(6)}
        result=m.lagged_frame_challenge(obs,lags=(1,3,5,))
        for lag in (1,3,5):
            z=result["lag_results"][str(lag)]
            self.assertEqual(z["admissible_fraction"],1.0)
        self.assertEqual(result["lag_results"]["5"]["status"],
             "COUNTERFACTUAL_GEOMETRIC_COINCIDENCE_NOT_TRACK")

    def test_source_gap_discontinuity(self):
        obs={0:[node(0)],1:[node(1,group=2)],2:[node(2,group=1)]}
        r=m.lagged_frame_challenge(obs,lags=(2,))
        self.assertEqual(r["lag_results"]["2"]["source_discontinuity_skipped_pairs"],1)

    def test_lag_refuses_invalid_clock(self):
        a=node(0,ms=1000);b=node(1,ms=3000)
        r=m.lagged_frame_challenge({0:[a],1:[b]},lags=(1,))
        self.assertEqual(r["lag_results"]["1"]["geometrically_admissible_pairs"],0)
        self.assertEqual(r["lag_results"]["1"]["source_discontinuity_skipped_pairs"],1)

    def test_area_and_displacement_gates(self):
        a=node(0)
        self.assertIsNone(m.geometric_compatibility(a,node(1,x=200)))
        self.assertIsNone(m.geometric_compatibility(a,node(1,area=900)))
        with self.assertRaises(ValueError):
            m.geometric_compatibility(a,node(1,area=0))
        with self.assertRaises(ValueError):
            m.geometric_compatibility(a,node(1,x=float("nan")))
        with self.assertRaises(ValueError):
            m.geometric_compatibility(a,node(1),effective_interval_ms=0)

    def test_duplicate_lags_refused(self):
        with self.assertRaises(ValueError):
            m.lagged_frame_challenge({0:[node(0)]},lags=(1,1))

    def test_path_switch_counts_are_diagnostic_only(self):
        nodes={
         "a":{"strong_r1":True,"spatial_supported":True},
         "b":{"strong_r1":False,"spatial_supported":True},
         "c":{"strong_r1":False,"spatial_supported":False},
        }
        edges=[{"src":"a","dst":"b"},{"src":"b","dst":"c"},{"src":"a","dst":"c"}]
        r=m.path_transition_diagnostics(edges,nodes,"strong_r1")
        self.assertEqual(r["total_edges"],3)
        self.assertEqual(r["both_rooted"],0)
        self.assertEqual(r["src_only_rooted"],2)
        self.assertEqual(r["neither_rooted"],1)
        self.assertEqual(r["spatial_both_edges"],1)
        self.assertEqual(r["spatial_both_root_switches"],1)
        self.assertAlmostEqual(r["candidate_root_switch_fraction"],2/3)
        self.assertTrue(r["production_mask_modified"] is False)

    def test_path_refuses_unknown_uid_and_nonbool(self):
        with self.assertRaises(ValueError):
            m.path_transition_diagnostics([{"src":"missing","dst":"b"}],
               {"b":{"strong_r1":True,"spatial_supported":True}},"strong_r1")
        with self.assertRaises(ValueError):
            m.path_transition_diagnostics([{"src":"a","dst":"b"}],{
              "a":{"strong_r1":"yes","spatial_supported":True},
              "b":{"strong_r1":True,"spatial_supported":True}},"strong_r1")

    def test_no_input_mutation(self):
        a=node(0);b=node(1)
        fields_a=a.copy();fields_b=b.copy()
        m.geometric_compatibility(a,b)
        m.lagged_frame_challenge({0:[a],1:[b]},lags=(1,))
        self.assertEqual(a,fields_a);self.assertEqual(b,fields_b)

if __name__=="__main__":
    unittest.main()
