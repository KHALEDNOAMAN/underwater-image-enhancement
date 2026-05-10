"""
Main Underwater Image Enhancement Pipeline
Orchestrates all processing modules and provides CLI + API interface.
"""
import cv2
import numpy as np
import json
import sys
import os
import base64
import time

from color_correction import apply_color_correction, compensate_red_channel, gray_world_white_balance, histogram_stretching
from contrast_enhancement import apply_clahe, histogram_equalization, gamma_correction
from dehazing import apply_dehazing, get_intermediate_results
from sharpening import unsharp_mask, laplacian_sharpen
from noise_reduction import bilateral_filter, nlm_denoise
from evaluation import evaluate, get_histogram_data, calculate_colorfulness, calculate_contrast, calculate_entropy


def analyze_image(img):
    """
    Analyze an underwater image and return recommended settings.
    Examines color cast, contrast, noise level, and haze to pick optimal params.
    """
    b, g, r = cv2.split(img.astype(np.float64))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float64)

    # --- Color cast detection ---
    r_mean, g_mean, b_mean = r.mean(), g.mean(), b.mean()
    total_mean = (r_mean + g_mean + b_mean) / 3.0
    # How much red is lost relative to blue/green
    red_deficit = max(0, (g_mean + b_mean) / 2 - r_mean)
    blue_excess = max(0, b_mean - total_mean)

    # --- Contrast level ---
    contrast = gray.std()  # low = poor contrast

    # --- Noise estimation (Laplacian variance) ---
    laplacian_var = cv2.Laplacian(gray.astype(np.uint8), cv2.CV_64F).var()

    # --- Haze estimation (dark channel) ---
    min_channel = np.min(img, axis=2).astype(np.float64)
    dark_mean = min_channel.mean() / 255.0  # higher = more haze

    # --- Build recommended settings ---
    settings = {
        "noise_reduction": True,
        "noise_method": "bilateral",
        "color_correction": True,
        "color_method": "gray_world",
        "red_compensation": True,
        "dehazing": True,
        "dehaze_omega": 0.95,
        "contrast_enhancement": True,
        "contrast_method": "clahe",
        "clahe_clip": 3.0,
        "sharpening": True,
        "sharpen_method": "unsharp",
        "unsharp_strength": 1.5,
    }

    # Adjust noise reduction based on noise level
    if laplacian_var < 100:
        # Very noisy → strong denoising
        settings["noise_method"] = "nlm"
        settings["nlm_h"] = 15
    elif laplacian_var < 500:
        settings["sigma_color"] = 90
        settings["sigma_space"] = 90
    else:
        # Already sharp → light denoising
        settings["sigma_color"] = 50
        settings["sigma_space"] = 50

    # Adjust color correction based on color cast
    if red_deficit > 30:
        # Strong blue/green cast → aggressive correction
        settings["red_compensation"] = True
        settings["color_method"] = "histogram_stretch"
    elif red_deficit > 15:
        settings["red_compensation"] = True
        settings["color_method"] = "gray_world"
    else:
        # Mild cast
        settings["red_compensation"] = False
        settings["color_method"] = "gray_world"

    # Adjust dehazing based on haze level
    if dark_mean > 0.4:
        # Very hazy
        settings["dehaze_omega"] = 0.98
    elif dark_mean > 0.2:
        settings["dehaze_omega"] = 0.90
    else:
        # Clear → light dehazing
        settings["dehaze_omega"] = 0.70

    # Adjust contrast based on current contrast level
    if contrast < 20:
        # Very low contrast → strong CLAHE
        settings["clahe_clip"] = 5.0
    elif contrast < 40:
        settings["clahe_clip"] = 3.0
    else:
        # Good contrast already
        settings["clahe_clip"] = 2.0

    # Adjust sharpening
    if laplacian_var < 200:
        settings["unsharp_strength"] = 2.0  # blurry → more sharpening
    elif laplacian_var > 1000:
        settings["unsharp_strength"] = 0.8  # already sharp
    else:
        settings["unsharp_strength"] = 1.5

    # Analysis info for display
    analysis = {
        "red_mean": round(r_mean, 1),
        "green_mean": round(g_mean, 1),
        "blue_mean": round(b_mean, 1),
        "red_deficit": round(red_deficit, 1),
        "contrast": round(contrast, 1),
        "noise_level": round(laplacian_var, 1),
        "haze_level": round(dark_mean, 3),
        "diagnosis": [],
    }

    # Human-readable diagnosis
    if red_deficit > 20:
        analysis["diagnosis"].append("Strong blue/green color cast detected")
    elif red_deficit > 10:
        analysis["diagnosis"].append("Mild color cast detected")

    if contrast < 25:
        analysis["diagnosis"].append("Low contrast — needs enhancement")
    
    if dark_mean > 0.3:
        analysis["diagnosis"].append("Significant haze/scatter present")

    if laplacian_var < 200:
        analysis["diagnosis"].append("Image appears blurry — sharpening recommended")

    if not analysis["diagnosis"]:
        analysis["diagnosis"].append("Image quality is reasonable — light enhancement applied")

    return settings, analysis


def enhance_image(img, settings=None):
    """
    Full enhancement pipeline. Applies techniques in optimal order:
    1. Noise reduction (clean first)
    2. Color correction (fix colors)
    3. Dehazing (remove haze)
    4. Contrast enhancement (boost contrast)
    5. Sharpening (enhance details last)
    """
    if settings is None:
        settings = {}

    result = img.copy()
    steps = {}

    # Step 1: Noise Reduction
    if settings.get("noise_reduction", True):
        method = settings.get("noise_method", "bilateral")
        if method == "bilateral":
            result = bilateral_filter(
                result,
                d=settings.get("bilateral_d", 9),
                sigma_color=settings.get("sigma_color", 75),
                sigma_space=settings.get("sigma_space", 75)
            )
        elif method == "nlm":
            result = nlm_denoise(result, h=settings.get("nlm_h", 10))
        steps["noise_reduction"] = img_to_base64(result)

    # Step 2: Color Correction
    if settings.get("color_correction", True):
        method = settings.get("color_method", "gray_world")
        red_comp = settings.get("red_compensation", True)
        result = apply_color_correction(result, method=method, red_comp=red_comp)
        steps["color_correction"] = img_to_base64(result)

    # Step 3: Dehazing
    if settings.get("dehazing", True):
        result = apply_dehazing(
            result,
            omega=settings.get("dehaze_omega", 0.95),
            patch_size=settings.get("dehaze_patch", 15)
        )
        steps["dehazing"] = img_to_base64(result)

    # Step 4: Contrast Enhancement
    if settings.get("contrast_enhancement", True):
        method = settings.get("contrast_method", "clahe")
        if method == "clahe":
            result = apply_clahe(
                result,
                clip_limit=settings.get("clahe_clip", 3.0),
                tile_size=settings.get("clahe_tile", 8)
            )
        elif method == "histogram_eq":
            result = histogram_equalization(result)
        elif method == "gamma":
            result = gamma_correction(result, gamma=settings.get("gamma", 1.2))
        steps["contrast_enhancement"] = img_to_base64(result)

    # Step 5: Sharpening
    if settings.get("sharpening", True):
        method = settings.get("sharpen_method", "unsharp")
        if method == "unsharp":
            result = unsharp_mask(
                result,
                sigma=settings.get("unsharp_sigma", 1.0),
                strength=settings.get("unsharp_strength", 1.5)
            )
        elif method == "laplacian":
            result = laplacian_sharpen(
                result, strength=settings.get("laplacian_strength", 0.5)
            )
        steps["sharpening"] = img_to_base64(result)

    return result, steps


def img_to_base64(img):
    """Convert OpenCV image to base64 string."""
    _, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    return base64.b64encode(buffer).decode('utf-8')


def process_from_cli():
    """Handle CLI calls from the web server."""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No image path provided"}))
        sys.exit(1)

    mode = sys.argv[1]

    # --- Analyze mode ---
    if mode == "--analyze":
        image_path = sys.argv[2]
        if not os.path.exists(image_path):
            print(json.dumps({"error": f"File not found: {image_path}"}))
            sys.exit(1)
        img = cv2.imread(image_path)
        if img is None:
            print(json.dumps({"error": "Could not read image"}))
            sys.exit(1)
        # Resize for fast analysis
        max_dim = 512
        h, w = img.shape[:2]
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            img = cv2.resize(img, (int(w * scale), int(h * scale)))
        settings, analysis = analyze_image(img)
        print(json.dumps({"settings": settings, "analysis": analysis}))
        return

    # --- Enhance mode ---
    image_path = mode
    settings = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

    if not os.path.exists(image_path):
        print(json.dumps({"error": f"File not found: {image_path}"}))
        sys.exit(1)

    start_time = time.time()

    img = cv2.imread(image_path)
    if img is None:
        print(json.dumps({"error": "Could not read image"}))
        sys.exit(1)

    # Resize if too large
    max_dim = 1024
    h, w = img.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))

    enhanced, step_images = enhance_image(img, settings)

    output_path = image_path.rsplit('.', 1)[0] + '_enhanced.jpg'
    cv2.imwrite(output_path, enhanced)

    metrics = evaluate(img, enhanced)
    hist_before = get_histogram_data(img)
    hist_after = get_histogram_data(enhanced)

    elapsed = round(time.time() - start_time, 2)

    result = {
        "success": True,
        "processing_time": elapsed,
        "original": img_to_base64(img),
        "enhanced": img_to_base64(enhanced),
        "enhanced_path": output_path,
        "steps": step_images,
        "metrics": metrics,
        "histogram_before": hist_before,
        "histogram_after": hist_after,
    }

    print(json.dumps(result))


if __name__ == "__main__":
    process_from_cli()
