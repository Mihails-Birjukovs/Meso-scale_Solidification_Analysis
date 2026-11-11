"""Source-hashed, flat-field-normalized timeline preflight for 2014-04-04 Ga-In.

Only descriptive full-detector image statistics and filename-clock segmentation.
This is NOT original Mathematica v25 MIL, ROI/phase segmentation, measured dark
correction, an accepted instrument timebase, or composition calibration.

Requires previously extracted private TIFFs and the SHA-verified 7z inventory.
Never redistributes or alters experiment or flat-field TIFFs.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import re
import zlib

import numpy as np
import tifffile


class AdmissionError(ValueError):
    """Source identity, radiometric format, or timeline cannot be admitted."""


def _records(inventory: dict) -> dict[str, list[dict]]:
    if (inventory.get("schema") != "ga-in-archive-inventory/v1"
            or inventory.get("case_id") != "2014-04-04"
            or not inventory.get("archive_sha256_verified")
            or not inventory.get("flat_field_role_confirmed")
            or inventory.get("reference_recording_role")
            != "flat_field_correction_owner_confirmed"):
        raise AdmissionError("Require SHA-verified 2014-04-04 inventory with confirmed flat-field role")
    raw = inventory.get("filename_candidate_frame_records")
    if not isinstance(raw, dict) or set(raw) != {"reference", "main", "end"}:
        raise AdmissionError("Missing exact reference/main/end source roles")
    streams = inventory.get("streams")
    if not isinstance(streams, dict):
        raise AdmissionError("Missing validated archive stream counts")
    seen = set()
    for role in ("reference", "main", "end"):
        recs = raw[role]
        if not isinstance(recs, list) or len(recs) < 1:
            raise AdmissionError(f"No {role} records")
        if streams.get(role, {}).get("count") != len(recs):
            raise AdmissionError(f"{role}: inventory count mismatch")
        previous = None
        for i, e in enumerate(recs):
            if not isinstance(e, dict):
                raise AdmissionError("Unexpected record")
            name = e.get("filename")
            if (not isinstance(name, str) or not name.endswith(".tif")
                    or name != Path(name).name or "\\" in name or "/" in name
                    or name in seen):
                raise AdmissionError("Invalid, repeated or unsafe source filename")
            seen.add(name)
            if e.get("candidate_ordinal_id_zero_based") != i:
                raise AdmissionError(f"{role}: ordinal missing or out of order")
            ms = e.get("filename_clock_ms")
            if type(ms) is not int or (previous is not None and ms <= previous):
                raise AdmissionError(f"{role}: nonmonotonic filename clock")
            previous = ms
            crc = e.get("member_crc32_header_unverified")
            size = e.get("member_size_bytes")
            if not isinstance(crc, str) or not re.fullmatch("[0-9A-Fa-f]{8}", crc):
                raise AdmissionError("Missing original 7z member CRC metadata")
            if type(size) is not int or size < 1:
                raise AdmissionError("Invalid archived TIFF member size")
    return raw


def _decode_and_check(path: Path, record: dict, shape_yx: tuple[int, int]) -> np.ndarray:
    if not path.is_file() or path.stat().st_size != record["member_size_bytes"]:
        raise AdmissionError(f"Missing or wrong-sized extracted TIFF: {path.name}")
    crc = 0
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            crc = zlib.crc32(chunk, crc)
    if f"{crc & 0xffffffff:08X}" != record["member_crc32_header_unverified"].upper():
        raise AdmissionError(f"Member CRC mismatch: {path.name}")
    with tifffile.TiffFile(path) as tf:
        if len(tf.pages) != 1:
            raise AdmissionError("Multiple TIFF pages not admitted")
        page = tf.pages[0]
        if page.bitspersample != 16 or page.samplesperpixel != 1:
            raise AdmissionError("Unexpected TIFF channels/sample depth")
        image = page.asarray()
    if image.dtype != np.uint16 or image.shape != shape_yx:
        raise AdmissionError(f"Invalid original TIFF shape/type: {path.name}")
    return image


def build_trace(
    inventory: dict, flat_field_dir: Path, experimental_dir: Path,
    *, expected_shape_yx: tuple[int, int] = (426, 761),
    flat_field_train_n: int = 80, max_candidate_frame_gap_s: float = 1.5,
) -> tuple[dict, list[dict]]:
    """Fully check source CRCs; emit descriptive uncalibrated quantities only."""
    recs = _records(inventory)
    if (len(expected_shape_yx) != 2 or any(type(x) is not int or x <= 0
                                            for x in expected_shape_yx)):
        raise AdmissionError("Positive expected source TIFF dimensions required")
    if (type(flat_field_train_n) is not int
            or not 2 <= flat_field_train_n < len(recs["reference"])):
        raise AdmissionError("Require separate flat-field training and held-out frames")
    if (not math.isfinite(max_candidate_frame_gap_s)
            or max_candidate_frame_gap_s <= 0):
        raise AdmissionError("Invalid candidate filename-gap threshold")

    expected_ref = {r["filename"] for r in recs["reference"]}
    expected_exp = {r["filename"] for role in ("main", "end") for r in recs[role]}
    if ({p.name for p in flat_field_dir.glob("*.tif")} != expected_ref
            or {p.name for p in experimental_dir.glob("*.tif")} != expected_exp):
        raise AdmissionError("Extracted TIFF set differs from exact archive filename inventory")
    refs = [_decode_and_check(flat_field_dir / r["filename"], r, expected_shape_yx)
            for r in recs["reference"]]
    stack = np.stack(refs, axis=0)
    # These are detector-level positivity/saturation checks, NOT an accepted cell ROI.
    usable_flat = np.all((stack > 0) & (stack < 65535), axis=0)
    if not usable_flat.any():
        raise AdmissionError("No consistently nonsaturated flat-field detector pixels")
    R = np.median(stack[:flat_field_train_n], axis=0).astype(np.float64)
    del refs, stack

    rows = []
    gaps = []
    last_t = None
    last_role = None
    last_filename = None
    group = 0
    for role in ("main", "end"):
        for item in recs[role]:
            img = _decode_and_check(experimental_dir / item["filename"],
                                    item, expected_shape_yx)
            t = item["filename_clock_ms"]
            dt_s = None if last_t is None else (t - last_t) / 1000.0
            if dt_s is not None and dt_s <= 0:
                raise AdmissionError("Experiment filename clock reversed")
            split = last_role != role or (dt_s is not None and dt_s > max_candidate_frame_gap_s)
            if split:
                group += 1
                if last_role is not None:
                    gaps.append({
                        "previous_role": last_role, "next_role": role,
                        "previous_filename": last_filename, "next_filename": item["filename"],
                        "candidate_filename_dt_s": dt_s,
                        "new_contiguous_group": group,
                    })
            valid = usable_flat & (img > 0) & (img < 65535)
            if not valid.any():
                raise AdmissionError("No jointly valid detector pixels for TIFF")
            p = -np.log(img[valid].astype(np.float64) / R[valid])
            rows.append({
                "global_source_ordinal_zero_based": len(rows),
                "stream_role": role,
                "stream_source_ordinal_zero_based": item["candidate_ordinal_id_zero_based"],
                "contiguous_filename_clock_group": group,
                "break_before": bool(split),
                "filename": item["filename"],
                "candidate_filename_clock_ms": t,
                "candidate_dt_from_previous_in_same_role_s": dt_s if role == last_role else None,
                "detector_jointly_valid_fraction": float(valid.mean()),
                "detector_at_65535_fraction": float(np.mean(img == 65535)),
                "mean_raw_counts": float(img.mean()),
                "mean_flat_field_log_ratio": float(p.mean()),
                "median_flat_field_log_ratio": float(np.median(p)),
            })
            last_t, last_role, last_filename = t, role, item["filename"]

    segments = []
    for index in range(1, group + 1):
        subset = [r for r in rows if r["contiguous_filename_clock_group"] == index]
        segments.append({
            "segment": index, "role": subset[0]["stream_role"],
            "count": len(subset), "first_filename": subset[0]["filename"],
            "last_filename": subset[-1]["filename"],
        })
    report = {
        "schema": "ga-in-source-flatfield-time-preflight/v1",
        "case_id": "2014-04-04",
        "status": "SOURCE_CRC_TIMELINE_ONLY_NO_PHYSICAL_CALIBRATION",
        "archive_sha256": inventory["archive_sha256"],
        "flat_field_role": "owner_confirmed_detector_flat_field_recording",
        "flat_field_source_frames_crc_checked": len(recs["reference"]),
        "flat_field_train_frames": flat_field_train_n,
        "flat_field_holdout_frames": len(recs["reference"]) - flat_field_train_n,
        "experiment_source_frames_crc_checked": len(rows),
        "shape_yx": list(expected_shape_yx),
        "flat_field_temporally_valid_detector_fraction": float(usable_flat.mean()),
        "candidate_filename_gap_threshold_s": max_candidate_frame_gap_s,
        "contiguous_candidate_segments": segments,
        "timestamp_discontinuities": gaps,
        "filename_clock_is_verified_camera_time": False,
        "measured_dark_admitted": False,
        "separate_homogeneous_25wtpct_sample_baseline_admitted": False,
        "physical_cell_or_liquid_roi_admitted": False,
        "original_v25_mil_reproduced_by_this_code": False,
        "composition_wt_pct_admitted": False,
        "ofv_time_or_image_registration_admitted": False,
    }
    return report, rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inventory", type=Path, required=True)
    ap.add_argument("--flat-field-dir", type=Path, required=True)
    ap.add_argument("--experiment-dir", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--out-csv", type=Path, required=True)
    ap.add_argument("--shape-yx", type=int, nargs=2, default=(426, 761))
    ap.add_argument("--flat-field-train", type=int, default=80)
    ap.add_argument("--filename-gap-threshold-s", type=float, default=1.5)
    args = ap.parse_args()
    if args.out_json.resolve() == args.out_csv.resolve():
        ap.error("Separate output paths are required")
    if args.out_json.exists() or args.out_csv.exists():
        ap.error("Refusing overwrite of prior analysis")
    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    report, rows = build_trace(inventory, args.flat_field_dir, args.experiment_dir,
                               expected_shape_yx=tuple(args.shape_yx),
                               flat_field_train_n=args.flat_field_train,
                               max_candidate_frame_gap_s=args.filename_gap_threshold_s)
    for out in (args.out_json, args.out_csv):
        out.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("x", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    args.out_json.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n",
                             encoding="utf-8")
    print(f"flat_field_crc={report['flat_field_source_frames_crc_checked']} "
          f"experiment_crc={report['experiment_source_frames_crc_checked']} "
          f"candidate_segments={len(report['contiguous_candidate_segments'])} "
          "camera_clock=False composition=False")


if __name__ == "__main__":
    main()
