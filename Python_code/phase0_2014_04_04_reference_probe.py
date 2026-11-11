"""Read-only, provenance-checked raw-reference and log-contrast diagnostic.

The Reference folder contains flat-field correction recordings (owner-confirmed),
not a homogeneous-alloy composition baseline. This code never
assigns 25/5-10/98.6 wt.% In, assumes a dark frame, identifies a liquid mask,
or certifies a camera clock. Input TIFFs must already have been extracted
privately from the admission-checked archive.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import zlib
from pathlib import Path

import numpy as np
import tifffile
from PIL import Image, __version__ as pillow_version

REPORT_SCHEMA = "ga-in-flat-field-raw-diagnostic/v2"
REF_PATTERN = re.compile(
    r"ga-25in-ref1_2014-04-04_(\d{2})-(\d{2})-(\d{2})-(\d{3})\.tif",
    re.ASCII,
)


class DiagnosticError(ValueError):
    """Cannot treat the input as a provenance-checked raw reference series."""


def quantiles(data):
    values = np.asarray(data, dtype=np.float64)
    if values.size == 0 or not np.isfinite(values).all():
        raise DiagnosticError("Empty or nonfinite statistic population")
    return {f"p{p:02d}": float(v) for p, v in
            zip((1, 5, 25, 50, 75, 95, 99),
                np.percentile(values, [1, 5, 25, 50, 75, 95, 99]))}


def reference_timestamp_ms(filename):
    match = REF_PATTERN.fullmatch(filename)
    if not match:
        raise DiagnosticError(f"Unexpected reference filename {filename}")
    h, minute, second, ms = (int(x) for x in match.groups())
    if h > 23 or minute > 59 or second > 59:
        raise DiagnosticError("Invalid filename clock component")
    return ((h * 60 + minute) * 60 + second) * 1000 + ms


def _member_map(inventory):
    if (inventory.get("schema") != "ga-in-archive-inventory/v1"
            or inventory.get("case_id") != "2014-04-04"
            or not inventory.get("archive_sha256_verified")):
        raise DiagnosticError("A SHA-checked 2014-04-04 inventory is required")
    records = inventory.get("filename_candidate_frame_records")
    if not isinstance(records, dict):
        raise DiagnosticError("An inventory with per-frame CRC records is required")
    result = {}
    for role in ("reference", "main", "end"):
        if not isinstance(records.get(role), list):
            raise DiagnosticError(f"Missing inventory role {role}")
        for entry in records[role]:
            filename = entry["filename"]
            if filename in result:
                raise DiagnosticError("Duplicate member filename in archive manifest")
            result[filename] = (role, entry)
    return result


def _check_extracted_member(path, expected):
    if path.stat().st_size != expected["member_size_bytes"]:
        raise DiagnosticError(f"File byte size differs from archive member: {path.name}")
    actual = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            actual = zlib.crc32(chunk, actual)
    if f"{actual & 0xffffffff:08X}" != expected["member_crc32_header_unverified"].upper():
        raise DiagnosticError(f"Archive member CRC disagrees: {path.name}")


def _read_tiff(path):
    with tifffile.TiffFile(path) as tf:
        if len(tf.pages) != 1:
            raise DiagnosticError("Only single-page raw radiographs are admitted")
        p = tf.pages[0]
        image = p.asarray()
        meta = {
            "shape_yx": list(image.shape),
            "dtype": str(image.dtype),
            "bitspersample": int(p.bitspersample),
            "samplesperpixel": int(p.samplesperpixel),
            "compression": int(p.compression),
            "photometric": str(p.photometric),
        }
    if image.ndim != 2 or image.dtype != np.uint16:
        raise DiagnosticError("Expected mono uint16 TIFF; not display-adjusted data")
    return image, meta


def _p_stats(image, flat_field_R, valid_reference):
    valid = valid_reference & (image > 0) & (image < 65535)
    if not valid.any():
        raise DiagnosticError("No nonsaturated reference-comparable pixels")
    p = -np.log(image[valid].astype(np.float64) / flat_field_R[valid])
    return {
        "valid_fraction_of_full_detector": float(valid.mean()),
        "median_flat_field_log_ratio": float(np.median(p)),
        "mean_flat_field_log_ratio": float(np.mean(p)),
        "quantiles_flat_field_log_ratio": quantiles(p),
        "negative_flat_field_log_ratio_fraction": float(np.mean(p < 0)),
    }


def examine(reference_dir: Path, inventory: dict, *, expected_n: int,
            reference_train_n: int, sample_dir: Path | None = None) -> tuple[dict, list[dict]]:
    if type(expected_n) is not int or expected_n < 3:
        raise DiagnosticError("Expected reference count must be at least 3")
    if type(reference_train_n) is not int or not (2 <= reference_train_n < expected_n):
        raise DiagnosticError("Training reference count must leave a held-out block")
    members = _member_map(inventory)
    refs = sorted(reference_dir.glob("*.tif"))
    if len(refs) != expected_n:
        raise DiagnosticError(f"Expected {expected_n} reference TIFFs; found {len(refs)}")
    manifest_names = {name for name, (role, _) in members.items() if role == "reference"}
    if len(manifest_names) != expected_n or {p.name for p in refs} != manifest_names:
        raise DiagnosticError("Extracted reference filenames differ from source inventory")
    ref_images = []
    series_rows = []
    meta = None
    stamps = []
    for path in refs:
        _check_extracted_member(path, members[path.name][1])
        stamp = reference_timestamp_ms(path.name)
        stamps.append(stamp)
        image, this_meta = _read_tiff(path)
        if meta is not None and meta != this_meta:
            raise DiagnosticError("Flat-field image geometry or encoding drift")
        meta = this_meta
        ref_images.append(image)
        series_rows.append({
            "filename": path.name,
            "candidate_filename_clock_ms": stamp,
            "raw_mean_counts": float(image.mean()),
            "raw_median_counts": float(np.median(image)),
            "fraction_at_uint16_max": float(np.mean(image == 65535)),
            "fraction_zero": float(np.mean(image == 0)),
        })
    if any(b <= a for a, b in zip(stamps, stamps[1:])):
        raise DiagnosticError("Reference filename clock is not increasing")
    stack = np.stack(ref_images)
    stable = np.all((stack > 0) & (stack < 65535), axis=0)
    if not stable.any():
        raise DiagnosticError("No pixel is valid through the reference series")
    temporal_median = np.median(stack, axis=0)
    temporal_mad = np.median(
        np.abs(stack.astype(np.float64) - temporal_median), axis=0)
    flat_field_R = np.median(stack[:reference_train_n], axis=0)
    per_frame_medians = [float(np.median(image[stable])) for image in ref_images]
    ref_median0 = per_frame_medians[0]
    ratios = np.array(per_frame_medians, dtype=np.float64) / ref_median0
    times = (np.array(stamps, dtype=np.float64) - stamps[0]) / 1000
    for row, ratio in zip(series_rows, ratios):
        row["stable_nonmax_median_ratio_to_first"] = float(ratio)
    agreement = []
    for i in sorted({0, expected_n // 2, expected_n - 1}):
        pil_image = np.array(Image.open(refs[i]))
        matched = pil_image.shape == ref_images[i].shape and np.array_equal(pil_image, ref_images[i])
        if not matched:
            raise DiagnosticError("Pillow and tifffile disagree on raw reference pixel values")
        agreement.append({"reference_ordinal_zero_based": i,
                          "exact_pixel_agreement": True})
    heldout_stats = [_p_stats(im, flat_field_R, stable)
                     for im in ref_images[reference_train_n:]]
    sample_stats = []
    if sample_dir is not None:
        paths = sorted(sample_dir.glob("*.tif"))
        if not paths:
            raise DiagnosticError("Selected experimental-sample folder is empty")
        for path in paths:
            info = members.get(path.name)
            if info is None or info[0] not in ("main", "end"):
                raise DiagnosticError("Experimental sample not in same archive inventory")
            _check_extracted_member(path, info[1])
            image, image_meta = _read_tiff(path)
            if image_meta != meta:
                raise DiagnosticError("Experimental/reference TIFF geometry or encoding mismatch")
            sample_stats.append({
                "filename": path.name,
                "stream_role": info[0],
                "candidate_ordinal_id_zero_based": info[1]["candidate_ordinal_id_zero_based"],
                "raw_median_counts": float(np.median(image)),
                "fraction_at_uint16_max": float(np.mean(image == 65535)),
                **_p_stats(image, flat_field_R, stable)
            })
    report = {
        "schema": REPORT_SCHEMA,
        "case_id": "2014-04-04",
        "status": "FLAT_FIELD_SOURCE_CONFIRMED_DESCRIPTIVE_LOG_RATIO_NOT_COMPOSITION",
        "reference_acquisition_role": "flat_field_recording_owner_confirmed",
        "flat_field_source_role_confirmed": True,
        "flat_field_spatial_validity_admitted": False,
        "separate_initial_homogeneous_sample_baseline_identified": False,
        "archive_sha256": inventory["archive_sha256"],
        "verified_extracted_member_crc32": True,
        "reference_count": len(refs),
        "reference_training_frames": reference_train_n,
        "reference_heldout_frames": len(heldout_stats),
        "source_tiff_metadata": meta,
        "python_decoder_versions": {
            "numpy": np.__version__, "tifffile": tifffile.__version__,
            "Pillow": pillow_version,
        },
        "independent_decoder_reference_checks": agreement,
        "reference_filename_span_s": float(times[-1]),
        "ever_uint16_max_pixel_fraction": float(np.mean(np.any(stack == 65535, axis=0))),
        "stable_nonmax_pixel_fraction": float(stable.mean()),
        "reference_max_pixel_fraction_quantiles": quantiles(
            [x["fraction_at_uint16_max"] for x in series_rows]),
        "reference_global_median_raw_counts_quantiles": quantiles(
            [x["raw_median_counts"] for x in series_rows]),
        "stable_nonmax_median_ratio_to_first": {
            "first": float(ratios[0]), "last": float(ratios[-1]),
            "max_abs_deviation": float(np.max(np.abs(ratios - 1))),
            "slope_per_candidate_second": float(np.polyfit(times, ratios, 1)[0]),
        },
        "temporal_pixelwise_MAD_counts_quantiles_stable_nonmax": quantiles(
            temporal_mad[stable]),
        "heldout_flat_field_median_absolute_log_ratio_quantiles": quantiles(
            [abs(x["median_flat_field_log_ratio"]) for x in heldout_stats]),
        "experimental_samples": sample_stats,
        "clock_source": "filename_candidate",
        "camera_clock_admitted": False,
        "physical_detector_mask_admitted": False,
        "reference_is_homogeneous_liquid_admitted": False,
        "reference_is_sample_composition_baseline": False,
        "detector_dark_measurement_admitted": False,
        "concentration_wt_pct_admitted": False,
        "no_physical_inferences_from_global_contrast": True,
        "limitations": [
            "Descriptive full-field counts include sample, walls and unknown beam profile",
            "The flat-field recording is not the required homogeneous-liquid pre-cooling composition baseline",
            "The first reference block is a measured flat-field acquisition; its spatial quality as R and any dark correction remain unverified",
            "No physical crop, solid boundary, plume, or path-integrated phase model has been admitted",
            "Negative log(I/R_flat) is NOT the specimen-relative P=-ln(J_t/J0) and is not an In mass fraction",
        ],
    }
    return report, series_rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-dir", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--expected-count", type=int, default=111)
    parser.add_argument("--reference-train-count", type=int, default=80)
    parser.add_argument("--experimental-samples", type=Path)
    args = parser.parse_args()
    if args.output_json.exists() or args.output_csv.exists():
        parser.error("Output exists; refuse overwrite")
    if args.output_json.resolve() == args.output_csv.resolve():
        parser.error("JSON and CSV output must be distinct")
    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    report, rows = examine(args.reference_dir, inventory,
                           expected_n=args.expected_count,
                           reference_train_n=args.reference_train_count,
                           sample_dir=args.experimental_samples)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n",
                                encoding="utf-8")
    with args.output_csv.open("x", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"raw_reference_frames={report['reference_count']} "
          f"valid_unsaturated_fraction={report['stable_nonmax_pixel_fraction']:.5f} "
          f"concentration_admitted=False")


if __name__ == "__main__":
    main()
