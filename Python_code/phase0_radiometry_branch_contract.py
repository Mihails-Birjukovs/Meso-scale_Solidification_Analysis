"""Conservative Ga–In radiometry admission policy.

This is a metadata/scalar reference contract, not a full processing pipeline.
The operational default is measured-flat-only normalization I/R_flat.

An available folder named "Dark Current" is NOT evidence that D is a valid
additive detector offset. No dark correction is admitted to production unless
all independent physical and source-matching gates pass.

Candidate sample baseline J0 is distinct from detector flat-field R_flat.
A specimen log ratio calculated against a provisional J0 cannot be published
as calibrated optical density P or In wt.% until phase and composition gates
are independently accepted.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Literal


WORKING_DEFAULT = "flat_only"
SCHEMA = "ga-in-radiometric-branch-contract/v1"
BRANCHES = ("flat_only", "dark_diagnostic", "dark_validated")


class RadiometryAdmissionError(ValueError):
    """The proposed radiometric analysis lacks required source/physics evidence."""


@dataclass(frozen=True)
class DarkGateEvidence:
    original_counts_verified: bool = False
    detector_is_true_dark_verified: bool = False
    exposure_gain_geometry_matched: bool = False
    dark_temporal_stability_verified: bool = False
    dark_spatial_validity_mask_verified: bool = False
    signal_above_dark_full_physical_roi_verified: bool = False
    explicit_owner_production_authorization: bool = False

    def blockers(self) -> tuple[str, ...]:
        return tuple(name for name in self.__dataclass_fields__
                     if not getattr(self, name))

    def fully_admitted(self) -> bool:
        return not self.blockers()


@dataclass(frozen=True)
class SampleBaselineEvidence:
    raw_experiment_frame_ids_verified: bool = False
    camera_geometry_and_ROI_verified: bool = False
    all_liquid_pre_cooling_verified: bool = False
    homogeneous_initial_alloy_verified: bool = False
    initial_25wtpct_composition_verified: bool = False
    sample_reference_heldout_validation_passed: bool = False

    def blockers(self) -> tuple[str, ...]:
        return tuple(name for name in self.__dataclass_fields__
                     if not getattr(self, name))

    def fully_admitted(self) -> bool:
        return not self.blockers()


def admit_branch(
    requested: str = WORKING_DEFAULT,
    *,
    flat_field_role_confirmed: bool = True,
    dark_gates: DarkGateEvidence | None = None,
) -> dict:
    """Choose analysis status without silently allowing experimental dark mode."""
    if requested not in BRANCHES:
        raise RadiometryAdmissionError("Unknown correction branch")
    if not flat_field_role_confirmed:
        raise RadiometryAdmissionError("Raw Reference must be verified as detector flat field")
    if requested == "flat_only":
        return {
            "schema": SCHEMA,
            "branch": "flat_only",
            "role_of_Reference": "measured_detector_flat_field",
            "dark_applied": False,
            "production_exploratory_normalization_admitted": True,
            "absolute_composition_calibration_admitted": False,
            "limitations": ("No measured additive offset is subtracted",
                            "A verified homogeneous specimen J0 is required separately"),
        }
    if requested == "dark_diagnostic":
        return {
            "schema": SCHEMA,
            "branch": requested,
            "role_of_Reference": "measured_detector_flat_field",
            "dark_applied": True,
            "production_exploratory_normalization_admitted": False,
            "absolute_composition_calibration_admitted": False,
            "limitations": ("Diagnostic only: invalid/unstable dark offset",
                            "Strict positivity and saturation mask required"),
        }
    if not isinstance(dark_gates, DarkGateEvidence) or not dark_gates.fully_admitted():
        bad = dark_gates.blockers() if isinstance(dark_gates, DarkGateEvidence) else ("missing_dark_gate_evidence",)
        raise RadiometryAdmissionError("Dark-corrected production mode BLOCKED: "+", ".join(bad))
    return {
        "schema": SCHEMA,
        "branch": requested,
        "role_of_Reference": "measured_detector_flat_field",
        "dark_applied": True,
        "production_exploratory_normalization_admitted": True,
        "absolute_composition_calibration_admitted": False,
        "limitations": ("A verified homogeneous specimen J0 and chemical anchors are still required",),
    }


def diagnostic_pixel_ratio(
    I: float,
    R_flat: float,
    *,
    mode: Literal["flat_only", "dark_diagnostic", "dark_validated"] = WORKING_DEFAULT,
    D: float | None = None,
    dark_gates: DarkGateEvidence | None = None,
    saturation_level: float = 65535.0,
) -> dict:
    """One unmodified raw-count pixel. Never fabricate a ratio at invalid pixels."""
    policy = admit_branch(mode, dark_gates=dark_gates)
    if not all(math.isfinite(float(v)) for v in (I, R_flat, saturation_level)):
        return {"status": "INVALID_INPUT", "ratio": None}
    if saturation_level <= 0 or I <= 0 or R_flat <= 0 or I >= saturation_level or R_flat >= saturation_level:
        return {"status": "INVALID_RAW_COUNTS_OR_SATURATION", "ratio": None}
    numerator = float(I)
    denominator = float(R_flat)
    if mode != "flat_only":
        if D is None or not math.isfinite(float(D)):
            return {"status": "MISSING_OR_NONFINITE_DARK", "ratio": None}
        if D < 0 or D >= saturation_level:
            return {"status": "INVALID_DARK_COUNTS", "ratio": None}
        numerator -= float(D)
        denominator -= float(D)
        if denominator <= 0:
            return {"status": "R_LE_D", "ratio": None}
        if numerator <= 0:
            return {"status": "I_LE_D", "ratio": None}
    ratio = numerator / denominator
    if ratio <= 0 or not math.isfinite(ratio):
        return {"status": "INVALID_RATIO", "ratio": None}
    return {"status": "VALID" if policy["production_exploratory_normalization_admitted"]
            else "DIAGNOSTIC_ONLY", "ratio": ratio}


def specimen_log_ratio(
    sample_flat_normalized: float,
    specimen_initial_flat_normalized: float,
    *,
    baseline_evidence: SampleBaselineEvidence | None = None,
) -> dict:
    """Specimen-relative logarithmic ratio, with explicit calibration admission."""
    if not all(math.isfinite(float(v)) and v > 0
               for v in (sample_flat_normalized, specimen_initial_flat_normalized)):
        return {"status": "INVALID_INTENSITIES", "P": None, "composition_admitted": False}
    p = -math.log(sample_flat_normalized/specimen_initial_flat_normalized)
    accepted = isinstance(baseline_evidence, SampleBaselineEvidence) and baseline_evidence.fully_admitted()
    return {
        "status": "SPECIMEN_BASELINE_ADMITTED" if accepted else "PROVISIONAL_SAMPLE_LOG_RATIO",
        "P": p,
        "composition_admitted": False,  # no solid/liquid end-point calibration
        "baseline_blockers": () if accepted else
           (baseline_evidence.blockers() if isinstance(baseline_evidence, SampleBaselineEvidence)
            else ("missing_sample_baseline_evidence",)),
    }
