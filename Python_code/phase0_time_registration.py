"""Phase 0 time-only admission contract for OFV/concentration co-registration.

This module deliberately does NOT parse image filenames, load concentration
TIFFs or flow PKLs, interpolate concentrations, assign pixel scales, or
certify an instrument clock. Every source time and raw-to-bin mapping must
be supplied explicitly by a provenance manifest.

A pair midpoint is registered to two concentration bin centers by weights;
it is NOT assigned to either concentration frame by its ordinal filename.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


SCHEMA = "ga-in-ofv-time-registration/v1"
TRUSTED_CLOCKS = {"camera_metadata", "verified_acquisition_log"}
DIAGNOSTIC_CLOCKS = {"filename_candidate"}


class AdmissionError(ValueError):
    """The provided manifest is not safe for the requested time alignment."""


def _number(value, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise AdmissionError(f"{name} must be a finite number")
    v = float(value)
    if not math.isfinite(v):
        raise AdmissionError(f"{name} must be finite")
    return v


def _integer(value, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise AdmissionError(f"{name} must be an integer")
    return value


def _sequence(value, name: str) -> list:
    if not isinstance(value, list) or not value:
        raise AdmissionError(f"{name} must be a nonempty list")
    return value


def plan_time_registration(manifest: dict) -> dict:
    """Validate actual acquisition/bin provenance and return a time-only plan.

    A 'filename_candidate' clock can produce preview output but is explicitly
    refused as authoritative quantitative timing. The caller must separately
    validate image geometry, concentration calibration and data integrity.
    """
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA:
        raise AdmissionError(f"Expected schema {SCHEMA}")
    source_kind = manifest.get("clock_source")
    if source_kind not in TRUSTED_CLOCKS | DIAGNOSTIC_CLOCKS:
        raise AdmissionError("clock_source must declare camera_metadata, verified_acquisition_log, or filename_candidate")
    origin = manifest.get("time_origin_description")
    if not isinstance(origin, str) or not origin.strip():
        raise AdmissionError("time_origin_description is required")
    nominal_dt = _number(manifest.get("nominal_source_dt_s"), "nominal_source_dt_s")
    allowed_jitter = _number(manifest.get("max_abs_frame_dt_deviation_s"), "max_abs_frame_dt_deviation_s")
    tolerance = _number(manifest.get("concentration_time_tolerance_s"), "concentration_time_tolerance_s")
    if nominal_dt <= 0 or allowed_jitter < 0 or allowed_jitter >= nominal_dt or tolerance < 0:
        raise AdmissionError("Invalid nominal frame spacing, allowed jitter or concentration tolerance")

    raw = _sequence(manifest.get("raw_frames"), "raw_frames")
    times = {}
    raw_ids = []
    last_time = None
    for j, obj in enumerate(raw):
        if not isinstance(obj, dict):
            raise AdmissionError("raw_frames must contain objects")
        rid = _integer(obj.get("id"), f"raw_frames[{j}].id")
        t = _number(obj.get("time_s"), f"raw_frames[{j}].time_s")
        if rid in times or (raw_ids and rid != raw_ids[-1] + 1):
            raise AdmissionError("raw_frame IDs must be contiguous and unique")
        if last_time is not None:
            delta = t - last_time
            if delta <= 0:
                raise AdmissionError("raw timestamps must be strictly increasing")
            if abs(delta - nominal_dt) > allowed_jitter + 1e-12:
                raise AdmissionError(f"Unexpected source-frame gap or cadence at id={rid}: dt={delta:g}s")
        raw_ids.append(rid)
        times[rid] = t
        last_time = t
    if len(raw) < 2:
        raise AdmissionError("At least two source frames required")

    bins = _sequence(manifest.get("image_bins"), "image_bins")
    if len(bins) < 2:
        raise AdmissionError("At least two image bins required")
    bin_centers = []
    previous_last_id = None
    seen_source = set()
    for i, obj in enumerate(bins):
        if not isinstance(obj, dict) or _integer(obj.get("id"), f"image_bins[{i}].id") != i:
            raise AdmissionError("image_bins must be zero-based, contiguous, ordered")
        ids = _sequence(obj.get("raw_ids"), f"image_bins[{i}].raw_ids")
        ids = [_integer(x, f"image_bins[{i}].raw_ids") for x in ids]
        if any(x not in times for x in ids):
            raise AdmissionError("image bin references missing raw source frame")
        if any(b != a+1 for a, b in zip(ids, ids[1:])):
            raise AdmissionError("bin source ids must be contiguous")
        if any(x in seen_source for x in ids):
            raise AdmissionError("overlapping bins are not admitted by this contract")
        if previous_last_id is not None and ids[0] != previous_last_id + 1:
            raise AdmissionError("unmapped source gap between adjacent image bins")
        previous_last_id = ids[-1]
        seen_source.update(ids)
        bin_centers.append(sum(times[x] for x in ids) / len(ids))

    concentrations = _sequence(manifest.get("concentration_frames"), "concentration_frames")
    if len(concentrations) != len(bins):
        raise AdmissionError("concentration frames must be one per binned image")
    conc_ids = []
    for i, obj in enumerate(concentrations):
        if not isinstance(obj, dict) or _integer(obj.get("image_id"), f"concentration_frames[{i}].image_id") != i:
            raise AdmissionError("concentration images must explicitly match ordered image_bin ids")
        cid = _integer(obj.get("id"), f"concentration_frames[{i}].id")
        if cid in conc_ids:
            raise AdmissionError("duplicate concentration image id")
        measured_t = _number(obj.get("time_s"), f"concentration_frames[{i}].time_s")
        if abs(measured_t - bin_centers[i]) > tolerance + 1e-12:
            raise AdmissionError(f"concentration time does not match binned image center at id={i}")
        conc_ids.append(cid)

    pairs = _sequence(manifest.get("flow_pairs"), "flow_pairs")
    if len(pairs) != len(bins) - 1:
        raise AdmissionError("Expected one flow record for each adjacent image pair")
    pair_output = []
    for i, obj in enumerate(pairs):
        if not isinstance(obj, dict) or _integer(obj.get("id"), f"flow_pairs[{i}].id") != i:
            raise AdmissionError("flow pair IDs must be zero-based and ordered")
        if obj.get("image_ids") != [i, i + 1]:
            raise AdmissionError("flow pair must explicitly cover adjacent image IDs")
        a, b = bin_centers[i:i+2]
        if b <= a:
            raise AdmissionError("bin centers must strictly increase")
        tm = (a + b) / 2
        # The midpoint is exactly equidistant between two bin centers;
        # the associated linear interpolation weights are, by definition, 1/2 each.
        pair_output.append({
            "flow_pair_id": i, "image_ids": [i,i+1],
            "time_midpoint_s": tm, "image_pair_duration_s": b-a,
            "concentration_image_ids": [conc_ids[i], conc_ids[i+1]],
            "concentration_interpolation_weights": [0.5, 0.5],
        })

    is_authoritative = source_kind in TRUSTED_CLOCKS
    return {
        "schema": "ga-in-ofv-time-registration-result/v1",
        "admission": "timing_preflight_passed" if is_authoritative else "diagnostic_only_unverified_filename_clock",
        "clock_source": source_kind,
        "time_origin_description": origin,
        "num_raw_frames": len(raw), "num_image_bins": len(bins),
        "num_flow_pairs": len(pair_output),
        "bin_center_times_s": bin_centers,
        "flow_pair_registrations": pair_output,
        "not_validated_by_this_module": [
            "absolute calibration of the acquisition clock",
            "source TIFF identity and file hashes",
            "image crop, field-of-view and physical walls",
            "radiometric correction and concentration-to-luminance mapping",
            "physical concentration interpolation accuracy and energy closure",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    result = plan_time_registration(data)
    if args.output.exists():
        parser.error("--output must be a new file; refusing to overwrite existing results")
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"admission={result['admission']} pairs={result['num_flow_pairs']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
