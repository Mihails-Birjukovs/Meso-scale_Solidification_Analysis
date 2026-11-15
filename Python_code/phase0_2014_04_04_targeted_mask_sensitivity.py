"""Targeted post-review candidate mask sensitivity for 2014-04-04 source radiography.

The USER APPROVED the existing baseline candidate masks as review aids, not
independent experimental phase ground truth. This is a new, separate,
non-destructive benchmark. Preserve original source masks, TIFFs and PR20.
Positive image change is NOT proven solid; negative is NOT proven Ga-rich plume.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
from matplotlib import cm

SOURCE_ARCHIVE_SHA = "77fac9a38a9cdaa41ee5ec9c9562acb7149ee1cee8f0246a80c2b267928f2510"
BASE=Path(r"X:\AI-Lab-Test\Solidification_OFV\analysis_outputs")
OLD=BASE/"phase0_2014-04-04_mil_candidate_benchmark_2026-11-14"
SRC=BASE/"phase0_2014-04-04_fullsource_preflight_2026-11-11"/"raw_extracted"/"2014-04-04"/"2014-04-04"
INV=BASE/"phase0_2014-04-04_archive_admission_2026-11-11"/"inventory_flatfield_role_v2.json"
REF=BASE/"phase0_2014-04-04_archive_admission_2026-11-11"/"reference_samples"/"2014-04-04"/"Reference"
OUT=BASE/"phase0_2014-04-04_targeted_mask_sensitivity_2026-11-15"/"sweep_v1"
OLD_MASKS=OLD/"candidate_sweep_v2_conda"/"review_binary_masks"
ORIGINAL_BENCH=OLD/"candidate_sweep_v2_conda"/"benchmark_manifest.json"
PY_SOURCE=OLD/"Python_code"/"phase0_2014_04_04_mil_candidate_benchmark.py"
FRAMES=(("main",119),("main",480),("main",639),("main",1200),("main",3147),("end",297))
FOCUS=(("main",639),("main",1200),("main",3147))
POS_THRESHOLDS=(.02,.025,.03,.035,.04,.05,.06,.08)
FILTERS=("gaussian_1px","gaussian_2px","median_3px")
NEG_THRESHOLDS=(.04,.05,.06,.08)
NEG_MIN_AREA=(25,75,150)
SHAPE=(426,761)
RANGE=(-.12,.12)
COLORS={"positive":np.array([255,45,45],np.uint8),
        "negative":np.array([20,235,240],np.uint8),
        "weak_positive":np.array([255,207,30],np.uint8)}
ROI=(120,412,155,690)
UPPER_STRIP=(120,175,155,690)
CENTRAL_CHANNEL_DIAGNOSTIC=(175,412,335,485)

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def font(n=17):
    for f in ("C:\\Windows\\Fonts\\arial.ttf","C:\\Windows\\Fonts\\segoeui.ttf"):
        try:return ImageFont.truetype(f,n)
        except OSError:pass
    return ImageFont.load_default()

def module():
    spec=importlib.util.spec_from_file_location("solidification_original_reviewed_benchmark_readonly",PY_SOURCE)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    return mod

def heatmap(p,valid):
    normalized=np.clip((p-RANGE[0])/(RANGE[1]-RANGE[0]),0,1)
    rgb=np.asarray(cm.get_cmap("coolwarm")(normalized)[...,:3]*255,dtype=np.uint8)
    rgb[~valid]=np.array([30,32,38],np.uint8)
    return rgb

def edge(mask):
    return mask & ~ndi.binary_erosion(mask,structure=np.ones((3,3),bool),border_value=0)

def paint(image,layers):
    out=image.copy()
    for mask,name,opacity in layers:
        col=COLORS[name]
        if opacity>0:
            out[mask]=np.clip((1-opacity)*out[mask].astype(float)+opacity*col,0,255).astype(np.uint8)
    # Use dark one-pixel halo to remain visible over saturated coolwarm red.
    for mask,name,opacity in layers:
        boundary=edge(mask)
        halo=ndi.binary_dilation(boundary,iterations=1)
        out[halo]=np.array([0,0,0],np.uint8)
        out[boundary]=COLORS[name]
    return out

def panel(image,title):
    w,h=SHAPE[1],SHAPE[0]
    ret=Image.new("RGB",(w,h+38),(23,25,30))
    draw=ImageDraw.Draw(ret)
    draw.text((8,8),title,font=font(18),fill=(245,245,245))
    ret.paste(Image.fromarray(image),(0,38))
    return ret

def sheet(panels,rows,cols,title,path):
    w,h=SHAPE[1],SHAPE[0]+38
    margin=14
    banner=62
    output=Image.new("RGB",(margin+cols*(w+margin),banner+rows*(h+margin)),(23,25,30))
    d=ImageDraw.Draw(output)
    d.text((margin,10),title,font=font(23),fill=(250,250,250))
    d.text((margin,37),"SOURCE PIXELS | same heat scale [-0.12,+0.12] | candidate masks, NOT phase truth",font=font(16),fill=(253,207,135))
    assert len(panels)==rows*cols
    for n,im in enumerate(panels):
        yy,xx=divmod(n,cols)
        output.paste(im,(margin+xx*(w+margin),banner+yy*(h+margin)))
    output.save(path)
    return sha(path)

def main():
    if OUT.exists():
        raise RuntimeError("Refuse overwrite of reviewer data")
    inv=json.loads(INV.read_text(encoding="utf-8"))
    exp=inv["filename_candidate_frame_records"]
    bench=json.loads(ORIGINAL_BENCH.read_text(encoding="utf-8"))
    m=module()
    if (inv["archive_sha256"]!=SOURCE_ARCHIVE_SHA
        or not inv["archive_sha256_verified"] or not inv["flat_field_role_confirmed"]
        or inv["reference_recording_role"]!="flat_field_correction_owner_confirmed"
        or bench["original_archive_sha256"]!=SOURCE_ARCHIVE_SHA
        or bench["candidate_ROI_y0_y1_x0_x1"]!=list(ROI)):
        raise RuntimeError("Original source/candidate-mask scientific contract changed")
    flat=np.stack([m.read_source(REF/e["filename"],e) for e in exp["reference"]])
    valid_flat=np.all((flat>0)&(flat<65535),axis=0)
    del flat
    initial=np.median(np.stack([
        m.read_source(SRC/e["filename"],e) for e in exp["main"][:80]]),axis=0)
    saved={(r["source_role"],r["source_ordinal0"],r["polarity"]):r for r in bench["review_output_masks"]}
    assert len(saved)==18
    prepared={}
    records=[]
    negative=[]
    # No files written until source/baseline/saved masks are validated for each frame.
    for role,ordinal in FRAMES:
        rec=exp[role][ordinal]
        img=m.read_source(SRC/rec["filename"],rec)
        p,valid=m.candidate_log_ratio(img,initial,valid_flat)
        results={}
        for filt in FILTERS:
            f,usable=m.filter_field(p,valid,filt)
            for t in POS_THRESHOLDS:
                a=m.generate_mask(f,usable,t,"positive",ROI,25)
                results[(filt,t,"positive",25)]=a
                metric=m.mask_metrics(a,usable,ROI)
                records.append({"role":role,"ordinal0":ordinal,"filter":filt,
                  "threshold_log":t,"polarity":"positive","min_component_px":25,
                  "candidate_pixels":metric["candidate_pixels"],
                  "candidate_fraction_valid_roi":metric["candidate_fraction_valid_roi"],
                  "components":metric["component_count_4connect"],
                  "largest_component_px":metric["largest_component_px"]})
            for th in NEG_THRESHOLDS:
                for min_area in NEG_MIN_AREA:
                    n=m.generate_mask(f,usable,th,"negative",ROI,min_area)
                    results[(filt,th,"negative",min_area)]=n
                    met=m.mask_metrics(n,usable,ROI)
                    upper=n[UPPER_STRIP[0]:UPPER_STRIP[1],UPPER_STRIP[2]:UPPER_STRIP[3]]
                    channel=n[CENTRAL_CHANNEL_DIAGNOSTIC[0]:CENTRAL_CHANNEL_DIAGNOSTIC[1],
                              CENTRAL_CHANNEL_DIAGNOSTIC[2]:CENTRAL_CHANNEL_DIAGNOSTIC[3]]
                    negative.append({"role":role,"ordinal0":ordinal,"filter":filt,
                       "threshold_log_abs":th,"min_component_px":min_area,
                       "negative_candidate_pixels_total":met["candidate_pixels"],
                       "upper_strip_candidate_pixels":int(upper.sum()),
                       "center_channel_candidate_pixels":int(channel.sum()),
                       "status":"arbitrary_unapproved_diagnostic_subregions_not_user-registered_annotations"})
        for polarity in ("positive","negative","absolute"):
            original_record=saved[(role,ordinal,polarity)]
            filename=original_record["name"]
            original_path=OLD_MASKS/filename
            if sha(original_path)!=original_record["sha256"]:
                raise RuntimeError("Existing immutable mask SHA changed: "+filename)
            original=np.array(Image.open(original_path))>0
            a=results[("gaussian_1px",.04,polarity,25)] if polarity!="absolute" else None
            if polarity=="absolute":
                f,usable=m.filter_field(p,valid,"gaussian_1px")
                a=m.generate_mask(f,usable,.04,"absolute",ROI,25)
            if not np.array_equal(a,original):
                raise RuntimeError("Found nonidentical regenerated historical candidate mask: "+filename)
        prepared[(role,ordinal)]={"role":role,"ordinal":ordinal,
           "source_filename":rec["filename"],"p":p,"valid":valid,
           "mask_results":results}
    OUT.mkdir(parents=True)
    artifacts=[]
    def save_panel_set(role,ordinal):
        entry=prepared[(role,ordinal)]
        results=entry["mask_results"]
        base=heatmap(entry["p"],entry["valid"])
        panels=[panel(base,f"{role} {ordinal} — provisional log heatmap")]
        for th in (.02,.03,.04,.06,.08):
            mask=results[("gaussian_1px",th,"positive",25)]
            panels.append(panel(paint(base,[(mask,"positive",0)]),
                                f"Positive outline | sigma1 | t={th:.2f}"))
        baseline=results[("gaussian_1px",.04,"positive",25)]
        broad=results[("gaussian_1px",.02,"positive",25)]
        strong=results[("gaussian_1px",.08,"positive",25)]
        neg=results[("gaussian_1px",.04,"negative",25)]
        if np.any(baseline&~broad):
            raise RuntimeError("Positive masks must nest for same filter and min area")
        uncertain=broad&~baseline
        tri=paint(base,[(uncertain,"weak_positive",.28),
                        (baseline,"positive",.10),(neg,"negative",.10)])
        np.save(OUT/f"{role}_{ordinal:04d}_candidate_masks_t002_t004_t008.npy",
               np.stack([broad,baseline,strong,uncertain,neg]).astype(np.uint8))
        # .npy are derived masks, new exploratory products; originals unchanged.
        panels.append(panel(tri,f"Expanded-only amber | baseline red | neg cyan"))
        dest=OUT/f"{role}_{ordinal:04d}_positive_threshold_review_v1.png"
        artifacts.append({"name":dest.name,"sha256":sheet(panels,1,7,
          f"{role} {ordinal} | positive candidate threshold sensitivity",dest)})
        return {"original_frame":f"{role}_{ordinal:04d}",
            "pos_broad_at002":int(broad.sum()),
            "pos_current_at004":int(baseline.sum()),
            "pos_strict_at008":int(strong.sum()),
            "newly_included_between_002_and_004":int(uncertain.sum()),
            "neg_current_at004":int(neg.sum())}
    per_frame=[]
    for role,ordinal in FRAMES:
        per_frame.append(save_panel_set(role,ordinal))
    # Negative-specific choices to scrutinize questioned upper patches versus plume-like center.
    for role,ordinal in (("main",1200),("main",3147),("end",297)):
        entry=prepared[(role,ordinal)]
        base=heatmap(entry["p"],entry["valid"])
        panels=[]
        for area in (25,150):
            for th in NEG_THRESHOLDS:
                mask=entry["mask_results"][("gaussian_1px",th,"negative",area)]
                panels.append(panel(paint(base,[(mask,"negative",.08)]),
                   f"Neg sigma1 | t={th:.2f}, minarea={area}"))
        dest=OUT/f"{role}_{ordinal:04d}_negative_threshold_area_review_v1.png"
        artifacts.append({"name":dest.name,"sha256":sheet(panels,2,4,
            f"{role} {ordinal} | negative plume-like candidates: spatial specificity",dest)})
    def to_csv(name,rows):
        p=OUT/name
        with p.open("x",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]))
            w.writeheader();w.writerows(rows)
        artifacts.append({"name":p.name,"sha256":sha(p)})
    to_csv("focused_positive_parameter_sweep.csv",records)
    to_csv("focused_negative_parameter_sweep.csv",negative)
    scientific={"schema":"ga-in-2014-04-04-focused-human-review-v1",
      "status":"EXPLORATORY_PARAMETER_SENSITIVITY_NO_INDEPENDENT_PHASE_GROUND_TRUTH",
      "original_archive_sha256":SOURCE_ARCHIVE_SHA,
      "original_authoritative_benchmark_manifest_sha256":sha(ORIGINAL_BENCH),
      "original_18_review_masks_unmodified_and_pixel_exactly_recomputed":True,
      "source_frames_crc_checked":len(FRAMES),
      "original_reference_tiffs_crc_checked":len(exp["reference"]),
      "original_provisional_sample_J0_tiffs_crc_checked":80,
      "ref_is_detector_flat_field":True,
      "provisional_sample_J0_is_original_main_0_to_79_median":True,
      "original_source_detector_xy":[761,426],
      "candidate_analysis_roi_y0_y1_x0_x1_unreviewed":list(ROI),
      "filters":list(FILTERS),
      "positive_thresholds":list(POS_THRESHOLDS),
      "negative_thresholds":list(NEG_THRESHOLDS),
      "negative_component_minimums":list(NEG_MIN_AREA),
      "upper_strip_y0_y1_x0_x1_unapproved":list(UPPER_STRIP),
      "central_channel_y0_y1_x0_x1_unapproved":list(CENTRAL_CHANNEL_DIAGNOSTIC),
      "uncertain_label_is_only_additional_low_contrast_candidate":True,
      "negative_regions_not_chemically_confirmed_plumes":True,
      "positive_regions_not_Phase_fraction_or_solid_ground_truth":True,
      "camera_clock_not_verified":True,
      "dark_current_not_applied":True,
      "source_frame_comparisons":per_frame,
      "numerical_positive_rows":len(records),
      "numerical_negative_rows":len(negative),
      "artifacts":artifacts,
      "scientific_cautions":[
        "Expanded positive candidate mask may include more true solid but also false positive liquid/noise",
        "Weak added positives in amber are explicitly uncertain candidates, not a new solid phase",
        "Area opening on negative masks can suppress real small fluid features as well as false positives",
        "Upper/central diagnostic subregions do NOT encode user screenshot box pixel coordinate registration",
        "No independent annotations or physical chamber ROI have yet been provided",
        "Original intensity-to-In composition mapping and full native temporal v25 MIL remain unaccepted",
      ],
    }
    out=OUT/"focused_sensitivity_manifest.json"
    out.write_text(json.dumps(scientific,indent=2,allow_nan=False)+"\n")
    print("SOURCE VERIFIED",len(FRAMES),"frames; PARAM rows",len(records),"positive and",len(negative),"negative")
    print("original source masks unchanged/recomputed",18)
    print("OUTPUT",OUT)
    for r in per_frame:print("RESULT",r)
    for case in (("main",1200),("main",3147),("end",297)):
        for th in (.04,.06,.08):
            neg=[r for r in negative if (r["role"],r["ordinal0"])==case and r["filter"]=="gaussian_1px"
                 and r["threshold_log_abs"]==th and r["min_component_px"]==25][0]
            print("NEG",case,th,"total",neg["negative_candidate_pixels_total"],
                "upper",neg["upper_strip_candidate_pixels"],
                "center",neg["center_channel_candidate_pixels"])
    print("MANIFEST SHA",sha(out))
if __name__=="__main__":
    main()
