"""Read-only candidate initial-sample baseline against SHA-verified original TIFFs.

Reference/ is detector flat-field R. This utility instead uses a selected EARLY
*experiment* image stack as provisional specimen J0; no sample 25 wt% In
homogeneity, chamber ROI, instrument clock, phase labels or chemical
calibration is automatically admitted.

Only raw counts and the flat-only branch are used here. For same unchanged R,
-ln((I_t/R)/(I_initial/R)) == -ln(I_t/I_initial), but additive detector dark
bias can invalidate quantitative physical attenuation even if this ratio is
numerically stable. Do NOT call this a validated composition map.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import zlib

import numpy as np
import tifffile


class BaselineGateError(ValueError):
    """Incomplete source, geometry or specimen-baseline admission."""


def _check_one(path: Path, frame: dict, shape_yx: tuple[int, int]) -> np.ndarray:
    if not path.is_file() or path.stat().st_size != frame["member_size_bytes"]:
        raise BaselineGateError("Missing or changed original source TIFF")
    crc=0
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):
            crc=zlib.crc32(chunk,crc)
    if f"{crc & 0xffffffff:08X}" != frame["member_crc32_header_unverified"].upper():
        raise BaselineGateError("Source member CRC mismatch")
    with tifffile.TiffFile(path) as tf:
        if len(tf.pages)!=1 or tf.pages[0].bitspersample!=16 or tf.pages[0].samplesperpixel!=1:
            raise BaselineGateError("Invalid source TIFF metadata")
        img=tf.pages[0].asarray()
    if img.dtype != np.uint16 or img.shape != shape_yx:
        raise BaselineGateError("Unexpected raw image shape or datatype")
    return img


def probe(
    inventory: dict, original_main_dir: Path, *, region_yx: tuple[int,int,int,int],
    train_n: int=80, heldout_n: int=40, sample_ordinals: tuple[int,...]=(0,79,119,720,1800,3147),
    shape_yx: tuple[int,int]=(426,761),
) -> dict:
    if (inventory.get("schema")!="ga-in-archive-inventory/v1"
        or inventory.get("case_id")!="2014-04-04"
        or not inventory.get("archive_sha256_verified")
        or not inventory.get("flat_field_role_confirmed")
        or inventory.get("reference_recording_role")!="flat_field_correction_owner_confirmed"):
        raise BaselineGateError("Require provenance-checked archive and owner-confirmed flat-field role")
    records=inventory.get("filename_candidate_frame_records",{}).get("main",[])
    if not isinstance(records,list):
        raise BaselineGateError("Missing main experimental stream")
    if type(train_n) is not int or type(heldout_n) is not int or train_n<2 or heldout_n<2:
        raise BaselineGateError("Nontrivial train/holdout sequence required")
    if len(records)<train_n+heldout_n:
        raise BaselineGateError("Insufficient source frames")
    if (len(shape_yx)!=2 or len(region_yx)!=4
        or any(type(x) is not int for x in (*shape_yx,*region_yx))):
        raise BaselineGateError("Integer raw geometry and ROI required")
    H,W=shape_yx
    y0,y1,x0,x1=region_yx
    if not (0<=y0<y1<=H and 0<=x0<x1<=W):
        raise BaselineGateError("Candidate ROI outside original source geometry")
    ordinals=tuple(sorted(set(range(train_n+heldout_n))|set(sample_ordinals)))
    if any(type(i) is not int or i<0 or i>=len(records) for i in ordinals):
        raise BaselineGateError("Invalid original source ordinal")
    # The early baseline must not silently cross an archive filename gap.
    t=[records[i]["filename_clock_ms"] for i in range(train_n+heldout_n)]
    if (any(records[i]["candidate_ordinal_id_zero_based"]!=i for i in ordinals)
        or any(t2<=t1 or t2-t1>1500 for t1,t2 in zip(t,t[1:]))):
        raise BaselineGateError("Early specimen window has noncontiguous filename time/ordinals")
    if len({records[i]["filename"] for i in ordinals})!=len(ordinals):
        raise BaselineGateError("Duplicate archive source filename")
    imgs={i:_check_one(original_main_dir/records[i]["filename"],records[i],shape_yx)
          for i in ordinals}
    baseline=np.median(
        np.stack([imgs[i] for i in range(train_n)],axis=0),axis=0)
    candidate_valid=(baseline>0)&(baseline<65535)
    region_valid=candidate_valid[y0:y1,x0:x1]
    if region_valid.mean()<0.5:
        raise BaselineGateError("Most of candidate sample ROI invalid at baseline")
    def describe(i):
        img=imgs[i][y0:y1,x0:x1]
        rr=baseline[y0:y1,x0:x1]
        valid=region_valid&(img>0)&(img<65535)
        if not valid.any():raise BaselineGateError("No valid sample pixels")
        p=-np.log(img[valid].astype(float)/rr[valid])
        return {
            "ordinal_main_zero_based":i,
            "filename":records[i]["filename"],
            "candidate_filename_clock_ms":records[i]["filename_clock_ms"],
            "median_provisional_specimen_log_ratio":float(np.median(p)),
            "p05_provisional_specimen_log_ratio":float(np.percentile(p,5)),
            "p95_provisional_specimen_log_ratio":float(np.percentile(p,95)),
            "valid_fraction_of_candidate_ROI":float(valid.mean()),
        }
    heldout=[describe(i) for i in range(train_n,train_n+heldout_n)]
    sampled=[describe(i) for i in sample_ordinals]
    return {
        "schema":"ga-in-2014-04-04-provisional-J0-admission/v1",
        "status":"CANDIDATE_SPECIMEN_BASELINE_NOT_EXPERT_ACCEPTED",
        "original_archive_sha256":inventory["archive_sha256"],
        "role_Reference":"detector_flat_field_R_not_J0",
        "candidate_specimen_J0":"per-pixel median of first contiguous experimental source TIFFs",
        "train_source_frames":train_n,
        "heldout_source_frames":heldout_n,
        "candidate_sample_roi_y0_y1_x0_x1":list(region_yx),
        "candidate_roi_valid_fraction":float(region_valid.mean()),
        "max_absolute_holdout_frame_median_P":float(max(abs(r["median_provisional_specimen_log_ratio"]) for r in heldout)),
        "heldout_per_frame":heldout,
        "sample_frames":sampled,
        "source_tiff_shape_yx":list(shape_yx),
        "raw_source_crc_checked_selected_count":len(imgs),
        "mode":"flat_only",
        "independent_expert_phase_and_ROI_review":False,
        "initial_25wtpct_composition_verified":False,
        "actual_camera_clock_verified":False,
        "dark_detector_offset_admitted":False,
        "chemical_concentration_calibration_admitted":False,
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inventory",type=Path,required=True)
    ap.add_argument("--main-dir",type=Path,required=True)
    ap.add_argument("--region-y0-y1-x0-x1",nargs=4,type=int,required=True)
    ap.add_argument("--train",type=int,default=80)
    ap.add_argument("--heldout",type=int,default=40)
    ap.add_argument("--sample-ordinals",nargs="+",type=int,default=[0,79,119,720,1800,3147])
    ap.add_argument("--shape-yx",nargs=2,type=int,default=[426,761])
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    if a.output.exists():ap.error("Output exists; refuse overwrite")
    inventory=json.loads(a.inventory.read_text(encoding="utf-8"))
    report=probe(inventory,a.main_dir,region_yx=tuple(a.region_y0_y1_x0_x1),
                 train_n=a.train,heldout_n=a.heldout,
                 sample_ordinals=tuple(a.sample_ordinals),shape_yx=tuple(a.shape_yx))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print("provisional_J0_only heldout_max_abs_median=",
          report["max_absolute_holdout_frame_median_P"],
          "sample_phase_accepted=False composition_calibration=False")


if __name__=="__main__":
    main()
