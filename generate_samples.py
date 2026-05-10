"""
Generate synthetic underwater sample images for testing.
Creates images with typical underwater degradation:
- Blue/green color cast
- Low contrast
- Haze effect
"""
import cv2
import numpy as np
import os


def create_underwater_effect(img, depth_level=0.5):
    """Apply synthetic underwater degradation to an image."""
    h, w = img.shape[:2]
    result = img.astype(np.float64)

    # 1. Color cast — absorb red, boost blue/green
    attenuation = {
        'r': 1.0 - depth_level * 0.7,   # Red is absorbed most
        'g': 1.0 - depth_level * 0.2,   # Green moderate
        'b': 1.0 + depth_level * 0.15,  # Blue increases
    }
    result[:, :, 2] *= attenuation['r']  # R
    result[:, :, 1] *= attenuation['g']  # G
    result[:, :, 0] *= attenuation['b']  # B

    # 2. Add haze/scatter
    haze_color = np.array([180, 200, 150], dtype=np.float64)  # blue-green haze
    haze_strength = depth_level * 0.4
    for c in range(3):
        result[:, :, c] = result[:, :, c] * (1 - haze_strength) + haze_color[c] * haze_strength

    # 3. Reduce contrast
    mean_val = result.mean()
    result = mean_val + (result - mean_val) * (1 - depth_level * 0.3)

    # 4. Add slight noise
    noise = np.random.normal(0, 5, result.shape)
    result = result + noise

    return np.clip(result, 0, 255).astype(np.uint8)


def generate_samples():
    """Generate sample underwater-style test images."""
    output_dir = os.path.join(os.path.dirname(__file__), 'sample_images')
    os.makedirs(output_dir, exist_ok=True)

    # Create test patterns
    samples = []

    # 1. Colorful coral reef scene (synthetic)
    img1 = np.zeros((400, 600, 3), dtype=np.uint8)
    # Sky gradient at top
    for y in range(200):
        img1[y, :] = [200 - y//2, 180 - y//3, 50 + y//2]
    # Sand/coral at bottom
    for y in range(200, 400):
        img1[y, :] = [60, 120 + (y-200)//4, 160 + (y-200)//5]
    # Add some "coral" shapes
    cv2.circle(img1, (150, 300), 50, (30, 80, 200), -1)
    cv2.circle(img1, (300, 280), 40, (40, 180, 50), -1)
    cv2.circle(img1, (450, 320), 60, (20, 60, 220), -1)
    cv2.circle(img1, (200, 250), 30, (50, 200, 200), -1)
    cv2.ellipse(img1, (400, 150), (80, 30), 20, 0, 360, (200, 200, 50), -1)
    samples.append(("coral_reef_shallow", img1, 0.3))
    samples.append(("coral_reef_deep", img1, 0.7))

    # 2. Fish school scene
    img2 = np.zeros((400, 600, 3), dtype=np.uint8)
    img2[:] = [160, 140, 40]  # deep water
    for _ in range(30):
        x, y = np.random.randint(50, 550), np.random.randint(50, 350)
        size = np.random.randint(8, 20)
        color = (np.random.randint(20, 80),
                 np.random.randint(100, 200),
                 np.random.randint(150, 255))
        cv2.ellipse(img2, (x, y), (size*2, size), np.random.randint(0, 180), 0, 360, color, -1)
    samples.append(("fish_school", img2, 0.5))

    # 3. Shipwreck / dark scene
    img3 = np.zeros((400, 600, 3), dtype=np.uint8)
    img3[:] = [120, 100, 30]
    # Structure
    cv2.rectangle(img3, (100, 150), (500, 380), (60, 70, 40), -1)
    cv2.rectangle(img3, (150, 100), (200, 150), (50, 60, 35), -1)
    cv2.rectangle(img3, (350, 80), (450, 150), (55, 65, 38), -1)
    cv2.line(img3, (200, 50), (200, 100), (70, 80, 45), 5)
    cv2.line(img3, (400, 30), (400, 80), (70, 80, 45), 5)
    samples.append(("shipwreck_murky", img3, 0.8))

    # Save all
    for name, img, depth in samples:
        underwater = create_underwater_effect(img, depth)
        path = os.path.join(output_dir, f"{name}.jpg")
        cv2.imwrite(path, underwater)
        print(f"  Created: {path}")

    print(f"\n✅ Generated {len(samples)} sample images in {output_dir}")


if __name__ == "__main__":
    generate_samples()
