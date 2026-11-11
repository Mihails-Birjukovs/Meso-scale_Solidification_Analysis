"""Standard-library regression tests for the conservative radiometry decision gate."""
import importlib.util
from pathlib import Path
import math
import unittest

SOURCE=Path(__file__).resolve().parents[1]/"Python_code"/"phase0_radiometry_branch_contract.py"
spec=importlib.util.spec_from_file_location("phase0_contract",SOURCE)
module=importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name]=module
spec.loader.exec_module(module)


class RadiometryPolicyTests(unittest.TestCase):
    def test_default_is_flat_field_only(self):
        r=module.admit_branch()
        self.assertEqual(module.WORKING_DEFAULT,"flat_only")
        self.assertFalse(r["dark_applied"])
        self.assertTrue(r["production_exploratory_normalization_admitted"])
        self.assertFalse(r["absolute_composition_calibration_admitted"])

    def test_dark_validation_requires_every_gate(self):
        with self.assertRaisesRegex(module.RadiometryAdmissionError,"BLOCKED"):
            module.admit_branch("dark_validated")
        with self.assertRaisesRegex(module.RadiometryAdmissionError,"detector_is_true_dark"):
            module.admit_branch("dark_validated",dark_gates=module.DarkGateEvidence(original_counts_verified=True))

    def test_dark_diagnostic_is_never_production(self):
        r=module.admit_branch("dark_diagnostic")
        self.assertTrue(r["dark_applied"])
        self.assertFalse(r["production_exploratory_normalization_admitted"])

    def test_unverified_reference_role_is_rejected(self):
        with self.assertRaisesRegex(module.RadiometryAdmissionError,"Reference"):
            module.admit_branch(flat_field_role_confirmed=False)

    def test_flat_ratio_no_dark_count(self):
        p=module.diagnostic_pixel_ratio(40000,50000)
        self.assertEqual(p["status"],"VALID")
        self.assertEqual(p["ratio"],0.8)

    def test_dark_diagnostic_uses_strict_positivity(self):
        r=module.diagnostic_pixel_ratio(40000,50000,mode="dark_diagnostic",D=30000)
        self.assertEqual(r["status"],"DIAGNOSTIC_ONLY")
        self.assertEqual(r["ratio"],0.5)
        self.assertEqual(module.diagnostic_pixel_ratio(40000,50000,mode="dark_diagnostic",D=50000)["status"],"R_LE_D")
        self.assertEqual(module.diagnostic_pixel_ratio(30000,50000,mode="dark_diagnostic",D=35000)["status"],"I_LE_D")

    def test_dark_mode_refuses_mislabeled_and_nonfinite(self):
        p=module.diagnostic_pixel_ratio(40000,50000,mode="dark_diagnostic")
        self.assertEqual(p["status"],"MISSING_OR_NONFINITE_DARK")
        self.assertEqual(module.diagnostic_pixel_ratio(40000,50000,mode="dark_diagnostic",D=float("nan"))["status"],"MISSING_OR_NONFINITE_DARK")

    def test_saturation_never_clipped_or_fabricated(self):
        self.assertEqual(module.diagnostic_pixel_ratio(65535,65000)["status"],"INVALID_RAW_COUNTS_OR_SATURATION")
        self.assertEqual(module.diagnostic_pixel_ratio(1,65535)["ratio"],None)
        self.assertEqual(module.diagnostic_pixel_ratio(0,10000)["ratio"],None)

    def test_bad_mode_refused(self):
        with self.assertRaisesRegex(module.RadiometryAdmissionError,"Unknown correction"):
            module.admit_branch("auto_dark_if_present")

    def test_fully_validated_dark_does_not_imply_calibrated_chemistry(self):
        evidence=module.DarkGateEvidence(**{n:True for n in module.DarkGateEvidence.__dataclass_fields__})
        r=module.admit_branch("dark_validated",dark_gates=evidence)
        self.assertTrue(r["production_exploratory_normalization_admitted"])
        self.assertFalse(r["absolute_composition_calibration_admitted"])
        p=module.diagnostic_pixel_ratio(40000,50000,mode="dark_validated",D=30000,dark_gates=evidence)
        self.assertEqual(p["status"],"VALID")
        self.assertEqual(p["ratio"],0.5)

    def test_provisional_specimen_reference_not_25wtpct_by_assumption(self):
        r=module.specimen_log_ratio(.8,1.0)
        self.assertAlmostEqual(r["P"],-math.log(.8))
        self.assertEqual(r["status"],"PROVISIONAL_SAMPLE_LOG_RATIO")
        self.assertFalse(r["composition_admitted"])

    def test_baseline_admission_does_not_supply_endpoints(self):
        e=module.SampleBaselineEvidence(**{n:True for n in module.SampleBaselineEvidence.__dataclass_fields__})
        r=module.specimen_log_ratio(.8,1.0,baseline_evidence=e)
        self.assertEqual(r["status"],"SPECIMEN_BASELINE_ADMITTED")
        self.assertFalse(r["composition_admitted"])

    def test_invalid_specimen_intensities_refused(self):
        self.assertIsNone(module.specimen_log_ratio(0,1.0)["P"])
        self.assertIsNone(module.specimen_log_ratio(1.0,float("nan"))["P"])


if __name__=="__main__":
    unittest.main()
