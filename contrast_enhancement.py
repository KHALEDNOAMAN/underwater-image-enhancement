"""
Contrast Enhancement Module
- CLAHE (Contrast Limited Adaptive Histogram Equalization)
- Histogram Equalization on LAB luminance channel
- Gamma Correction
"""
import cv2
import numpy as np


def apply_clahe(img, clip_limit=3.0, tile_size=8):
    """
    CLAHE — Contrast Limited Adaptive Histogram Equalization.
    Applied to the L channel in LAB color space to enhance
    local contrast without amplifying noise.

    Parameters:
        clip_limit: contrast limit (higher = more contrast)
        tile_size: grid size for local regions
    """
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=clip_limit,
        tileGridSize=(tile_size, tile_size)
    )
    l_enhanced = clahe.apply(l)

    enhanced_lab = cv2.merge([l_enhanced, a, b])
    return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)


def histogram_equalization(img):
    """
    Global histogram equalization on luminance channel (LAB).
    Spreads pixel intensities across the full range.
    """
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    l_eq = cv2.equalizeHist(l)

    enhanced_lab = cv2.merge([l_eq, a, b])
    return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)


def gamma_correction(img, gamma=1.2):
    """
    Gamma correction to adjust overall brightness.
    Formula: output = 255 * (input / 255) ^ (1/gamma)

    gamma > 1 → brightens the image
    gamma < 1 → darkens the image
    """
    inv_gamma = 1.0 / gamma
    table = np.array([
        ((i / 255.0) ** inv_gamma) * 255
        for i in range(256)
    ]).astype(np.uint8)

    return cv2.LUT(img, table)


def apply_contrast_enhancement(img, method="clahe", **kwargs):
    """Apply contrast enhancement with the specified method."""
    if method == "clahe":
        clip = kwargs.get("clip_limit", 3.0)
        tile = kwargs.get("tile_size", 8)
        return apply_clahe(img, clip, tile)
    elif method == "histogram_eq":
        return histogram_equalization(img)
    elif method == "gamma":
        g = kwargs.get("gamma", 1.2)
        return gamma_correction(img, g)
    return img
