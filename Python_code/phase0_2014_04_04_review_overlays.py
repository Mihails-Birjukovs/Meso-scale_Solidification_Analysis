"""Presentation-only pixel-aligned overlays for the 2014-04-04 candidate mask benchmark.

Run on authorized private X: input. Checks original SHA-pinned archive metadata,
original TIFF member CRCs, all existing mask SHA-256 values, and independently
recomputes the benchmark's Gaussian-1 / |log contrast| > 0.04 / area>=25 masks.

OUTPUTS NEVER ALTER the original data, existing masks or numerical benchmark.
Source coordinates 761 x 426, left/top origin; Reference is detector flat field,
not the provisional initial specimen J0 (main source ordinals 0-79).
Every output remains a review aid, NOT a verified solid/liquid phase mask.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import textwrap
import zlib
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
import tifffile
import matplotlib
matplotlib.use("Agg")
from matplotlib import cm

CASE_SHA = "77fac9a38a9cdaa41ee5ec9c9562acb7149ee1cee8f0246a80c2b267928f2510"
ROOT = Path(r"X:\AI-Lab-Test\Solidification_OFV\analysis_outputs\phase0_2014-04-04_mil_candidate_benchmark_2026-11-14")
BASE = Path(r"X:\AI-Lab-Test\Solidification_OFV\analysis_outputs")
CAND = ROOT / "candidate_sweep_v2_conda"
INV = BASE / "phase0_2014-04-04_archive_admission_2026-11-11" / "inventory_flatfield_role_v2.json"
SOURCE = BASE / "phase0_2014-04-04_fullsource_preflight_2026-11-11" / "raw_extracted" / "2014-04-04" / "2014-04-04"
REF = BASE / "phase0_2014-04-04_archive_admission_2026-11-11" / "reference_samples" / "2014-04-04" / "Reference"
OUT = ROOT / "review_overlays_v1"
ZIP = ROOT / "review_overlays_v1.zip"
SHAPE = (426, 761)
ROI = (120, 412, 155, 690)  # only the unapproved candidate rectangle
SELECTED = (("main",119),("main",480),("main",639),("main",1200),("main",3147),("end",297))
POLARITIES = ("positive","negative","absolute")
COLOR_POS = np.array([255,43,53], np.float32)
COLOR_NEG = np.array([27,235,240], np.float32)
CITATION = "Candidate mask overlay | NOT validated solid/liquid or physical ROI"
VMIN, VMAX = -0.12, 0.12
ALPHA = 0.24

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()

def load_verified_raw(path: Path, record: dict):
    if path.name != record["filename"] or path.stat().st_size != record["member_size_bytes"]:
        raise ValueError("Original TIFF name/size mismatch: " + str(path))
    crc=0
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            crc=zlib.crc32(chunk,crc)
    if f"{crc & 0xffffffff:08X}" != record["member_crc32_header_unverified"].upper():
        raise ValueError("Original member CRC mismatch: "+str(path))
    with tifffile.TiffFile(path) as f:
        if len(f.pages) != 1 or f.pages[0].bitspersample != 16 or f.pages[0].samplesperpixel != 1:
            raise ValueError("Original TIFF pixel encoding changed")
        img=f.pages[0].asarray()
    if img.shape!=SHAPE or img.dtype!=np.uint16:
        raise ValueError("Expected source uint16 426x761 detector image")
    return img

def load_mask(path:Path, expected_sha:str):
    if digest(path) != expected_sha:
        raise ValueError("Existing candidate mask checksum mismatch: "+path.name)
    with Image.open(path) as im:
        a=np.asarray(im)
    if a.shape != SHAPE or not np.isin(a, [0,255]).all():
        raise ValueError("Existing mask has wrong geometry or values: "+path.name)
    return a > 0

def independently_recompute(frame, j0, refvalid, polarity):
    valid=refvalid&(frame>0)&(frame<65535)&(j0>0)&(j0<65535)
    p=np.zeros(SHAPE,dtype=np.float64)
    p[valid]=-np.log(frame[valid].astype(np.float64)/j0[valid])
    weight=ndi.gaussian_filter(valid.astype(float),1.0,mode="nearest")
    numerator=ndi.gaussian_filter(np.where(valid,p,0.0),1.0,mode="nearest")
    filtvalid=valid&(weight>=0.999)
    filtered=np.zeros(SHAPE,float)
    filtered[filtvalid]=numerator[filtvalid]/weight[filtvalid]
    if polarity=="positive": rawmask=filtered>0.04
    elif polarity=="negative": rawmask=filtered< -0.04
    elif polarity=="absolute": rawmask=np.abs(filtered)>0.04
    else: raise ValueError(polarity)
    y0,y1,x0,x1=ROI
    region=np.zeros(SHAPE,bool);region[y0:y1,x0:x1]=True
    rawmask &= filtvalid & region
    label,n=ndi.label(rawmask,structure=ndi.generate_binary_structure(2,1))
    sizes=np.bincount(label.ravel())
    keep=sizes>=25
    keep[0]=False
    return keep[label],p,valid

def outline(mask):
    return mask & ~ndi.binary_erosion(mask,structure=np.ones((3,3),dtype=bool),border_value=0)

def make_heat(p,valid):
    normalized=np.clip((p-VMIN)/(VMAX-VMIN),0,1)
    rgb=(cm.get_cmap("coolwarm")(normalized)[...,:3]*255).astype(np.uint8)
    rgb[~valid]=[30,32,38]
    return rgb

def paint(base, masks, *, positive=False, negative=False, filled=False):
    rgb=base.astype(np.float32).copy()
    for choice,flag,color in (("positive",positive,COLOR_POS),("negative",negative,COLOR_NEG)):
        if not flag:
            continue
        m=masks[choice]
        if filled:
            rgb[m]=(1-ALPHA)*rgb[m]+ALPHA*color
    rgb=np.clip(rgb,0,255).astype(np.uint8)
    # A black one-pixel halo makes red boundaries visible even on red heatmap areas.
    for choice,flag,color in (("positive",positive,COLOR_POS),("negative",negative,COLOR_NEG)):
        if not flag:
            continue
        edge=outline(masks[choice])
        halo=ndi.binary_dilation(edge,iterations=1)
        rgb[halo]=[0,0,0]
        rgb[edge]=color.astype(np.uint8)
    return rgb

def font(size):
    try:
        return ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf",size)
    except OSError:
        return ImageFont.load_default()

def make_review_sheet(views, ident, per_frame=False):
    w=SHAPE[1];h=SHAPE[0]
    pad=16
    columns=5
    titlebar=62
    rowcaption=32
    rowheight=h+rowcaption+pad
    rows=len(views)
    banner=112 if not per_frame else 80
    page=Image.new("RGB",(columns*(w+pad)+pad,banner+rows*rowheight+pad),(21,24,30))
    draw=ImageDraw.Draw(page)
    draw.text((pad,12),"2014-04-04 | provisional -ln(I/J0) | candidate mask overlays",font=font(26),fill=(248,248,248))
    draw.text((pad,49),"Red = positive candidate   |   Cyan = negative candidate   |   outlines have 1-pixel dark halo",font=font(18),fill=(225,225,225))
    if not per_frame:
        draw.text((pad,78),"Unreviewed ROI y[120,412), x[155,690); no validated solid/liquid boundaries",font=font(18),fill=(255,210,130))
    colnames=("Provisional log ratio","Positive outline","Negative outline","Both outlines","Both + 24% fills")
    for row,(name,variant) in enumerate(views):
        basey=banner+row*rowheight
        for col,label in enumerate(colnames):
            x=pad+col*(w+pad)
            draw.text((x,basey),f"{name} — {label}",font=font(18),fill=(230,230,230))
            page.paste(Image.fromarray(variant[label]),(x,basey+rowcaption))
    return page

def main():
    if OUT.exists() or ZIP.exists():
        raise RuntimeError("A review overlay output already exists; refusing overwrite")
    inventory=json.loads(INV.read_text(encoding="utf-8"))
    source_list=inventory["filename_candidate_frame_records"]
    existing=json.loads((CAND/"benchmark_manifest.json").read_text(encoding="utf-8"))
    if (inventory.get("archive_sha256")!=CASE_SHA
            or not inventory.get("archive_sha256_verified")
            or inventory.get("reference_recording_role")!="flat_field_correction_owner_confirmed"
            or existing.get("original_archive_sha256")!=CASE_SHA
            or existing.get("candidate_ROI_y0_y1_x0_x1")!=list(ROI)
            or existing.get("summary_rows")!=756):
        raise ValueError("Benchmark identity / raw Reference role / ROI / experiment matrix changed")
    mask_map={}
    original_hashes={}
    for rec in existing["review_output_masks"]:
        key=(rec["source_role"],rec["source_ordinal0"],rec["polarity"])
        mask_map[key]=(CAND/"review_binary_masks"/rec["name"],rec["sha256"])
        original_hashes[rec["name"]]=rec["sha256"]
    if len(mask_map)!=18:
        raise ValueError("Expected exactly 18 source-hashed original mask files")
    # All source-input checks happen before output directory is created.
    reference_stack=np.stack([
        load_verified_raw(REF/r["filename"],r)
        for r in source_list["reference"]])
    refvalid=np.all((reference_stack>0)&(reference_stack<65535),axis=0)
    initial=np.median(np.stack([
        load_verified_raw(SOURCE/r["filename"],r)
        for r in source_list["main"][:80]]),axis=0)
    del reference_stack
    prepared=[]
    for role,idx in SELECTED:
        record=source_list[role][idx]
        original=load_verified_raw(SOURCE/record["filename"],record)
        masks={}
        log=None; valid=None
        for pol in POLARITIES:
            path,hashval=mask_map[(role,idx,pol)]
            existingmask=load_mask(path,hashval)
            regen,p,validp=independently_recompute(original,initial,refvalid,pol)
            if not np.array_equal(existingmask,regen):
                raise ValueError("Existing mask differs from independently reconstructed mask: "+path.name)
            masks[pol]=existingmask
            log=p;valid=validp
        if np.any(masks["positive"] & masks["negative"]):
            raise ValueError("Positive/negative sign masks overlap")
        heat=make_heat(log,valid)
        variants={
          "Provisional log ratio":heat,
          "Positive outline":paint(heat,masks,positive=True),
          "Negative outline":paint(heat,masks,negative=True),
          "Both outlines":paint(heat,masks,positive=True,negative=True),
          "Both + 24% fills":paint(heat,masks,positive=True,negative=True,filled=True),
        }
        prepared.append({"name":f"{role} {idx:04d}","role":role,"ordinal":idx,"record":record,
                         "masks":masks,"variants":variants})
    OUT.mkdir(parents=True,exist_ok=False)
    artifacts=[]
    reportframes=[]
    for f in prepared:
        stem=f"{f['role']}_{f['ordinal']:04d}"
        filenames=[]
        tag={
          "Provisional log ratio":"lnJ0_heatmap",
          "Positive outline":"lnJ0_outline_pos",
          "Negative outline":"lnJ0_outline_neg",
          "Both outlines":"lnJ0_outline_posneg",
          "Both + 24% fills":"lnJ0_filled_posneg",
        }
        for title, pixels in f["variants"].items():
            dest=OUT/(stem+"_"+tag[title]+".png")
            Image.fromarray(pixels).save(dest,optimize=False)
            with Image.open(dest) as re:
                if re.size!=(761,426):raise RuntimeError("Native source detector pixel resolution changed")
            filenames.append(dest.name)
            artifacts.append({"filename":dest.name,"sha256":digest(dest),
                              "source_dimensions_wh":[761,426],"variant":tag[title]})
        pane=make_review_sheet([(f["name"],f["variants"])],stem,per_frame=True)
        dest=OUT/(stem+"_all_views.png")
        pane.save(dest)
        artifacts.append({"filename":dest.name,"sha256":digest(dest),"variant":"five_column_frame_review"})
        reportframes.append({"role":f["role"],"ordinal":f["ordinal"],
                            "original_filename":f["record"]["filename"],
                            "filename_candidate_clock_ms":f["record"]["filename_clock_ms"],
                            "existing_masks_checked_sha256":{
                               pol:mask_map[(f["role"],f["ordinal"],pol)][1] for pol in POLARITIES},
                            "independent_mask_exact_pixel_match":True,
                            "positive_mask_pixels":int(f["masks"]["positive"].sum()),
                            "negative_mask_pixels":int(f["masks"]["negative"].sum()),
                            "overlay_files":filenames+[dest.name]})
    sheet=make_review_sheet([(f["name"],f["variants"]) for f in prepared],
                            "combined_contact_sheet")
    sheet_file=OUT/"review_overlay_contact_sheet_v1.png"
    sheet.save(sheet_file)
    artifacts.append({"filename":sheet_file.name,"sha256":digest(sheet_file),
                      "variant":"six_source_five_column_contact_sheet"})
    # Ensure original benchmark masks were not modified or replaced.
    for name,hashval in original_hashes.items():
        if digest(CAND/"review_binary_masks"/name)!=hashval:
            raise RuntimeError("Authoritative source mask hash changed after overlay creation")
    report={
      "schema":"ga-in-2014-04-04-review-overlays/v1",
      "status":"SOURCE_AND_MASK_HASH_VERIFIED_PRESENTATION_ONLY_NOT_PHASE_GROUND_TRUTH",
      "original_archive_sha256":CASE_SHA,
      "original_benchmark_manifest_sha256":digest(CAND/"benchmark_manifest.json"),
      "original_masks_unchanged_sha256_count":len(original_hashes),
      "original_source_geometry_xy":[761,426],
      "source_coordinate_origin":"upper_left_x_right_y_down",
      "provisional_specimen_J0":"median first 80 original main frames; NOT Reference flat field",
      "flat_field_R":"separate owner-confirmed Reference recordings; used for invalid detector pixel screening",
      "dark_subtraction":False,
      "flat_only_working_branch":True,
      "provisional_log_image_colormap":"coolwarm",
      "fixed_log_display_range":[VMIN,VMAX],
      "invalid_pixels_rgb":[30,32,38],
      "outlines":{"positive":"red_RGB_255_43_53","negative":"cyan_RGB_27_235_240",
                  "edge":"one_source_pixel_black_halo_then_one_source_pixel_colored_boundary"},
      "fill_opacity":ALPHA,
      "mask_filter":"gaussian_1px",
      "mask_abs_log_threshold":0.04,
      "mask_component_minimum_px":25,
      "candidate_analysis_roi_y0_y1_x0_x1_unreviewed":list(ROI),
      "source_mask_pixel_exactly_reproduced":True,
      "expert_review_of_physical_chamber_roi":False,
      "phase_or_chemical_label_admitted":False,
      "camera_clock_admitted":False,
      "numerical_benchmark_modified":False,
      "independently_verified_frames":reportframes,
      "artifacts":artifacts,
    }
    manifest=OUT/"review_overlay_manifest_v1.json"
    manifest.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    with zipfile.ZipFile(ZIP,"x",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as zipf:
        for path in sorted(OUT.iterdir()):
            if path.is_file():zipf.write(path,arcname=path.name)
    print("SAVED",OUT)
    print("CHECKED source: 111 Reference, 80 original baseline, six original selected TIFFs; original 18 masks")
    print("EXACT_MASK_MATCH all 18, source-native pixel overlay dimensions 761x426")
    print("OUTPUT_COUNT",len(artifacts),"ZIP_BYTES",ZIP.stat().st_size)
    print("CONTACT_SHA256",digest(sheet_file))
    print("MANIFEST_SHA256",digest(manifest))
    print("ZIP_SHA256",digest(ZIP))
    print("NUMERICAL_BENCHMARK_UNMODIFIED")
if __name__=="__main__":
    main()
