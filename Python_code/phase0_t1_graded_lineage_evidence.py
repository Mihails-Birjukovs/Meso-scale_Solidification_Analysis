"""T1 v0.2 EXPLORATORY graded evidence for frozen component links.

Five terms remain distinct from physical plume truth:
  geom         = original T1 candidate geometric score [0,1],
  shape        = optimistic native-mask centroid-aligned IoU [0,1],
  motion       = 1/(1+median *candidate triplet* velocity jump ratio),
  channel      = hypothetical 2D not-positive path support; unknown otherwise,
  uniqueness   = 1/sqrt(competitive graph in-/out-degree product).

Weight vector is PREDECLARED and NOT trained; numbers are sensitivity
bookkeeping, not physical/posterior probabilities, segmentation accuracy or
evidence of a unique real track. A cue with unverified availability is
represented as an interval [0,1] of contribution, never reweighted to 1.

The spatially accepted mask decision is ALWAYS copied from the immutable
morphology field. Nothing here promotes a rejected magenta component,
suppresses a real plume, selects graph edges, or changes original masks.
"""
from __future__ import annotations
from dataclasses import dataclass
import math

SCHEMA="ga-in-T1-graded-evidence-not-probability/v0.2.0"
WEIGHTS={
    "geometry":0.10,
    "shape_optimistic":0.30,
    "triplet_motion_consistency":0.30,
    "channel_hypothesis":0.15,
    "graph_uniqueness":0.15,
}
assert abs(sum(WEIGHTS.values())-1)<1e-12
# These are PREDECLARED EXPLORATORY bins for audit, NEVER trained cutoffs.
LOW_DIAGNOSTIC_UPPER=0.35
HIGH_DIAGNOSTIC_LOWER=0.75
STATIONARY_PX_PER_S=0.5

def _unit(x,label):
    if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or x<0 or x>1:
        raise ValueError(label+" must be a finite 0..1 diagnostic")
    return float(x)

def _bool(x,label):
    if type(x) is not bool:raise ValueError(label+" must be Boolean")
    return x

def grade_candidate_link(*,geometry:float,shape_optimistic:float|None,
                         median_triplet_jump_ratio:float|None,
                         strong_root_a:bool|None,strong_root_b:bool|None,
                         broad_root_a:bool|None,broad_root_b:bool|None,
                         source_follow_candidates:int,dest_preced_candidates:int,
                         source_spatial_accepted:bool,dest_spatial_accepted:bool,
                         stationary_triplet_possible:bool=False)->dict:
    """Return audit support interval, absent cues and nonphysical review tier.

    Root status TRUE is a hypothetical 2D candidate channel. FALSE may mean
    the real channel was missed, so it is **unknown**, not evidence of true
    liquid disconnection. Stability across obstacle thresholds is required
    for stronger corroboration but does not certify real liquid.
    """
    geom=_unit(geometry,"geometry")
    if shape_optimistic is not None:shape=_unit(shape_optimistic,"shape")
    else:shape=None
    if median_triplet_jump_ratio is None:motion=None
    else:
        if (isinstance(median_triplet_jump_ratio,bool) or
            not isinstance(median_triplet_jump_ratio,(int,float)) or
            not math.isfinite(median_triplet_jump_ratio) or median_triplet_jump_ratio<0):
            raise ValueError("motion jump must be finite nonnegative ratio")
        motion=1/(1+float(median_triplet_jump_ratio))
    if (type(source_follow_candidates) is not int or type(dest_preced_candidates) is not int
        or source_follow_candidates<1 or dest_preced_candidates<1):
        raise ValueError("candidate graph degrees must be positive integers")
    for k,v in (
        ("source_spatial_accepted",source_spatial_accepted),
        ("dest_spatial_accepted",dest_spatial_accepted),
        ("stationary_triplet_possible",stationary_triplet_possible)):
        _bool(v,k)
    raw_roots=(strong_root_a,strong_root_b,broad_root_a,broad_root_b)
    if any(v is not None and type(v) is not bool for v in raw_roots):
        raise ValueError("channel states must be Boolean or missing")
    if all(v is not None for v in raw_roots):
        if broad_root_a and not strong_root_a:
            raise ValueError("broad-positive path must not be more connected than strong-positive path")
        if broad_root_b and not strong_root_b:
            raise ValueError("broad-positive path must not be more connected than strong-positive path")
    # Path absence is not physical evidence for non-liquid. For safety, unknown
    # provides only an interval; no automatic negative score.
    if all(v is not None for v in raw_roots) and broad_root_a and broad_root_b:
        channel=1.0
        channel_case="both_endpoints_supported_under_broad_and_strong_barriers"
    elif all(v is not None for v in raw_roots) and strong_root_a and strong_root_b:
        channel=0.5
        channel_case="both_endpoints_supported_only_under_strong_barrier"
    else:
        channel=None
        channel_case="unknown_phase_path_or_source_to_bulk_connectivity"
    uniqueness=1/math.sqrt(source_follow_candidates*dest_preced_candidates)
    parts={
        "geometry":geom,
        "shape_optimistic":shape,
        "triplet_motion_consistency":motion,
        "channel_hypothesis":channel,
        "graph_uniqueness":uniqueness,
    }
    lower=sum(WEIGHTS[k]*v for k,v in parts.items() if v is not None)
    missing=[k for k,v in parts.items() if v is None]
    upper=lower+sum(WEIGHTS[k] for k in missing)
    lower=min(1.,max(0.,lower))
    upper=min(1.,max(lower,upper))
    branch_ambiguous=(source_follow_candidates>1 or dest_preced_candidates>1)
    morphology_both=bool(source_spatial_accepted and dest_spatial_accepted)
    if not morphology_both:
        tier="SPATIALLY_EXCLUDED_FROM_ACCEPTED_LINEAGE"
    elif stationary_triplet_possible or branch_ambiguous:
        tier="ABSTAIN_COMPETING_BRANCH_OR_STATIONARY_COUNTEREXAMPLE"
    elif lower>=HIGH_DIAGNOSTIC_LOWER and not missing:
        tier="HIGH_CANDIDATE_CORROBORATION_NOT_PHYSICAL_TRUTH"
    elif upper<LOW_DIAGNOSTIC_UPPER:
        tier="LOW_CANDIDATE_CORROBORATION_NOT_PHYSICAL_FALSE"
    else:
        tier="ABSTAIN_UNCERTAIN_OR_MISSING_CUES"
    return {
        "schema":SCHEMA,
        "predeclared_weighted_support_lower":round(lower,9),
        "predeclared_weighted_support_upper":round(upper,9),
        "all_cues_available":not missing,
        "missing_cues":missing,
        "individual_diagnostic_cues":parts,
        "channel_case":channel_case,
        "degree_competition_source_follow":source_follow_candidates,
        "degree_competition_dest_preced":dest_preced_candidates,
        "middle_or_endpoint_stationarity_risk":stationary_triplet_possible,
        "branch_ambiguity":branch_ambiguous,
        "experimental_review_tier":tier,
        "original_morphology_retains_src":source_spatial_accepted,
        "original_morphology_retains_dst":dest_spatial_accepted,
        "retained_original_spatial_decisions_unmodified":True,
        "actual_plume_lineage_verified":False,
        "support_is_calibrated_probability":False,
        "original_candidate_edge_pruned":False,
    }

def summarize_graded_edges(records:list[dict])->dict:
    """Report source-block evidence coverage without claiming GT accuracy."""
    bins={}
    diag={"graded_edges":len(records),"morphology_both_edges":0,
          "with_all_cues":0,"missing_motion":0,"missing_shape":0,
          "missing_channel":0,"stationary_risk_edges":0,"branch_ambiguous_edges":0,
          "morphology_disagreement_edges":0,"source_original_edges_unchanged":True,
          "experimental_review_tiers":{}}
    for x in records:
        if not x["retained_original_spatial_decisions_unmodified"] or x["original_candidate_edge_pruned"]:
            raise ValueError("graded evidence attempted source modification")
        both=x["original_morphology_retains_src"] and x["original_morphology_retains_dst"]
        diag["morphology_both_edges"]+=both
        diag["with_all_cues"]+=x["all_cues_available"]
        for field,word in (("triplet_motion_consistency","missing_motion"),
                           ("shape_optimistic","missing_shape"),
                           ("channel_hypothesis","missing_channel")):
            diag[word]+=field in x["missing_cues"]
        diag["stationary_risk_edges"]+=x["middle_or_endpoint_stationarity_risk"]
        diag["branch_ambiguous_edges"]+=x["branch_ambiguity"]
        diag["morphology_disagreement_edges"]+=not both
        tier=x["experimental_review_tier"]
        bins[tier]=bins.get(tier,0)+1
    diag["experimental_review_tiers"]=bins
    return {"schema":SCHEMA,"status":"UNSUPERVISED_DIAGNOSTIC_COVERAGE_NO_PHYSICAL_ACCURACY",**diag}
