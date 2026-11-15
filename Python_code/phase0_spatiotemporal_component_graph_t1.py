"""Experimental T1 component-level spatial-temporal association; NOT plume ground truth.

Versioned science contract:
- consume existing candidate masks and morphology zone; never mutate them;
- do not link different acquisition groups or nonconsecutive original ordinals;
- association uses only original detector-pixel geometry, not unverified OFV;
- allow split/merge by retaining multiple admissible graph edges;
- temporal evidence may upgrade rejection only to UNCERTAIN, never silently
  promote a user-rejected candidate to a published physical plume;
- retain original candidate mask bytes; return machine-readable diagnostics.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import math
from typing import Sequence
import numpy as np
from scipy import ndimage as ndi

SCHEMA="ga-in-spatiotemporal-negative-component-t1/v0.1.0"
MAX_INTERVAL_MS=1500
MAX_CENTROID_STEP_PX=30.0
MIN_ZONE_OVERLAP_PIXELS=10
MAX_AREA_RATIO=8.0

@dataclass(frozen=True)
class FrameObservation:
    role:str
    ordinal:int
    time_ms:int
    group:int
    negative:np.ndarray
    zone:np.ndarray|None
    valid:np.ndarray
    signed_contrast:np.ndarray

@dataclass
class Component:
    uid:str
    role:str
    ordinal:int
    time_ms:int
    group:int
    label:int
    area:int
    centroid_y:float
    centroid_x:float
    bbox_y0:int
    bbox_y1:int
    bbox_x0:int
    bbox_x1:int
    elongation:float
    mean_negative_magnitude:float
    zone_overlap_pixels:int
    spatial_supported:bool
    signed_detector_pixels:np.ndarray # flattened y*width+x, not exported
    def public(self):
        d=asdict(self)
        d.pop("signed_detector_pixels")
        return d

def components(frame:FrameObservation,min_component_px:int=25,min_overlap_px:int=MIN_ZONE_OVERLAP_PIXELS)->list[Component]:
    negative=np.asarray(frame.negative,dtype=bool)
    valid=np.asarray(frame.valid,dtype=bool)
    contrast=np.asarray(frame.signed_contrast,dtype=float)
    if negative.ndim!=2 or negative.shape!=valid.shape or negative.shape!=contrast.shape:
        raise ValueError("original detector shape/source validity mismatch")
    if np.any(negative & ~valid):
        raise ValueError("source mask contains invalid detector pixels")
    if not np.isfinite(contrast[valid]).all():
        raise ValueError("non-finite valid contrast")
    if frame.zone is not None and frame.zone.shape!=negative.shape:
        raise ValueError("zone shape mismatch")
    if frame.ordinal<0 or frame.time_ms<0 or min_component_px<1 or min_overlap_px<1:
        raise ValueError("invalid source ordinal/clock/component parameters")
    zone=np.zeros_like(negative) if frame.zone is None else np.asarray(frame.zone,dtype=bool)
    labs,n=ndi.label(negative,structure=ndi.generate_binary_structure(2,1))
    boxes=ndi.find_objects(labs)
    out=[]
    width=negative.shape[1]
    for ix,slices in enumerate(boxes,1):
        if slices is None:continue
        local=(labs[slices]==ix)
        iy,ixs=np.nonzero(local)
        area=len(iy)
        if area<min_component_px:continue
        y=iy+slices[0].start
        x=ixs+slices[1].start
        overlap=int(np.count_nonzero(zone[y,x]))
        cov=np.cov(np.stack((y,x))) if area>2 else np.eye(2)
        eig=np.maximum(np.linalg.eigvalsh(cov),1e-9)
        elong=float(np.sqrt(eig[-1]/eig[0]))
        pixels=y.astype(np.int64)*width+x.astype(np.int64)
        out.append(Component(
            uid=f"{frame.role}:{frame.ordinal}:{ix}",
            role=frame.role,ordinal=frame.ordinal,time_ms=frame.time_ms,
            group=frame.group,label=ix,area=area,
            centroid_y=float(y.mean()),centroid_x=float(x.mean()),
            bbox_y0=slices[0].start,bbox_y1=slices[0].stop,
            bbox_x0=slices[1].start,bbox_x1=slices[1].stop,
            elongation=elong,
            mean_negative_magnitude=float(-contrast[y,x].mean()),
            zone_overlap_pixels=overlap,
            spatial_supported=bool(overlap>=min_overlap_px),
            signed_detector_pixels=pixels))
    return out

def adjacent(left:FrameObservation,right:FrameObservation,
             max_interval_ms:int=MAX_INTERVAL_MS)->bool:
    if left.role!=right.role or left.group!=right.group:return False
    if right.ordinal!=left.ordinal+1:return False
    dt=right.time_ms-left.time_ms
    return 0<dt<=max_interval_ms

def associate(left:list[Component],right:list[Component],max_step_px:float=MAX_CENTROID_STEP_PX,
              max_area_ratio:float=MAX_AREA_RATIO)->list[dict]:
    """Keep all admissible edges: graph is many-to-many, not greedy 1-to-1."""
    edges=[]
    if max_step_px<=0 or max_area_ratio<1:raise ValueError("invalid gates")
    for a in left:
        for b in right:
            if a.role!=b.role or a.group!=b.group or b.ordinal!=a.ordinal+1:continue
            dt=b.time_ms-a.time_ms
            if dt<=0 or dt>MAX_INTERVAL_MS:continue
            distance=math.hypot(b.centroid_y-a.centroid_y,b.centroid_x-a.centroid_x)
            # scale gate only by *observed* elapsed source time; no inferred OFV.
            scale=min(1.5,max(.3,dt/1000.0))
            if distance>max_step_px*scale:continue
            area_ratio=max(a.area,b.area)/min(a.area,b.area)
            if area_ratio>max_area_ratio:continue
            shape_ratio=min(a.elongation,b.elongation)/max(a.elongation,b.elongation)
            area_similarity=min(a.area,b.area)/max(a.area,b.area)
            # Not a calibrated probability; gate/score dimensions are explicit.
            score=float(math.exp(-.5*(distance/(max_step_px*scale))**2)
                *(area_similarity**.5)*(shape_ratio**.25))
            edges.append({"src":a.uid,"dst":b.uid,"source_interval_ms":dt,
                          "centroid_displacement_px":distance,
                          "area_similarity":area_similarity,
                          "shape_similarity":shape_ratio,
                          "association_weight_unscaled":score})
    return edges

def graph(frames:Sequence[FrameObservation])->dict:
    if not frames:raise ValueError("no observations")
    uid=set()
    nodes=[]
    edges=[]
    prior=None
    last_nodes=[]
    status=[]
    for f in frames:
        if f.ordinal<0:raise ValueError("invalid frame ordinal")
        this=components(f)
        if any(c.uid in uid for c in this):raise ValueError("duplicate source frame/component ID")
        uid.update(c.uid for c in this)
        nodes.extend(this)
        if prior is not None:
            if f.role==prior.role and f.group==prior.group and f.ordinal<=prior.ordinal:
                raise ValueError("duplicate or reordered source sequence")
            if adjacent(prior,f):
                edges.extend(associate(last_nodes,this))
            else:
                status.append({"after":f"{prior.role}:{prior.ordinal}",
                  "before":f"{f.role}:{f.ordinal}",
                  "reason":"acquisition stream/gap/discontinuity; no temporal edge"})
        prior=f
        last_nodes=this
    pred={c.uid:0 for c in nodes}
    succ={c.uid:0 for c in nodes}
    for e in edges:
        succ[e["src"]]+=1
        pred[e["dst"]]+=1
    public=[]
    for c in nodes:
        d=c.public()
        d["preceding_associations"]=pred[c.uid]
        d["following_associations"]=succ[c.uid]
        d["temporal_association_present"]=bool(pred[c.uid] or succ[c.uid])
        d["decision"]=("spatial_supported" if c.spatial_supported else
                       "uncertain_temporal_evidence_only" if pred[c.uid] or succ[c.uid] else
                       "spatial_rejected_no_temporal_support")
        d["retained_by_frozen_spatial_baseline"]=c.spatial_supported
        # No automatic temporal promotion to actual mask:
        d["retained_by_T1_exploratory"]=c.spatial_supported
        public.append(d)
    return {
        "schema":SCHEMA,
        "status":"EXPERIMENTAL_T1_COMPONENT_ASSOCIATIONS_NOT_PHASE_GROUND_TRUTH",
        "frames":len(frames),"component_nodes":len(public),"edges":len(edges),
        "components":public,"associations":edges,"discontinuities":status,
        "note":"Temporal evidence is diagnostic only; must not resurrect user-rejected artifacts",
        "physical_channel_rooting_verified":False,
        "ofv_motion_used":False,
    }
