"""T1 grading sensitivity grids: no scientific optimization or plume truth.

All weights are PREDECLARED and normalized BEFORE reading full-source
private edge evidence. Fitted or accuracy-optimized weights are forbidden
in this stage. A high-corroboration flag is a heuristic reviewer priority,
not a physically accepted trajectory or a calibrated probability.
"""
from __future__ import annotations
import math
from . import phase0_t1_graded_lineage_evidence as original

SCHEMA="ga-in-t1-grading-weight-sensitivity/v0.1.0"
CUES=tuple(original.WEIGHTS)
REFERENCE=dict(original.WEIGHTS)

def normalize(weights:dict)->dict:
    if set(weights)!=set(CUES):
        raise ValueError("weights must contain all original diagnostic cues")
    if any(type(v) not in (int,float) or not math.isfinite(v) or v<0 for v in weights.values()):
        raise ValueError("weights must be nonnegative finite numbers")
    total=sum(weights.values())
    if total<=0:raise ValueError("at least one weight must be positive")
    return {k:round(weights[k]/total,12) for k in CUES}

def drop(name:str)->dict:
    if name not in CUES:raise ValueError("unknown cue")
    return normalize({k:REFERENCE[k] if k!=name else 0. for k in CUES})

GRID={
    "reference":normalize(REFERENCE),
    **{"omit_"+k:drop(k) for k in CUES},
    "uniform":normalize({k:.2 for k in CUES}),
    "shape_heavy":normalize(dict(geometry=.05,shape_optimistic=.45,
        triplet_motion_consistency=.20,channel_hypothesis=.15,graph_uniqueness=.15)),
    "motion_heavy":normalize(dict(geometry=.05,shape_optimistic=.20,
        triplet_motion_consistency=.45,channel_hypothesis=.15,graph_uniqueness=.15)),
    "channel_heavy":normalize(dict(geometry=.05,shape_optimistic=.25,
        triplet_motion_consistency=.20,channel_hypothesis=.35,graph_uniqueness=.15)),
    "uniqueness_heavy":normalize(dict(geometry=.05,shape_optimistic=.25,
        triplet_motion_consistency=.25,channel_hypothesis=.15,graph_uniqueness=.30))
}
assert len(GRID)==11
assert GRID["reference"]==REFERENCE

def rescore(graded:dict,weights:dict)->dict:
    """Rank sensitivity only. Never changes source morphology/edges."""
    w=normalize(weights)
    if not graded["retained_original_spatial_decisions_unmodified"] or graded["original_candidate_edge_pruned"]:
        raise ValueError("input violates immutable source baseline")
    cues=graded["individual_diagnostic_cues"]
    if set(cues)!=set(CUES):raise ValueError("source cue set mismatch")
    for key,value in cues.items():
        if value is not None and (type(value) not in (float,int) or not math.isfinite(value) or not 0<=value<=1):
            raise ValueError("invalid source cue")
    lower=sum(w[k]*cues[k] for k in CUES if cues[k] is not None)
    unknown=sum(w[k] for k in CUES if cues[k] is None)
    missing=[k for k in CUES if cues[k] is None and w[k]>0]
    both=graded["original_morphology_retains_src"] and graded["original_morphology_retains_dst"]
    safety=bool(graded["branch_ambiguity"] or graded["middle_or_endpoint_stationarity_risk"])
    high=bool(both and not safety and not missing and lower>=original.HIGH_DIAGNOSTIC_LOWER)
    return {
       "schema":SCHEMA,
       "score_lower":round(lower,9),
       "score_upper":round(min(1.,lower+unknown),9),
       "positive_weight_missing_cues":missing,
       "both_spatial_baseline_retained":bool(both),
       "requires_expert_plume_identity":True,
       "safety_abstention_competing_branch_or_stationary":safety,
       "heuristic_high_corroboration":high,
       "source_morphology_decisions_changed":False,
       "probabilistically_calibrated":False
    }

def grid_scores(record:dict)->dict:
    return {name:rescore(record,weights) for name,weights in GRID.items()}
