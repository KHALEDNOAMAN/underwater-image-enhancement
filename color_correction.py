"""
Color Correction Module
- Red channel compensation (underwater red attenuation)
- White balance (Gray World, Max-RGB, Histogram Stretching)
"""
import cv2
import numpy as np


def compensate_red_channel(img):
    """
    Compensate for red light absorption in underwater images.
    Red light is absorbed first in water, so we boost the red channel
    based on the green and blue channel averages.
    """
    b, g, r = cv2.split(img.astype(np.float64))

    r_mean = r.mean()
    g_mean = g.mean()
    b_mean = b.mean()

    # Compensation factor: how much red is lost relative to green
    if r_mean > 0:
        compensation = (g_mean - r_mean) * (r / g_mean) if g_mean > 0 else 0
        r_compensated = np.clip(r + compensation, 0, 255)
    else:
        r_compensated = r

    result = cv2.merge([b, g, r_compensated]).astype(np.uint8)
    return result


def gray_world_white_balance(img):
    """
    Gray World Assumption: the average color of a scene should be gray.
    Adjusts each channel so its mean equals the overall mean.
    Formula: channel_out = channel * (avg_all / avg_channel)
    """
    b, g, r = cv2.split(img.astype(np.float64))
    avg_all = (b.mean() + g.mean() + r.mean()) / 3.0

    b_balanced = np.clip(b * (avg_all / max(b.mean(), 1)), 0, 255)
    g_balanced = np.clip(g * (avg_all / max(g.mean(), 1)), 0, 255)
    r_balanced = np.clip(r * (avg_all / max(r.mean(), 1)), 0, 255)

    return cv2.merge([b_balanced, g_balanced, r_balanced]).astype(np.uint8)


def max_rgb_white_balance(img):
    """
    Max-RGB White Balance: normalize each channel by its maximum value.
    Formula: channel_out = channel * (255 / max_channel)
    """
    b, g, r = cv2.split(img.astype(np.float64))

    b_balanced = np.clip(b * (255.0 / max(b.max(), 1)), 0, 255)
    g_balanced = np.clip(g * (255.0 / max(g.max(), 1)), 0, 255)
    r_balanced = np.clip(r * (255.0 / max(r.max(), 1)), 0, 255)

    return cv2.merge([b_balanced, g_balanced, r_balanced]).astype(np.uint8)


def histogram_stretching(img):
    """
    Stretch each color channel's histogram to full [0, 255] range.
    Formula: out = (pixel - min) / (max - min) * 255
    """
    result = np.zeros_like(img, dtype=np.float64)
    for i in range(3):
        channel = img[:, :, i].astype(np.float64)
        c_min = np.percentile(channel, 1)   # 1st percentile to avoid outliers
        c_max = np.percentile(channel, 99)  # 99th percentile
        if c_max - c_min > 0:
            result[:, :, i] = np.clip((channel - c_min) / (c_max - c_min) * 255, 0, 255)
        else:
            result[:, :, i] = channel

    return result.astype(np.uint8)


def apply_color_correction(img, method="gray_world", red_comp=True):
    """Apply color correction with optional red channel compensation."""
    result = img.copy()

    if red_comp:
        result = compensate_red_channel(result)

    if method == "gray_world":
        result = gray_world_white_balance(result)
    elif method == "max_rgb":
        result = max_rgb_white_balance(result)
    elif method == "histogram_stretch":
        result = histogram_stretching(result)

    return result
