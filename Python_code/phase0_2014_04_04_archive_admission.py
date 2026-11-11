"""Read-only 7z-header admission of raw 2014-04-04 Ga-In radiographs.

This tool does NOT extract/decode images, validate detector radiometry,
establish the camera clock or assign chemical composition. Filename times are
diagnostic candidates only. No private image bytes belong in GitHub.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from collections import Counter
from pathlib import Path

SCHEMA = "ga-in-archive-case/v1"
REPORT_SCHEMA = "ga-in-archive-inventory/v1"

ROLE_PATHS = {
    "reference": ("Reference", "ga-25in-ref1"),
    "main": ("2014-04-04", "ga-25in-1"),
    "end": ("2014-04-04", "ga-25in-end1"),
}
TIMESTAMP_RE = re.compile(
    r"^(?P<prefix>ga-25in-(?:ref1|end1|1))_2014-04-04_"
    r"(?P<hh>\d{2})-(?P<mm>\d{2})-(?P<ss>\d{2})-(?P<ms>\d{3})\.tif$",
    re.ASCII,
)
CRC_RE = re.compile(r"[0-9A-Fa-f]{8}\Z")


class AdmissionError(ValueError):
    """Archive metadata failed an admission check."""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_listing(text: str) -> tuple[dict, list[dict]]:
    """Parse native 7z 'l -slt' output without accepting arbitrary paths."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if "\n----------\n" not in normalized:
        raise AdmissionError("7z technical listing has no entry separator")
    header, entries_text = normalized.split("\n----------\n", 1)
    header_fields = {}
    for line in header.splitlines():
        if " = " in line:
            k, v = line.split(" = ", 1)
            header_fields[k.strip()] = v.strip()
    if header_fields.get("Type") != "7z":
        raise AdmissionError("Expected a 7z archive")
    entries = []
    for block in re.split(r"\n\s*\n", entries_text.strip()):
        fields = {}
        for line in block.splitlines():
            if " = " in line:
                key, value = line.split(" = ", 1)
                if key in fields:
                    raise AdmissionError("Repeated 7z metadata field")
                fields[key] = value.strip()
        if not fields:
            continue
        if "Path" not in fields or "Attributes" not in fields:
            raise AdmissionError("Incomplete 7z entry metadata")
        entries.append(fields)
    if not entries:
        raise AdmissionError("No 7z entries")
    return header_fields, entries


def filename_ms(filename: str, prefix: str) -> int:
    m = TIMESTAMP_RE.fullmatch(filename)
    if m is None or m["prefix"] != prefix:
        raise AdmissionError("Unexpected TIFF name, date, or stream prefix")
    hour, minute, second, milli = (int(m[k]) for k in ("hh", "mm", "ss", "ms"))
    if hour > 23 or minute > 59 or second > 59:
        raise AdmissionError("Out-of-range filename clock")
    return ((hour * 60 + minute) * 60 + second) * 1000 + milli


def summary_for(frames: list[dict]) -> dict:
    frames = sorted(frames, key=lambda e: e["filename_ms"])
    times = [e["filename_ms"] for e in frames]
    if len(times) != len(set(times)):
        raise AdmissionError("Repeated filename timestamps in a stream")
    spacings = [b-a for a, b in zip(times, times[1:])]
    if any(dt <= 0 for dt in spacings):
        raise AdmissionError("Non-increasing filename times")
    gaps = [
        {"previous": frames[i]["filename"], "next": frames[i+1]["filename"],
         "filename_interval_ms": dt}
        for i, dt in enumerate(spacings) if dt > 1500
    ]
    return {
        "count": len(frames),
        "first_filename": frames[0]["filename"],
        "last_filename": frames[-1]["filename"],
        "first_filename_clock_ms": times[0],
        "last_filename_clock_ms": times[-1],
        "span_s": round((times[-1]-times[0])/1000, 3),
        "min_adjacent_filename_interval_ms": min(spacings) if spacings else None,
        "max_adjacent_filename_interval_ms": max(spacings) if spacings else None,
        "filename_gaps_over_1p5_s_count": len(gaps),
        "filename_gaps_over_1p5_s_first_20": gaps[:20],
    }


def admit_listing(text: str, case: dict, *, archive_sha256: str | None) -> dict:
    """Admit metadata, not pixels. Requires a case with exact expected counts."""
    if not isinstance(case, dict) or case.get("schema") != SCHEMA or case.get("id") != "2014-04-04":
        raise AdmissionError("Unsupported case or case schema")
    expected = case.get("expected_tiff_counts")
    if not isinstance(expected, dict) or set(expected) != set(ROLE_PATHS):
        raise AdmissionError("Missing exact TIFF stream counts")
    if any(type(v) is not int or v < 1 for v in expected.values()):
        raise AdmissionError("Bad expected stream count")
    accepted_hash = case.get("archive_sha256")
    if not isinstance(accepted_hash, str) or not re.fullmatch("[0-9a-fA-F]{64}", accepted_hash):
        raise AdmissionError("Case must declare archive SHA256")
    if archive_sha256 is not None and archive_sha256.lower() != accepted_hash.lower():
        raise AdmissionError("Source archive SHA256 mismatch")
    header, entries = parse_listing(text)
    allowed_dirs = {"2014-04-04", "2014-04-04\\Reference", "2014-04-04\\2014-04-04"}
    allowed_auxiliary = {"2014-04-04\\Thumbs.db"}
    groups: dict[str, list[dict]] = {k: [] for k in ROLE_PATHS}
    auxiliary = []
    seen_paths = set()
    directories = 0
    for entry in entries:
        path = entry["Path"].replace("/", "\\")
        if path in seen_paths or path.startswith("\\") or ":" in path or ".." in path.split("\\"):
            raise AdmissionError("Duplicate or unsafe archive member path")
        seen_paths.add(path)
        if entry.get("Encrypted") != "-":
            raise AdmissionError("Encrypted or unknown encryption status")
        if "D" in entry["Attributes"]:
            if path not in allowed_dirs:
                raise AdmissionError("Unexpected directory")
            directories += 1
            continue
        try:
            size = int(entry["Size"])
        except (ValueError, KeyError) as exc:
            raise AdmissionError("Missing or malformed member size") from exc
        if size <= 0:
            raise AdmissionError("Empty archive member")
        if not CRC_RE.fullmatch(entry.get("CRC", "")):
            raise AdmissionError("Missing member CRC metadata")
        pieces = path.split("\\")
        if len(pieces) != 3 or pieces[0] != "2014-04-04":
            if path in allowed_auxiliary:
                auxiliary.append({"path": path, "size_bytes": size})
                continue
            raise AdmissionError("Unexpected file path")
        folder, name = pieces[1:]
        role = next((role for role, (directory, prefix) in ROLE_PATHS.items()
                     if folder == directory and name.startswith(prefix + "_")), None)
        if role is None:
            raise AdmissionError("Unrecognized TIFF role or filename")
        stamp = filename_ms(name, ROLE_PATHS[role][1])
        groups[role].append({
            "filename": name, "filename_ms": stamp,
            "size_bytes": size, "header_crc32": entry["CRC"].upper(),
        })
    for role, count in expected.items():
        if len(groups[role]) != count:
            raise AdmissionError(f"{role} count mismatch: expected {count}, got {len(groups[role])}")
    if directories != case.get("expected_directories") or len(auxiliary) != case.get("expected_auxiliary_files"):
        raise AdmissionError("Unexpected directory or non-TIFF count")
    report_groups = {role: summary_for(group) for role, group in groups.items()}
    ref = report_groups["reference"]
    main = report_groups["main"]
    end = report_groups["end"]
    if ref["last_filename_clock_ms"] >= main["first_filename_clock_ms"]:
        raise AdmissionError("Reference sequence does not precede main series")
    if main["last_filename_clock_ms"] >= end["first_filename_clock_ms"]:
        raise AdmissionError("End sequence does not follow main series")
    return {
        "schema": REPORT_SCHEMA,
        "case_id": case["id"],
        "archive_sha256": archive_sha256,
        "archive_sha256_verified": archive_sha256 is not None,
        "status": "ARCHIVE_HEADER_INVENTORY_ONLY",
        "archive_header": {
            "physical_size_bytes": int(header["Physical Size"]),
            "archive_format": header["Type"],
            "solid": header.get("Solid"),
            "blocks": header.get("Blocks"),
        },
        "total_tiff_files": sum(len(group) for group in groups.values()),
        "total_files": sum(len(group) for group in groups.values()) + len(auxiliary),
        "total_directories": directories,
        "auxiliary_files": auxiliary,
        "streams": report_groups,
        "filename_candidate_frame_records": {
            role: [
                {"candidate_ordinal_id_zero_based": idx,
                 "filename": e["filename"],
                 "filename_clock_ms": e["filename_ms"],
                 "member_size_bytes": e["size_bytes"],
                 "member_crc32_header_unverified": e["header_crc32"]}
                for idx, e in enumerate(sorted(group, key=lambda f: f["filename_ms"]))
            ] for role, group in groups.items()
        },
        "filename_reference_to_main_gap_s": round(
            (main["first_filename_clock_ms"] - ref["last_filename_clock_ms"]) / 1000, 3),
        "filename_main_to_end_gap_s": round(
            (end["first_filename_clock_ms"] - main["last_filename_clock_ms"]) / 1000, 3),
        "clock_source": "filename_candidate",
        "physical_clock_admitted": False,
        "reference_recording_role": "flat_field_correction_owner_confirmed",
        "flat_field_role_confirmed": True,
        "flat_field_spatial_validity_admitted": False,
        "separate_initial_homogeneous_sample_baseline_identified": False,
        "original_tiff_pixels_decoded": False,
        "member_crc32_is_verified": False,
        "dark_reference_recovered": False,
        "image_registration_admitted": False,
        "absolute_C_In_calibration_admitted": False,
        "blockers": [
            "Filename timestamps are not a verified acquisition log/camera clock",
            "Reference files are flat-field correction recordings (owner-confirmed); their spatial validity, stability and beam/detector drift require testing",
            "A distinct pre-solidification homogeneous sample reference is required for C_In=25 wt% at P=0",
            "No measured dark stack identified; no dark-corrected absorption admitted",
            "TIFF sample format, pixel integrity and detector validity need independent decoding",
            "Crop, chamber boundaries and source-matched masks/OFV are unregistered",
            "5-10/25/98.6 wt% chemical reference regions not independently established",
        ],
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--case", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--seven-zip", default=shutil.which("7z") or shutil.which("7zz"))
    p.add_argument("--skip-archive-hash", action="store_true")
    args = p.parse_args()
    if args.output.exists():
        p.error("Refusing to overwrite an existing inventory")
    if not args.archive.is_file() or args.archive.suffix.lower() != ".7z":
        p.error("Source archive missing or wrong extension")
    if not args.seven_zip:
        p.error("Pass --seven-zip to an installed 7z/7zz executable")
    proc = subprocess.run([args.seven_zip, "l", "-slt", str(args.archive)],
                          capture_output=True, text=True, errors="replace", check=False)
    if proc.returncode != 0:
        raise AdmissionError(f"7z header listing failed (exit {proc.returncode})")
    digest = None if args.skip_archive_hash else sha256(args.archive)
    case = json.loads(args.case.read_text(encoding="utf-8"))
    report = admit_listing(proc.stdout, case, archive_sha256=digest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"case={report['case_id']} TIFFs={report['total_tiff_files']} "
          "clock=filename_candidate radiometry=BLOCKED C_In=BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
