"""Run an exact pinned EXTERNAL checkout of 2WCF-SVD without vendoring its code.

Requires the upstream dependencies including wolframclient. Deliberately refuses
an unknown or modified upstream revision and refuses occupied output folders.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
from pathlib import Path

from phase0_contract import (IMAGE_PATTERN, UPSTREAM_SHA, UPSTREAM_FILE,
                             indexed_files, is_tiff)


UPSTREAM_BLOB = "52d20820314a1e4283a325dc34e899191bf267b4"


def _git(cwd: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(cwd), *args],
                            capture_output=True, text=True, check=True)
    return result.stdout.strip()


def validate_upstream(checkout: Path) -> Path:
    checkout = checkout.resolve()
    source = checkout / UPSTREAM_FILE
    if not source.is_file():
        raise ValueError(f"Missing pinned upstream source: {source}")
    actual = _git(checkout, "rev-parse", "HEAD")
    if actual != UPSTREAM_SHA:
        raise ValueError(f"Wrong upstream commit: expected {UPSTREAM_SHA}, got {actual}")
    blob = _git(checkout, "hash-object", str(source))
    if blob != UPSTREAM_BLOB:
        raise ValueError(f"Upstream source differs from audited blob: {blob}")
    return source


def import_upstream(source: Path):
    spec = importlib.util.spec_from_file_location("pinned_2wcf_svd", source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {source}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def collect_parameter_snapshot(module) -> dict:
    """Capture upstream settings, not a complete environment lock."""
    items = {}
    for name, value in vars(module).items():
        if not name or not name[0].isupper():
            continue
        if isinstance(value, (bool, int, float, str)):
            items[name] = value
        elif isinstance(value, (tuple, list)) and all(isinstance(v, (bool, int, float, str)) for v in value):
            items[name] = list(value)
    return items


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--upstream-checkout", type=Path, required=True)
    p.add_argument("--images-tiff", type=Path, required=True, help="Already staged .tiff images")
    p.add_argument("--output", type=Path, required=True, help="New/empty run output folder")
    p.add_argument("--arrow-step", type=int, default=7)
    p.add_argument("--velocity-inversion", type=int, choices=(-1, 1), default=-1)
    p.add_argument("--video-fps", type=float, default=1.0,
                   help="Effective frame rate AFTER binning, only used for visualization")
    p.add_argument("--parallel", action="store_true",
                   help="Enable original parallel flow computation; default is reproducible serial")
    p.add_argument("--workers", type=int)
    args = p.parse_args()

    source = validate_upstream(args.upstream_checkout)
    images_index = indexed_files(args.images_tiff, IMAGE_PATTERN)
    if len(images_index) < 2:
        raise ValueError("At least two images required")
    if any(file.suffix.lower() != ".tiff" for _, file in images_index):
        raise ValueError("The upstream loader only discovers .tiff; stage inputs first")
    if any(not is_tiff(file) for _, file in images_index):
        raise ValueError("Some staged files lack a TIFF header")
    if args.output.exists() and any(args.output.iterdir()):
        raise ValueError(f"Output must be new or empty: {args.output}")
    if args.arrow_step < 1 or args.video_fps <= 0 or (args.workers is not None and args.workers < 1):
        raise ValueError("Invalid arrow-step, video-fps or worker count")
    os.environ.setdefault("MPLBACKEND", "Agg")

    # Upstream imports optional WXF serializer at module import, so all the
    # documented upstream dependencies must be available in this environment.
    ofv = import_upstream(source)
    ofv.USE_SVD = False
    ofv.UseParallelFlow = args.parallel
    ofv.MaxFlowWorkers = args.workers
    ofv.ArrowDensityStep = args.arrow_step
    ofv.VelocityInversion = args.velocity_inversion
    ofv.VideoFPS = args.video_fps
    args.output.mkdir(parents=True, exist_ok=True)
    pkl_dir = args.output / "pkl"
    wxf_dir = args.output / "wxf"
    pkl_dir.mkdir(exist_ok=False)
    wxf_dir.mkdir(exist_ok=False)

    snapshot = collect_parameter_snapshot(ofv)
    snapshot.update({
        "upstream_repo": "pienins/Optical-flow-svd-and-fourier-filtering",
        "upstream_commit_sha": UPSTREAM_SHA,
        "upstream_blob_sha": UPSTREAM_BLOB,
        "input_folder": str(args.images_tiff.resolve()),
        "input_files": [f.name for _, f in images_index],
        "output_timing_note": "Pair i is image i and image i+1; use phase0_contract for time mapping",
    })
    (args.output / "parameters.json").write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")

    images, file_names = ofv.load_images_without_svd(str(args.images_tiff))
    if file_names != [f.name for _, f in images_index]:
        raise RuntimeError("Upstream frame order disagrees with validated manifest")
    ofv.run_optical_flow(images, str(args.output), str(pkl_dir), str(wxf_dir))

    result_files = indexed_files(pkl_dir, __import__("phase0_contract").VECTOR_PATTERN)
    if len(result_files) != len(images_index) - 1:
        raise RuntimeError(f"Expected {len(images_index)-1} flow vectors, got {len(result_files)}")
    summary = {"source_commit": UPSTREAM_SHA, "image_frames": len(images_index),
               "flow_pairs": len(result_files), "output": str(args.output)}
    (args.output / "phase0-run-summary.json").write_text(json.dumps(summary, indent=2) + "\n",
                                                           encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
