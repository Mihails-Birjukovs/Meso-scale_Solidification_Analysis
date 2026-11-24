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
# I_corr = I / I0  (bez dark-current korekcijas, jo tev tādu datu nav —
# tas ir zināms un pieņemts tuvinājums, ir minēts darba metodoloģijā)

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
plt.title("I / I0")
plt.axis("off")
plt.show()

# %% Check data type of I_corrr, is it float (not uint)
print("I_corr dtype:", I_corr.dtype)

# %% Optical density
# =============================================================================
g_raw = -np.log(I_corr)   # naturāllogaritms
print("g_raw value range:", np.nanmin(g_raw), np.nanmax(g_raw))

plt.figure(figsize=(6,5))
plt.imshow(g_raw[0], cmap="viridis")
plt.colorbar(label="g")
plt.title("Raw optical density, first cropped frame")
plt.axis("off")
plt.show()


# %% Diagnostika - kur atrodas negatīvās g vērtības
# =============================================================================

# Select frame (Python indexing starts from 0)
frame_idx = 10

# Check that the selected frame exists
if not (0 <= frame_idx < len(g_raw)):
    raise ValueError(
        f"Invalid frame index: {frame_idx}. "
        f"Available indices: 0 to {len(g_raw) - 1}"
    )

# Calculate the fraction of negative g values
negative_mask = g_raw < 0
print("Negative pixel part:", negative_mask.mean())

# Plot selected frame
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.imshow(g_raw[frame_idx], cmap="RdBu_r", vmin=-0.1, vmax=0.1)
plt.colorbar(label="g")
plt.title(f"g (red = positive, blue = negative), frame {frame_idx + 1}")
plt.axis("off")

# Histogram of the selected frame
plt.subplot(1, 2, 2)
plt.hist(g_raw[frame_idx].ravel(), bins=100)
plt.axvline(0, color="r", linestyle="--")
plt.xlabel("g")
plt.title(f"g raw histogram, frame {frame_idx + 1}")

plt.tight_layout()
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

print(
    "g_downsampled value range:",
    np.nanmin(g_downsampled),
    np.nanmax(g_downsampled)
)

# =============================================================================
# Find global minimum and maximum of g_downsampled
# =============================================================================

g_min = np.nanmin(g_downsampled)
g_max = np.nanmax(g_downsampled)

# Find their positions (frame, y, x)
min_pos = np.unravel_index(
    np.nanargmin(g_downsampled),
    g_downsampled.shape
)

max_pos = np.unravel_index(
    np.nanargmax(g_downsampled),
    g_downsampled.shape
)

print(f"Global g minimum: {g_min:.6f}")
print(f"Global g maximum: {g_max:.6f}")

print("Minimum position (frame, y, x):", min_pos)
print("Maximum position (frame, y, x):", max_pos)

# =============================================================================
# Select frame for visualization
# =============================================================================

# Python indexing starts at 0
frame_idx = 10

# Check that the selected frame exists
if not (0 <= frame_idx < len(g_downsampled)):
    raise ValueError(
        f"Invalid frame index: {frame_idx}. "
        f"Available indices: 0 to {len(g_downsampled) - 1}"
    )

# =============================================================================
# Plot selected frame
# =============================================================================

plt.figure(figsize=(6, 5))

plt.imshow(
    g_downsampled[frame_idx],
    cmap="viridis"
)

plt.colorbar(label="g")

plt.title(
    f"Downsampled optical density, frame {frame_idx + 1}"
)

plt.axis("off")
plt.tight_layout()
plt.show()

# =============================================================================
# Check invalid values
# =============================================================================

print(
    "g contains NaN/Inf:",
    np.any(~np.isfinite(g_downsampled))
)

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
plt.title(f"g downsampled histogram, frame {frame_idx + 1}")
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


# %% Manual sampling: N windows for three calibration regions
# ============================================================
# 1. User selects N for each region.
# 2. Before every window, user selects a g frame with a slider.
# 3. User enters window coordinates.
# 4. Code calculates window statistics.
# 5. Code calculates g_bar, s_g and u_g for each region.
# 6. Results are saved to CSV and JSON.
#
# IMPORTANT:
# All calculations use quantitative g from calculate_full_g().
# This section does NOT calculate concentration or calibration
# coefficients alpha and beta.

import csv
from datetime import datetime
from matplotlib.widgets import Slider, Button
from matplotlib.patches import Rectangle

# ------------------------------------------------------------
# Three calibration regions
# ------------------------------------------------------------

sampling_regions = [
    ("liquid", "Initial liquid (nominal 25 wt.% In)"),
    ("plume", "Ga-rich plume"),
    ("dendrite", "In-rich dendrite"),
]

# ------------------------------------------------------------
# Ask the user for a separate N for every region
# ------------------------------------------------------------

N_by_region = {}

for region_key, region_label in sampling_regions:

    while True:

        try:
            N = int(input(
                f"Number of windows for {region_label} "
                "(0 = skip, >=2 = sample): "
            ))

        except ValueError:
            print("Enter an integer.")
            continue

        if N == 0 or N >= 2:
            N_by_region[region_key] = N
            break

        print("Choose 0 or an integer >= 2.")


# ------------------------------------------------------------
# Create output folder for this sampling session
# ------------------------------------------------------------

run_stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

sampling_output = (
    base_folder
    / "Calibration"
    / "sampling_N_full"
    / run_stamp
)

sampling_output.mkdir(parents=True, exist_ok=False)

sampling_records = []



# %% Function: choose the g frame
# ============================================================

def select_g_frame(region_label, window_number, N):

    selected = {"frame": None}

    viewer_fig, viewer_ax = plt.subplots(figsize=(11, 7))

    # Reserve space on the RIGHT for the button.
    # Reserve space at the BOTTOM for the frame slider.
    viewer_fig.subplots_adjust(
        left=0.08,
        right=0.76,
        bottom=0.20,
        top=0.92
    )

    first_frame = calculate_full_g(0)

    image_artist = viewer_ax.imshow(
        first_frame,
        cmap="viridis",
        vmin=vmin,
        vmax=vmax
    )

    viewer_fig.colorbar(
        image_artist,
        ax=viewer_ax,
        label="Optical density g"
    )

    viewer_ax.set_xlabel("x (downsampled pixels)")
    viewer_ax.set_ylabel("y (downsampled pixels)")

    viewer_ax.set_title(
        f"{region_label} | Window {window_number}/{N} | Frame 1"
    )

    # --------------------------------------------------------
    # Frame slider at the bottom
    # --------------------------------------------------------

    slider_axis = viewer_fig.add_axes(
        [0.16, 0.07, 0.57, 0.035]
    )

    frame_slider = Slider(
        slider_axis,
        "Frame",
        1,
        n_full_bins,
        valinit=1,
        valstep=1
    )

    # --------------------------------------------------------
    # Confirmation button on the RIGHT side
    # --------------------------------------------------------

    button_axis = viewer_fig.add_axes(
        [0.80, 0.46, 0.18, 0.09]
    )

    choose_button = Button(
        button_axis,
        "Use this frame"
    )

    # --------------------------------------------------------
    # Update image when slider changes
    # --------------------------------------------------------

    def on_frame_change(frame_number):

        index = int(frame_number) - 1

        image_artist.set_data(
            calculate_full_g(index)
        )

        viewer_ax.set_title(
            f"{region_label} | "
            f"Window {window_number}/{N} | "
            f"Frame {index + 1}"
        )

        viewer_fig.canvas.draw_idle()

    # --------------------------------------------------------
    # Confirm frame and close ONLY this viewer
    # --------------------------------------------------------

    def on_frame_confirm(_event):

        selected["frame"] = int(frame_slider.val) - 1

        print(
            f"\nSelected frame: {selected['frame'] + 1}"
        )

        print(
            "Frame confirmed. "
            "Enter coordinates in the Spyder console."
        )

        plt.close(viewer_fig)

    frame_slider.on_changed(on_frame_change)
    choose_button.on_clicked(on_frame_confirm)

    # --------------------------------------------------------
    # Show viewer without blocking on OTHER figures
    # --------------------------------------------------------

    print(
        "\nChoose a frame using the slider, "
        "then click 'Use this frame'."
    )

    plt.show(block=False)

    # Wait ONLY for this frame selection.
    # Other previously opened figures do not block progress.
    while (
        selected["frame"] is None
        and plt.fignum_exists(viewer_fig.number)
    ):
        plt.pause(0.05)

    return selected["frame"]


# %% Function: calculate statistics between windows
# ============================================================

def summarize_g_windows(records):

    results = []

    for region_key, region_label in sampling_regions:

        # One mean g value for each accepted window
        window_means = np.asarray([
            rec["g_mean_window"]
            for rec in records
            if rec["region"] == region_key
        ], dtype=float)

        N = len(window_means)

        if N >= 1:
            g_bar = float(np.mean(window_means))
        else:
            g_bar = None

        # Sample standard deviation between window means
        if N >= 2:
            s_g = float(np.std(window_means, ddof=1))
            u_g = float(s_g / np.sqrt(N))
        else:
            s_g = None
            u_g = None

        results.append({
            "region": region_key,
            "region_label": region_label,
            "N_windows": N,
            "g_bar": g_bar,
            "s_g_between_windows": s_g,
            "u_g_naive_sem": u_g,
        })

    return results


# %% Function: save individual windows and summary
# ============================================================

def save_sampling_progress():

    windows_path = sampling_output / "sampling_windows.csv"
    summary_path = sampling_output / "sampling_summary.csv"
    summary_json_path = sampling_output / "sampling_summary.json"

    # Save individual windows
    if sampling_records:

        with windows_path.open(
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=list(sampling_records[0])
            )

            writer.writeheader()
            writer.writerows(sampling_records)

    # Calculate group statistics
    summary = summarize_g_windows(sampling_records)

    # Save summary CSV
    with summary_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=list(summary[0])
        )

        writer.writeheader()
        writer.writerows(summary)

    # Save summary JSON
    with summary_json_path.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            summary,
            file,
            indent=2,
            ensure_ascii=False
        )

    return summary



# %% Main sampling procedure
# ============================================================
# For every region:
# 1. Select a frame using the slider.
# 2. Keep the selected g frame OPEN.
# 3. Enter window coordinates while looking at the image.
# 4. Display the selected rectangle on the SAME image.
# 5. Accept, change coordinates or change frame.
# 6. Calculate and save statistics.
# ============================================================

for region_key, region_label in sampling_regions:

    required_N = N_by_region[region_key]

    print("\n======================================")
    print("REGION:", region_label)
    print("NUMBER OF WINDOWS:", required_N)
    print("======================================")

    # --------------------------------------------------------
    # Repeat the selection N times
    # --------------------------------------------------------

    for window_number in range(1, required_N + 1):

        # Repeat until this window has been accepted
        while True:

            print(
                f"\nSelecting window "
                f"{window_number}/{required_N}"
            )

            # ------------------------------------------------
            # 1. Choose frame using the slider
            # ------------------------------------------------

            frame_index = select_g_frame(
                region_label,
                window_number,
                required_N
            )

            if frame_index is None:
                print("No frame confirmed. Try again.")
                continue

            # ------------------------------------------------
            # 2. Obtain the quantitative g image
            # ------------------------------------------------

            g_frame = calculate_full_g(frame_index)

            height, width = g_frame.shape

            print(f"\nSelected frame: {frame_index + 1}")
            print(f"Image width: {width} pixels")
            print(f"Image height: {height} pixels")

            # ------------------------------------------------
            # 3. Open the selected frame and KEEP IT OPEN
            # ------------------------------------------------

            selected_fig, selected_ax = plt.subplots(
                figsize=(11, 8)
            )

            selected_fig.subplots_adjust(
                left=0.09,
                right=0.86,
                bottom=0.12,
                top=0.91
            )

            image_artist = selected_ax.imshow(
                g_frame,
                cmap="viridis",
                vmin=vmin,
                vmax=vmax,
                interpolation="nearest"
            )

            selected_fig.colorbar(
                image_artist,
                ax=selected_ax,
                label="Optical density g"
            )

            selected_ax.set_xlabel(
                "X coordinate (downsampled pixels)"
            )

            selected_ax.set_ylabel(
                "Y coordinate (downsampled pixels)"
            )

                
            selected_ax.set_title(
                f"{region_label}\n"
                f"Frame {frame_index + 1} | "
                f"Window {window_number}/{required_N}"
            )
            
            # ============================================================
            # Display mouse cursor coordinates and optical density g
            # ============================================================
            
            # Text at the bottom of the figure
            cursor_text = selected_fig.text(
                0.10,
                0.045,
                "Move the mouse over the image to see X, Y and g",
                fontsize=11,
                fontweight="bold"
            )
            
            # Show coordinates in the Matplotlib toolbar as well
            selected_ax.format_coord = (
                lambda x, y: f"X = {x:.2f}, Y = {y:.2f}"
            )
            
            # Update cursor coordinates when the mouse moves
            def on_mouse_move(event):
            
                if event.inaxes != selected_ax:
                    return
            
                if event.xdata is None or event.ydata is None:
                    return
            
                # Actual mouse position
                x = event.xdata
                y = event.ydata
            
                # Nearest pixel indices
                px = int(np.floor(x + 0.5))
                py = int(np.floor(y + 0.5))
            
                # Check image boundaries
                if 0 <= px < width and 0 <= py < height:
            
                    g_value = g_frame[py, px]
            
                    cursor_text.set_text(
                        f"X = {x:.2f}    "
                        f"Y = {y:.2f}    "
                        f"Pixel = ({px}, {py})    "
                        f"g = {g_value:.6f}"
                    )
            
                selected_fig.canvas.draw_idle()
            
            # Connect mouse movement to the figure
            mouse_connection = selected_fig.canvas.mpl_connect(
                "motion_notify_event",
                on_mouse_move
            )
            
            # Show image without blocking the console
            plt.show(block=False)
            plt.pause(0.2)


            print("\n======================================")
            print("SELECT WINDOW COORDINATES")
            print("======================================")
            print("The selected g frame remains OPEN.")
            print("Look at the figure while entering coordinates.")
            print("Use x1 y1 x2 y2.")
            print("Coordinates refer to downsampled pixels.")
            print("======================================")

            accepted = False

            # Rectangle displayed on the image
            current_rectangle = None

            try:

                # --------------------------------------------
                # 4. Coordinate selection loop
                # --------------------------------------------

                while True:

                    print(
                        f"\nFrame {frame_index + 1}, "
                        f"window {window_number}/{required_N}"
                    )

                    raw = input(
                        "Enter x1 y1 x2 y2 "
                        "(example: 10 15 15 20): "
                    ).replace(",", " ")

                    # Check four coordinate values
                    try:

                        values = [
                            int(value)
                            for value in raw.split()
                        ]

                        if len(values) != 4:
                            raise ValueError

                        x1, y1, x2, y2 = values

                    except ValueError:

                        print(
                            "ERROR: Enter exactly four "
                            "integer coordinates."
                        )

                        continue

                    # ----------------------------------------
                    # 5. Check coordinate boundaries
                    # ----------------------------------------

                    valid_coordinates = (
                        0 <= x1 < x2 <= width
                        and 0 <= y1 < y2 <= height
                    )

                    if not valid_coordinates:

                        print("Invalid coordinates!")

                        print(
                            f"Allowed X range: 0 to {width}"
                        )

                        print(
                            f"Allowed Y range: 0 to {height}"
                        )

                        continue

                    # ----------------------------------------
                    # 6. Check whether exact window exists
                    # ----------------------------------------

                    duplicate = any(

                        rec["region"] == region_key

                        and rec["frame_index_0based"]
                        == frame_index

                        and (
                            rec["x1"],
                            rec["y1"],
                            rec["x2"],
                            rec["y2"]
                        ) == (x1, y1, x2, y2)

                        for rec in sampling_records
                    )

                    if duplicate:

                        print(
                            "This exact window has "
                            "already been selected."
                        )

                        continue

                    # ----------------------------------------
                    # 7. Extract g values from the window
                    # ----------------------------------------

                    g_window = g_frame[y1:y2, x1:x2]

                    g_values = g_window[
                        np.isfinite(g_window)
                    ]

                    if g_values.size < 2:

                        print(
                            "Not enough valid g pixels. "
                            "Choose another window."
                        )

                        continue

                    # ----------------------------------------
                    # 8. Calculate window statistics
                    # ----------------------------------------

                    g_mean_window = float(
                        np.mean(g_values)
                    )

                    g_median_window = float(
                        np.median(g_values)
                    )

                    g_std_pixels = float(
                        np.std(g_values, ddof=1)
                    )

                    print("\nWINDOW STATISTICS")
                    print("------------------------------")

                    print(
                        f"Mean g:   {g_mean_window:.8f}"
                    )

                    print(
                        f"Median g: {g_median_window:.8f}"
                    )

                    print(
                        f"Std g:    {g_std_pixels:.8f}"
                    )

                    print(
                        f"Valid pixels: {g_values.size}"
                    )

                    # ----------------------------------------
                    # 9. Draw rectangle on the SAME image
                    # ----------------------------------------

                    # Remove previous rectangle if coordinates
                    # were changed.
                    if current_rectangle is not None:
                        current_rectangle.remove()

                    current_rectangle = Rectangle(
                        (x1 - 0.5, y1 - 0.5),
                        x2 - x1,
                        y2 - y1,
                        fill=False,
                        edgecolor="red",
                        linewidth=2.5
                    )

                    selected_ax.add_patch(
                        current_rectangle
                    )

                    selected_ax.set_title(
                        f"{region_label}\n"
                        f"Frame {frame_index + 1} | "
                        f"Window {window_number}/{required_N}\n"
                        f"ROI: ({x1}, {y1}) to ({x2}, {y2})"
                    )

                    selected_fig.canvas.draw_idle()
                    plt.pause(0.15)

                    print(
                        "\nThe selected window is shown "
                        "as a RED rectangle."
                    )

                    # ----------------------------------------
                    # 10. Accept or modify selection
                    # ----------------------------------------

                    answer = input(
                        "\n[y] Save window, "
                        "[n] Change coordinates, "
                        "[f] Choose another frame: "
                    ).strip().lower()

                    if answer in ("y", "yes", "j", "ja"):

                        # ------------------------------------
                        # 11. Save accepted window
                        # ------------------------------------

                        sampling_records.append({

                            "region": region_key,

                            "window_number": window_number,

                            "frame_index_0based": frame_index,

                            "frame_number_1based": (
                                frame_index + 1
                            ),

                            "x1": x1,
                            "y1": y1,
                            "x2": x2,
                            "y2": y2,

                            "N_valid_pixels": int(
                                g_values.size
                            ),

                            "g_mean_window": g_mean_window,

                            "g_median_window": g_median_window,

                            "g_std_pixels": g_std_pixels,
                        })

                        save_sampling_progress()

                        print(
                            f"\nSaved window "
                            f"{window_number}/{required_N}"
                        )

                        accepted = True

                        break

                    elif answer in ("f", "frame"):

                        print(
                            "Changing frame..."
                        )

                        break

                    else:

                        print(
                            "Window not saved. "
                            "Enter new coordinates."
                        )

                        # Keep the SAME frame visible.
                        # Next iteration will replace the
                        # previous rectangle.
                        continue

            finally:

                # Close only the confirmed-frame preview
                # after saving or choosing another frame.
                plt.close(selected_fig)

            # --------------------------------------------
            # If saved, go to the next sampling window
            # --------------------------------------------

            if accepted:
                break

            # Otherwise select a new frame
            # for the SAME sampling window.

    # --------------------------------------------------------
    # 12. Calculate statistics for this region
    # --------------------------------------------------------

    region_summary = next(

        row

        for row in summarize_g_windows(
            sampling_records
        )

        if row["region"] == region_key
    )

    if required_N > 0:

        print("\n======================================")
        print("FINAL RESULTS:", region_label)
        print("======================================")

        print(
            f"N = {region_summary['N_windows']}"
        )

        print(
            f"g_bar = {region_summary['g_bar']:.8f}"
        )

        print(
            f"s_g = "
            f"{region_summary['s_g_between_windows']:.8f}"
        )

        print(
            f"u_g = "
            f"{region_summary['u_g_naive_sem']:.8f}"
        )

# %% Final summary
# ============================================================

sampling_summary = save_sampling_progress()

print("\n======================================")
print("SAMPLING COMPLETED")
print("======================================")

for row in sampling_summary:

    print("\nRegion:", row["region_label"])
    print("N:", row["N_windows"])
    print("Mean g:", row["g_bar"])
    print("Standard deviation:", row["s_g_between_windows"])
    print("Standard error:", row["u_g_naive_sem"])

print("\nResults saved to:")
print(sampling_output)


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
    "calculation": "g_raw = -ln(I_corr)",
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