"""Read-only acquisition/case preflight for MIL + liquid-plume calibration benchmarks.

No source TIFF/PNG pixels are modified or resampled; no composition is fitted.
A count or filename match is never accepted as an image-to-mask transform.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path


class AdmissionError(ValueError):
    """A benchmark input failed source-identity or image-format admission."""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def source_frame_files(root: Path, folder: str, ext: str, expected: int) -> list[Path]:
    if not isinstance(expected, int) or isinstance(expected, bool) or expected < 1:
        raise AdmissionError("expected_count must be a positive integer")
    full = (root / folder).resolve()
    if not full.is_relative_to(root.resolve()) or not full.is_dir():
        raise AdmissionError("Source folder missing or outside authorized case root")
    found = {}
    for p in full.iterdir():
        if not p.is_file():
            continue
        if p.suffix.lower() != ext:
            continue
        m = re.fullmatch(r"Frame_(\d+)" + re.escape(ext), p.name, re.IGNORECASE)
        if m is None:
            raise AdmissionError(f"Unexpected frame filename {p.name}")
        idx = int(m.group(1))
        if idx in found:
            raise AdmissionError("Duplicate numeric frame ID")
        found[idx] = p
    if sorted(found) != list(range(1, expected + 1)):
        raise AdmissionError(f"Frame IDs must be contiguous 1..{expected}: saw {len(found)}")
    return [found[k] for k in range(1, expected + 1)]


def tiff_shape_and_dtype(path: Path) -> tuple[int, int, int, int]:
    """Read classic TIFF IFD header tags only: width, height and bits/sample."""
    with path.open("rb") as fh:
        header = fh.read(8)
        if len(header) != 8 or header[:2] not in (b"II", b"MM"):
            raise AdmissionError("Invalid TIFF header")
        endian = "<" if header[:2] == b"II" else ">"
        if struct.unpack_from(endian + "H", header, 2)[0] != 42:
            raise AdmissionError("Unsupported BigTIFF or malformed TIFF")
        offset = struct.unpack_from(endian + "I", header, 4)[0]
        fh.seek(offset)
        nb = fh.read(2)
        if len(nb) != 2:
            raise AdmissionError("Truncated TIFF IFD")
        n = struct.unpack(endian + "H", nb)[0]
        if n > 1024:
            raise AdmissionError("Unreasonable TIFF IFD size")
        tags = {}
        for _ in range(n):
            entry = fh.read(12)
            if len(entry) != 12:
                raise AdmissionError("Truncated TIFF IFD entry")
            tag, typ, count = struct.unpack_from(endian + "HHI", entry, 0)
            if tag in (256, 257, 258, 259, 277, 339):
                if count != 1 or typ not in (3,4):
                    raise AdmissionError("Unsupported multi-valued TIFF geometry/sample tag")
                tags[tag] = struct.unpack_from(endian + ("H" if typ==3 else "I"), entry, 8)[0]
        try:
            width, height, bits = (tags[k] for k in (256,257,258))
        except KeyError as e:
            raise AdmissionError("Missing TIFF geometry or sample-depth tag") from e
        if width <= 0 or height <= 0 or bits != 16:
            raise AdmissionError("Only positive-geometry uint16 TIFF admitted")
        # Header-only inventory. Real archive TIFFs use old-style Deflate
        # (Compression=32946); never silently decode TIFF pixels here.
        compression = tags.get(259, 1)
        if compression not in (1, 5, 8, 32946) or tags.get(277, 1) != 1 or tags.get(339, 1) != 1:
            raise AdmissionError("Unsupported TIFF compression, channel count or sample type")
    return width, height, bits, compression


def png_shape(path: Path) -> tuple[int, int, int, int]:
    with path.open("rb") as fh:
        hdr = fh.read(26)
    if len(hdr) != 26 or hdr[:8] != b"\x89PNG\r\n\x1a\n" or hdr[12:16] != b"IHDR":
        raise AdmissionError("Invalid PNG IHDR")
    width, height = struct.unpack_from(">II", hdr, 16)
    if width < 1 or height < 1:
        raise AdmissionError("Bad PNG geometry")
    return width, height, hdr[24], hdr[25]


def source_ids(path: Path, count: int, start: int, step: int) -> list[int]:
    content = path.read_text(encoding="utf-8-sig").strip()
    if not re.fullmatch(r"[\d,;\s]+", content):
        raise AdmissionError("Source frame-ID file contains unexpected text")
    ids = [int(s) for s in re.findall(r"\d+", content)]
    expected = [start+step*i for i in range(count)]
    if ids != expected:
        raise AdmissionError("Source-frame ID list does not match declared acquisition selection")
    return ids


def admit(root: Path, case: dict, *, include_all_hashes: bool = True) -> dict:
    """Return exact frame inventory, but explicitly *deny* calibrated mask comparisons."""
    if case.get("schema") != "ga-in-calibration-case/v1":
        raise AdmissionError("Unknown case schema")
    if case.get("id") != "2014-03-07":
        raise AdmissionError("This baseline only admits the 2014-03-07 case")
    nimg = case["expected_images"]
    nmask = case["expected_masks"]
    images = source_frame_files(root, case["image_folder"], ".tiff", nimg)
    masks = source_frame_files(root, case["mask_folder"], ".png", nmask)
    sid = source_ids(root/case["source_frame_id_file"], nmask,
                     case["first_source_frame"], case["source_frame_step"])
    shapes_i = {tiff_shape_and_dtype(p) for p in images}
    shapes_m = {png_shape(p) for p in masks}
    if len(shapes_i)!=1 or len(shapes_m)!=1:
        raise AdmissionError("Within-series image geometry/encoding inconsistency")
    width,height,bits,compression = next(iter(shapes_i))
    maskw,maskh,maskdepth,maskcolor = next(iter(shapes_m))
    if [width,height] != case["expected_image_width_height"]:
        raise AdmissionError("Unexpected input TIFF geometry")
    if [maskw,maskh] != case["expected_mask_width_height"]:
        raise AdmissionError("Unexpected historical mask PNG geometry")
    def entries(paths):
        return [{"filename":p.name,"size_bytes":p.stat().st_size,
                 "sha256":sha256(p) if include_all_hashes else None}
                for p in paths]
    match = width==maskw and height==maskh
    if case.get("verified_pixel_transform") is not None:
        # User-supplied numeric transform alone is insufficient for science acceptance.
        raise AdmissionError("Transform admission requires a separately reviewed validation method")
    return {
      "schema":"ga-in-calibration-case-inventory/v1",
      "case_id":case["id"],
      "status":"SOURCE_INVENTORY_VERIFIED_NOT_CALIBRATION_ADMITTED",
      "image_format":{"width":width,"height":height,"bits_per_sample":bits,
                      "compression_tag":compression,"pixel_data_decoded_by_this_tool":False},
      "historical_mask_format":{"width":maskw,"height":maskh,
                                 "png_bit_depth":maskdepth,"png_color_type":maskcolor},
      "source_frame_id_range":{"first":sid[0],"last":sid[-1],
                               "step":case["source_frame_step"],"count":len(sid)},
      "count_images":len(images),"count_masks":len(masks),
      "same_pixel_geometry":match,
      "spatially_registered":False,
      "mask_iou_admitted":False,
      "physical_concentration_curve_admitted":False,
      "timebase_admitted":False,
      "plume_cluster_level_candidates":case["plume_cluster_level_candidates"],
      "known_blockers":["source TIFF radiometric meaning unverified",
        "image-to-historical-mask spatial transform not independently verified",
        "historical mask frame/source correspondence is candidate only",
        "physical 2014-03-07 calibration P anchor measurements missing",
        "source camera timebase and dark/reference provenance not verified",
        "historical masks are not independent manual ground truth"],
      "image_files":entries(images),
      "mask_files":entries(masks),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root",type=Path,required=True)
    ap.add_argument("--case",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    if args.output.exists():
        ap.error("Output exists, refusing overwrite")
    case=json.loads(args.case.read_text(encoding="utf-8"))
    report=admit(args.root,case)
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    print(f"case={report['case_id']} images={report['count_images']} "
          f"masks={report['count_masks']} spatially_registered=False "
          f"calibration_admitted=False")


if __name__ == "__main__":
    main()
