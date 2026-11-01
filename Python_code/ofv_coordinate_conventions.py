"""Coordinate conventions for 2WCF-SVD outputs.

2WCF performs OpenCV forward flow (pixel-right, pixel-DOWN), then multiplies
BOTH output components by VelocityInversion. The legacy postprocessor keeps
positions and regular grids in image coordinates, so invert BOTH saved
components before interpolation. Do NOT flip only v while keeping y down.
"""
from __future__ import annotations
import math


def require_inversion(parameters: dict) -> float:
    """Refuse guessing about the saved vector direction."""
    if "VelocityInversion" not in parameters:
        raise ValueError("Missing upstream VelocityInversion in parameters.json")
    inversion = float(parameters["VelocityInversion"])
    if not math.isfinite(inversion) or inversion == 0:
        raise ValueError("VelocityInversion must be finite and nonzero")
    return inversion


def forward_image_components(u_saved, v_saved, *, inversion: float, m_per_pixel: float,
                             pair_dt_s: float):
    """Return image-forward velocity components (x-right, y-DOWN), in m/s.

    Accepts scalar or NumPy-array-like velocities. Arrays undergo only scalar
    multiplication, avoiding accidental changes of observation positions.
    """
    if not math.isfinite(inversion) or inversion == 0:
        raise ValueError("Invalid VelocityInversion")
    if not math.isfinite(m_per_pixel) or m_per_pixel <= 0:
        raise ValueError("m_per_pixel must be positive and finite")
    if not math.isfinite(pair_dt_s) or pair_dt_s <= 0:
        raise ValueError("pair_dt_s must be positive and finite")
    factor = m_per_pixel / (pair_dt_s * inversion)
    return u_saved * factor, v_saved * factor


def physical_cartesian_velocity(u_image, v_image):
    """Cartesian x-right/y-UP components from image-forward components."""
    return u_image, -v_image


def physical_vorticity_from_image_derivatives(du_dy_image, dv_dx_image):
    """Physical out-of-plane vorticity for y-down grid gradients.

    For u_cart = u_image, v_cart = -v_image, y_cart = -y_image:
    dv_cart/dx - du_cart/dy_cart = du_image/dy_image - dv_image/dx.
    """
    return du_dy_image - dv_dx_image
