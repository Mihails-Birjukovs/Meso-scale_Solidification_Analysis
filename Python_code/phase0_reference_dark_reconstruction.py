"""Reconstruct per-pixel reference and dark means from explicitly selected TIFFs.

Read-only source inputs; pure stdlib, no display normalization, no implicit
dark-current correction and no composition calibration. Run on PRIVATE source
images; do not commit the data or generated images to public repositories.
"""
from __future__ import annotations

import argparse
from array import array
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import struct
import sys


class Refusal(ValueError):
    """Source frame representation is unsupported or provenance incomplete."""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_u16_tiff(path: Path) -> tuple[array, tuple[int, int]]:
    """Decode uncompressed single-channel, unsigned 16-bit classic TIFF only."""
    b = path.read_bytes()
    if len(b) < 8 or b[:2] not in (b"II", b"MM"):
        raise Refusal("Invalid TIFF header")
    endian = "<" if b[:2] == b"II" else ">"
    if struct.unpack_from(endian + "H", b, 2)[0] != 42:
        raise Refusal("Not a classic TIFF")
    ifd = struct.unpack_from(endian + "I", b, 4)[0]
    if ifd + 2 > len(b):
        raise Refusal("Out-of-range IFD")
    n = struct.unpack_from(endian + "H", b, ifd)[0]
    if ifd + 2 + 12 * n + 4 > len(b):
        raise Refusal("Truncated IFD")
    tags = {}
    for j in range(n):
        pos = ifd + 2 + 12*j
        tag, typ, count = struct.unpack_from(endian + "HHI", b, pos)
        size = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8}.get(typ)
        if size is None:
            continue
        byte_count = size * count
        off = pos + 8 if byte_count <= 4 else struct.unpack_from(endian + "I", b, pos + 8)[0]
        if off + byte_count > len(b):
            raise Refusal("Out-of-range TIFF tag")
        if typ == 3:
            vals = struct.unpack_from(endian + str(count) + "H", b, off)
        elif typ == 4:
            vals = struct.unpack_from(endian + str(count) + "I", b, off)
        elif typ in (1, 2):
            vals = b[off:off+byte_count]
        else:
            continue
        tags[tag] = vals[0] if isinstance(vals, tuple) and count == 1 else vals

    w, h = tags.get(256), tags.get(257)
    if not isinstance(w, int) or not isinstance(h, int) or w < 1 or h < 1:
        raise Refusal("Invalid width or height")
    for tag, wanted in ((258,16), (259,1), (262,1), (277,1), (284,1), (339,1)):
        if tags.get(tag, 1 if tag in (259, 277, 284, 339) else None) != wanted:
            raise Refusal("Unsupported TIFF samples, compression, or pixel encoding")
    offsets, sizes = tags.get(273), tags.get(279)
    if isinstance(offsets, int):
        offsets = (offsets,)
    if isinstance(sizes, int):
        sizes = (sizes,)
    if not isinstance(offsets, tuple) or not isinstance(sizes, tuple) or len(offsets) != len(sizes):
        raise Refusal("Unsupported strip layout")
    buf = bytearray()
    for offset, nbytes in zip(offsets, sizes):
        if not isinstance(offset,int) or not isinstance(nbytes,int) or offset+nbytes > len(b):
            raise Refusal("Invalid strip offset or length")
        buf.extend(b[offset:offset+nbytes])
    if len(buf) != w*h*2:
        raise Refusal("Unexpected pixel payload length")
    samples = array("H")
    if samples.itemsize != 2:
        raise Refusal("Expected two-byte native unsigned short")
    samples.frombytes(buf)
    if (endian == ">" and sys.byteorder == "little") or (endian == "<" and sys.byteorder == "big"):
        samples.byteswap()
    return samples, (w, h)


def write_f32_tiff(path: Path, values: array, shape: tuple[int,int]) -> None:
    """Export one-strip 32-bit IEEE grayscale TIFF of *unaltered raw-count means*."""
    width,height=shape
    if len(values) != width*height or not all(math.isfinite(x) for x in values):
        raise Refusal("Invalid float mean image")
    tags = [(256,4,width),(257,4,height),(258,3,32),(259,3,1),(262,3,1),
            (273,4,0),(277,3,1),(278,4,height),(279,4,width*height*4),
            (284,3,1),(339,3,3)]
    offset = 8+2+12*len(tags)+4
    values_f32 = array("f", values)
    if sys.byteorder != "little":
        values_f32.byteswap()
    with path.open("xb") as f:
        f.write(b"II" + struct.pack("<HI",42,8))
        f.write(struct.pack("<H",len(tags)))
        for tag,typ,val in tags:
            f.write(struct.pack("<HHI",tag,typ,1))
            f.write(struct.pack("<H",val)+b"\0\0" if typ==3 else struct.pack("<I", offset if tag==273 else val))
        f.write(struct.pack("<I",0))
        if f.tell() != offset:
            raise Refusal("Internal TIFF IFD offset mismatch")
        values_f32.tofile(f)


def reconstruct(paths: list[Path]) -> tuple[array,tuple[int,int],dict]:
    if len(paths)<2:
        raise Refusal("At least two explicitly selected exposures required")
    if len(set(str(p.resolve()) for p in paths)) != len(paths):
        raise Refusal("Duplicate frame paths")
    shape=None
    sums=None
    frames=[]
    for p in paths:
        pixels,current_shape=read_u16_tiff(p)
        if shape is None:
            shape=current_shape
            sums=array("d",[0.0])*len(pixels)
        elif current_shape != shape:
            raise Refusal("Different source frame geometries")
        for j,v in enumerate(pixels):
            sums[j]+=v
        frames.append({"filename":p.name,"sha256":sha256(p),
                       "mean_raw_counts":sum(pixels)/len(pixels),
                       "saturated_fraction":sum(v==65535 for v in pixels)/len(pixels)})
    mean=array("d",(v/len(paths) for v in sums))
    return mean,shape,{"frames":frames,"count":len(paths),
                        "range_of_frame_means": [min(x["mean_raw_counts"] for x in frames),
                                                  max(x["mean_raw_counts"] for x in frames)],
                        "mean_detector_counts":sum(mean)/len(mean)}


def compare_archived(reconstructed:array, path:Path) -> dict:
    original,shape=read_u16_tiff(path)
    if len(original)!=len(reconstructed):
        raise Refusal("Archived averaged TIFF has different dimensions")
    n=len(original)
    ma=sum(original)/n
    mr=sum(reconstructed)/n
    cov=sum((x-ma)*(y-mr) for x,y in zip(original,reconstructed))/n
    vx=sum((x-ma)**2 for x in original)/n
    vy=sum((x-mr)**2 for x in reconstructed)/n
    return {"archive_basename":path.name,"archive_sha256":sha256(path),
            "archive_pixel_mean":ma,"reconstructed_pixel_mean":mr,
            "pixelwise_correlation":cov/math.sqrt(vx*vy) if vx*vy>0 else None,
            "pixelwise_rmse_counts":math.sqrt(sum((x-y)**2 for x,y in zip(original,reconstructed))/n)}


def build(reference_paths:list[Path],dark_paths:list[Path],output:Path,
          archive_reference:Path|None=None,archive_dark:Path|None=None) -> dict:
    if output.exists():
        raise Refusal("Output already exists; refusing overwrite")
    if not reference_paths or not dark_paths:
        raise Refusal("Missing reference or dark input series")
    all_paths=reference_paths+dark_paths
    if len(set(str(p.resolve()) for p in all_paths))!=len(all_paths):
        raise Refusal("Same source file supplied more than once")
    r,shape,rm=reconstruct(reference_paths)
    d,dshape,dm=reconstruct(dark_paths)
    if shape!=dshape:
        raise Refusal("Reference and dark stack geometry differs")
    dif=array("d",(a-b for a,b in zip(r,d)))
    comp={}
    if archive_reference:
        comp["reference"]=compare_archived(r,archive_reference)
    if archive_dark:
        comp["dark"]=compare_archived(d,archive_dark)
    output.mkdir(parents=False)
    files={}
    for name,values in (("reference_mean_raw_counts_float32.tif",r),
                        ("dark_mean_raw_counts_float32.tif",d),
                        ("reference_minus_dark_raw_counts_float32.tif",dif)):
        dest=output/name
        write_f32_tiff(dest,values,shape)
        files[name]=sha256(dest)
    result={"schema":"ga-in-reference-dark-mean-reconstruction/v1",
            "status":"RAW_COUNT_MEANS_NOT_COMPOSITION_OR_ACCEPTED_DETECTOR_CALIBRATION",
            "created_utc":datetime.now(timezone.utc).isoformat(),
            "definition":"independent per-pixel arithmetic means, float64 accumulation, float32 TIFF output",
            "shape":[shape[0],shape[1]],"reference":rm,"dark":dm,
            "reference_minus_dark":{"pixel_mean":sum(dif)/len(dif),
                                    "positive_pixel_fraction":sum(x>0 for x in dif)/len(dif),
                                    "negative_pixel_fraction":sum(x<0 for x in dif)/len(dif)},
            "archived_average_comparisons":comp,
            "output_sha256":files,
            "not_proven":["detector stability", "physical field-of-view", "same acquisition reference identity",
                          "concentration-to-luminance calibration","absolute pixel size","timebase"]}
    (output/"manifest.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--reference-dir",type=Path,required=True)
    p.add_argument("--reference-glob",required=True)
    p.add_argument("--dark-dir",type=Path,required=True)
    p.add_argument("--dark-glob",required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--archived-reference",type=Path)
    p.add_argument("--archived-dark",type=Path)
    args=p.parse_args()
    refs=sorted(args.reference_dir.glob(args.reference_glob))
    darks=sorted(args.dark_dir.glob(args.dark_glob))
    result=build(refs,darks,args.output,args.archived_reference,args.archived_dark)
    print(f"reference={result['reference']['count']} dark={result['dark']['count']}")
    print("Outputs and hash manifest written to",args.output)


if __name__=="__main__":
    main()
