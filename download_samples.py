"""
Download real underwater sample images for testing.
Uses publicly available underwater photography datasets.
"""
import urllib.request
import os

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'sample_images')

# Publicly available underwater images (Unsplash/Pexels-style free images)
SAMPLE_URLS = [
    ("https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&q=80", "coral_reef.jpg"),
    ("https://images.unsplash.com/photo-1582967788606-a171c7a4e01b?w=800&q=80", "sea_turtle.jpg"),
    ("https://images.unsplash.com/photo-1546026423-cc4642628d2b?w=800&q=80", "tropical_fish.jpg"),
    ("https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=800&q=80", "deep_ocean.jpg"),
    ("https://images.unsplash.com/photo-1583212292454-1fe6229603b7?w=800&q=80", "underwater_reef.jpg"),
    ("https://images.unsplash.com/photo-1590401887373-c8f95c80ed25?w=800&q=80", "whale_shark.jpg"),
    ("https://images.unsplash.com/photo-1544552866-d3ed42536cfd?w=800&q=80", "diver.jpg"),
]


def download_samples():
    os.makedirs(SAMPLES_DIR, exist_ok=True)

    for url, filename in SAMPLE_URLS:
        filepath = os.path.join(SAMPLES_DIR, filename)
        if os.path.exists(filepath):
            print(f"  ✓ Already exists: {filename}")
            continue

        try:
            print(f"  ⬇ Downloading: {filename}...", end=" ")
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
            with open(filepath, 'wb') as f:
                f.write(data)
            size_kb = len(data) / 1024
            print(f"OK ({size_kb:.0f} KB)")
        except Exception as e:
            print(f"FAILED: {e}")

    # Count final images
    count = len([f for f in os.listdir(SAMPLES_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    print(f"\n✅ {count} sample images ready in {SAMPLES_DIR}")


if __name__ == "__main__":
    download_samples()
