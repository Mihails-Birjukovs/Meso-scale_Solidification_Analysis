"""Synthetic preregistered T1 cue-weight sensitivity tests (no source data)."""
import unittest
from Python_code import phase0_t1_graded_lineage_evidence as base
from Python_code import phase0_t1_weight_grid_sensitivity as sensitivity

def sample(**updates):
 d=dict(geometry=.85,shape_optimistic=.9,median_triplet_jump_ratio=.05,
        strong_root_a=True,strong_root_b=True,broad_root_a=True,broad_root_b=True,
        source_follow_candidates=1,dest_preced_candidates=1,
        source_spatial_accepted=True,dest_spatial_accepted=True,
        stationary_triplet_possible=False)
 d.update(updates)
 return base.grade_candidate_link(**d)

class WeightGridTests(unittest.TestCase):
 def test_frozen_reference_grid(self):
  self.assertEqual(sensitivity.GRID["reference"],base.WEIGHTS)
  self.assertEqual(len(sensitivity.GRID),11)
  for weights in sensitivity.GRID.values():
   self.assertAlmostEqual(sum(weights.values()),1)
 def test_no_retraining_or_renormalization_of_missing_cue(self):
  g=sample(median_triplet_jump_ratio=None)
  reference=sensitivity.rescore(g,sensitivity.GRID["reference"])
  self.assertIn("triplet_motion_consistency",reference["positive_weight_missing_cues"])
  self.assertAlmostEqual(reference["score_upper"]-reference["score_lower"],.30)
 def test_baseline_exact_score_reproduced(self):
  g=sample()
  q=sensitivity.rescore(g,sensitivity.GRID["reference"])
  self.assertEqual(q["score_lower"],g["predeclared_weighted_support_lower"])
  self.assertEqual(q["score_upper"],g["predeclared_weighted_support_upper"])
 def test_omitted_cue_its_missingness_is_not_a_failure(self):
  g=sample(median_triplet_jump_ratio=None)
  q=sensitivity.rescore(g,sensitivity.GRID["omit_triplet_motion_consistency"])
  self.assertNotIn("triplet_motion_consistency",q["positive_weight_missing_cues"])
  self.assertEqual(q["score_lower"],q["score_upper"])
 def test_spatial_source_rejection_never_promoted(self):
  g=sample(source_spatial_accepted=False)
  for val in sensitivity.grid_scores(g).values():
   self.assertFalse(val["heuristic_high_corroboration"])
   self.assertFalse(val["source_morphology_decisions_changed"])
 def test_stationarity_and_competing_lineage_still_abstain(self):
  for g in (sample(stationary_triplet_possible=True),sample(source_follow_candidates=2)):
   for val in sensitivity.grid_scores(g).values():
    self.assertTrue(val["safety_abstention_competing_branch_or_stationary"])
    self.assertFalse(val["heuristic_high_corroboration"])
 def test_calibration_claim_always_false(self):
  r=sensitivity.grid_scores(sample())
  self.assertTrue(all(not q["probabilistically_calibrated"] for q in r.values()))
 def test_invalid_weight_grid_refused(self):
  with self.assertRaises(ValueError):sensitivity.normalize({"geometry":.4})
  with self.assertRaises(ValueError):sensitivity.normalize(dict(base.WEIGHTS,geometry=-1))
  with self.assertRaises(ValueError):sensitivity.normalize({k:0 for k in base.WEIGHTS})
 def test_score_bounds_every_weight(self):
  for g in (sample(),sample(strong_root_a=False,strong_root_b=False,
                      broad_root_a=False,broad_root_b=False),
            sample(shape_optimistic=None,median_triplet_jump_ratio=None)):
   for x in sensitivity.grid_scores(g).values():
    self.assertTrue(0<=x["score_lower"]<=x["score_upper"]<=1+1e-10)
if __name__=="__main__":unittest.main()
