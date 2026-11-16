"""T1 source-pixel shape evidence for candidate temporal associations.

Diagnostic ONLY. No physical plume classification or automatic edge deletion.
Centroid alignment uses the observed pair and is therefore an *optimistic*
shape match, not a source-independent motion-prediction validation.
"""
from __future__ import annotations
import numpy as np

SCHEMA="ga-in-t1-pixel-shape-link-diagnostic/v0.1.0"

def shape_consistency(a, b, shape:tuple[int,int])->dict:
    """Compare original and centroid-translated candidate masks, with clipping QA.

    Inputs are Component instances from the frozen T1 module, providing flat
    native detector indices. Assumes both masks have the SAME source image shape.
    """
    if len(shape)!=2 or any(int(k)!=k or k<=0 for k in shape):
        raise ValueError("invalid detector shape")
    height,width=map(int,shape)
    if a.role!=b.role or a.group!=b.group or b.ordinal!=a.ordinal+1:
        raise ValueError("unrelated source group or non-adjacent frame")
    aa=np.asarray(a.signed_detector_pixels)
    bb=np.asarray(b.signed_detector_pixels)
    if not len(aa) or not len(bb):
        raise ValueError("empty candidate component")
    if (not np.issubdtype(aa.dtype,np.integer) or not np.issubdtype(bb.dtype,np.integer)
        or np.any(aa<0) or np.any(bb<0)
        or np.any(aa>=height*width) or np.any(bb>=height*width)):
        raise ValueError("source pixel index outside detector")
    if len(np.unique(aa))!=len(aa) or len(np.unique(bb))!=len(bb):
        raise ValueError("duplicate detector pixel indices")
    overlap=int(np.intersect1d(aa,bb,assume_unique=True).size)
    raw=float(overlap/(len(aa)+len(bb)-overlap))
    # This shift is estimated from BOTH observations: diagnostic matching
    # upper bound, NOT independent physical velocity or causal prediction.
    shift_y=int(np.rint(b.centroid_y-a.centroid_y))
    shift_x=int(np.rint(b.centroid_x-a.centroid_x))
    yy=aa//width+shift_y
    xx=aa%width+shift_x
    inside=(yy>=0)&(yy<height)&(xx>=0)&(xx<width)
    translated=yy[inside]*width+xx[inside]
    compensated_overlap=int(np.intersect1d(translated,bb,assume_unique=True).size)
    aligned=float(compensated_overlap/(len(translated)+len(bb)-compensated_overlap))
    clip=float(1-int(inside.sum())/len(aa))
    area_ratio=float(min(len(aa),len(bb))/max(len(aa),len(bb)))
    return {
        "schema":SCHEMA,"src":a.uid,"dst":b.uid,
        "native_source_shape_yx":[height,width],
        "centroid_alignment_dy_dx":[shift_y,shift_x],
        "unshifted_pixel_iou":raw,
        "centroid_aligned_pixel_iou_optimistic":aligned,
        "source_footprint_clipped_fraction":clip,
        "area_similarity":area_ratio,
        "warning":"Centroid alignment uses future observation; not an independently predicted flow.",
        "manual_review_only":True,
    }

def annotate_candidate_edges(left:list,right:list,edges:list[dict],shape:tuple[int,int])->list[dict]:
    """Attach shape diagnostics to existing frozen T1 edges, without filtering."""
    byid={x.uid:x for x in list(left)+list(right)}
    result=[]
    for edge in edges:
        if edge["src"] not in byid or edge["dst"] not in byid:
            raise ValueError("edge refers to an unknown component")
        extra=shape_consistency(byid[edge["src"]],byid[edge["dst"]],shape)
        new=dict(edge)
        new.update({k:v for k,v in extra.items() if k not in ("src","dst")})
        result.append(new)
    if len(result)!=len(edges):
        raise AssertionError("diagnostic changed number of candidate edges")
    return result
