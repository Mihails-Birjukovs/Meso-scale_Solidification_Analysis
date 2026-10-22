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
# %% Interactive slider (palaid šo šūnu atsevišķi un apskaties attēlus)
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
if start_frame < 0 or end_frame >= len(images):
    raise ValueError("Frame range outside available images.")

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
referenceFrame_safe = np.where(referenceFrame == 0, 1e-6, referenceFrame)

zero_reference = np.sum(referenceFrame == 0)

print("Zero reference pixels:", zero_reference)
print("Total pixels:", referenceFrame.size)
print("Fraction:", zero_reference / referenceFrame.size)

# =============================================================================
# I_corr = I / I0  (bez dark-current korekcijas, jo tev tādu datu nav —
# tas ir zināms un pieņemts tuvinājums, ir minēts darba metodoloģijā)

I_corr = croppedImages.astype(np.float32) / referenceFrame_safe
print("I_corr shape:", I_corr.shape)
print("I_corr value range:", I_corr.min(), I_corr.max())



# %% Diagnostic: invalid normalized intensities

invalid_mask = ~np.isfinite(I_corr) | (I_corr <= 0)

print("Invalid intensity pixels:", np.sum(invalid_mask))
print("Invalid intensity fraction:", np.mean(invalid_mask))
print("Non-finite pixels:", np.sum(~np.isfinite(I_corr)))
print("Zero pixels:", np.sum(I_corr == 0))
print("Negative pixels:", np.sum(I_corr < 0))

if np.any(np.isfinite(I_corr)):
    finite_values = I_corr[np.isfinite(I_corr)]
    print("Finite I_corr min:", finite_values.min())
    print("Finite I_corr max:", finite_values.max())
    
    
    
    
# %%

# =============================================================================
# Quick preview of I_corr
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

# %%
# Cik daudz un kur ir problemātiskie pikseļi?
zero_count = np.sum(I_corr == 0)
negative_count = np.sum(I_corr < 0)
print("Nulles vērtību skaits:", zero_count)
print("Negatīvu vērtību skaits:", negative_count)

if negative_count > 0:
    neg_values = I_corr[I_corr < 0]
    print("Negatīvo vērtību diapazons:", neg_values.min(), "līdz", neg_values.max())
    
# Pārbaudi, vai I_corr datu tips ir float (nevis uint)
print("I_corr dtype:", I_corr.dtype)

# %%
problem_pixels = np.argwhere(I_corr == 0)
unique_positions = np.unique(problem_pixels[:, 1:], axis=0)  # tikai (y, x)
print("Unikālu problemātisko pikseļu pozīciju skaits:", len(unique_positions))
print("Pozīcijas:", unique_positions)
# %% Optical density
# =============================================================================
g_raw = -np.log(I_corr)   # naturāllogaritms
print("g_raw value range:", g_raw.min(), g_raw.max())

plt.figure(figsize=(6,5))
plt.imshow(g_raw[0], cmap="viridis")
plt.colorbar(label="g")
plt.title("Optical density, frame 101")
plt.axis("off")
plt.show()

# %% Diagnostika - kur atrodas negatīvās g vērtības
# =============================================================================
negative_mask = g_raw < 0
print("Negatīvo pikseļu daļa:", negative_mask.mean())
plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
plt.imshow(g_raw[0], cmap="RdBu_r", vmin=-0.1, vmax=0.1)
plt.colorbar(label="g")
plt.title("g (sarkans = pozitīvs, zils = negatīvs), frame 1")
plt.axis("off")

plt.subplot(1,2,2)
plt.hist(g_raw[0].ravel(), bins = 100)
plt.axvline(0, color='r', linestyle='--')
plt.xlabel("g")
plt.title("g histogramma, frame 1")
plt.show()


# %%
print(f"I_corr minimums: {np.nanmin(I_corr):.6f}")
print(f"I_corr maksimums: {np.nanmax(I_corr):.6f}")
print(f"Pikseļi ar I_corr <= 0: {np.sum(invalid_mask)}")

# Pārbaude pēc logaritma
negative_g_mask = np.isfinite(g_raw) & (g_raw < 0)

print(f"g minimums: {np.nanmin(g_raw):.6f}")
print(f"g maksimums: {np.nanmax(g_raw):.6f}")
print(f"Negatīvo g pikseļu skaits: {np.sum(negative_g_mask)}")
print(f"Negatīvo g īpatsvars: {100 * np.mean(negative_g_mask):.2f}%")
# %% Uzsvērts kur tieši ir tie pzoitīvie rezultāti.
frame = g_raw[0]
positive_mask = frame > 0

# Bāzes attēls pelēkā skalā
plt.figure(figsize=(8,6))
plt.imshow(frame, cmap="gray")
# Overlay: oranžs tikai tur, kur positive_mask == True, citur caurspīdīgs
overlay = np.zeros((*frame.shape, 4))  # RGBA
overlay[positive_mask] = [1.0, 0.55, 0.0, 0.6]  # oranžs, alpha=0.6 (caurspīdīgums)
overlay[~positive_mask] = [0, 0, 0, 0]  # pilnīgi caurspīdīgs, kur nav pozitīvs

plt.imshow(overlay)
plt.title("Oranžs = g > 0 (pozitīvs)")
plt.axis("off")
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

print(f"Kadri sākotnēji: {n_frames}, izmesti (atlikums): {discarded}")
print(f"Binoti kadri: {I_corr_binned.shape[0]}")
print(f"dt: {dt_eff} s, kadru frekvence: {f_eff} Hz")


# %% Spatial downsampling (Lanczos, on binned I_corr, still linear domain)
# =============================================================================
downsample_factor = 4

height, width = I_corr_binned.shape[1:]
target_size = (round(width / downsample_factor), round(height / downsample_factor))  # cv2: (w, h)

I_corr_downsampled = np.stack([
cv2.resize(frame, target_size, interpolation=cv2.INTER_LANCZOS4)
    for frame in I_corr_binned])

print("Downsampled shape:", I_corr_downsampled.shape)

# Lanczos ringing pārbaude - negatīvas/nulles vērtības PIRMS log
n_bad = np.sum(I_corr_downsampled <= 0)
print("Negatīvi/nulles pikseļi pēc Lanczos:", n_bad)

eps = 1e-6
I_corr_downsampled_safe = np.clip(I_corr_downsampled, eps, None)
dx0 = 17.5  # µm/px
dx_eff = downsample_factor * dx0
print(f"Reālais pikseļa izmērs: {dx_eff} µm/px")


# %% Optical density - uz tā paša režģa, ko izmantos ātruma lauks
# =============================================================================
g_downsampled = -np.log(I_corr_downsampled_safe)
print("g_downsampled value range:", g_downsampled.min(), g_downsampled.max())

plt.figure(figsize=(6,5))
plt.imshow(g_downsampled[0], cmap="viridis")
plt.colorbar(label="g")
plt.title("Optical density, frame 1")
plt.axis("off")
plt.show()

print("Pirmsapstrādes downsampled g vērtību diapazons:", g_downsampled.min(), g_downsampled.max())
print("g satur NaN/Inf:", np.any(~np.isfinite(g_downsampled)))

# %% Diagnostika - kur atrodas negatīvās g vērtības
# =============================================================================
negative_mask = g_downsampled < 0
print("Negatīvo pikseļu daļa:", negative_mask.mean())
plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
plt.imshow(g_downsampled[25], cmap="RdBu_r", vmin=-0.1, vmax=0.1)
plt.colorbar(label="g")
plt.title("g (sarkans = pozitīvs, zils = negatīvs), frame 26")
plt.axis("off")

plt.subplot(1,2,2)
plt.hist(g_downsampled[25].ravel(), bins = 100)
plt.axvline(0, color='r', linestyle='--')
plt.xlabel("g")
plt.title("g histogramma, frame 26")
plt.show()


# %% Validation preview - sākums, vidus, beigas (checklist p.8 no dokumenta)
# =============================================================================
fig, axes = plt.subplots(1, 3, figsize=(15,5))
for ax, idx, label in zip(axes, [0, len(g_downsampled)//2, len(g_downsampled) - 1], ["Start", "Middle", "End"]):
    im = ax.imshow(g_downsampled[idx], cmap="viridis")
    ax.set_title(f"{label} (frame {idx + 1})")
    ax.axis("off")
fig.colorbar(im, ax=axes, shrink=0.6, label="g")
plt.show()

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
    "value_min": float(g_raw.min()),
    "value_max": float(g_raw.max()),
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
    "value_min": float(g_downsampled.min()),
    "value_max": float(g_downsampled.max()),
    "source_shape": list(I_corr_downsampled_safe.shape),
    "downsample_factor": downsample_factor,
    "dx_eff_um_per_pixel": dx_eff}

g_preprocess_json_path = (g_preprocess_output_folder / "g_parameters.json")

with open(g_preprocess_json_path, "w") as file:
    json.dump(g_preprocess_parameters, file, indent = 4)

print("Saved g parameters:", g_preprocess_json_path)


# %% Calibration
C_in_percent = 270.1341 * g_downsampled + 29.2945

print("Min:", np.min(C_in_percent))
print("Max:", np.max(C_in_percent))
print("Mean:", np.mean(C_in_percent))
print("Median:", np.median(C_in_percent))

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

axes[1].imshow(g_median[frame_idx],
               cmap="gray", vmin=vmin, vmax=vmax)
axes[1].set_title("Median-filtered g")

axes[2].imshow(g_filtered[frame_idx],
               cmap="gray", vmin=vmin, vmax=vmax)
axes[2].set_title("Median + TV filtered g")


for ax in axes:
    ax.axis("off")

plt.tight_layout()
plt.show()

# %% Calibration
# =============================================================================
# Apply calibration AFTER filtering g
C_in_percent_filtered = 270.1341 * g_filtered + 29.2945

print("Concentration min:", np.nanmin(C_in_percent))
print("Concentration max:", np.nanmax(C_in_percent))
print("Concentration mean:", np.nanmean(C_in_percent))
print("Concentration median:", np.nanmedian(C_in_percent))

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
    "calibration": "C_in_percent_filtered = 270.1341 * g + 29.2945",
    "source": "g_downsampled",
    "filtering_domain": "optical_density_g",
    "median_filter_size": median_filter_size,
    "tv_weight": tv_weight,
    "sharpening": False,
    "concentration_clipped": False,
    "number_of_frames": int(C_in_percent.shape[0]),
    "image_shape": list(C_in_percent.shape[1:]),
    "concentration_min": float(np.nanmin(C_in_percent)),
    "concentration_max": float(np.nanmax(C_in_percent))
}


with open(conc_output_folder / "concentration_parameters.json", "w") as f:
    json.dump(parameters, f, indent=4)

print("Concentration export completed.")
print("Saved frames:", len(C_in_percent))
print("Location:", conc_output_folder)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

# %% 2D Denoising & Contrast Boosting
# =============================================================================
from scipy.ndimage import median_filter
from skimage.restoration import denoise_tv_chambolle
from skimage.filters import unsharp_mask

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

# Sharpen - atgriež smalkās detaļas, ko TV izpludināja
images_sharpened = np.stack([
    unsharp_mask(frame, radius=2, amount=1.0)
    for frame in images_tv])

testImagesFiltered = images_sharpened
print("testImagesFiltered shape:", testImagesFiltered.shape)
print("Value range:", testImagesFiltered.min(), testImagesFiltered.max())

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
