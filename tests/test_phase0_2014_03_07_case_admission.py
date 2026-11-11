"""Dependency-free synthetic admission tests; source image pixels never redistributed."""
import importlib.util
import struct
import tempfile
from pathlib import Path
import unittest
import zlib

SOURCE=Path(__file__).resolve().parents[1]/"Python_code"/"phase0_2014_03_07_case_admission.py"
spec=importlib.util.spec_from_file_location("phase0_2014_admission",SOURCE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def sample_tiff(path, w, h, compression=32946):
    tags=[(256,3,w),(257,3,h),(258,3,16),(259,3,compression),
          (277,3,1),(339,3,1)]
    with path.open("wb") as f:
        f.write(b"II" + struct.pack("<HI",42,8))
        f.write(struct.pack("<H",len(tags)))
        for tag,typ,value in tags:
            f.write(struct.pack("<HHI",tag,typ,1))
            f.write(struct.pack("<H",value)+b"\0\0")
        f.write(struct.pack("<I",0))
        f.write(zlib.compress(struct.pack("<"+str(w*h)+"H",*([1000]*(w*h)))))


def sample_png(path,w,h):
    def chunk(typ,data):
        return struct.pack(">I",len(data))+typ+data+struct.pack(">I",zlib.crc32(typ+data)&0xffffffff)
    ihdr=struct.pack(">IIBBBBB",w,h,8,0,0,0,0)
    pixels=bytes([0]+[0]*w)*h
    path.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",ihdr)+chunk(b"IDAT",zlib.compress(pixels))+chunk(b"IEND",b""))


class HistoricalCaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/"images").mkdir()
        (self.root/"masks").mkdir()
        for i in range(1,4):
            sample_tiff(self.root/"images"/f"Frame_{i}.tiff",2,2)
        for i in range(1,3):
            sample_png(self.root/"masks"/f"Frame_{i}.png",3,3)
        (self.root/"ids.csv").write_text("600\n605\n")
        self.case={"schema":"ga-in-calibration-case/v1","id":"2014-03-07",
          "image_folder":"images","mask_folder":"masks",
          "source_frame_id_file":"ids.csv","expected_images":3,"expected_masks":2,
          "expected_image_width_height":[2,2],
          "expected_mask_width_height":[3,3],
          "first_source_frame":600,"source_frame_step":5,
          "verified_pixel_transform":None,
          "plume_cluster_level_candidates":[9,12,16]}

    def test_realistic_unsupported_registration_remains_blocked(self):
        result=m.admit(self.root,self.case)
        self.assertEqual(result["count_images"],3)
        self.assertEqual(result["count_masks"],2)
        self.assertEqual(result["source_frame_id_range"]["last"],605)
        self.assertFalse(result["same_pixel_geometry"])
        self.assertFalse(result["spatially_registered"])
        self.assertFalse(result["mask_iou_admitted"])
        self.assertFalse(result["physical_concentration_curve_admitted"])
        self.assertTrue(all(f["sha256"] for f in result["image_files"]))
        self.assertEqual(result["image_format"]["compression_tag"],32946)
        self.assertFalse(result["image_format"]["pixel_data_decoded_by_this_tool"])

    def test_same_shape_does_not_establish_registration(self):
        for i in range(1,3):
            sample_png(self.root/"masks"/f"Frame_{i}.png",2,2)
        self.case["expected_mask_width_height"]=[2,2]
        result=m.admit(self.root,self.case,include_all_hashes=False)
        self.assertTrue(result["same_pixel_geometry"])
        self.assertFalse(result["spatially_registered"])
        self.assertFalse(result["physical_concentration_curve_admitted"])

    def test_reject_missing_frame(self):
        (self.root/"images"/"Frame_3.tiff").unlink()
        with self.assertRaisesRegex(m.AdmissionError,"contiguous"):
            m.admit(self.root,self.case)

    def test_reject_unexpected_source_id(self):
        (self.root/"ids.csv").write_text("600\n606\n")
        with self.assertRaisesRegex(m.AdmissionError,"Source-frame ID"):
            m.admit(self.root,self.case)

    def test_reject_arbitrary_declared_transform(self):
        self.case["verified_pixel_transform"]={"scale":2}
        with self.assertRaisesRegex(m.AdmissionError,"separately reviewed"):
            m.admit(self.root,self.case)

    def test_reject_per_frame_geometry_drift(self):
        sample_tiff(self.root/"images"/"Frame_3.tiff",3,2)
        with self.assertRaisesRegex(m.AdmissionError,"Within-series"):
            m.admit(self.root,self.case)

    def test_reject_unrecognized_compression(self):
        sample_tiff(self.root/"images"/"Frame_3.tiff",2,2,compression=3)
        with self.assertRaisesRegex(m.AdmissionError,"Unsupported TIFF compression"):
            m.admit(self.root,self.case)

    def test_refuse_wrong_case(self):
        self.case["id"]="other"
        with self.assertRaisesRegex(m.AdmissionError,"only admits"):
            m.admit(self.root,self.case)


if __name__=="__main__":
    unittest.main()
