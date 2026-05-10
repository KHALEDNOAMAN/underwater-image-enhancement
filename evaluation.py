"""
Evaluation Metrics Module
- PSNR (Peak Signal-to-Noise Ratio)
- SSIM (Structural Similarity Index)
- UIQM (Underwater Image Quality Measure) - simplified
- Histogram statistics
"""
import cv2
import numpy as np


def calculate_psnr(original, enhanced):
    """
    PSNR = 10 * log10(MAX² / MSE)
    Higher PSNR = less distortion from original.
    """
    mse = np.mean((original.astype(np.float64) - enhanced.astype(np.float64)) ** 2)
    if mse == 0:
        return float('inf')
    return 10 * np.log10(255.0 ** 2 / mse)


def calculate_ssim(original, enhanced):
    """
    SSIM — compares luminance, contrast, and structure.
    Range: [-1, 1], where 1 = identical images.
    """
    gray1 = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY).astype(np.float64)
    gray2 = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY).astype(np.float64)

    C1 = (0.01 * 255) ** 2
    C2 = (0.03 * 255) ** 2

    mu1 = cv2.GaussianBlur(gray1, (11, 11), 1.5)
    mu2 = cv2.GaussianBlur(gray2, (11, 11), 1.5)

    mu1_sq = mu1 ** 2
    mu2_sq = mu2 ** 2
    mu1_mu2 = mu1 * mu2

    sigma1_sq = cv2.GaussianBlur(gray1 ** 2, (11, 11), 1.5) - mu1_sq
    sigma2_sq = cv2.GaussianBlur(gray2 ** 2, (11, 11), 1.5) - mu2_sq
    sigma12 = cv2.GaussianBlur(gray1 * gray2, (11, 11), 1.5) - mu1_mu2

    ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / \
               ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))

    return float(ssim_map.mean())


def calculate_colorfulness(img):
    """
    Colorfulness metric (Hasler & Süsstrunk, 2003).
    Higher values = more colorful image.
    """
    b, g, r = cv2.split(img.astype(np.float64))
    rg = r - g
    yb = 0.5 * (r + g) - b

    std_rg = np.std(rg)
    std_yb = np.std(yb)
    mean_rg = np.mean(rg)
    mean_yb = np.mean(yb)

    std_root = np.sqrt(std_rg ** 2 + std_yb ** 2)
    mean_root = np.sqrt(mean_rg ** 2 + mean_yb ** 2)

    return std_root + 0.3 * mean_root


def calculate_contrast(img):
    """Average local contrast using standard deviation of luminance."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float64)
    return float(gray.std())


def calculate_entropy(img):
    """Shannon entropy of the grayscale image — measures information content."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
    hist = hist / hist.sum()
    hist = hist[hist > 0]
    return float(-np.sum(hist * np.log2(hist)))


def get_histogram_data(img):
    """Get histogram data for all 3 channels."""
    colors = ('b', 'g', 'r')
    histograms = {}
    for i, color in enumerate(colors):
        hist = cv2.calcHist([img], [i], None, [256], [0, 256]).flatten()
        histograms[color] = hist.tolist()
    return histograms


def evaluate(original, enhanced):
    """Run all evaluation metrics."""
    return {
        "psnr": round(calculate_psnr(original, enhanced), 2),
        "ssim": round(calculate_ssim(original, enhanced), 4),
        "colorfulness_before": round(calculate_colorfulness(original), 2),
        "colorfulness_after": round(calculate_colorfulness(enhanced), 2),
        "contrast_before": round(calculate_contrast(original), 2),
        "contrast_after": round(calculate_contrast(enhanced), 2),
        "entropy_before": round(calculate_entropy(original), 4),
        "entropy_after": round(calculate_entropy(enhanced), 4),
    }
