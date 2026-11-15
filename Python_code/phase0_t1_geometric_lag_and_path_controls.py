"""Frozen T1 geometric lag challenge / path-label transition diagnostics.

This module produces NO plume trajectories, physical phase labels, actual
false-positive rates, calibrated probabilities, or modified source masks.
A virtual time interval applied to a nonadjacent pair is explicitly a
counterfactual *geometric coincidence test*, never an accepted T1 link.

Inputs are public-shaped component dictionaries from the original detector
T1 v0.1 graph. No raw TIFFs, external 2WCF data or private paths required.
"""
from __future__ import annotations
import math

SCHEMA="ga-in-t1-geometry-counterfactual-and-path-switch/v0.1.0"
DEFAULT_LAGS=(1,3,5,10,25)

def geometric_compatibility(a:dict,b:dict,*,effective_interval_ms:int=1000,
                            max_step_px:float=30.,max_area_ratio:float=8.)->float|None:
    """Apply v0.1 T1 centroid, area, elongation gates; return score or None.

    Ignore original ordinals intentionally; the calling challenge must
    label lag>1 as counterfactual rather than actual association.
    Physical group/recording guard is mandatory. No frame or node mutation.
    """
    if a["role"]!=b["role"] or a["group"]!=b["group"]:
        raise ValueError("cross-acquisition or cross-group pair not comparable")
    if not isinstance(effective_interval_ms,int) or not 0<effective_interval_ms<=1500:
        raise ValueError("virtual source interval must be 1..1500 ms")
    if not math.isfinite(max_step_px) or max_step_px<=0 or not math.isfinite(max_area_ratio) or max_area_ratio<1:
        raise ValueError("invalid geometric gate")
    if b["ordinal"]<=a["ordinal"]:
        raise ValueError("counterfactual must be forward in source ordinal")
    area_a=float(a["area"]);area_b=float(b["area"])
    elong_a=float(a["elongation"]);elong_b=float(b["elongation"])
    coords=[float(a["centroid_y"]),float(a["centroid_x"]),
            float(b["centroid_y"]),float(b["centroid_x"])]
    if any(not math.isfinite(z) for z in (area_a,area_b,elong_a,elong_b,*coords)):
        raise ValueError("nonfinite source geometry")
    if min(area_a,area_b,elong_a,elong_b)<=0:
        raise ValueError("invalid positive geometry")
    scale=min(1.5,max(.3,effective_interval_ms/1000.))
    dist=math.hypot(coords[2]-coords[0],coords[3]-coords[1])
    if dist>max_step_px*scale:return None
    area_ratio=max(area_a,area_b)/min(area_a,area_b)
    if area_ratio>max_area_ratio:return None
    area_similarity=min(area_a,area_b)/max(area_a,area_b)
    shape_similarity=min(elong_a,elong_b)/max(elong_a,elong_b)
    return math.exp(-.5*(dist/(max_step_px*scale))**2)*area_similarity**.5*shape_similarity**.25

def lagged_frame_challenge(byframe:dict[int,list[dict]],*,lags:tuple[int,...]=DEFAULT_LAGS,
                           strict_source_clock:bool=True)->dict:
    """Compare geometric coincidence across source frames without T1 linking.

    Normalizations matter: pairs of distant frames have a smaller observation
    horizon. Lags cannot cross a genuine source group/time discontinuity. For
    lag=1 exact source candidate time increments are used, including 1001 ms.
    For lag>1 virtual 1000 ms IS A CONTROL, not elapsed experimental time.
    """
    if not byframe:raise ValueError("no source components")
    if len(set(lags))!=len(lags) or any(type(lag) is not int or lag<1 for lag in lags):
        raise ValueError("invalid lag list")
    frames={int(i):nodes for i,nodes in byframe.items()}
    summary={}
    for lag in lags:
        total=0;potential=0;high=0;very=0;nonempty=0;skipped=0
        for i in sorted(frames):
            if i+lag not in frames:continue
            a=frames[i];b=frames[i+lag]
            if not a or not b:continue
            if any(x["ordinal"]!=i for x in a) or any(x["ordinal"]!=i+lag for x in b):
                raise ValueError("input component source-ordinal mismatch")
            if len({(x["role"],x["group"]) for x in a+b})!=1:
                skipped+=1;continue
            # Refuse counterfactual comparisons when any intermediate frame has
            # a declared group change. Data can be sparse; original group
            # certification beyond known end-points belongs to source manifest.
            groups=[frames.get(k,[]) for k in range(i,i+lag+1)]
            if any(y and (y[0]["role"],y[0]["group"])!=(a[0]["role"],a[0]["group"]) for y in groups):
                skipped+=1;continue
            dt=b[0]["time_ms"]-a[0]["time_ms"]
            if lag==1 and strict_source_clock:
                if dt<=0 or dt>1500:skipped+=1;continue
                effective=round(dt)
            else:effective=1000
            potential+=len(a)*len(b);nonempty+=1
            for x in a:
                for y in b:
                    v=geometric_compatibility(x,y,effective_interval_ms=effective)
                    if v is None:continue
                    total+=1;high+=v>=.7;very+=v>=.9
        summary[str(lag)]={
            "source_frame_separation":lag,
            "status":"ADJACENT_GEOMETRIC_REPLAY" if lag==1 else "COUNTERFACTUAL_GEOMETRIC_COINCIDENCE_NOT_TRACK",
            "nonempty_frame_pairs":nonempty,
            "source_discontinuity_skipped_pairs":skipped,
            "component_pair_opportunities":potential,
            "geometrically_admissible_pairs":total,
            "score_ge_0p7":high,"score_ge_0p9":very,
            "admissible_fraction":total/potential if potential else None,
            "admissible_per_nonempty_frame_pair":total/nonempty if nonempty else None,
        }
    return {"schema":SCHEMA,
            "status":"CONTROL_DIAGNOSTICS_NOT_PHYSICAL_LABELS_OR_FALSE_LINK_RATES",
            "lag_results":summary}

def path_transition_diagnostics(edges:list[dict],per_node:dict[str,dict],path_state:str)->dict:
    """Count source-to-destination candidate path-state changes, without edits."""
    counts={"total_edges":0,"both_rooted":0,"src_only_rooted":0,
            "dst_only_rooted":0,"neither_rooted":0,
            "spatial_both_edges":0,"spatial_both_root_switches":0}
    for e in edges:
        a=per_node.get(e["src"]);b=per_node.get(e["dst"])
        if a is None or b is None:raise ValueError("unknown original T1 node UID")
        if path_state not in a or path_state not in b:
            raise ValueError("missing tentative path state")
        if not isinstance(a[path_state],bool) or not isinstance(b[path_state],bool):
            raise ValueError("path state must be a Boolean hypothesis")
        A=a[path_state];B=b[path_state]
        counts["total_edges"]+=1
        counts[("both_rooted" if A and B else "src_only_rooted" if A else
                "dst_only_rooted" if B else "neither_rooted")]+=1
        if a["spatial_supported"] and b["spatial_supported"]:
            counts["spatial_both_edges"]+=1
            counts["spatial_both_root_switches"]+=A!=B
    denom=counts["total_edges"]
    return {"schema":SCHEMA,
      "path_state":path_state,**counts,
      "candidate_root_switch_fraction":(counts["src_only_rooted"]+counts["dst_only_rooted"])/denom if denom else None,
      "spatially_retained_candidate_root_switch_fraction":counts["spatial_both_root_switches"]/counts["spatial_both_edges"] if counts["spatial_both_edges"] else None,
      "interpretation":"framewise candidate traversable-path evidence may change; never infer true liquid-channel reconnection",
      "production_mask_modified":False}
