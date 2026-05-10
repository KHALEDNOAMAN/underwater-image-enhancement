"""
Noise Reduction Module
- Bilateral Filtering (edge-preserving smoothing)
- Non-Local Means Denoising
"""
import cv2
import numpy as np


def bilateral_filter(img, d=9, sigma_color=75, sigma_space=75):
    """
    Bilateral Filter: smooths while preserving edges.
    Each pixel is replaced by a weighted average of neighbors where the
    weight depends on both spatial distance AND intensity difference.

    Parameters:
        d: diameter of pixel neighborhood
        sigma_color: filter sigma in color space (larger = more mixing)
        sigma_space: filter sigma in coordinate space (larger = wider area)
    """
    return cv2.bilateralFilter(img, d, sigma_color, sigma_space)


def nlm_denoise(img, h=10, template_size=7, search_size=21):
    """
    Non-Local Means Denoising: compares patches across the image
    to find similar regions and averages them.

    Parameters:
        h: filter strength (larger = more smoothing, less noise)
        template_size: size of template patch
        search_size: size of area to search for similar patches
    """
    return cv2.fastNlMeansDenoisingColored(
        img, None, h, h, template_size, search_size
    )


def apply_noise_reduction(img, method="bilateral", **kwargs):
    """Apply noise reduction with specified method."""
    if method == "bilateral":
        d = kwargs.get("d", 9)
        sc = kwargs.get("sigma_color", 75)
        ss = kwargs.get("sigma_space", 75)
        return bilateral_filter(img, d, sc, ss)
    elif method == "nlm":
        h = kwargs.get("h", 10)
        return nlm_denoise(img, h)
    return img
