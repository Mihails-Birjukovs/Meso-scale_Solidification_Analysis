"""Synthetic header-only tests; never access the owner's 1.5 GB source archive."""
import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "Python_code" / "phase0_2014_04_04_archive_admission.py"
spec = importlib.util.spec_from_file_location("archive2014", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

SHA = "77fac9a38a9cdaa41ee5ec9c9562acb7149ee1cee8f0246a80c2b267928f2510"


def item(path, size=648658, crc="ABCDEF12", directory=False):
    return (
        f"Path = {path}\nSize = {0 if directory else size}\n"
        f"Packed Size = \nAttributes = {'D' if directory else 'A'}\n"
        f"CRC = {'' if directory else crc}\n"
        "Encrypted = -\nMethod = \nBlock = 0\n"
    )


def fixture(*, include_end=True, altered_path=None):
    paths = [
        ("2014-04-04", 0, "", True),
        ("2014-04-04\\2014-04-04", 0, "", True),
        ("2014-04-04\\Reference", 0, "", True),
        ("2014-04-04\\Reference\\ga-25in-ref1_2014-04-04_10-07-43-889.tif", 648664, "1234ABCD", False),
        ("2014-04-04\\2014-04-04\\ga-25in-1_2014-04-04_10-25-47-069.tif", 648658, "1234ABCD", False),
        ("2014-04-04\\2014-04-04\\ga-25in-1_2014-04-04_10-25-48-069.tif", 648658, "1234ABCD", False),
        ("2014-04-04\\2014-04-04\\ga-25in-end1_2014-04-04_11-21-20-997.tif", 648658, "1234ABCD", False),
        ("2014-04-04\\2014-04-04\\ga-25in-end1_2014-04-04_11-21-21-997.tif", 648658, "1234ABCD", False),
        ("2014-04-04\\Thumbs.db", 7680, "1234ABCD", False),
    ]
    if not include_end:
        paths = paths[:6] + paths[8:]
    if altered_path:
        path, size, crc, directory = paths[5]
        paths[5] = (altered_path, size, crc, directory)
    header = (
        "7-Zip 26.02 (x64)\n\nListing archive: mock.7z\n\n--\n"
        "Path = mock.7z\nType = 7z\nPhysical Size = 123456\n"
        "Headers Size = 2345\nSolid = +\nBlocks = 2\n\n----------\n"
    )
    return header + "\n".join(item(*v) for v in paths)


def case():
    return {
        "schema": module.SCHEMA, "id": "2014-04-04",
        "archive_sha256": SHA,
        "expected_tiff_counts": {"reference": 1, "main": 2, "end": 2},
        "expected_auxiliary_files": 1,
        "expected_directories": 3,
    }


class ArchiveAdmissionTests(unittest.TestCase):
    def test_admits_header_only_and_refuses_physical_assumptions(self):
        result = module.admit_listing(fixture(), case(), archive_sha256=SHA)
        self.assertEqual(result["total_tiff_files"], 5)
        self.assertEqual(result["total_files"], 6)
        self.assertEqual(len(result["filename_candidate_frame_records"]["reference"]), 1)
        self.assertEqual(len(result["filename_candidate_frame_records"]["main"]), 2)
        self.assertEqual(result["filename_candidate_frame_records"]["main"][0]["candidate_ordinal_id_zero_based"], 0)
        self.assertTrue(result["archive_sha256_verified"])
        self.assertEqual(result["streams"]["main"]["span_s"], 1)
        self.assertEqual(result["filename_reference_to_main_gap_s"], 1083.18)
        self.assertFalse(result["physical_clock_admitted"])
        self.assertFalse(result["original_tiff_pixels_decoded"])
        self.assertFalse(result["member_crc32_is_verified"])
        self.assertFalse(result["reference_is_verified_homogeneous_liquid"])
        self.assertFalse(result["absolute_C_In_calibration_admitted"])

    def test_hash_not_optional_when_provided(self):
        with self.assertRaisesRegex(module.AdmissionError, "SHA256 mismatch"):
            module.admit_listing(fixture(), case(), archive_sha256="0"*64)

    def test_without_hash_is_lower_evidence(self):
        result = module.admit_listing(fixture(), case(), archive_sha256=None)
        self.assertFalse(result["archive_sha256_verified"])

    def test_missing_stream_rejected(self):
        with self.assertRaisesRegex(module.AdmissionError, "end count mismatch"):
            module.admit_listing(fixture(include_end=False), case(), archive_sha256=SHA)

    def test_unsafe_member_path_rejected(self):
        with self.assertRaisesRegex(module.AdmissionError, "unsafe"):
            module.admit_listing(fixture(altered_path="2014-04-04\\..\\evil.tif"),
                                 case(), archive_sha256=SHA)

    def test_duplicate_path_rejected(self):
        text = fixture().replace(
            "ga-25in-1_2014-04-04_10-25-48-069.tif",
            "ga-25in-1_2014-04-04_10-25-47-069.tif")
        with self.assertRaisesRegex(module.AdmissionError, "Duplicate"):
            module.admit_listing(text, case(), archive_sha256=SHA)

    def test_reject_wrong_stream_prefix(self):
        with self.assertRaisesRegex(module.AdmissionError, "Unrecognized"):
            module.admit_listing(
                fixture(altered_path="2014-04-04\\2014-04-04\\unknown_2014-04-04.tif"),
                case(), archive_sha256=SHA)

    def test_invalid_clock_rejected(self):
        with self.assertRaisesRegex(module.AdmissionError, "Out-of-range"):
            module.admit_listing(
                fixture(altered_path="2014-04-04\\2014-04-04\\ga-25in-1_2014-04-04_25-25-48-069.tif"),
                case(), archive_sha256=SHA)

    def test_malformed_header_or_extra_file_rejected(self):
        with self.assertRaisesRegex(module.AdmissionError, "separator"):
            module.parse_listing("Path = archive.7z\nType = 7z\n")
        with self.assertRaisesRegex(module.AdmissionError, "Unexpected file path"):
            module.admit_listing(
                fixture().replace("2014-04-04\\Thumbs.db", "2014-04-04\\notes.txt"),
                case(), archive_sha256=SHA)

    def test_duplicate_clock_different_filename_rejected(self):
        with self.assertRaisesRegex(module.AdmissionError, "Repeated filename timestamps"):
            module.summary_for([{"filename": "a", "filename_ms": 1000},
                                {"filename": "b", "filename_ms": 1000}])


if __name__ == "__main__":
    unittest.main()
