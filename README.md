# 🌊 AquaClear — Underwater Image Enhancement System

> A full-stack image processing system that automatically detects and corrects underwater image degradation — color casts, haze, low contrast, and blur — using classical computer vision techniques.

---

## 📸 Overview

Underwater images suffer from color distortion (blue/green cast), light scattering, haze, and low contrast due to the absorption and scattering of light in water. **AquaClear** applies a smart, multi-step enhancement pipeline that analyzes each image and applies the optimal combination of corrections.

---

## ✨ Features

- 🎨 **Color Correction** — Gray World white balance, histogram stretching, red channel compensation
- 🌫️ **Dehazing** — Dark Channel Prior algorithm (He et al.)
- 📊 **Contrast Enhancement** — CLAHE, histogram equalization, gamma correction
- 🔍 **Sharpening** — Unsharp masking and Laplacian sharpening
- 🔇 **Noise Reduction** — Bilateral filter and Non-Local Means (NLM) denoising
- 🤖 **Auto-Analysis** — Automatically detects image issues and recommends optimal settings
- 📈 **Quality Metrics** — PSNR, colorfulness, contrast, and entropy scores
- 🌐 **Web Interface** — Interactive browser UI with step-by-step visualization
- 🐳 **Docker Support** — Containerized for easy deployment

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                  Web Interface                   │
│              (Node.js + Express)                 │
└──────────────────────┬──────────────────────────┘
                       │ HTTP / CLI bridge
┌──────────────────────▼──────────────────────────┐
│            Python Enhancement Pipeline           │
│                                                  │
│  noise_reduction → color_correction → dehazing   │
│       → contrast_enhancement → sharpening        │
└──────────────────────────────────────────────────┘
```

### Module Breakdown

| File | Description |
|------|-------------|
| `app.py` | Main pipeline orchestrator — CLI + analysis entry point |
| `server.js` | Node.js/Express web server |
| `color_correction.py` | Gray world, histogram stretch, red compensation |
| `contrast_enhancement.py` | CLAHE, histogram EQ, gamma correction |
| `dehazing.py` | Dark Channel Prior dehazing |
| `sharpening.py` | Unsharp mask, Laplacian sharpening |
| `noise_reduction.py` | Bilateral filter, NLM denoising |
| `evaluation.py` | PSNR, colorfulness, contrast, entropy metrics |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/KHALEDNOAMAN/underwater-image-enhancement.git
cd underwater-image-enhancement

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install
```

### Running the Web App

```bash
npm start
```

Then open your browser at **http://localhost:3000**

### Using the CLI

```bash
# Auto-analyze an image
python app.py --analyze path/to/image.jpg

# Enhance with default settings
python app.py path/to/image.jpg

# Enhance with custom settings (JSON)
python app.py path/to/image.jpg '{"clahe_clip": 4.0, "dehaze_omega": 0.95}'
```

---

## 🐳 Docker

```bash
# Build the image
docker build -t aquaclear .

# Run the container
docker run -p 3000:3000 aquaclear
```

---

## 🔬 Enhancement Pipeline

The pipeline processes images in this optimal order:

```
1. 🔇 Noise Reduction    →  Clean the image first
2. 🎨 Color Correction   →  Fix color cast
3. 🌫️ Dehazing           →  Remove haze/scatter
4. 📊 Contrast Boost     →  Improve visibility
5. 🔍 Sharpening         →  Recover fine details
```

The `analyze_image()` function automatically tunes each step based on:
- **Color cast severity** (red deficit vs. blue/green dominance)
- **Contrast level** (standard deviation of grayscale)
- **Noise level** (Laplacian variance)
- **Haze level** (dark channel mean)

---

## 📊 Quality Metrics

After enhancement, the system reports:

| Metric | Description |
|--------|-------------|
| **PSNR** | Peak Signal-to-Noise Ratio |
| **Colorfulness** | Hasler & Süsstrunk colorfulness score |
| **Contrast** | RMS contrast of the image |
| **Entropy** | Information entropy (detail richness) |

---

## 📁 Project Structure

```
underwater-image-enhancement/
├── app.py                  # Main Python pipeline
├── server.js               # Node.js web server
├── requirements.txt        # Python dependencies
├── package.json            # Node.js dependencies
├── Dockerfile              # Container configuration
├── color_correction.py
├── contrast_enhancement.py
├── dehazing.py
├── sharpening.py
├── noise_reduction.py
├── evaluation.py
├── public/                 # Frontend assets
├── uploads/                # Uploaded images (temp)
└── sample_images/          # Test images
```

---

## 📽️ Presentation

See [`last.pptx`](./last.pptx) for the full project presentation.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Image Processing | Python, OpenCV, NumPy |
| Web Server | Node.js, Express |
| Frontend | HTML, CSS, JavaScript |
| Containerization | Docker |

---

## 👨‍💻 Author

**Khaled Noaman**
- GitHub: [@KHALEDNOAMAN](https://github.com/KHALEDNOAMAN)

---

## 📄 License

This project is for academic purposes — CENG 455 Course Project.
