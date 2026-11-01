"""Synthetic, dependency-free tests for reference/dark mean reconstruction."""
import importlib.util
import struct
import tempfile
from pathlib import Path
import unittest

FILE=Path(__file__).resolve().parents[1]/"Python_code"/"phase0_reference_dark_reconstruction.py"
spec=importlib.util.spec_from_file_location("phase0_recon",FILE)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def make_u16_tiff(path,values,w=3,h=2,endian="<"):
    assert len(values)==w*h
    tags=[(256,4,w),(257,4,h),(258,3,16),(259,3,1),(262,3,1),
          (273,4,0),(277,3,1),(278,4,h),(279,4,w*h*2),
          (284,3,1),(339,3,1)]
    offset=8+2+12*len(tags)+4
    with path.open("wb") as f:
        f.write((b"II" if endian=="<" else b"MM")+struct.pack(endian+"HI",42,8))
        f.write(struct.pack(endian+"H",len(tags)))
        for tag,typ,val in tags:
            f.write(struct.pack(endian+"HHI",tag,typ,1))
            f.write(struct.pack(endian+"H",val)+b"\0\0" if typ==3 and endian=="<"
                    else (struct.pack(endian+"H",val)+b"\0\0" if typ==3
                          else struct.pack(endian+"I",offset if tag==273 else val)))
        f.write(struct.pack(endian+"I",0))
        assert f.tell()==offset
        f.write(struct.pack(endian+str(len(values))+"H",*values))


def f32_tiff_pixels(path):
    b=path.read_bytes()
    self_count=(len(b)-146)//4
    assert b[:8]==b"II*\0\x08\0\0\0"
    return struct.unpack_from("<"+str(self_count)+"f",b,146)


class ReconstructionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir=Path(self.temp.name)
        self.r1=self.dir/"r1.tif"
        self.r2=self.dir/"r2.tif"
        self.d1=self.dir/"d1.tif"
        self.d2=self.dir/"d2.tif"
        make_u16_tiff(self.r1,[100,200,300,400,500,600])
        make_u16_tiff(self.r2,[120,220,320,420,520,620])
        make_u16_tiff(self.d1,[20,30,40,50,60,70])
        make_u16_tiff(self.d2,[40,50,60,70,80,90])

    def test_mean_and_delta_are_raw_counts_without_clipping(self):
        before=[mod.sha256(p) for p in (self.r1,self.r2,self.d1,self.d2)]
        out=self.dir/"out"
        report=mod.build([self.r1,self.r2],[self.d1,self.d2],out)
        self.assertEqual(report["shape"],[3,2])
        self.assertEqual(report["reference"]["count"],2)
        self.assertEqual(report["dark"]["count"],2)
        self.assertEqual(report["reference_minus_dark"]["positive_pixel_fraction"],1.0)
        self.assertEqual(f32_tiff_pixels(out/"reference_mean_raw_counts_float32.tif"),(110,210,310,410,510,610))
        self.assertEqual(f32_tiff_pixels(out/"dark_mean_raw_counts_float32.tif"),(30,40,50,60,70,80))
        self.assertEqual(f32_tiff_pixels(out/"reference_minus_dark_raw_counts_float32.tif"),(80,170,260,350,440,530))
        self.assertEqual(before,[mod.sha256(p) for p in (self.r1,self.r2,self.d1,self.d2)])
        self.assertTrue((out/"manifest.json").is_file())

    def test_negative_detector_difference_is_preserved(self):
        make_u16_tiff(self.d1,[200,30,40,50,60,70])
        make_u16_tiff(self.d2,[200,50,60,70,80,90])
        out=self.dir/"negative"
        report=mod.build([self.r1,self.r2],[self.d1,self.d2],out)
        self.assertEqual(f32_tiff_pixels(out/"reference_minus_dark_raw_counts_float32.tif")[0],-90.0)
        self.assertAlmostEqual(report["reference_minus_dark"]["negative_pixel_fraction"],1/6)

    def test_big_endian_source_round_trip(self):
        be=self.dir/"big.tif"
        make_u16_tiff(be,[25,125,1025,5000,65535,200],endian=">")
        px,shape=mod.read_u16_tiff(be)
        self.assertEqual(shape,(3,2))
        self.assertEqual(list(px),[25,125,1025,5000,65535,200])

    def test_refuse_missing_or_duplicate_exposures(self):
        with self.assertRaises(mod.Refusal):
            mod.reconstruct([self.r1])
        with self.assertRaises(mod.Refusal):
            mod.reconstruct([self.r1,self.r1])
        with self.assertRaises(mod.Refusal):
            mod.build([self.r1,self.r2],[self.r2,self.d1],self.dir/"dupout")

    def test_refuse_geometry_mismatch(self):
        make_u16_tiff(self.r2,[10,20,30,40,50,60,70,80],w=4,h=2)
        with self.assertRaisesRegex(mod.Refusal,"geometries"):
            mod.reconstruct([self.r1,self.r2])
        with self.assertRaises(mod.Refusal):
            mod.build([self.r1,self.d1],[self.r2,self.d2],self.dir/"badout")

    def test_refuse_unsupported_encoding(self):
        b=bytearray(self.r1.read_bytes())
        # TIFF IFD: tag #3 is Compression=259; write compression 5.
        i=8+2+3*12+8
        struct.pack_into("<H",b,i,5)
        self.r1.write_bytes(b)
        with self.assertRaisesRegex(mod.Refusal,"Unsupported"):
            mod.read_u16_tiff(self.r1)

    def test_refuse_output_overwrite(self):
        out=self.dir/"out"
        mod.build([self.r1,self.r2],[self.d1,self.d2],out)
        with self.assertRaisesRegex(mod.Refusal,"already exists"):
            mod.build([self.r1,self.r2],[self.d1,self.d2],out)

    def test_archived_average_comparison_identity(self):
        report=mod.build([self.r1,self.r1.with_name("r2.tif")],[self.d1,self.d2],
                          self.dir/"compare",archive_reference=self.r1)
        self.assertGreater(report["archived_average_comparisons"]["reference"]["pixelwise_correlation"],0.99)


if __name__=="__main__":
    unittest.main()
