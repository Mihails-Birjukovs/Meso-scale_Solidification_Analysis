"""Exploratory 2014-04-04 morphology-derived *zone envelope*, not phase mask.

Owner suggested v25-style solid-zone filling/closing to reject isolated negative
candidate fragments above the developing solid zone while retaining connected
channel/plume-like components. The old candidate masks/RAW frames are read only.

This first pilot labels all zone envelopes as UNVERIFIED. It does not close
the physical G0 gate, and preserves plume extensions reaching above the front
if they are connected to a component that intersects the zone.
"""
import importlib.util, json, sys
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from PIL import Image

ROOT=Path(r"X:\AI-Lab-Test\Solidification_OFV\analysis_outputs")
OLD=ROOT/"phase0_2014-04-04_mil_candidate_benchmark_2026-11-14"
OUTPUT=ROOT/"phase0_2014-04-04_targeted_mask_sensitivity_2026-11-15"
ROI=(120,412,155,690)
SOURCE_SHA="77fac9a38a9cdaa41ee5ec9c9562acb7149ee1cee8f0246a80c2b267928f2510"
SELECTION=(("main",119),("main",480),("main",639),("main",1200),("main",3147),("end",297))

def module():
    spec=importlib.util.spec_from_file_location("read_only_original_scientific_benchmark",OLD/"Python_code"/"phase0_2014_04_04_mil_candidate_benchmark.py")
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m

def disk(radius):
    yy,xx=np.ogrid[-radius:radius+1,-radius:radius+1]
    return xx*xx+yy*yy<=radius*radius

def envelope(positive,*,radius=8,margin=8,median_size=15):
    y0,y1,x0,x1=ROI
    if positive.shape!=(426,761):raise ValueError("Source geometry mismatch")
    if not (0<=radius<=20 and 0<=margin<=30):raise ValueError("Invalid morphological parameters")
    r=positive[y0:y1,x0:x1].astype(bool)
    closed=ndi.binary_closing(r,structure=disk(radius),border_value=0)
    # Binary closing erodes the ROI bottom border. Pad the region on three sides
    # but provide strong lower anchors before computing bottom-connected pieces.
    # Keep source morphology independent of padding and candidate wall labels.
    labels,k=ndi.label(closed,structure=ndi.generate_binary_structure(2,1))
    # Eroded closing typically removes the bottom few rows: anchor within radius+3px.
    anchor_row=max(0,closed.shape[0]-(radius+5))
    seeds=np.unique(labels[anchor_row:,:])
    seeds=seeds[seeds>0]
    bottom_connected=np.isin(labels,seeds) if len(seeds) else np.zeros_like(closed)
    xvalid=np.flatnonzero(np.any(bottom_connected,axis=0))
    stats={"positive_pixels_in_unapproved_roi":int(r.sum()),
           "closed_pixels":int(closed.sum()),
           "bottom_connected_pixels":int(bottom_connected.sum()),
           "number_bottom_touching_labels":int(len(seeds)),
           "supported_columns":int(xvalid.size),
           "supported_column_fraction":float(xvalid.size/r.shape[1]),
           "method":"morph_close_bottom_connected_fill_columns_interpolate_smooth",
           "reason_if_rejected":None}
    if xvalid.size<30 or bottom_connected.sum()<300:
        stats["reason_if_rejected"]="Insufficient source positive anchors to define front"
        return np.zeros_like(positive,bool),None,stats
    front_raw=np.full(r.shape[1],np.nan)
    for x in xvalid:
        front_raw[x]=np.flatnonzero(bottom_connected[:,x])[0]
    interp=np.interp(np.arange(r.shape[1]),xvalid,front_raw[xvalid])
    med=ndi.median_filter(interp,size=median_size,mode="nearest")
    sm=ndi.gaussian_filter1d(med,2,mode="nearest")
    zone_small=(np.arange(r.shape[0])[:,None]>=np.maximum(0,sm[None,:]-margin))
    zone=np.zeros_like(positive,bool)
    zone[y0:y1,x0:x1]=zone_small
    stats.update({"front_ymin":float(y0+sm.min()),"front_ymedian":float(y0+np.median(sm)),
        "front_ymax":float(y0+sm.max()),"zone_fraction_in_unapproved_roi":float(zone_small.mean())})
    return zone,y0+sm,stats

def keep_connected_negative(negative,zone,min_overlap=10):
    labels,n=ndi.label(negative,structure=ndi.generate_binary_structure(2,1))
    overlap=np.bincount(labels[zone].ravel(),minlength=n+1)
    good=overlap>=min_overlap
    good[0]=False
    kept=good[labels]
    return kept,{"component_count_original":n,"original_pixels":int(negative.sum()),
                 "retained_pixels":int(kept.sum()),"rejected_pixels":int((negative&~kept).sum()),
                 "retained_component_count":int(good.sum()),
                 "min_overlap_source_pixels":min_overlap}

def main():
    m=module()
    inventory=json.loads((ROOT/"phase0_2014-04-04_archive_admission_2026-11-11"/"inventory_flatfield_role_v2.json").read_text())
    old=json.loads((OLD/"candidate_sweep_v2_conda"/"benchmark_manifest.json").read_text())
    assert inventory["archive_sha256"]==SOURCE_SHA and old["original_archive_sha256"]==SOURCE_SHA
    assert old["candidate_ROI_y0_y1_x0_x1"]==list(ROI)
    origdir=OLD/"candidate_sweep_v2_conda"/"review_binary_masks"
    src=OUTPUT/"sweep_v1"
    result=[]
    for role,i in SELECTION:
        path=src/f"{role}_{i:04d}_candidate_masks_t002_t004_t008.npy"
        masks=np.load(path)
        assert masks.shape==(5,426,761) and masks.dtype==np.uint8
        broad=masks[0].astype(bool);n040=masks[4].astype(bool)
        originalrec={x["polarity"]:x for x in old["review_output_masks"] if x["source_role"]==role and x["source_ordinal0"]==i}
        for polarity,k in [("positive",1),("negative",4)]:
            p=origdir/originalrec[polarity]["name"]
            assert m.sha(p)==originalrec[polarity]["sha256"]
            assert np.array_equal(np.array(Image.open(p))>0,masks[k].astype(bool))
        for radius in (4,8,12):
            for margin in (0,8,16):
                zone,front,stat=envelope(broad,radius=radius,margin=margin)
                if front is None:
                    print("UNAVAILABLE",role,i,radius,margin,stat["reason_if_rejected"])
                    continue
                kept,metric=keep_connected_negative(n040,zone,min_overlap=10)
                y0,y1,x0,x1=ROI
                # Provisional diagnostic strip and center from earlier review; neither corresponds to user's pixel-perfect annotations.
                upper=(slice(120,175),slice(155,690))
                central=(slice(175,412),slice(335,485))
                result.append({"role":role,"ordinal":i,"radius":radius,"margin":margin,
                 "front_supported_fraction":stat["supported_column_fraction"],
                 "front_median_source_y":stat["front_ymedian"],
                 "negative_total":int(n040.sum()),"negative_retained":metric["retained_pixels"],
                 "upper_total":int(n040[upper].sum()),"upper_retained":int(kept[upper].sum()),
                 "central_total":int(n040[central].sum()),"central_retained":int(kept[central].sum()),
                 "component_count_original":metric["component_count_original"],
                 "component_count_retained":metric["retained_component_count"]})
                if (role,i) in (("main",1200),("main",3147),("end",297)) and radius==8 and margin==8:
                    OUT=OUTPUT/"morphological_zone_pilot_v1"
                    OUT.mkdir(exist_ok=True)
                    npz_path=OUT/f"{role}_{i:04d}_radius8_margin8_provisional.npz"
                    if npz_path.exists():
                        raise RuntimeError("Refuse overwrite of existing expert-review arrays")
                    np.savez_compressed(npz_path,
                      zone_envelope=zone,original_negative=n040,retained_negative=kept,
                      removed_negative=n040&~kept,
                      front_y=front)
                    print("PILOT",role,i,stat,metric)
    OUT=OUTPUT/"morphological_zone_pilot_v1"
    OUT.mkdir(exist_ok=True)
    js=OUT/"source_zone_sensitivity_v1.json"
    if js.exists():raise RuntimeError("refuse overwrite manifest")
    js.write_text(json.dumps({"schema":"ga-in-provisional-solid-zone-morphology/v1",
     "status":"UNVERIFIED_FRONT_ENVELOPE_NOT_PHASE_TRUTH",
     "source_archive_sha256":SOURCE_SHA,
     "source_review_archive_sha256":"62a8833a38faf8f38117f7d1c0d3f557355debb57d8e2b73dc06628aa846105b",
     "method":"derive bottom-connected candidate positive region by binary closing; per-x earliest positive (after interpolation/smoothing) defines provisional solid-zone envelope; keep entire negative component if at least 10 pixels overlap envelope",
     "negative_baseline":"t=0.04, gaussian sigma1, minarea25, original",
     "source_positive_proxy":"t=0.02 original source contrast mask, NOT independently verified phase segmentation",
     "source_roi_y0_y1_x0_x1_unapproved":list(ROI),
     "critical_caveat":"May reject real small plumes above front and falsely retain isolated artifacts on or below front; morphology is a geometric hypothesis, not a physical phase estimator",
     "records":result},indent=2)+"\n")
    print("DONE records",len(result))
    for o in result:
        if o["radius"]==8 and o["margin"]==8 and (o["role"],o["ordinal"]) in (("main",1200),("main",3147),("end",297)):
            print("SUMMARY",o)
if __name__=="__main__":
    main()
