"""Reproducible 2014-04-04 *candidate* anomaly-mask sensitivity benchmark.

Source-faithfulness: raw source TIFFs and Reference=flat-field roles, source SHA,
CRC32, candidate filename time/group and native geometry. Intensity masks are
NOT the v25 temporal-MIL dynamic-threshold algorithm, NOT phase ground truth,
NOT chemical calibration. Native v25 MIL series is evaluated separately using
licensed Wolfram. Never use an automatic threshold as a chemical phase label.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import sys
import zlib
from pathlib import Path

import numpy as np
import tifffile
from PIL import Image
from scipy import ndimage as ndi

SCHEMA="ga-in-2014-04-04-source-relative-candidate-mask-benchmark/v1"
EXPECTED_ARCHIVE_SHA="77fac9a38a9cdaa41ee5ec9c9562acb7149ee1cee8f0246a80c2b267928f2510"
SHAPE=(426,761)
FILTERS=("none","gaussian_1px","gaussian_2px","median_3px")
THRESHOLDS=(0.02,0.04,0.08)
POLARITIES=("positive","negative","absolute")
MIN_COMPONENT=25
ROI=(120,412,155,690)   # unreviewed y0,y1,x0,x1, never accepted chamber geometry
MAIN=(0,40,79,119,240,400,479,480,565,639,720,900,918,919,1200,1800,2600,3147)
END=(0,150,297)

class GateError(ValueError):
    pass

def sha(path:Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def validate_inventory(inv):
    if inv.get("schema")!="ga-in-archive-inventory/v1" or inv.get("case_id")!="2014-04-04":
        raise GateError("Wrong source manifest")
    if not inv.get("archive_sha256_verified") or inv.get("archive_sha256")!=EXPECTED_ARCHIVE_SHA:
        raise GateError("Archive SHA not independently verified")
    if inv.get("reference_recording_role")!="flat_field_correction_owner_confirmed":
        raise GateError("Reference must be owner-confirmed flat field, NOT specimen J0")
    if not inv.get("flat_field_role_confirmed"):
        raise GateError("Flat-field provenance unconfirmed")
    rec=inv.get("filename_candidate_frame_records")
    if not isinstance(rec,dict) or any(x not in rec for x in ("reference","main","end")):
        raise GateError("Incomplete per-member source manifest")
    if [len(rec[x]) for x in ("reference","main","end")] != [111,3148,298]:
        raise GateError("Unexpected 2014-04-04 original source stream lengths")
    for role,seq in rec.items():
        prior=None
        for idx,r in enumerate(seq):
            if r["candidate_ordinal_id_zero_based"]!=idx:
                raise GateError("Source ordinal not preserved")
            if prior is not None and r["filename_clock_ms"]<=prior:
                raise GateError("Source clock nonmonotonic")
            prior=r["filename_clock_ms"]
    return rec

def read_source(path:Path,record):
    filename=record["filename"]
    if path.name!=filename or path.stat().st_size!=record["member_size_bytes"]:
        raise GateError("Source filename/size mismatch")
    with path.open("rb") as f:
        crc=0
        for chunk in iter(lambda:f.read(1024*1024),b""):
            crc=zlib.crc32(chunk,crc)
    if f"{crc&0xffffffff:08X}"!=record["member_crc32_header_unverified"].upper():
        raise GateError("Source CRC32 failed")
    with tifffile.TiffFile(path) as t:
        if len(t.pages)!=1 or t.pages[0].bitspersample!=16 or t.pages[0].samplesperpixel!=1:
            raise GateError("Wrong TIFF encoding")
        arr=t.pages[0].asarray()
    if arr.dtype!=np.uint16 or arr.shape!=SHAPE:
        raise GateError("Wrong TIFF shape/type")
    return arr

def candidate_log_ratio(frame,baseline,reference_valid):
    if frame.shape!=baseline.shape or frame.shape!=reference_valid.shape:
        raise GateError("Per-pixel raw detector correspondence missing")
    valid=reference_valid&(baseline>0)&(baseline<65535)&(frame>0)&(frame<65535)
    p=np.zeros(frame.shape,np.float64)
    p[valid]=-np.log(frame[valid].astype(np.float64)/baseline[valid])
    return p,valid

def filter_field(p,valid,method):
    if method not in FILTERS:
        raise GateError("Unknown image filter")
    if method=="none":
        return p.copy(),valid.copy()
    if method.startswith("gaussian_"):
        sigma=1.0 if method=="gaussian_1px" else 2.0
        numerator=ndi.gaussian_filter(np.where(valid,p,0.0),sigma,mode="nearest")
        weight=ndi.gaussian_filter(valid.astype(float),sigma,mode="nearest")
        usable=valid&(weight>=0.999)
        x=np.zeros_like(p)
        x[usable]=numerator[usable]/weight[usable]
        return x,usable
    if method=="median_3px":
        x=ndi.median_filter(np.where(valid,p,0.0),size=3,mode="nearest")
        usable=valid&ndi.minimum_filter(valid.astype(np.uint8),size=3,mode="nearest").astype(bool)
        return x,usable
    raise GateError("Unhandled filter")

def generate_mask(filtered,valid,threshold,polarity,roi_yx=ROI,min_area=MIN_COMPONENT):
    if not math.isfinite(float(threshold)) or threshold<=0:
        raise GateError("Require positive finite contrast threshold")
    if polarity not in POLARITIES or min_area<1:
        raise GateError("Invalid polarity/minimum component")
    y0,y1,x0,x1=roi_yx
    if not (0<=y0<y1<=filtered.shape[0] and 0<=x0<x1<=filtered.shape[1]):
        raise GateError("Candidate ROI outside original source detector")
    roi=np.zeros(filtered.shape,bool);roi[y0:y1,x0:x1]=True
    if polarity=="positive": hits=filtered>threshold
    elif polarity=="negative": hits=filtered < -threshold
    else: hits=np.abs(filtered)>threshold
    mask=hits&valid&roi
    labels,n=ndi.label(mask,structure=ndi.generate_binary_structure(2,1))
    sizes=np.bincount(labels.ravel())
    keep=sizes>=min_area
    keep[0]=False
    return keep[labels]

def mask_metrics(mask,valid,roi_yx=ROI):
    y0,y1,x0,x1=roi_yx
    roi=np.zeros(mask.shape,bool);roi[y0:y1,x0:x1]=True
    support=valid&roi
    n=int(np.count_nonzero(support))
    if n<1:
        raise GateError("No valid ROI detector pixels")
    lab,k=ndi.label(mask,structure=ndi.generate_binary_structure(2,1))
    counts=np.bincount(lab.ravel())[1:]
    ys,xs=np.nonzero(mask)
    return {
      "support_pixels":n,
      "candidate_pixels":int(mask.sum()),
      "candidate_fraction_valid_roi":float(mask.sum()/n),
      "component_count_4connect":int(k),
      "largest_component_px":int(counts.max()) if len(counts) else 0,
      "mask_bbox_ymin_ymax_xmin_xmax":[int(ys.min()),int(ys.max()),int(xs.min()),int(xs.max())] if len(ys) else None,
    }

def jaccard(a,b):
    intersection=int(np.logical_and(a,b).sum())
    union=int(np.logical_or(a,b).sum())
    return float(intersection/union) if union else None # 0/0 = undefined, not 1.0

def write_mask(out:Path, mask):
    if out.exists():raise GateError("Refuse mask overwrite")
    out.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray((mask.astype(np.uint8)*255)).save(out)
    return {"name":str(out.name),"sha256":sha(out)}

def run(inv,ref_dir:Path,exp_dir:Path,out:Path):
    if out.exists():
        raise GateError("Refusing to replace an existing benchmark output directory")
    records=validate_inventory(inv)
    # Derive candidate temporal segments from actual archive filenames, never
    # hard-code ordinal boundaries or silently bridge acquisition interruptions.
    candidate_groups={}
    group=0
    previous_time=None
    previous_role=None
    for stream_role in ("main","end"):
        for rec in records[stream_role]:
            t=rec["filename_clock_ms"]
            if previous_time is not None and t<=previous_time:
                raise GateError("Cross-stream filename clock nonmonotonic")
            if previous_role!=stream_role or (previous_time is not None and t-previous_time>1500):
                group+=1
            candidate_groups[(stream_role,rec["candidate_ordinal_id_zero_based"])]=group
            previous_time=t
            previous_role=stream_role
    if group!=5:
        raise GateError("Unexpected original source filename-gap segmentation")
    if not ref_dir.is_dir() or not exp_dir.is_dir():
        raise GateError("Source roots absent")
    # Build baseline ONLY from the first contiguous 80 original experiment frames.
    source_base=[]
    for i in range(80):
        r=records["main"][i]
        source_base.append(read_source(exp_dir/r["filename"],r))
    t=[r["filename_clock_ms"] for r in records["main"][:80]]
    if any(not (0<b-a<=1500) for a,b in zip(t,t[1:])):
        raise GateError("Baseline training crossed a candidate time break")
    initial=np.median(np.stack(source_base),axis=0)
    del source_base
    flat_stacks=[]
    for rec in records["reference"]:
        flat_stacks.append(read_source(ref_dir/rec["filename"],rec))
    flat_stack=np.stack(flat_stacks)
    valid_flat=np.all((flat_stack>0)&(flat_stack<65535),axis=0)
    R0=np.median(flat_stack[:80],axis=0)
    Rhold=np.median(flat_stack[80:],axis=0)
    del flat_stack
    out.mkdir(parents=True)
    controls=[]
    images=[]
    summaries=[]
    review_masks=[]
    comparisons=[]
    rendered={}

    def analyze(role,ordinal,image,tag,control_kind=None):
        p,valid=candidate_log_ratio(image,initial,valid_flat)
        products={}
        for name in FILTERS:
            v,usable=filter_field(p,valid,name)
            for th in THRESHOLDS:
                for polarity in POLARITIES:
                    mask=generate_mask(v,usable,th,polarity)
                    products[(name,th,polarity)]=(mask,usable)
                    metrics=mask_metrics(mask,usable)
                    summaries.append({
                       "source_role":role,"source_ordinal0":ordinal,"tag":tag,
                       "control_kind":control_kind or "",
                       "filter":name,"threshold_abs_log_ratio":th,"polarity":polarity,
                       "min_component_px":MIN_COMPONENT,**metrics})
        # Parameter sensitivity is NOT ground-truth accuracy.
        for polarity in POLARITIES:
            a=products[("gaussian_1px",0.02,polarity)][0]
            b=products[("gaussian_1px",0.04,polarity)][0]
            c=products[("gaussian_1px",0.08,polarity)][0]
            comparisons.append({"source_role":role,"source_ordinal0":ordinal,"polarity":polarity,
              "gaussian1_jaccard_002_vs_004":jaccard(a,b),
              "gaussian1_jaccard_004_vs_008":jaccard(b,c),
              "at004_none_vs_gaussian1":jaccard(products[("none",0.04,polarity)][0],b),
              "at004_median3_vs_gaussian1":jaccard(products[("median_3px",0.04,polarity)][0],b)})
        if (role,ordinal) in (("main",119),("main",480),("main",639),("main",1200),("main",3147),("end",297)):
            # Only small, fixed, reviewable outputs. No automatic phase semantics.
            for polarity in POLARITIES:
                m=products[("gaussian_1px",0.04,polarity)][0]
                info=write_mask(out/"review_binary_masks"/f"{role}_{ordinal:04d}_gauss1_t004_{polarity}.png",m)
                review_masks.append({"source_role":role,"source_ordinal0":ordinal,
                      "filter":"gaussian_1px","threshold":0.04,"polarity":polarity,**info})
                rendered[(role,ordinal,polarity)]=m
            images.append({"role":role,"ordinal":ordinal,"p":p,"valid":valid,"raw":image})
        return summaries[-36:]

    # True algorithmic null: exactly unchanged sample baseline -> no detection for any nonzero threshold.
    null_image=initial.copy().astype(float)
    pzero=np.zeros_like(null_image)
    fzero=valid_flat&(initial>0)&(initial<65535)
    zero_count=0
    for filt in FILTERS:
      p_f,v_f=filter_field(pzero,fzero,filt)
      for th in THRESHOLDS:
        for pol in POLARITIES:
          zero_count+=int(generate_mask(p_f,v_f,th,pol).sum())
    if zero_count: raise GateError("Nonzero segmentation on exact unchanged synthetic J0")

    # Independent flat-reference variability control (different semantics from specimen J0).
    rf=(Rhold/R0)
    fl_valid=valid_flat&(Rhold>0)&(Rhold<65535)&(R0>0)&(R0<65535)
    flp=np.zeros(SHAPE,float)
    flp[fl_valid]=-np.log(rf[fl_valid])
    for filt in FILTERS:
      v,valid=filter_field(flp,fl_valid,filt)
      for th in THRESHOLDS:
        for pol in POLARITIES:
          m=generate_mask(v,valid,th,pol)
          controls.append({"kind":"flatfield_holdout_80train_31test","filter":filt,
            "threshold":th,"polarity":pol,**mask_metrics(m,valid)})
    verified=[]
    for role,ordinal_set in (("main",MAIN),("end",END)):
      for ordinal in ordinal_set:
        r=records[role][ordinal]
        img=read_source(exp_dir/r["filename"],r)
        if role=="main" and ordinal in (0,40,79,119,240):
            control="early_experimental_candidate_not_truth"
        else: control=None
        analyze(role,ordinal,img,r["filename"],control_kind=control)
        verified.append({"role":role,"ordinal":ordinal,"filename":r["filename"],
          "filename_clock_ms":r["filename_clock_ms"],
          "member_crc32_verified":True,"size_bytes":r["member_size_bytes"],
          "candidate_contiguous_group":candidate_groups[(role,ordinal)],
          "source_temporal_group_index_is_candidate":True})
        print("verified_source",role,ordinal,flush=True)

    # Explicit synthetic spatial misregistration stress, never a real frame.
    r=records["main"][1200]
    im=read_source(exp_dir/r["filename"],r)
    shifted=np.roll(im,4,axis=1)
    ptrue,validtrue=candidate_log_ratio(im,initial,valid_flat)
    pshift,validshift=candidate_log_ratio(shifted,initial,valid_flat)
    validshift[:,:4]=False
    t1,v1=filter_field(ptrue,validtrue,"gaussian_1px")
    t2,v2=filter_field(pshift,validshift,"gaussian_1px")
    mis={}
    for pol in POLARITIES:
      original=generate_mask(t1,v1,.04,pol)
      perturbed=generate_mask(t2,v2,.04,pol)
      mis[pol]={"unshifted_fraction":mask_metrics(original,v1)["candidate_fraction_valid_roi"],
        "synthetically_shifted_4px_fraction":mask_metrics(perturbed,v2)["candidate_fraction_valid_roi"],
        "mask_jaccard":jaccard(original,perturbed)}
    # Note synthetic 4 px roll is a stress test; never evidence of real registration error.

    # Persist all statistics with no private TIFFs in public GitHub.
    with (out/"per_source_parameter_sweep.csv").open("x",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(summaries[0]))
        w.writeheader();w.writerows(summaries)
    with (out/"parameter_sensitivity.csv").open("x",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(comparisons[0]))
        w.writeheader();w.writerows(comparisons)
    report={
      "schema":SCHEMA,
      "status":"CANDIDATE_ANOMALY_MASK_SWEEP_NOT_ORIGINAL_V25_SEGMENTATION_NOT_PHASE_GROUND_TRUTH",
      "original_archive_sha256":inv["archive_sha256"],
      "source_frame_records_crc_verified":verified,
      "reference_flat_field_111_crc_verified":True,
      "original_experiment_baseline_80_crc_verified":True,
      "original_source_shape_yx":list(SHAPE),
      "flat_field_role":"owner-confirmed Reference recordings",
      "candidate_J0":"median first 80 original contiguous main frames, NOT flat field, not verified homogeneous",
      "no_dark_applied":True,
      "signal":"P_candidate=-ln(I_original/J0_candidate) on jointly valid unsaturated detector pixels",
      "v25_native_MIL_values_are_separate":True,
      "NOT_v25_dynamic_threshold_reproduction":True,
      "candidate_ROI_y0_y1_x0_x1":list(ROI),
      "candidate_ROI_physically_accepted":False,
      "filters":list(FILTERS),"threshold_abs_log_ratios":list(THRESHOLDS),
      "polarities":list(POLARITIES),"min_4connected_component_px":MIN_COMPONENT,
      "zero_image_algorithmic_negative_control_pixels":zero_count,
      "flatfield_heldout_negative_diagnostic":controls,
      "synthetic_4px_shift_sensitivity_main1200":mis,
      "review_output_masks":review_masks,
      "summary_rows":len(summaries),
      "parameter_comparison_rows":len(comparisons),
      "negative_control_early_frames_are_candidate_only":[0,40,79,119,240],
      "independent_expert_phase_annotations_available":False,
      "original_v25_threshold_factor_or_temporal_MIL_reproduction_accepted":False,
      "absolute_composition_wt_pct_admitted":False,
      "camera_clock_admitted":False,
      "detector_geometry_761x426_but_chamber_ROI_unverified":True,
      "library_versions":{"numpy":np.__version__,"scipy":__import__("scipy").__version__,
            "tifffile":tifffile.__version__,"pillow":__import__("PIL").__version__},
      "limitations":[
        "Mask polarity is a diagnostic sign; none is a validated solid label",
        "Thresholds 0.02/0.04/0.08 are fixed exploratory values, not recovered v25 dynamic threshold",
        "ROI rectangle not verified chamber boundary, historical microscopy segmentation not replayed",
        "Flat-only is the working policy; true detector dark offset remains uncharacterized",
        "Image sequence timestamps derive from filenames only and contain documented gaps",
        "Spatial and temporal dependence prevents interpreting sample frames as independent replicates",
      ],
    }
    (out/"benchmark_manifest.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    return report,images,summaries

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inventory",type=Path,required=True)
    ap.add_argument("--reference-dir",type=Path,required=True)
    ap.add_argument("--experiment-dir",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    inv=json.loads(a.inventory.read_text(encoding="utf-8"))
    report,images,rows=run(inv,a.reference_dir,a.experiment_dir,a.output)
    # Presentation only, no scientific mask label or physical boundary assertion.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(len(images),5,figsize=(17,3.2*len(images)),layout="constrained")
    for j,rec in enumerate(images):
        role,i=rec["role"],rec["ordinal"]
        p,valid=rec["p"],rec["valid"]
        raw=rec["raw"].astype(float)
        titles=["Original 16-bit counts","Provisional -ln(I/J0)","positive >.04","negative < -.04","absolute >.04"]
        views=[raw,np.where(valid,p,np.nan)]
        vf,vvalid=filter_field(p,valid,"gaussian_1px")
        views.extend([generate_mask(vf,vvalid,.04,pol) for pol in POLARITIES])
        for k,view in enumerate(views):
            if k==0:
                ax=axes[j,k];ax.imshow(view,cmap="gray",vmin=35000,vmax=65000,origin="upper")
            elif k==1:
                ax=axes[j,k];ax.imshow(view,cmap="coolwarm",vmin=-.12,vmax=.12,origin="upper")
            else:
                ax=axes[j,k];ax.imshow(view,cmap="gray",vmin=0,vmax=1,origin="upper")
            ax.set_title(f"{role} {i}: {titles[k]}",fontsize=8)
            ax.set_xticks([]);ax.set_yticks([])
    fig.suptitle("2014-04-04 candidate segmentation ONLY: no verified chamber/solid/phase labels",fontsize=11)
    fig.savefig(a.output/"candidate_mask_contact_sheet.png",dpi=125)
    plt.close(fig)
    # Print compact review metrics for named early/mid/late candidate filters.
    for role,idx in (("main",119),("main",639),("main",1200),("main",3147),("end",297)):
      q=[r for r in rows if r["source_role"]==role and r["source_ordinal0"]==idx
         and r["filter"]=="gaussian_1px" and r["threshold_abs_log_ratio"]==0.04]
      print("SOURCE",role,idx,{r["polarity"]:round(r["candidate_fraction_valid_roi"],5) for r in q})
    for name in ("benchmark_manifest.json","per_source_parameter_sweep.csv","parameter_sensitivity.csv","candidate_mask_contact_sheet.png"):
      f=a.output/name
      print("OUTPUT",f.name,"SHA256",sha(f))
    print("REVIEW_NOT_PHASE_GROUND_TRUTH",len(report["source_frame_records_crc_verified"]),
          "source frames",report["summary_rows"],"filter threshold polarity rows")

if __name__=="__main__":
    main()