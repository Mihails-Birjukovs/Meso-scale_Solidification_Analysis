# -*- coding: utf-8 -*-

"""
Step 1:
Load measurement images and reference images.

No preprocessing yet.
Interactive slider viewer and crop selection.
"""

# %% Libraries
from pathlib import Path
import numpy as np
import tifffile
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
# from pathlib import Path # for cropping
import json
from scipy.ndimage import uniform_filter # for uniform filter making
import cv2 # for downsampling
# %% Cropping part
# =============================================================================
# Function to load image sequence

def load_image_folder(folder_path):
    folder = Path(folder_path)
    files = sorted(folder.glob("*.tif"))
    if len(files) == 0:
        raise FileNotFoundError(f"No TIFF images found in:\n{folder}")

    images = []
    for file in files:
        # Keep original TIFF datatype
        image = tifffile.imread(file)
        images.append(image)

    # Convert list to numpy array
    # Shape: (frames, height, width)
    images = np.array(images)

    print("--------------------------------")
    print("Folder:")
    print(folder)

    print("Number of images:", len(images))
    print("Image stack shape:", images.shape)
    print("Data type:", images.dtype)
    print("--------------------------------\n")
    return images

# =============================================================================
# Paths
IMAGES_FOLDER = (
    r"C:\Users\Lenovo\OneDrive - University of Latvia\Desktop"
    r"\Maģistra darbs\Solidification_image_analysis_code"
    r"\Pre-processing\Example_input_output\Input"
    r"\2011-09-09-Experiment-1")

REFERENCE_FOLDER = (
    r"C:\Users\Lenovo\OneDrive - University of Latvia\Desktop"
    r"\Maģistra darbs\Solidification_image_analysis_code"
    r"\Pre-processing\Example_input_output\Input"
    r"\Reference")

# =============================================================================
# Load data
images = load_image_folder(IMAGES_FOLDER)
reference_images = load_image_folder(REFERENCE_FOLDER)
print("Image shape ", images.shape)
print("Reference image shape", reference_images.shape)
# Check image and reference spatial dimensions
if images.shape[1:] != reference_images.shape[1:]:
    raise ValueError("Measurement and reference images have different spatial dimensions!")
print("Spatial dimensions match: OK")

# =============================================================================
# See picture examples
plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
plt.imshow(images[-1], cmap="gray")
plt.title(f"Measurement image\n{images[0].shape}")
plt.axis("off")

plt.subplot(1,2,2)
plt.imshow(reference_images[-1],cmap="gray")
plt.title(f"Reference image\n{reference_images[0].shape}")
plt.axis("off")
plt.show()


# =============================================================================
# %% Interactive slider (run to look at pictures before clipping)
# if you dont see the slide, try this in console: %matplotlib qt and press Enter
# =============================================================================
plt.ion()
fig, ax = plt.subplots(figsize=(8,6))
# Leave space for slider
fig.subplots_adjust(bottom=0.15)

# Initial frame
current_frame = 0
img_plot = ax.imshow(images[current_frame], cmap="gray")
ax.set_title(f"Frame {current_frame}")

# slider position
slider_ax = plt.axes([0.2, 0.04, 0.6, 0.03])
slider = Slider(slider_ax, "Frame", 0, len(images)-1, valinit=0, valstep=1)

def update(frame):
    frame = int(frame)
    img_plot.set_data(images[frame])
    ax.set_title(f"Frame {frame}")
    fig.canvas.draw_idle()

slider.on_changed(update)

# Give Matplotlib time to create and display the window
plt.pause(1)
print("\n========================================")
print("Image viewer")
print("========================================")
print("Use the slider to inspect the image sequence.")
print("The X and Y axes show the pixel coordinates.")
print("")
print("When you have finished inspecting the images,")
print("run the next cell to enter crop coordinates.")
print("========================================")


# %% Cropping by using coordinates (palaid šo šūnu, kad slideri esi apskatījis)
# =============================================================================
print("\n==============================")
print("CROP SELECTION")
print("==============================")
print("Image size (height, width):", images.shape[1:])

# Coordinates
x1 = int(input("Enter top-left corner X coordinate: "))
y1 = int(input("Enter top-left corner Y coordinate: "))
x2 = int(input("Enter bottom-right corner X coordinate: "))
y2 = int(input("Enter bottom-right corner Y coordinate: "))

# Frame range
start_frame = int(input("Enter first frame number: "))
end_frame = int(input("Enter last frame number: "))

# Check that all bounds are natural numbers
for name, value in [("x1", x1), ("y1", y1), ("x2", x2), ("y2", y2),
                     ("start_frame", start_frame), ("end_frame", end_frame)]:
    if not isinstance(value, (int, np.integer)) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer, got {type(value).__name__}.")

# Check coordinates and frames
if x1 < 0 or y1 < 0:
    raise ValueError("Crop coordinates cannot be negative.")
if x2 > images.shape[2] or y2 > images.shape[1]:
    raise ValueError("Crop coordinates exceed image dimensions.")
if x2 <= x1 or y2 <= y1:
    raise ValueError("Invalid crop coordinates: x2 must be greater than x1 "
        "and y2 must be greater than y1.")
if start_frame < 0 or end_frame >= len(images):
    raise ValueError("Frame range outside available images.")
if end_frame < start_frame:
    raise ValueError("Invalid frame range: end_frame must be >= start_frame.")

# =============================================================================
# Create cropped images
croppedImages = images[start_frame:end_frame + 1, y1:y2, x1:x2]
print("\n==============================")
print("Cropping completed")
print("==============================")
print("Original images:", images.shape)
print("Cropped images:", croppedImages.shape)

# =============================================================================
# Crop reference images
croppedReferenceImages = reference_images[:, y1:y2, x1:x2]
print("\n==============================")
print("Reference cropping completed")
print("==============================")
print("Original reference images:", reference_images.shape)
print("Cropped reference images:", croppedReferenceImages.shape)

# =============================================================================
# SAVE CROPPED IMAGES
# Main output folder
base_folder = Path(
    r"C:\Users\Lenovo\OneDrive - University of Latvia\Desktop"
    r"\Maģistra darbs\Solidification_image_analysis_code"
    r"\Pre-processing\Example_input_output\Output\2011-09-09-Experiment-1")

# Create croppedImages folder if it does not exist
cropped_folder = base_folder / "croppedImages"
cropped_folder.mkdir(parents=True, exist_ok=True)

# Ask user for subfolder name
folder_name = input("Enter name for cropped image folder: ")

# Create user-defined folder inside croppedImages
output_folder = cropped_folder / folder_name
output_folder.mkdir(parents=True, exist_ok=True)

# Save images
for i, image in enumerate(croppedImages):
    filename = (output_folder / f"croppedImage_{start_frame+i:05d}.tif")
    tifffile.imwrite(filename, image)

print("\n==============================")
print("Cropping export completed")
print("==============================")
print(f"Saved {len(croppedImages)} images")
print("Location:", output_folder)

# =============================================================================
# Save cropped reference images
reference_output_folder = cropped_folder / (folder_name + "_Reference")
reference_output_folder.mkdir(parents=True, exist_ok=True)

for i, image in enumerate(croppedReferenceImages):
    filename = (reference_output_folder / f"croppedReferenceImage_{i:05d}.tif")
    tifffile.imwrite(filename, image)

print(f"Saved {len(croppedReferenceImages)} cropped reference images")
print("Reference location:", reference_output_folder)

# =============================================================================
# Save cropp parameters
crop_parameters = {"x1": x1, "y1": y1, "x2": x2, "y2": y2,
"start_frame": start_frame, "end_frame": end_frame,
"original_image_shape": list(images.shape),
"cropped_image_shape": [end_frame - start_frame + 1, y2 - y1, x2 - x1]}

json_path = output_folder / "crop_parameters.json"
with open(json_path, "w") as file:
    json.dump(crop_parameters, file, indent=4)
print("Saved crop parameters:", json_path)



# %% Flat field correction
# =============================================================================
referenceFrame = croppedReferenceImages.astype(np.float32).mean(axis=0)
print("Reference frame shape:", referenceFrame.shape)
print("Reference frame min/max:", referenceFrame.min(), referenceFrame.max())
# we canot replace zero values just by 1e-6...
# referenceFrame_safe = np.where(referenceFrame == 0, 1e-6, referenceFrame)
zero_reference = np.sum(referenceFrame == 0)

print("Zero reference pixels:", zero_reference)
print("Total pixels:", referenceFrame.size)
print("Fraction:", zero_reference / referenceFrame.size)

# =============================================================================
# R_flat is the owner-confirmed flat-field recording in Reference/, NOT J0.
# Operational branch: I_corr=I/R_flat, no additive dark subtraction.
# Historical Dark Current recordings require independent stability/offset QA.

# Convert measurement images to float32
I_measurement = croppedImages.astype(np.float32)

# Check where measurement and reference intensities are valid
valid_mask = (np.isfinite(I_measurement) & (I_measurement > 0) &
    np.isfinite(referenceFrame)[None, :, :] & (referenceFrame[None, :, :] > 0))

# Create an array filled with NaN
I_corr = np.full(I_measurement.shape, np.nan, dtype=np.float32)

# Divide only where both intensities are valid
np.divide(I_measurement, referenceFrame[None, :, :],
    out=I_corr, where = valid_mask)
print("I_corr shape:", I_corr.shape)
print("I_corr value range:", I_corr.min(), I_corr.max())
print("I_corr value range:", np.nanmin(I_corr), np.nanmax(I_corr))


# %% Diagnostic: invalid normalized intensities

invalid_mask = ~np.isfinite(I_corr) | (I_corr <= 0)

print("Invalid intensity pixels:", np.sum(invalid_mask))
print("Invalid intensity fraction:", np.mean(invalid_mask))
print("Non-finite pixels:", np.sum(~np.isfinite(I_corr)))
print("Zero pixels:", np.sum(I_corr == 0))
print("Negative pixels:", np.sum(I_corr < 0))

valid_values = I_corr[np.isfinite(I_corr) & (I_corr > 0)]

if valid_values.size > 0:
    print("Valid I_corr min:", valid_values.min())
    print("Valid I_corr max:", valid_values.max())
else:
    raise ValueError("No valid I_corr values found!")
    
# =============================================================================
# %%Quick preview of I_corr
plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
plt.imshow(croppedImages[0], cmap="gray")
plt.title("Before correction")
plt.axis("off")

plt.subplot(1,2,2)
plt.imshow(I_corr[0], cmap="gray")
plt.title("I / R_flat (flat-field only)")
plt.axis("off")
plt.show()

# %% Check data type of I_corrr, is it float (not uint)
print("I_corr dtype:", I_corr.dtype)

# %% Optical density
# =============================================================================
g_raw = -np.log(I_corr)   # diagnostic -ln(I/R_flat), not specimen P
print("g_raw value range:", np.nanmin(g_raw), np.nanmax(g_raw))

plt.figure(figsize=(6,5))
plt.imshow(g_raw[0], cmap="viridis")
plt.colorbar(label="g")
plt.title("Flat-field log ratio, first cropped frame (uncalibrated)")
plt.axis("off")
plt.show()

# %% Diagnostika - kur atrodas negatīvās g vērtības
# =============================================================================
negative_mask = g_raw < 0
print("Negative pixel part:", negative_mask.mean())
plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
plt.imshow(g_raw[0], cmap="RdBu_r", vmin=-0.1, vmax=0.1)
plt.colorbar(label="g")
plt.title("g (red = positive, blue = negative), frame 1")
plt.axis("off")

plt.subplot(1,2,2)
plt.hist(g_raw[0].ravel(), bins = 100)
plt.axvline(0, color='r', linestyle='--')
plt.xlabel("g")
plt.title("g histogram, frame 1")
plt.show()


# %% Temporal binning (on I_corr)
# =============================================================================
bin_size = 5
n_frames = I_corr.shape[0]
n_complete_bins = n_frames // bin_size
discarded = n_frames % bin_size

I_corr_trimmed = I_corr[:n_complete_bins * bin_size]
I_corr_binned = I_corr_trimmed.reshape(
    n_complete_bins, bin_size, *I_corr.shape[1:]).mean(axis=1)

dt0 = 0.2 # oriģinālais kadra ilgums [s]
dt_eff = bin_size * dt0
f_eff = 1.0 / dt_eff

print(f"Initial frames: {n_frames}, dropped out (what is left): {discarded}")
print(f"Binned frames: {I_corr_binned.shape[0]}")
print(f"dt: {dt_eff} s, frame frequency: {f_eff} Hz")


# %% Spatial downsampling (Lanczos, on binned I_corr, still linear domain)
# =============================================================================
downsample_factor = 4

height, width = I_corr_binned.shape[1:]
target_size = (round(width / downsample_factor), round(height / downsample_factor))  # cv2: (w, h)

I_corr_downsampled = np.stack([
cv2.resize(frame, target_size, interpolation = cv2.INTER_AREA)
    for frame in I_corr_binned])

print("Downsampled shape:", I_corr_downsampled.shape)

# Check invalid intensities after downsampling
n_bad = np.sum(~np.isfinite(I_corr_downsampled) | (I_corr_downsampled <= 0))
print("Invalid pixels after downsampling:", n_bad)

if n_bad > 0:
    raise ValueError("Invalid intensities after downsampling!")

I_corr_downsampled_safe = I_corr_downsampled

dx0 = 17.5  # µm/px
dx_eff = downsample_factor * dx0
print(f"Effective pixel size: {dx_eff} µm/px")

# %% Optical density - uz tā paša režģa, ko izmantos ātruma lauks
# =============================================================================
g_downsampled = -np.log(I_corr_downsampled_safe)
print("g_downsampled value range:", g_downsampled.min(), g_downsampled.max())

# Find global minimum and maximum of g_downsampled
g_min = np.nanmin(g_downsampled)
g_max = np.nanmax(g_downsampled)

# Find their positions (frame, y, x)
min_pos = np.unravel_index(np.nanargmin(g_downsampled), g_downsampled.shape)
max_pos = np.unravel_index(np.nanargmax(g_downsampled), g_downsampled.shape)

print(f"Global g minimum: {g_min:.6f}")
print(f"Global g maximum: {g_max:.6f}")

print("Minimum position (frame, y, x):", min_pos)
print("Maximum position (frame, y, x):", max_pos)

plt.figure(figsize=(6,5))
plt.imshow(g_downsampled[0], cmap="viridis")
plt.colorbar(label="g")
plt.title("Optical density, frame 1")
plt.axis("off")
plt.show()

print("g satur NaN/Inf:", np.any(~np.isfinite(g_downsampled)))

# %% Diagnostika - kur atrodas negatīvās g vērtības
# =============================================================================
negative_mask = g_downsampled < 0
print(f"Negative g fraction: {100 * negative_mask.mean():.2f}%")
plt.figure(figsize=(12,5))
frame_idx = len(g_downsampled) // 2
plt.subplot(1,2,1)
plt.imshow(g_downsampled[frame_idx], cmap="RdBu_r", vmin=-0.1, vmax=0.1)
plt.colorbar(label="g")
plt.title("g (red = positive, blue = negative), frame {frame_idx + 1}")
plt.axis("off")

plt.subplot(1,2,2)
plt.hist(g_downsampled[frame_idx].ravel(), bins=100)
plt.axvline(0, color='r', linestyle='--')
plt.xlabel("g")
plt.title(f"g histogram, frame {frame_idx + 1}")
plt.show()


# %% Validation preview - sākums, vidus, beigas (checklist p.8 no dokumenta)
# =============================================================================
vmin = np.nanmin(g_downsampled)
vmax = np.nanmax(g_downsampled)
fig, axes = plt.subplots(1, 3, figsize=(15,5))
for ax, idx, label in zip(axes, [0, len(g_downsampled)//2, len(g_downsampled) - 1], ["Start", "Middle", "End"]):
    im = ax.imshow(g_downsampled[idx], cmap="viridis", vmin=vmin, vmax=vmax)
    ax.set_title(f"{label} (frame {idx + 1})")
    ax.axis("off")
fig.colorbar(im, ax=axes, shrink=0.6, label="g")
plt.show()


# %% Calibration - full image g viewer
# ============================================================
# Use the ORIGINAL full images, not croppedImages.
# Apply the same correction, temporal binning and downsampling.
# Calculate one frame at a time to save memory.
# ============================================================

# Average full reference image
reference_full = reference_images.astype(np.float32).mean(axis=0)

# Check image dimensions
if images.shape[1:] != reference_full.shape:
    raise ValueError("Measurement and reference image sizes do not match!")

# Number of complete temporal bins
n_full_bins = len(images) // bin_size
if n_full_bins < 2:
    raise ValueError("At least two binned frames are required for the slider.")

# Full image dimensions
H, W = reference_full.shape

target_size_full = (round(W / downsample_factor), round(H / downsample_factor))


# ============================================================
# Calculate g for one full-image temporal bin
# ============================================================

def calculate_full_g(bin_idx):

    start = bin_idx * bin_size
    end = start + bin_size

    # Select original full-size frames
    measurement = images[start:end].astype(np.float32)

    # Check valid intensities
    valid = (np.isfinite(measurement) &
        (measurement > 0) &
        np.isfinite(reference_full)[None, :, :] &
        (reference_full[None, :, :] > 0))

    # Reference correction
    I_corr_full = np.full(measurement.shape, np.nan, dtype=np.float32)

    np.divide(measurement,
        reference_full[None, :, :],
        out=I_corr_full,
        where=valid)

    # Temporal average, ignoring invalid values
    valid_count = np.sum(valid, axis=0)
    intensity_sum = np.nansum(I_corr_full, axis=0)

    I_binned_full = np.zeros((H, W), dtype=np.float32)

    np.divide(intensity_sum,
        valid_count,
        out=I_binned_full,
        where=valid_count > 0)

    # Spatial downsampling, respecting invalid pixels
    coverage = (valid_count > 0).astype(np.float32)

    numerator = cv2.resize(
        I_binned_full * coverage,
        target_size_full,
        interpolation=cv2.INTER_AREA)

    denominator = cv2.resize(coverage,
        target_size_full,
        interpolation=cv2.INTER_AREA)

    I_downsampled_full = np.full_like(numerator, np.nan)

    np.divide(numerator,
        denominator,
        out=I_downsampled_full,
        where=denominator > 0)

    # Optical density
    g_full = np.full_like(I_downsampled_full, np.nan)

    valid_g = (np.isfinite(I_downsampled_full) &
        (I_downsampled_full > 0))

    g_full[valid_g] = -np.log(I_downsampled_full[valid_g])

    return g_full


# ============================================================
# Interactive viewer
# ============================================================

plt.ion()

# Keep track of the selected frame
calibration_selection = {"frame_idx": 0}
initial_g = calculate_full_g(0)

# Find common color limits across all full-image frames
vmin = np.inf
vmax = -np.inf

for i in range(n_full_bins):
    g_frame = calculate_full_g(i)
    valid_values = g_frame[np.isfinite(g_frame)]

    if valid_values.size > 0:
        vmin = min(vmin, valid_values.min())
        vmax = max(vmax, valid_values.max())

if not np.isfinite(vmin) or not np.isfinite(vmax):
    raise ValueError("No valid g values found!")

print(f"Common g color range: {vmin:.6f} to {vmax:.6f}")
fig, ax = plt.subplots(figsize=(9, 7))
fig.subplots_adjust(bottom=0.18)
img_plot = ax.imshow(initial_g, cmap="viridis", vmin=vmin, vmax=vmax)
fig.colorbar(img_plot, ax=ax, label="Optical density g")
ax.set_title("Full image - frame 1")
ax.set_xlabel("X (downsampled pixels)")
ax.set_ylabel("Y (downsampled pixels)")
slider_ax = fig.add_axes([0.2, 0.06, 0.6, 0.03])
slider = Slider(slider_ax, "Frame", 0, n_full_bins - 1, valinit = 0, valstep = 1)
 

def update_full_g(frame):
    frame = int(frame)
    calibration_selection["frame_idx"] = frame
    g_frame = calculate_full_g(frame)
    img_plot.set_data(g_frame)
    ax.set_title(f"Full image - frame {frame + 1}")
    fig.canvas.draw_idle()

slider.on_changed(update_full_g)

plt.show()


# %% Initialize calibration regions
calibration_rois = []

# %% Select calibration region (P1, P2 or P3)
# ============================================================
from matplotlib.patches import Rectangle

# Select point name
point_name = input("Point name (P1, P2, P3): ").strip()
# Read frame selected with the slider
frame_idx = calibration_selection["frame_idx"]
# Calculate full optical density for this frame
g_frame = calculate_full_g(frame_idx)
print(f"\nSelected frame: {frame_idx + 1}")
print("Image size (height, width):", g_frame.shape)

# Enter crop coordinates
x1 = int(input("Enter X1: "))
y1 = int(input("Enter Y1: "))
x2 = int(input("Enter X2: "))
y2 = int(input("Enter Y2: "))
# Validate coordinates
height, width = g_frame.shape

if not (0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height):
    raise ValueError("Invalid crop coordinates!")

# Extract selected region
g_roi = g_frame[y1:y2, x1:x2]
# Keep only valid g values
g_values = g_roi[np.isfinite(g_roi)]

if g_values.size == 0:
    raise ValueError("No valid g values in selected region!")

# Calculate statistics
g_mean = float(np.mean(g_values))
g_median = float(np.median(g_values))
g_std = float(np.std(g_values))

print("\n================================")
print(f"CALIBRATION REGION {point_name}")
print("================================")
print("Frame:", frame_idx + 1)
print("Coordinates:", (x1, y1, x2, y2))
print("Valid pixels:", g_values.size)
print(f"Mean g:   {g_mean:.6f}")
print(f"Median g: {g_median:.6f}")
print(f"Std g:    {g_std:.6f}")
print(f"Min g:    {np.min(g_values):.6f}")
print(f"Max g:    {np.max(g_values):.6f}")

# Save selected region information
roi_data = {
    "point": point_name,
    "frame_index": int(frame_idx),
    "frame_number": int(frame_idx + 1),
    "coordinates": [x1, y1, x2, y2],
    "g_mean": g_mean,
    "g_median": g_median,
    "g_std": g_std,
    "valid_pixels": int(g_values.size)}

# Replace previous selection if the same point is selected again
calibration_rois = [p for p in calibration_rois
    if p["point"] != point_name]
calibration_rois.append(roi_data)

# Save all selected regions to JSON
calibration_folder = base_folder / "Calibration"
calibration_folder.mkdir(parents=True, exist_ok=True)

with open(calibration_folder / "calibration_rois.json", "w") as file:
    json.dump(calibration_rois, file, indent=4)

# Preview selected region
fig, ax = plt.subplots(figsize=(8, 6))
ax.imshow(g_frame, cmap="viridis", vmin=vmin, vmax=vmax)

rectangle = Rectangle((x1, y1), x2 - x1, y2 - y1,
    fill=False, edgecolor="red", linewidth=2)

ax.add_patch(rectangle)
ax.set_title(f"{point_name} - Frame {frame_idx + 1}")
ax.set_xlabel("X (pixels)")
ax.set_ylabel("Y (pixels)")

plt.show()

print("\nSaved regions:", len(calibration_rois))
print("Saved to:", calibration_folder / "calibration_rois.json")

# %% Add concentration to calibration point
# ============================================================

json_path = base_folder / "Calibration" / "calibration_rois.json"

# Load previously saved calibration regions
with open(json_path, "r") as file:
    calibration_rois = json.load(file)

# Choose point
point_name = input("Point name (P1, P2, P3): ").strip().upper()

# Find selected point
point = next(
    (p for p in calibration_rois if p["point"] == point_name),
    None
)

if point is None:
    raise ValueError(f"{point_name} has not been selected yet!")

# Enter indium concentration
C = float(input("Indium concentration (wt.%): "))

if not np.isfinite(C) or not (0 <= C <= 100):
    raise ValueError("Concentration must be between 0 and 100 wt.%.")

# Record whether concentration is known or assumed
basis = input("Concentration basis (measured/assumed): ").strip().lower()

if basis not in ("measured", "assumed"):
    raise ValueError("Enter 'measured' or 'assumed'.")

# Add concentration to existing point
point["C_in_percent"] = C
point["concentration_basis"] = basis

# Save updated JSON
with open(json_path, "w") as file:
    json.dump(calibration_rois, file, indent=4)

print(f"\nCalibration point {point_name}:")
print(f"g = {point['g_median']:.6f}")
print(f"C_In = {C:.2f} wt.%")
print(f"Concentration basis: {basis}")
print("Saved to:", json_path)
# %% Save binned/downsampled images
# =============================================================================
# Create binnedImages folder if it does not exist
binned_folder = base_folder / "binnedImages"
binned_folder.mkdir(parents=True, exist_ok=True)
# Ask user for subfolder name
binned_folder_name = input("Enter name for binned image folder: ")
# Create user-defined folder inside binnedImages
binned_output_folder = binned_folder / binned_folder_name
binned_output_folder.mkdir(parents=True, exist_ok=True)

# =============================================================================
# Save binned images
for i, image in enumerate(I_corr_downsampled_safe):
    filename = (binned_output_folder / f"binnedImage_{i:05d}.tif")
    tifffile.imwrite(filename, image.astype(np.float32))

print("\n==============================")
print("Binned/downsampled export completed")
print("==============================")
print(f"Saved {len(I_corr_downsampled_safe)} images")
print("Location:", binned_output_folder)

# =============================================================================
# Save binning/downsampling parameters

binning_parameters = {
    "bin_size": bin_size,
    "discarded_frames": int(discarded),
    "downsample_factor": downsample_factor,
    "dt0": dt0,
    "dt_eff": dt_eff,
    "f_eff": f_eff,
    "dx0": dx0,
    "dx_eff": dx_eff,
    "original_binned_shape": list(I_corr_binned.shape),
    "final_downsampled_shape": list(I_corr_downsampled_safe.shape)}

binning_json_path = binned_output_folder / "binning_parameters.json"
with open(binning_json_path, "w") as file:
    json.dump(binning_parameters, file, indent=4)

print("Saved binning parameters:", binning_json_path)

# %% Save raw optical density g_raw
# =============================================================================
# Create gRaw folder if it does not exist
g_raw_folder = base_folder / "gRaw"
g_raw_folder.mkdir(parents=True, exist_ok=True)
# Ask user for subfolder name
g_raw_folder_name = input("Enter name for raw optical density folder: ")

# Create user-defined folder inside gRaw
g_raw_output_folder = g_raw_folder / g_raw_folder_name
g_raw_output_folder.mkdir(parents=True, exist_ok=True)

# =============================================================================
# Save g_raw images

for i, image in enumerate(g_raw):
    filename = (g_raw_output_folder / f"gRaw_{i:05d}.tif")

    tifffile.imwrite(filename, image.astype(np.float32))

print("\n==============================")
print("Raw optical density export completed")
print("==============================")

print(f"Saved {len(g_raw)} g_raw images")
print("Location:", g_raw_output_folder)

# =============================================================================
# Save g_raw parameters

g_raw_parameters = {
    "calculation": "g_raw = -ln(I_corr) = -ln(I/R_flat)",
    "radiometric_branch": "flat_only",
    "reference_role": "detector_flat_field_correction_recording",
    "measured_dark_subtracted": False,
    "separate_homogeneous_specimen_J0_admitted": False,
    "absolute_composition_calibration_admitted": False,
    "number_of_frames": int(g_raw.shape[0]),
    "image_shape": list(g_raw.shape[1:]),
    "data_type": "float32",
    "value_min": float(np.nanmin(g_raw)),
    "value_max": float(np.nanmax(g_raw)),
    "source_shape": list(I_corr.shape)
}

g_raw_json_path = (g_raw_output_folder / "g_raw_parameters.json")

with open(g_raw_json_path, "w") as file:
    json.dump(g_raw_parameters, file, indent=4)

print("Saved g_raw parameters:", g_raw_json_path)

# %% Save preprocess downsampled optical density g
# =============================================================================

# Create g preprocess folder if it does not exist
g_preprocess_folder = base_folder / "g_preprocess"
g_preprocess_folder.mkdir(parents=True, exist_ok=True)
# Ask user for subfolder name
g_preprocess_folder_name = input("Enter name for optical density g folder: ")
# Create user-defined folder inside g
g_preprocess_output_folder = g_preprocess_folder / g_preprocess_folder_name
g_preprocess_output_folder.mkdir(parents=True, exist_ok=True)

# =============================================================================
# Save g preprocess images
for i, image in enumerate(g_downsampled):
    filename = (g_preprocess_output_folder / f"g_{i:05d}.tif")
    tifffile.imwrite(filename, image.astype(np.float32))

print("\n==============================")
print("Optical density g export completed")
print("==============================")
print(f"Saved {len(g_downsampled)} g images")

print("Location:", g_preprocess_output_folder)

# =============================================================================
# Save g parameters
g_preprocess_parameters = {
    "calculation": "g = -ln(I_corr_downsampled_safe)",
    "radiometric_branch": "flat_only",
    "reference_role": "detector_flat_field_correction_recording",
    "measured_dark_subtracted": False,
    "separate_homogeneous_specimen_J0_admitted": False,
    "absolute_composition_calibration_admitted": False,
    "number_of_frames": int(g_downsampled.shape[0]),
    "image_shape": list(g_downsampled.shape[1:]),
    "data_type": "float32",
    "value_min": float(np.nanmin(g_downsampled)),
    "value_max": float(np.nanmax(g_downsampled)),
    "source_shape": list(I_corr_downsampled_safe.shape),
    "downsample_factor": downsample_factor,
    "dx_eff_um_per_pixel": dx_eff}

g_preprocess_json_path = (g_preprocess_output_folder / "g_parameters.json")

with open(g_preprocess_json_path, "w") as file:
    json.dump(g_preprocess_parameters, file, indent = 4)

print("Saved g parameters:", g_preprocess_json_path)



# %% Check calibration points P1, P2, P3
# ============================================================

json_path = base_folder / "Calibration" / "calibration_rois.json"

# Load saved calibration points
with open(json_path, "r") as file:
    calibration_rois = json.load(file)

print("\n================================")
print("CALIBRATION POINTS")
print("================================")

for name in ["P1", "P2", "P3"]:

    point = next(
        (p for p in calibration_rois if p["point"] == name),
        None
    )

    if point is None:
        raise ValueError(f"{name} is missing!")

    if "C_in_percent" not in point:
        raise ValueError(f"{name} has no concentration value!")

    print(f"\n{name}:")
    print(f"g = {point['g_median']:.6f}")
    print(f"C_In = {point['C_in_percent']:.2f} wt.%")
    print(f"Basis = {point['concentration_basis']}")
    print(f"Frame = {point['frame_number']}")
    print(f"Coordinates = {point['coordinates']}")

print("\nAll three calibration points are available.")
# %% Calibration from saved P1, P2, P3
# =============================================================================

# Load calibration points from JSON
json_path = base_folder / "Calibration" / "calibration_rois.json"

with open(json_path, "r") as file:
    calibration_rois = json.load(file)

# Read the three calibration points
g_points = []
C_points = []

for name in ["P1", "P2", "P3"]:

    point = next(
        (p for p in calibration_rois if p["point"] == name),
        None
    )

    if point is None:
        raise ValueError(f"Calibration point {name} is missing!")

    if "C_in_percent" not in point:
        raise ValueError(f"Concentration is missing for {name}!")

    g_points.append(point["g_median"])
    C_points.append(point["C_in_percent"])

    print(
        f"{name}: g = {point['g_median']:.6f}, "
        f"C_In = {point['C_in_percent']:.2f} wt.%, "
        f"basis = {point['concentration_basis']}"
    )

# Convert to NumPy arrays
g_points = np.array(g_points, dtype=np.float64)
C_points = np.array(C_points, dtype=np.float64)

# Validate calibration values
if not np.all(np.isfinite(g_points)) or not np.all(np.isfinite(C_points)):
    raise ValueError("Calibration points must contain finite values!")

if np.unique(g_points).size < 2:
    raise ValueError("At least two different g values are required!")

# Calculate calibration coefficients
a, b = np.polyfit(g_points, C_points, 1)

print("\n================================")
print("CALIBRATION RESULTS")
print("================================")
print(f"Slope a: {a:.6f}")
print(f"Intercept b: {b:.6f}")
print(f"C_In (wt.%) = {a:.6f} * g + {b:.6f}")

# Compare input concentrations with fitted values
C_fitted = a * g_points + b

for i in range(3):
    print(
        f"P{i+1}: C_input = {C_points[i]:.3f}%, "
        f"C_fitted = {C_fitted[i]:.3f}%"
    )

# Apply calibration to g_downsampled
C_in_percent = a * g_downsampled + b

print("\nConcentration statistics:")
print("Min:", np.nanmin(C_in_percent))
print("Max:", np.nanmax(C_in_percent))
print("Mean:", np.nanmean(C_in_percent))
print("Median:", np.nanmedian(C_in_percent))
# =============================================================================
# Save concentration field

conc_folder = base_folder / "Conc_In"
conc_folder.mkdir(parents=True, exist_ok=True)

# Ask user for subfolder name
conc_folder_name = input("Enter name for concentration folder: ")

# Create user-defined folder
conc_output_folder = conc_folder / conc_folder_name
conc_output_folder.mkdir(parents=True, exist_ok=True)

# Save concentration images
for i, conc in enumerate(C_in_percent):
    filename = conc_output_folder / f"Conc_In_{i:05d}.tif"
    tifffile.imwrite(filename, conc.astype(np.float32))

print("\n==============================")
print("Indium concentration export completed")
print("==============================")
print(f"Saved {len(C_in_percent)} concentration images")
print("Location:", conc_output_folder)


# %% Filter optical density g
# =============================================================================
from scipy.ndimage import median_filter
from skimage.restoration import denoise_tv_chambolle
import numpy as np
import matplotlib.pyplot as plt
import tifffile
import json
# Parameters
median_filter_size = 3
tv_weight = 0.01

# 1. Median filter directly on g
g_median = np.stack([
    median_filter(frame, size=median_filter_size)
    for frame in g_downsampled
])

# 2. Total Variation denoising directly on g
g_filtered = np.stack([
    denoise_tv_chambolle(frame, weight=tv_weight)
    for frame in g_median
])

# Diagnostics
print("g raw range:", np.nanmin(g_downsampled),
      np.nanmax(g_downsampled))
print("g filtered range:", np.nanmin(g_filtered),
      np.nanmax(g_filtered))
print("Negative g fraction before filtering:",
      np.mean(g_downsampled < 0) * 100, "%")
print("Negative g fraction after filtering:",
      np.mean(g_filtered < 0) * 100, "%")

# Compare one frame


frame_idx = 25

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

vmin = np.nanpercentile(g_downsampled[frame_idx], 1)
vmax = np.nanpercentile(g_downsampled[frame_idx], 99)

axes[0].imshow(g_downsampled[frame_idx],
               cmap="gray", vmin=vmin, vmax=vmax)
axes[0].set_title("Raw g")
axes[1].imshow(g_median[frame_idx],               cmap="gray", vmin=vmin, vmax=vmax)
axes[1].set_title("Median-filtered g")
axes[2].imshow(g_filtered[frame_idx],               cmap="gray", vmin=vmin, vmax=vmax)
axes[2].set_title("Median + TV filtered g")


for ax in axes:
    ax.axis("off")

plt.tight_layout()
plt.show()

# %% Calibration
# =============================================================================
# Apply calibration AFTER filtering g
C_in_percent_filtered = a * g_filtered + b

print("Concentration min:", np.nanmin(C_in_percent_filtered))
print("Concentration max:", np.nanmax(C_in_percent_filtered))
print("Concentration mean:", np.nanmean(C_in_percent_filtered))
print("Concentration median:", np.nanmedian(C_in_percent_filtered))

outside_range = (
    (C_in_percent_filtered < 0) |
    (C_in_percent_filtered > 100) |
    ~np.isfinite(C_in_percent_filtered)
)

print("Concentration values outside 0–100%:",
      np.mean(outside_range) * 100, "%")


# %% Save concentration field
# =============================================================================
conc_filtered_folder = base_folder / "Conc_In"
conc_filtered_folder.mkdir(parents=True, exist_ok=True)

conc_filtered_folder_name = input("Enter name for filtered concentration folder: ")
conc_filtered_output_folder = conc_filtered_folder / conc_filtered_folder_name
conc_filtered_output_folder.mkdir(parents=True, exist_ok=True)

for i, conc in enumerate(C_in_percent_filtered):
    filename = conc_filtered_output_folder / f"Conc_In_{i:05d}.tif"
    tifffile.imwrite(filename, conc.astype(np.float32))

# Save processing parameters
parameters = {
    "calibration": f"C_In = {a:.8f} * g + {b:.8f}",
    "slope_a": float(a),
    "intercept_b": float(b),
    "source": "g_filtered",
    "filtering_domain": "optical_density_g",
    "median_filter_size": median_filter_size,
    "tv_weight": tv_weight,
    "sharpening": False,
    "concentration_clipped": False,
    "number_of_frames": int(C_in_percent_filtered.shape[0]),
    "image_shape": list(C_in_percent_filtered.shape[1:]),
    "concentration_min": float(np.nanmin(C_in_percent_filtered)),
    "concentration_max": float(np.nanmax(C_in_percent_filtered)),
    "calibration_status": "provisional_assumed_points",
    "radiometric_branch": "flat_only",
    "measured_dark_subtracted": False,
    "separate_homogeneous_specimen_J0_admitted": False,
    "absolute_composition_calibration_admitted": False
}


with open(conc_filtered_output_folder / "concentration_parameters.json", "w") as f:
    json.dump(parameters, f, indent=4)

print("Filtered concentration export completed.")
print("Saved frames:", len(C_in_percent_filtered))
print("Location:", conc_filtered_output_folder)
    

    

    
    
    
    

# %% 2D Denoising & Contrast Boosting
# =============================================================================
from scipy.ndimage import median_filter
from skimage.restoration import denoise_tv_chambolle

r = 1 # median filter radius = 1, size ir 3 by 3 window.
size = 2*r + 1
# Median filter - noņem punktveida troksni
images_median = np.stack([median_filter(frame, size = size)
    for frame in I_corr_downsampled_safe])

# Total variation filter - izlīdzina, saglabājot robežas
# (Mathematica Method->"Poisson" - tuvinājums, ne precīza atbilstība)
tv_weight = 0.05
# tv_weight = 0.95

images_tv = np.stack([
    denoise_tv_chambolle(frame, weight=tv_weight)
    for frame in images_median])

testImagesFiltered = images_tv
# =============================================================================
plt.figure(figsize=(20,5))
plt.subplot(1,4,1)
plt.imshow(I_corr_downsampled_safe[25], cmap="gray")
plt.title("Original")
plt.axis("off")

plt.subplot(1,4,2)
plt.imshow(images_median[25], cmap="gray")
plt.title("After median")
plt.axis("off")

plt.subplot(1,4,3)
plt.imshow(images_tv[25], cmap="gray")
plt.title("After median + TV")
plt.axis("off")

plt.subplot(1,4,4)
plt.imshow(testImagesFiltered[25], cmap="gray")
plt.title("After median + TV + sharpen")
plt.axis("off")
plt.show()



# %% Tone mapping (ColorToneMapping tuvinājums)
# =============================================================================
def color_tone_mapping_approx(image, target_luminance=0.5):
    img_norm = (image - image.min()) / (image.max() - image.min() + 1e-12)
    current_mean = img_norm.mean()
    if current_mean > 1e-12:
        scaled = img_norm * (target_luminance / current_mean)
    else:
        scaled = img_norm
    return np.clip(scaled, 0, 1)

testImagesContrastBoosted = np.stack([
    color_tone_mapping_approx(frame, target_luminance=0.5)
    for frame in testImagesFiltered])

print("testImagesContrastBoosted shape:", testImagesContrastBoosted.shape)
# %% Squared enhancement (ImageAdjust@#^2)
# =============================================================================
def image_adjust(img):
    img_min, img_max = img.min(), img.max()
    if img_max - img_min < 1e-12:
        return np.zeros_like(img)
    return (img - img_min) / (img_max - img_min)

testImagesEnhanced = np.stack([
    image_adjust(frame) ** 2
    for frame in testImagesContrastBoosted])

print("testImagesEnhanced shape:", testImagesEnhanced.shape)
print("Value range:", testImagesEnhanced.min(), testImagesEnhanced.max())
# =============================================================================
fig, axes = plt.subplots(1, 3, figsize=(15,5))
axes[0].imshow(testImagesFiltered[0], cmap="gray")
axes[0].set_title("testImagesFiltered")
axes[0].axis("off")

axes[1].imshow(testImagesContrastBoosted[0], cmap="gray")
axes[1].set_title("testImagesContrastBoosted")
axes[1].axis("off")

axes[2].imshow(testImagesEnhanced[0], cmap="gray")
axes[2].set_title("testImagesEnhanced")
axes[2].axis("off")
plt.show()

# %% 3D Denoising (spatiotemporal TV filter)
# =============================================================================
from skimage.restoration import denoise_tv_chambolle

# Image3D(testImagesEnhanced) - laiku uzskata par trešo telpisko asi (t, y, x)
imageStack = testImagesEnhanced  # shape (n_frames, H, W)

# TotalVariationFilter[..., 0.05, Method->"Gaussian"] tuvinājums.
# denoise_tv_chambolle strādā uz N-dimensiju masīviem - filtrējot arī
# pa laika asi (axis=0), tas ir spatiotemporal (nevis tikai 2D) filtrs,
# tāpat kā Mathematica Image3D pieeja.
tv_weight_3d = 0.05
imageStackFiltered = denoise_tv_chambolle(imageStack, weight=tv_weight_3d)
imagesFiltered3D = imageStackFiltered  # shape paliek (n_frames, H, W)

print("imagesFiltered3D shape:", imagesFiltered3D.shape)
print("Value range:", imagesFiltered3D.min(), imagesFiltered3D.max())

# =============================================================================
# Preview - salīdzini 2D-filtrēto un 3D-filtrēto to pašu kadru

plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
plt.imshow(testImagesEnhanced[0], cmap="gray")
plt.title("Pirms 3D TV (testImagesEnhanced)")
plt.axis("off")

plt.subplot(1,2,2)
plt.imshow(imagesFiltered3D[0], cmap="gray")
plt.title("Pēc 3D TV filtra")
plt.axis("off")
plt.show()

# =============================================================================
# Preview - laika asī (redzēt, vai 3D filtrs izlīdzina arī laikā)

fig, axes = plt.subplots(1, 4, figsize=(20,5))
for ax, idx in zip(axes, [0, 1, 2, 3]):
    ax.imshow(imagesFiltered3D[idx], cmap="gray")
    ax.set_title(f"Frame {idx}")
    ax.axis("off")
plt.suptitle("3D TV filtra rezultāts pa secīgiem kadriem")
plt.show()
# %% Save 3D filtered images (imagesFiltered3D)
# =============================================================================
# NOTE: imagesFiltered3D is built from testImagesEnhanced (contrast-boosted +
# squared, linear/display domain, NOT optical density g), then spatiotemporally
# TV-filtered. Saved separately from gFiltered, which stays in the g-domain.
 
# Create filtered3DImages folder if it does not exist
 
filtered3D_folder = base_folder / "filtered3DImages"
filtered3D_folder.mkdir(parents=True, exist_ok=True)
 
# Ask user for subfolder name
filtered3D_folder_name = input("Enter name for 3D filtered image folder: ")
# Create user-defined subfolder
filtered3D_output_folder = (filtered3D_folder / filtered3D_folder_name)
filtered3D_output_folder.mkdir(parents=True, exist_ok=True)
 
# =============================================================================
# Save 3D filtered images
 
for i, image in enumerate(imagesFiltered3D):
    filename = (filtered3D_output_folder / f"filtered3D_{i:05d}.tif")
    tifffile.imwrite(filename, image.astype(np.float32))
 
print("\n========================================")
print("3D filtered image export completed")
print("========================================")
print(f"Saved {len(imagesFiltered3D)} 3D filtered images")
print("Location:", filtered3D_output_folder)
 
# =============================================================================
# Save 3D filtered parameters

filtered3D_parameters = {
    "calculation": (
        "imagesFiltered3D = denoise_tv_chambolle("
        "testImagesEnhanced, weight=tv_weight_3d, "
        "filtering also across the frame axis)"),
    "number_of_frames": int(imagesFiltered3D.shape[0]),
    "image_shape": list(imagesFiltered3D.shape[1:]),
    "data_type": "float32",
    "value_min": float(imagesFiltered3D.min()),
    "value_max": float(imagesFiltered3D.max()),
    "source_shape": list(testImagesEnhanced.shape),
    "tv_weight_3d": tv_weight_3d,
    "downsample_factor": downsample_factor,
    "dx_eff_um_per_pixel": dx_eff}
 
filtered3D_json_path = (filtered3D_output_folder / "filtered3D_parameters.json")
 
with open(filtered3D_json_path, "w") as file:
    json.dump(filtered3D_parameters, file, indent = 4)
 
print("Saved 3D filtered parameters:", filtered3D_json_path)
