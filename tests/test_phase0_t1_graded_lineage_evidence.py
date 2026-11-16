"""No physical truth or mask changes: graded diagnostic contracts."""
import importlib.util,sys,unittest
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"Python_code"/"phase0_t1_graded_lineage_evidence.py"
spec=importlib.util.spec_from_file_location("t1_graded_science",p)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
BASE=dict(
 geometry=.8,shape_optimistic=.8,median_triplet_jump_ratio=.2,
 strong_root_a=True,strong_root_b=True,
 broad_root_a=True,broad_root_b=True,
 source_follow_candidates=1,dest_preced_candidates=1,
 source_spatial_accepted=True,dest_spatial_accepted=True,
 stationary_triplet_possible=False
)
class GradedEvidenceTests(unittest.TestCase):
 def grade(self,**kw):return m.grade_candidate_link(**dict(BASE,**kw))
 def test_all_five_cues_are_present_and_bounded(self):
  r=self.grade()
  self.assertTrue(r["all_cues_available"])
  self.assertEqual(r["missing_cues"],[])
  self.assertTrue(0<=r["predeclared_weighted_support_lower"]<=1)
  self.assertEqual(r["predeclared_weighted_support_lower"],r["predeclared_weighted_support_upper"])
  self.assertFalse(r["support_is_calibrated_probability"])
 def test_missing_motion_widens_not_reweights(self):
  full=self.grade()
  r=self.grade(median_triplet_jump_ratio=None)
  self.assertAlmostEqual(r["predeclared_weighted_support_upper"]-r["predeclared_weighted_support_lower"],.3)
  self.assertLess(r["predeclared_weighted_support_lower"],full["predeclared_weighted_support_lower"])
  self.assertIn("triplet_motion_consistency",r["missing_cues"])
 def test_missing_shape_widens_interval(self):
  r=self.grade(shape_optimistic=None)
  self.assertAlmostEqual(r["predeclared_weighted_support_upper"]-r["predeclared_weighted_support_lower"],.3)
 def test_no_channel_path_cannot_be_used_as_true_negative(self):
  r=self.grade(strong_root_a=False,strong_root_b=False,broad_root_a=False,broad_root_b=False)
  self.assertIn("channel_hypothesis",r["missing_cues"])
  self.assertEqual(r["channel_case"],"unknown_phase_path_or_source_to_bulk_connectivity")
 def test_strong_only_path_weaker_than_stable_path_hypothesis(self):
  s=self.grade(broad_root_a=False,broad_root_b=False)
  b=self.grade()
  self.assertAlmostEqual(b["predeclared_weighted_support_lower"]-s["predeclared_weighted_support_lower"],.075)
 def test_broad_path_cannot_exceed_strong(self):
  with self.assertRaises(ValueError):
   self.grade(strong_root_a=False,broad_root_a=True)
 def test_spatial_user_rejection_never_promoted(self):
  r=self.grade(source_spatial_accepted=False)
  self.assertEqual(r["experimental_review_tier"],"SPATIALLY_EXCLUDED_FROM_ACCEPTED_LINEAGE")
  self.assertFalse(r["original_morphology_retains_src"])
  self.assertTrue(r["retained_original_spatial_decisions_unmodified"])
  self.assertFalse(r["original_candidate_edge_pruned"])
 def test_hard_graph_branch_ambiguity_forces_abstention(self):
  r=self.grade(source_follow_candidates=3)
  self.assertTrue(r["branch_ambiguity"])
  self.assertTrue(r["experimental_review_tier"].startswith("ABSTAIN"))
 def test_stationary_artifact_prevents_automatic_qualifier(self):
  r=self.grade(geometry=1.,shape_optimistic=1.,
   median_triplet_jump_ratio=0.,stationary_triplet_possible=True)
  self.assertTrue(r["experimental_review_tier"].startswith("ABSTAIN"))
 def test_negative_and_nonfinite_cues_refused(self):
  for kw in (dict(geometry=-.1),dict(shape_optimistic=1.1),
             dict(median_triplet_jump_ratio=float("nan")),
             dict(median_triplet_jump_ratio=-1),
             dict(dest_preced_candidates=0),
             dict(strong_root_a=1)):
   with self.assertRaises(ValueError):
    self.grade(**kw)
 def test_interval_calibration_never_claimed(self):
  r=self.grade()
  self.assertIn("not",r["experimental_review_tier"].lower())
  self.assertFalse(r["actual_plume_lineage_verified"])
 def test_aggregate_preserves_edge_decisions(self):
  x=self.grade()
  y=self.grade(source_spatial_accepted=False,median_triplet_jump_ratio=None)
  r=m.summarize_graded_edges([x,y])
  self.assertEqual(r["graded_edges"],2)
  self.assertEqual(r["morphology_both_edges"],1)
  self.assertEqual(r["with_all_cues"],1)
  self.assertEqual(r["missing_motion"],1)
  self.assertEqual(r["morphology_disagreement_edges"],1)
  self.assertTrue(r["source_original_edges_unchanged"])
 def test_missing_path_state_abstains_on_channel(self):
  r=self.grade(strong_root_a=None,broad_root_a=None)
  self.assertIn("channel_hypothesis",r["missing_cues"])
 def test_no_mutation_of_input_payload(self):
  kwargs=BASE.copy()
  self.grade(**{})
  self.assertEqual(kwargs,BASE)
if __name__=="__main__":unittest.main()
