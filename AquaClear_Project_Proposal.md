# Project Proposal: AquaClear Underwater Image Enhancement System
**Course:** CENG 455 Digital Image Processing
**Institution:** Istanbul Arel University, 2026
**Student:** Khaled Noaman

---

## 1. Introduction and Background
Underwater photography and videography suffer from severe degradation compared to terrestrial imaging. Due to the physical properties of water, light is exponentally attenuated and scattered as it travels from the surface to the object, and back to the camera lens. This results in three primary issues:
1. **Color Cast (Attenuation):** Water absorbs wavelengths differently. Red light (650nm) is absorbed first, often disappearing completely within the first 5 meters. This leaves deep underwater images with a dominant, washed-out blue/green tint.
2. **Haze and Fog (Backscattering):** Suspended particles in the water—such as plankton, sand, and marine snow—scatter the light before it reaches the camera sensor. This creates a thick "fog" that heavily reduces visibility and contrast.
3. **Loss of High-Frequency Detail (Forward Scattering):** Light reflecting directly off the object is slightly scattered on its path to the camera, resulting in blurred edges and a lack of sharpness.

Enhancing these images is critical for marine biology research, underwater robotics (AUVs/ROVs), oceanography, and consumer underwater photography.

## 2. Problem Statement
Standard image enhancement techniques (such as global histogram equalization or basic brightness/contrast adjustments) are insufficient for underwater images. For instance, applying a global histogram equalization often "washes out" the image, destroying local contrast and amplifying noise. Standard linear noise filters (like Gaussian blur) further degrade the already blurred edges caused by forward scattering. 

A specialized, multi-stage image processing pipeline is required to reverse the specific physical degradations caused by the aquatic environment.

## 3. Proposed Solution
**AquaClear** is a proposed web-based software application that implements a purely classical Image Processing (IP) pipeline to restore underwater images. The project deliberately avoids black-box Neural Networks or Deep Learning in favor of deterministic, highly interpretable mathematical algorithms. 

The pipeline consists of the following modular stages:
1. **Non-Linear Noise Reduction:** Using a Bilateral Filter to smooth wide areas (removing marine snow and sensor noise) while strictly preserving sharp edges.
2. **Color Correction:** Implementing the Gray World Theorem to globally estimate color deficits and selectively boost the attenuated red channel, neutralizing the blue/green tint.
3. **Dehazing (Dark Channel Prior):** Estimating the atmospheric light and transmission map of the water to mathematically subtract the backscattered haze and restore original scene radiance.
4. **Adaptive Contrast Enhancement:** Applying Contrast Limited Adaptive Histogram Equalization (CLAHE) on the Luminance (L) channel of the LAB color space. This prevents color distortion while boosting local contrast and capping noise amplification.
5. **Frequency Domain Sharpening:** Applying Unsharp Masking to extract and boost high-frequency edge data, counteracting forward-scatter blur.

## 4. System Architecture
The application will be developed as a modern, full-stack web application to provide an intuitive Graphic User Interface (GUI) for end-users.
*   **Frontend Interface:** A responsive HTML/CSS/JS interface featuring a "Dark/Light" mode toggle, an image upload area, and interactive sliders/toggles for fine-tuning the processing parameters.
*   **Backend Server:** A Node.js (Express) server responsible for managing HTTP requests, handling temporary image uploads via Multer, and routing data to the processing engine.
*   **Image Processing Engine:** A Python 3 core utilizing OpenCV (`cv2`) and NumPy. The engine operates statelessly, receiving Base64 encoded images from Node.js, executing the matrix operations, and returning the processed result along with objective quality metrics (PSNR, SSIM, Colorfulness, Entropy).

## 5. Key Feature: Auto-Analysis
To improve user experience, the system will feature an "Auto-Analyze" module. When an image is uploaded, the Python backend will perform a preliminary diagnostic pass:
*   Checking the global variance of a Laplacian filter to determine the blur level.
*   Checking the Dark Channel mean to estimate the density of the haze.
*   Comparing the global averages of the Blue and Red channels to quantify depth/color loss.

Based on these heuristics, the system will automatically configure the optimal parameters for the enhancement pipeline (e.g., dynamically increasing CLAHE clip limits or Dehazing omega values for severely degraded images).

## 6. Expected Outcomes and Deliverables
1.  **Functional Web Application:** A fully operational local server allowing users to upload real underwater photos and instantly see the enhanced results alongside before/after metrics.
2.  **Source Code Repository:** Including the Python processing modules, the Node.js server, and the frontend assets.
3.  **Project Presentation:** A formal slide deck demonstrating the physics of underwater light, the mathematical theory behind the chosen algorithms, a live demonstration workflow, and an architectural overview.
4.  **Final Report:** An academic summation of the project's methodologies, challenges, and quantitative results (using PSNR and SSIM benchmarks).

## 7. Timeline
*   **Week 1:** Research and implementation of core Python IP modules (Color Correction, Filtering).
*   **Week 2:** Implementation of Dehazing (Dark Channel Prior) and adaptive contrast (CLAHE).
*   **Week 3:** Development of the Node.js backend and HTML/CSS web interface.
*   **Week 4:** Integration of the Auto-Analysis feature, final UI polish (Dark Mode), and documentation generation.
