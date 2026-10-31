"""Phase-0 contract checker for projected Ga-In OFV data.

Independent of the original interactive scripts and the upstream 2WCF-SVD
implementation. No experimental data are bundled and no pickle is loaded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
from pathlib import Path

UPSTREAM_REPO = "pienins/Optical-flow-svd-and-fourier-filtering"
UPSTREAM_SHA = "27659ae0e0f798189e1fc7c4516453374ad3c9eb"
UPSTREAM_FILE = "2WCF-SVD_v4_4.py"
IMAGE_PATTERN = re.compile(r"^filtered3D_(\d+)\.tiff?$", re.IGNORECASE)
CONCENTRATION_PATTERN = re.compile(r"^Conc_In_(\d+)\.tiff?$", re.IGNORECASE)
VECTOR_PATTERN = re.compile(r"^velocity_field_(\d+)\.pkl$", re.IGNORECASE)


def indexed_files(folder: Path, pattern: re.Pattern[str]) -> list[tuple[int, Path]]:
    """Require unique, zero-based contiguous indices; skip unrelated files."""
    if not folder.is_dir():
        raise ValueError(f"Missing folder: {folder}")
    entries: list[tuple[int, Path]] = []
    for file in folder.iterdir():
        if not file.is_file():
            continue
        match = pattern.fullmatch(file.name)
        if match:
            entries.append((int(match.group(1)), file))
    entries.sort(key=lambda item: item[0])
    ids = [index for index, _ in entries]
    if not ids:
        raise ValueError(f"No matching files in {folder} for {pattern.pattern}")
    if ids != list(range(len(ids))):
        raise ValueError(f"Expected unique contiguous indices 0..N-1 in {folder}, got {ids[:12]}")
    return entries


def bin_center_time(index: int, *, raw_dt_s: float, bin_size: int,
                    source_start_index: int = 0, acquisition_t0_s: float = 0.0) -> float:
    """Time at the center of original exposure centers in nonoverlapping bin."""
    if index < 0 or source_start_index < 0:
        raise ValueError("Image index and source_start_index must be >= 0")
    if not math.isfinite(raw_dt_s) or raw_dt_s <= 0 or bin_size < 1:
        raise ValueError("raw_dt_s must be positive and bin_size >= 1")
    if not math.isfinite(acquisition_t0_s):
        raise ValueError("acquisition_t0_s must be finite")
    return acquisition_t0_s + (source_start_index + index * bin_size +
                               (bin_size - 1) / 2.0) * raw_dt_s


def pair_center_time(index: int, **kwargs: float) -> float:
    return (bin_center_time(index, **kwargs) + bin_center_time(index + 1, **kwargs)) / 2.0


def to_physical(x_px: float, y_px: float, u_saved_px: float, v_saved_px: float, *,
                image_height_px: int, pixel_size_m: float, pair_dt_s: float,
                velocity_inversion: float) -> dict[str, float]:
    """Interpret 2WCF's saved u,v using known upstream VelocityInversion.

    Upstream Farneback computes image-forward flow (right/down positive);
    BOTH saved components are then multiplied by VelocityInversion.
    Physical coordinate origin here is the bottom-left pixel CENTER of the
    cropped, downsampled frame; y is positive UP.
    """
    if image_height_px <= 0 or pixel_size_m <= 0 or pair_dt_s <= 0:
        raise ValueError("positive image height, pixel size and pair duration required")
    if not math.isfinite(velocity_inversion) or velocity_inversion == 0:
        raise ValueError("VelocityInversion must be known and nonzero")
    values = (x_px, y_px, u_saved_px, v_saved_px, pixel_size_m, pair_dt_s)
    if not all(math.isfinite(float(v)) for v in values):
        raise ValueError("nonfinite position, displacement, scale or interval")
    u_img = u_saved_px / velocity_inversion
    v_img = v_saved_px / velocity_inversion
    return {
        "x_m": x_px * pixel_size_m,
        "y_m": (image_height_px - 1 - y_px) * pixel_size_m,
        "u_m_s": u_img * pixel_size_m / pair_dt_s,
        "v_m_s": -v_img * pixel_size_m / pair_dt_s,
    }


def is_tiff(path: Path) -> bool:
    """Check only standard TIFF magic, not full image integrity."""
    with path.open("rb") as stream:
        magic = stream.read(4)
    return magic in (b"II*\x00", b"MM\x00*")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stage_tiff(images: list[tuple[int, Path]], dest: Path) -> list[dict[str, object]]:
    """Byte-copy to .tiff staging folder; refuse any existing destination."""
    if dest.exists() and any(dest.iterdir()):
        raise ValueError(f"Staging destination must be empty: {dest}")
    for _, source in images:
        if not is_tiff(source):
            raise ValueError(f"Invalid TIFF header: {source}")
    dest.mkdir(parents=True, exist_ok=True)
    files = []
    for index, source in images:
        output = dest / f"filtered3D_{index:05d}.tiff"
        shutil.copyfile(source, output)
        src_hash = sha256(source)
        if sha256(output) != src_hash:
            raise OSError(f"Staged TIFF checksum mismatch: {source}")
        files.append({"index": index, "source": str(source), "staged": str(output),
                      "sha256": src_hash})
    return files


def make_manifest(images: list[tuple[int, Path]], *,
                  concentration: list[tuple[int, Path]] | None = None,
                  vectors: list[tuple[int, Path]] | None = None,
                  raw_dt_s: float, bin_size: int, source_start_index: int,
                  acquisition_t0_s: float, pixel_size_m: float,
                  velocity_inversion: float | None,
                  ofv_parameters: dict | None = None) -> dict:
    """Make aligned frame-pair records; do not assume an OFV field exists."""
    if len(images) < 2:
        raise ValueError("At least two filtered images are required for OFV")
    if not math.isfinite(pixel_size_m) or pixel_size_m <= 0:
        raise ValueError("Positive physical pixel size required")
    if concentration is not None and len(concentration) != len(images):
        raise ValueError("Concentration must have one frame per OFV input image")
    if vectors is not None and len(vectors) != len(images) - 1:
        raise ValueError("Expected exactly N-1 OFV PKLs for N image frames")
    if velocity_inversion is not None and (not math.isfinite(velocity_inversion)
                                          or velocity_inversion == 0):
        raise ValueError("VelocityInversion must be nonzero if supplied")
    if ofv_parameters is not None and velocity_inversion is not None:
        actual = ofv_parameters.get("VelocityInversion")
        if actual is not None and actual != velocity_inversion:
            raise ValueError(f"VelocityInversion mismatch: {actual} != {velocity_inversion}")
    dt_pair = bin_size * raw_dt_s
    pairs = []
    for index in range(len(images) - 1):
        pairs.append({
            "velocity_pair_id": index,
            "first_image": images[index][1].name,
            "second_image": images[index + 1][1].name,
            "first_image_center_s": bin_center_time(index, raw_dt_s=raw_dt_s,
                bin_size=bin_size, source_start_index=source_start_index,
                acquisition_t0_s=acquisition_t0_s),
            "second_image_center_s": bin_center_time(index + 1, raw_dt_s=raw_dt_s,
                bin_size=bin_size, source_start_index=source_start_index,
                acquisition_t0_s=acquisition_t0_s),
            "velocity_center_s": pair_center_time(index, raw_dt_s=raw_dt_s,
                bin_size=bin_size, source_start_index=source_start_index,
                acquisition_t0_s=acquisition_t0_s),
            "concentration_pair": [concentration[index][1].name, concentration[index + 1][1].name]
                                  if concentration else None,
            "vector_file": vectors[index][1].name if vectors else None,
        })
    return {
        "schema": "ga-in/phase0-ofv-contract/v1",
        "upstream": {"repository": UPSTREAM_REPO, "commit": UPSTREAM_SHA,
                     "source": UPSTREAM_FILE, "license_status": "not_declared"},
        "geometry": {"coordinate": "x_right_y_up_bottom_left_crop_pixel_center",
                     "pixel_size_m": pixel_size_m},
        "timing": {"raw_frame_period_s": raw_dt_s, "bin_size": bin_size,
                   "source_start_index": source_start_index, "acquisition_t0_s": acquisition_t0_s,
                   "ofv_image_pair_dt_s": dt_pair,
                   "velocity_timestamp": "midpoint_of_adjacent_binned_image_centers"},
        "velocity": {"saved_displacement_basis": "image_pixel_right_down",
                     "upstream_velocity_inversion": velocity_inversion,
                     "physical_conversion_ready": velocity_inversion is not None},
        "validation": {"has_calibrated_concentration": concentration is not None,
                       "has_ofv_vectors": vectors is not None,
                       "image_dimensions_verified": False,
                       "image_radiometry_verified": False,
                       "physical_wall_boundary_verified": False},
        "frame_pairs": pairs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--concentration", type=Path)
    parser.add_argument("--flow-pkl", type=Path)
    parser.add_argument("--ofv-parameters", type=Path, help="Upstream parameters.json")
    parser.add_argument("--raw-dt-s", type=float, required=True)
    parser.add_argument("--bin-size", type=int, required=True)
    parser.add_argument("--source-start-index", type=int, required=True)
    parser.add_argument("--acquisition-t0-s", type=float, default=0)
    parser.add_argument("--pixel-size-m", type=float, required=True)
    parser.add_argument("--velocity-inversion", type=float,
                        help="Required to convert saved PKL displacement to forward flow")
    parser.add_argument("--stage-tiff", type=Path, help="Optional EMPTY destination; byte-copy only")
    parser.add_argument("--manifest-out", type=Path, help="Optional output JSON")
    args = parser.parse_args()
    images = indexed_files(args.images, IMAGE_PATTERN)
    concentration = (indexed_files(args.concentration, CONCENTRATION_PATTERN)
                     if args.concentration else None)
    vectors = indexed_files(args.flow_pkl, VECTOR_PATTERN) if args.flow_pkl else None
    params = json.loads(args.ofv_parameters.read_text(encoding="utf-8")) if args.ofv_parameters else None
    inversion = args.velocity_inversion
    if params is not None and inversion is None:
        inversion = params.get("VelocityInversion")
    manifest = make_manifest(images, concentration=concentration, vectors=vectors,
        raw_dt_s=args.raw_dt_s, bin_size=args.bin_size,
        source_start_index=args.source_start_index, acquisition_t0_s=args.acquisition_t0_s,
        pixel_size_m=args.pixel_size_m, velocity_inversion=inversion, ofv_parameters=params)
    if args.stage_tiff:
        manifest["staged_tiffs"] = stage_tiff(images, args.stage_tiff)
    payload = json.dumps(manifest, indent=2)
    if args.manifest_out:
        args.manifest_out.parent.mkdir(parents=True, exist_ok=True)
        args.manifest_out.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)


if __name__ == "__main__":
    main()
