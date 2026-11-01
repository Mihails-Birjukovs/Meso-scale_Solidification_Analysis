"""Offline tests for explicit OFV pair and concentration timestamp admission."""
import importlib.util
import math
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "Python_code" / "phase0_time_registration.py"
spec = importlib.util.spec_from_file_location("phase0_time_registration", PATH)
registration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registration)


def fixture(dt=0.2, frame_count=15, bin_size=5, source="camera_metadata"):
    raw = [{"id": i, "time_s": i * dt} for i in range(frame_count)]
    bins = [{"id": i, "raw_ids": list(range(i * bin_size, (i + 1) * bin_size))}
            for i in range(frame_count // bin_size)]
    centers = [sum(raw[j]["time_s"] for j in b["raw_ids"]) / len(b["raw_ids"]) for b in bins]
    return {
        "schema": registration.SCHEMA,
        "clock_source": source, "time_origin_description": "Synthetic observation clock t=0 at first image center",
        "nominal_source_dt_s": dt, "max_abs_frame_dt_deviation_s": dt * 0.1,
        "concentration_time_tolerance_s": 1e-7,
        "raw_frames": raw, "image_bins": bins,
        "concentration_frames": [{"id": i, "image_id": i, "time_s": centers[i]}
                                  for i in range(len(bins))],
        "flow_pairs": [{"id": i, "image_ids": [i, i + 1]} for i in range(len(bins) - 1)],
    }


class TimeRegistrationTests(unittest.TestCase):
    def test_raw_5hz_bin5_pair_midpoints(self):
        x = registration.plan_time_registration(fixture())
        self.assertEqual(x["admission"], "timing_preflight_passed")
        self.assertEqual(x["bin_center_times_s"], [0.4, 1.4, 2.4])
        self.assertAlmostEqual(x["flow_pair_registrations"][0]["time_midpoint_s"], 0.9)
        self.assertAlmostEqual(x["flow_pair_registrations"][0]["image_pair_duration_s"], 1)
        self.assertEqual(x["flow_pair_registrations"][0]["concentration_interpolation_weights"], [0.5, 0.5])

    def test_raw_1hz_is_not_assumed_to_be_5hz(self):
        x = registration.plan_time_registration(fixture(dt=1))
        self.assertEqual(x["bin_center_times_s"], [2, 7, 12])
        self.assertEqual(x["flow_pair_registrations"][0]["time_midpoint_s"], 4.5)
        self.assertEqual(x["flow_pair_registrations"][0]["image_pair_duration_s"], 5.0)

    def test_filename_clock_is_diagnostic_only(self):
        x = registration.plan_time_registration(fixture(source="filename_candidate"))
        self.assertEqual(x["admission"], "diagnostic_only_unverified_filename_clock")

    def test_rejects_gap_in_raw_frame_timestamps(self):
        x = fixture(dt=1)
        for r in x["raw_frames"][8:]:
            r["time_s"] += 3
        with self.assertRaisesRegex(registration.AdmissionError, "gap"):
            registration.plan_time_registration(x)

    def test_rejects_missing_concentration_frame(self):
        x = fixture()
        x["concentration_frames"].pop()
        with self.assertRaisesRegex(registration.AdmissionError, "one per"):
            registration.plan_time_registration(x)

    def test_rejects_unregistered_concentration_time(self):
        x = fixture()
        x["concentration_frames"][0]["time_s"] += .08
        with self.assertRaisesRegex(registration.AdmissionError, "concentration time"):
            registration.plan_time_registration(x)

    def test_rejects_unverified_or_missing_clock_provenance(self):
        for source in (None, "guess_from_avi", "unknown"):
            with self.subTest(source=source):
                x = fixture(source=source)
                with self.assertRaisesRegex(registration.AdmissionError, "clock_source"):
                    registration.plan_time_registration(x)

    def test_rejects_nonmonotonic_source(self):
        x = fixture()
        x["raw_frames"][4]["time_s"] = x["raw_frames"][3]["time_s"]
        with self.assertRaisesRegex(registration.AdmissionError, "strictly"):
            registration.plan_time_registration(x)

    def test_rejects_duplicate_ids_and_missing_source(self):
        x = fixture()
        x["raw_frames"][6]["id"] = 5
        with self.assertRaisesRegex(registration.AdmissionError, "contiguous"):
            registration.plan_time_registration(x)
        x = fixture()
        x["image_bins"][1]["raw_ids"][1] = 100
        with self.assertRaisesRegex(registration.AdmissionError, "missing raw"):
            registration.plan_time_registration(x)

    def test_rejects_pair_misassociation(self):
        x = fixture()
        x["flow_pairs"][0]["image_ids"] = [1,2]
        with self.assertRaisesRegex(registration.AdmissionError, "adjacent"):
            registration.plan_time_registration(x)

    def test_rejects_overlapping_bins(self):
        x = fixture()
        x["image_bins"][1]["raw_ids"] = [4,5,6,7,8]
        with self.assertRaisesRegex(registration.AdmissionError, "overlapping"):
            registration.plan_time_registration(x)

    def test_rejects_bin_index_gap(self):
        x = fixture()
        x["image_bins"][1]["raw_ids"] = [6,7,8,9,10]
        with self.assertRaisesRegex(registration.AdmissionError, "gap"):
            registration.plan_time_registration(x)

    def test_rejects_nan_and_bool_times(self):
        for invalid in (float("nan"), float("inf"), True, None):
            with self.subTest(invalid=invalid):
                x = fixture()
                x["raw_frames"][2]["time_s"] = invalid
                with self.assertRaises(registration.AdmissionError):
                    registration.plan_time_registration(x)


if __name__ == "__main__":
    unittest.main()
