"""
Sharpening Module
- Unsharp Masking
- Laplacian Sharpening
"""
import cv2
import numpy as np


def unsharp_mask(img, sigma=1.0, strength=1.5):
    """
    Unsharp Masking: enhance edges by subtracting a blurred version.
    Formula: sharpened = original + strength * (original - blurred)

    Parameters:
        sigma: Gaussian blur sigma (controls what "detail" means)
        strength: how much to amplify edges (1.0-3.0 typical)
    """
    blurred = cv2.GaussianBlur(img, (0, 0), sigma)
    sharpened = cv2.addWeighted(img, 1.0 + strength, blurred, -strength, 0)
    return np.clip(sharpened, 0, 255).astype(np.uint8)


def laplacian_sharpen(img, strength=0.5):
    """
    Laplacian Sharpening: uses the 2nd derivative to detect edges.
    Formula: sharpened = original - strength * Laplacian(original)

    The Laplacian kernel:
        [0, -1,  0]
        [-1, 4, -1]
        [0, -1,  0]
    """
    # Apply Laplacian to each channel
    laplacian = cv2.Laplacian(img, cv2.CV_64F)
    sharpened = img.astype(np.float64) + strength * laplacian
    return np.clip(sharpened, 0, 255).astype(np.uint8)


def apply_sharpening(img, method="unsharp", **kwargs):
    """Apply sharpening with specified method."""
    if method == "unsharp":
        sigma = kwargs.get("sigma", 1.0)
        strength = kwargs.get("strength", 1.5)
        return unsharp_mask(img, sigma, strength)
    elif method == "laplacian":
        strength = kwargs.get("strength", 0.5)
        return laplacian_sharpen(img, strength)
    return img
