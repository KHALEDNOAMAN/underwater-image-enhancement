"""
Dehazing Module — Dark Channel Prior
Based on He et al. "Single Image Haze Removal Using Dark Channel Prior"
Adapted for underwater images.

Key formula:
    J(x) = (I(x) - A) / max(t(x), t0) + A

Where:
    I(x) = observed hazy image
    A    = atmospheric (water) light
    t(x) = transmission map
    J(x) = recovered scene radiance
"""
import cv2
import numpy as np


def get_dark_channel(img, patch_size=15):
    """
    Compute the dark channel of an image.
    dark(x) = min_{y in patch(x)} ( min_{c in {R,G,B}} I_c(y) )

    The dark channel finds the darkest pixel in a local patch
    across all color channels.
    """
    min_channel = np.min(img, axis=2)
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (patch_size, patch_size)
    )
    dark = cv2.erode(min_channel, kernel)
    return dark


def estimate_atmospheric_light(img, dark_channel, top_percent=0.001):
    """
    Estimate atmospheric light A from the brightest pixels
    in the dark channel (top 0.1%).
    """
    h, w = dark_channel.shape
    num_pixels = max(int(h * w * top_percent), 1)

    # Find brightest pixels in dark channel
    flat_dark = dark_channel.ravel()
    indices = np.argsort(flat_dark)[-num_pixels:]

    # Get corresponding pixels from original image
    flat_img = img.reshape(-1, 3)
    atmospheric_light = flat_img[indices].mean(axis=0)

    return atmospheric_light


def estimate_transmission(img, atmospheric_light, omega=0.95, patch_size=15):
    """
    Estimate transmission map:
    t(x) = 1 - omega * dark_channel(I(x) / A)

    omega < 1 keeps a small amount of haze for natural look.
    """
    normalized = img.astype(np.float64) / atmospheric_light
    dark = get_dark_channel(normalized, patch_size)
    transmission = 1.0 - omega * dark
    return transmission


def guided_filter(guide, src, radius=60, eps=1e-3):
    """
    Guided filter to refine the transmission map.
    Smooths the transmission while preserving edges from the guide image.
    """
    guide_gray = cv2.cvtColor(guide, cv2.COLOR_BGR2GRAY).astype(np.float64) / 255.0
    src = src.astype(np.float64)

    mean_g = cv2.boxFilter(guide_gray, -1, (radius, radius))
    mean_s = cv2.boxFilter(src, -1, (radius, radius))
    mean_gs = cv2.boxFilter(guide_gray * src, -1, (radius, radius))
    mean_gg = cv2.boxFilter(guide_gray * guide_gray, -1, (radius, radius))

    cov_gs = mean_gs - mean_g * mean_s
    var_g = mean_gg - mean_g * mean_g

    a = cov_gs / (var_g + eps)
    b = mean_s - a * mean_g

    mean_a = cv2.boxFilter(a, -1, (radius, radius))
    mean_b = cv2.boxFilter(b, -1, (radius, radius))

    result = mean_a * guide_gray + mean_b
    return result


def recover_scene(img, atmospheric_light, transmission, t0=0.1):
    """
    Recover the dehazed image:
    J(x) = (I(x) - A) / max(t(x), t0) + A
    """
    img_float = img.astype(np.float64)
    t_clamped = np.maximum(transmission, t0)
    result = np.zeros_like(img_float)

    for c in range(3):
        result[:, :, c] = (
            (img_float[:, :, c] - atmospheric_light[c]) / t_clamped
            + atmospheric_light[c]
        )

    return np.clip(result, 0, 255).astype(np.uint8)


def apply_dehazing(img, omega=0.95, patch_size=15, t0=0.1):
    """Full dehazing pipeline using Dark Channel Prior."""
    dark = get_dark_channel(img, patch_size)
    atm_light = estimate_atmospheric_light(img, dark)
    transmission = estimate_transmission(img, atm_light, omega, patch_size)
    transmission = guided_filter(img, transmission)
    result = recover_scene(img, atm_light, transmission, t0)
    return result


def get_intermediate_results(img, omega=0.95, patch_size=15):
    """Return intermediate results for visualization."""
    dark = get_dark_channel(img, patch_size)
    atm_light = estimate_atmospheric_light(img, dark)
    transmission = estimate_transmission(img, atm_light, omega, patch_size)
    refined_transmission = guided_filter(img, transmission)

    return {
        "dark_channel": (dark * 255).astype(np.uint8) if dark.max() <= 1 else dark.astype(np.uint8),
        "transmission": (transmission * 255).astype(np.uint8),
        "refined_transmission": (refined_transmission * 255).astype(np.uint8),
        "atmospheric_light": atm_light.tolist(),
    }
