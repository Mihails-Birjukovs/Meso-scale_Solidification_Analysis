"""Experimental source-pixel LIQUID-LIKE corridor graph (not phase truth).

Construct candidate *unblocked* corridors between a tentative upper-bulk seed
and regions below a previously estimated front. Positive log-contrast masks
are used ONLY as tentative obstacles; complement-of-positive is NOT proven
liquid metal. This module never overrides owner-reviewed negative masks.

One connected traversable zone is equivalent to a flood fill in a 4-neighbor
source-detector pixel graph. This is not the historical v25 liquid-channel
segmentation, a chemically verified Ga-rich phase, or a true 3-D metal path.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from scipy import ndimage as ndi

SCHEMA="ga-in-t1-tentative-liquid-corridor/v0.1"
DEFAULT_ROI=(120,412,155,690)

def disk(radius:int)->np.ndarray:
    if not isinstance(radius,int) or not 0<=radius<=8:
        raise ValueError("invalid neck/opening radius")
    if radius==0:return np.array([[True]])
    yy,xx=np.ogrid[-radius:radius+1,-radius:radius+1]
    return xx**2+yy**2<=radius**2

@dataclass
class Corridor:
    source_bulk_connected:np.ndarray
    potential_traversable:np.ndarray
    upper_bulk_seeds:np.ndarray
    below_front_connected:np.ndarray
    metadata:dict

def candidate_corridor(
    positive_obstacles:np.ndarray,
    valid:np.ndarray,
    front_y:np.ndarray|None,
    *,
    roi:tuple[int,int,int,int]=DEFAULT_ROI,
    neck_radius:int=1,
    source_bulk_band:int=12,
    above_front_clearance:int=3,
)->Corridor:
    """4-connected flood from tentative detector-ROI top, no physical labels.

    Thin passages are challenged with binary opening of *traversable*
    pixels. With radius=0 the original candidate paths are unaltered.
    Padding is NOT applied; border-aware rejection must be reported.
    """
    pos=np.asarray(positive_obstacles,dtype=bool)
    valid=np.asarray(valid,dtype=bool)
    if pos.ndim!=2 or pos.shape!=valid.shape:
        raise ValueError("detector shape/validity mismatch")
    if np.any(pos&~valid):
        raise ValueError("positive candidate includes invalid detector pixels")
    y0,y1,x0,x1=roi
    if not (0<=y0<y1<=pos.shape[0] and 0<=x0<x1<=pos.shape[1]):
        raise ValueError("unapproved ROI outside detector")
    if not (3<=source_bulk_band<=40 and 0<=above_front_clearance<=20):
        raise ValueError("invalid seed/clearance parameters")
    if front_y is None:
        z=np.zeros_like(pos,bool)
        return Corridor(z.copy(),z.copy(),z.copy(),z.copy(),{
            "schema":SCHEMA,"status":"NO_FRONT_NO_TOPOLOGICAL_CLAIM",
            "reason":"Provisional front unavailable",
            "physical_bulk_connection_verified":False})
    front=np.asarray(front_y,dtype=float)
    if front.shape!=(x1-x0,) or not np.isfinite(front).all():
        raise ValueError("front original-column geometry mismatch")
    if np.any(front<y0) or np.any(front>=y1):
        raise ValueError("front outside candidate source rectangle")
    if neck_radius<0 or neck_radius>8:
        raise ValueError("unapproved opening radius")
    original=np.zeros_like(pos,bool)
    original[y0:y1,x0:x1]=valid[y0:y1,x0:x1]&~pos[y0:y1,x0:x1]
    if neck_radius:
        cropped=original[y0:y1,x0:x1]
        opened=ndi.binary_opening(cropped,structure=disk(neck_radius),border_value=0)
        traversable=np.zeros_like(original)
        traversable[y0:y1,x0:x1]=opened
    else:
        traversable=original.copy()
    yy=np.arange(y0,y1)[:,None]
    # The initial band is only a hypothesis of upper bulk-liquid presence.
    band=np.zeros_like(original,bool)
    band[y0:min(y1,y0+source_bulk_band),x0:x1]=True
    above=np.zeros_like(original,bool)
    above[y0:y1,x0:x1]=(yy<front[None,:]-above_front_clearance)
    seeds=band&above&traversable
    labels,n=ndi.label(traversable,structure=ndi.generate_binary_structure(2,1))
    label_ids=np.unique(labels[seeds])
    label_ids=label_ids[label_ids>0]
    connected=np.isin(labels,label_ids)&traversable
    below=np.zeros_like(original)
    below[y0:y1,x0:x1]=(yy>=front[None,:])
    under=connected&below
    return Corridor(connected,traversable,seeds,under,{
       "schema":SCHEMA,"status":"UNVERIFIED_2D_CANDIDATE_UNBLOCKED_CORRIDOR",
       "roi_y0_y1_x0_x1":[y0,y1,x0,x1],
       "neck_radius_px":neck_radius,
       "source_bulk_band_px":source_bulk_band,
       "above_front_clearance_px":above_front_clearance,
       "candidate_obstacle_positive_px":int(pos[y0:y1,x0:x1].sum()),
       "traversable_pixels":int(traversable.sum()),
       "seed_pixels":int(seeds.sum()),
       "bulk_connected_candidate_pixels":int(connected.sum()),
       "below_front_connected_pixels":int(under.sum()),
       "all_candidate_path_labels":int(len(label_ids)),
       "physical_bulk_connection_verified":False,
       "source_flat_only_and_phase_geometry_unverified":True,
       "opening_border_erosion_applies":bool(neck_radius),
    })

def component_root_diagnostics(negative:np.ndarray, corridor:Corridor,
       zone:np.ndarray, min_original_area:int=25, min_zone_overlap:int=10,
       min_below_front_bulk_overlap:int=10)->list[dict]:
    """Report topological support per negative component, never classify physics."""
    neg=np.asarray(negative,dtype=bool)
    if not (neg.shape==zone.shape==corridor.source_bulk_connected.shape):
        raise ValueError("mismatched native detector geometry")
    if any(x<1 for x in (min_original_area,min_zone_overlap,min_below_front_bulk_overlap)):
        raise ValueError("unphysical component thresholds")
    lab,k=ndi.label(neg,structure=ndi.generate_binary_structure(2,1))
    out=[]
    for i,s in enumerate(ndi.find_objects(lab),1):
        if s is None:continue
        mask=lab[s]==i
        size=int(mask.sum())
        if size<min_original_area:continue
        zone_count=int(np.count_nonzero(mask&zone[s]))
        bulk_count=int(np.count_nonzero(mask&corridor.source_bulk_connected[s]))
        rooted_count=int(np.count_nonzero(mask&corridor.below_front_connected[s]))
        out.append({
          "component_label":i,"area_px":size,
          "zone_overlap_px":zone_count,
          "candidate_bulk_connected_overlap_px":bulk_count,
          "candidate_below_front_bulk_connected_overlap_px":rooted_count,
          "baseline_spatial_supported":zone_count>=min_zone_overlap,
          "proposed_candidate_corridor_supported":rooted_count>=min_below_front_bulk_overlap,
          "physical_liquid_channel_verified":False,
        })
    return out

def corridor_comparison(positive_strong:np.ndarray,positive_broad:np.ndarray,
           valid:np.ndarray,front_y:np.ndarray|None,negative:np.ndarray,zone:np.ndarray,
           *,roi=DEFAULT_ROI,neck_radii=(0,1,2))->dict:
    if not (positive_strong.shape==positive_broad.shape==valid.shape==negative.shape==zone.shape):
        raise ValueError("input geometry mismatch")
    if np.any(positive_strong&~positive_broad):
        raise ValueError("strong positive must be subset of broad positive")
    records=[]
    for label,pos in (("strong_positive_0p04",positive_strong),
                      ("broad_positive_0p02",positive_broad)):
        for radius in neck_radii:
            c=candidate_corridor(pos,valid,front_y,roi=roi,neck_radius=radius)
            comp=component_root_diagnostics(negative,c,zone)
            records.append({
                "barrier_hypothesis":label,
                "neck_radius":radius,
                "corridor":c.metadata,
                "negative_candidate_components":len(comp),
                "spatial_retained_components":sum(x["baseline_spatial_supported"] for x in comp),
                "spatial_retained_with_candidate_root":sum(x["baseline_spatial_supported"] and x["proposed_candidate_corridor_supported"] for x in comp),
                "spatial_retained_without_candidate_root":sum(x["baseline_spatial_supported"] and not x["proposed_candidate_corridor_supported"] for x in comp),
                "root_only_excluded_by_original_spatial_rule":sum(not x["baseline_spatial_supported"] and x["proposed_candidate_corridor_supported"] for x in comp),
                "per_component":comp,
                "note":"Corroborative topology only; none of these counts changes baseline decisions.",
            })
    return {"schema":SCHEMA,"status":"TENTATIVE_2D_PATH_CONNECTIVITY_NOT_TRUE_LIQUID",
            "hypotheses":records,
            "original_masks_changed":False,
            "physical_channel_path_admitted":False}
