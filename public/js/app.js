/* ═══════════════════════════════════════════════
   AquaClear — Frontend JavaScript
   With auto-analyze, dark/light mode, presets
   ═══════════════════════════════════════════════ */

let currentFile = null;
let currentSamplePath = null;
let enhancedDataUrl = null;
let autoSettings = null;
let currentPreset = 'auto';

// ─── Init ───
document.addEventListener('DOMContentLoaded', () => {
    loadSamples();
    setupUpload();
    setupSliders();
    loadTheme();
});

// ─── Theme Toggle ───
function toggleTheme() {
    const html = document.documentElement;
    const current = html.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    document.getElementById('themeIcon').textContent = next === 'dark' ? '🌙' : '☀️';
    localStorage.setItem('aquaclear-theme', next);
}

function loadTheme() {
    const saved = localStorage.getItem('aquaclear-theme');
    if (saved) {
        document.documentElement.setAttribute('data-theme', saved);
        document.getElementById('themeIcon').textContent = saved === 'dark' ? '🌙' : '☀️';
    }
}

// ─── Upload ───
function setupUpload() {
    const area = document.getElementById('uploadArea');
    const input = document.getElementById('fileInput');

    area.addEventListener('click', (e) => {
        if (e.target.tagName !== 'BUTTON') input.click();
    });
    area.addEventListener('dragover', (e) => { e.preventDefault(); area.classList.add('dragover'); });
    area.addEventListener('dragleave', () => area.classList.remove('dragover'));
    area.addEventListener('drop', (e) => {
        e.preventDefault(); area.classList.remove('dragover');
        if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
    });
    input.addEventListener('change', (e) => {
        if (e.target.files.length) handleFile(e.target.files[0]);
    });
}

function handleFile(file) {
    if (!file.type.startsWith('image/')) { alert('Please select an image file'); return; }
    currentFile = file;
    currentSamplePath = null;
    // Clear sample selection
    document.querySelectorAll('.sample-card').forEach(c => c.classList.remove('selected'));
    showSettingsAndAnalyze();
}

// ─── Samples ───
async function loadSamples() {
    try {
        const res = await fetch('/api/samples');
        const samples = await res.json();
        const grid = document.getElementById('samplesGrid');
        if (samples.length === 0) {
            grid.innerHTML = '<p style="color: var(--text-secondary); font-size: 0.85rem;">No sample images found.</p>';
            return;
        }
        grid.innerHTML = samples.map(s => `
            <div class="sample-card" onclick="selectSample('${s.path}', this)" data-path="${s.path}">
                <img src="${s.path}" alt="${s.name}" loading="lazy">
                <div class="sample-name">${s.name}</div>
            </div>
        `).join('');
    } catch (e) { console.error('Failed to load samples:', e); }
}

function selectSample(path, el) {
    currentSamplePath = path;
    currentFile = null;
    document.querySelectorAll('.sample-card').forEach(c => c.classList.remove('selected'));
    if (el) el.classList.add('selected');
    showSettingsAndAnalyze();
}

// ─── Auto Analyze ───
async function showSettingsAndAnalyze() {
    const panel = document.getElementById('settingsPanel');
    const banner = document.getElementById('analysisBanner');
    panel.style.display = 'block';
    banner.style.display = 'block';

    // Show analyzing state
    document.getElementById('analysisStatus').textContent = 'Analyzing...';
    document.getElementById('analysisDetails').innerHTML = '<em>Detecting image quality...</em>';

    banner.scrollIntoView({ behavior: 'smooth' });

    try {
        let res;
        if (currentFile) {
            const formData = new FormData();
            formData.append('image', currentFile);
            res = await fetch('/api/analyze', { method: 'POST', body: formData });
        } else {
            res = await fetch('/api/analyze-sample', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ samplePath: currentSamplePath }),
            });
        }

        const data = await res.json();
        if (data.error) {
            document.getElementById('analysisStatus').textContent = 'Failed';
            document.getElementById('analysisDetails').innerHTML = `Error: ${data.error}`;
            return;
        }

        autoSettings = data.settings;
        const a = data.analysis;

        // Display analysis
        document.getElementById('analysisStatus').textContent = 'Complete ✓';
        let tags = a.diagnosis.map(d => {
            const cls = d.includes('Low') || d.includes('Strong') || d.includes('blurry') ? 'warning' : (d.includes('reasonable') ? 'good' : '');
            return `<span class="analysis-tag ${cls}">${d}</span>`;
        }).join('');

        document.getElementById('analysisDetails').innerHTML = `
            ${tags}<br>
            <small style="color: var(--text-muted)">
                R: ${a.red_mean} · G: ${a.green_mean} · B: ${a.blue_mean} &nbsp;|&nbsp;
                Contrast: ${a.contrast} &nbsp;|&nbsp;
                Haze: ${a.haze_level} &nbsp;|&nbsp;
                Noise: ${a.noise_level}
            </small>
        `;

        // Apply auto settings
        applyAutoSettings(autoSettings);
        setActivePreset('auto');

    } catch (e) {
        console.error('Analysis failed:', e);
        document.getElementById('analysisStatus').textContent = 'Failed';
    }
}

function applyAutoSettings(s) {
    document.getElementById('noiseReduction').checked = s.noise_reduction;
    document.getElementById('noiseMethod').value = s.noise_method;
    document.getElementById('colorCorrection').checked = s.color_correction;
    document.getElementById('colorMethod').value = s.color_method;
    document.getElementById('redCompensation').checked = s.red_compensation;
    document.getElementById('dehazing').checked = s.dehazing;
    document.getElementById('dehazeOmega').value = s.dehaze_omega;
    document.getElementById('omegaValue').textContent = s.dehaze_omega;
    document.getElementById('contrastEnhancement').checked = s.contrast_enhancement;
    document.getElementById('contrastMethod').value = s.contrast_method;
    document.getElementById('claheClip').value = s.clahe_clip;
    document.getElementById('claheValue').textContent = s.clahe_clip;
    document.getElementById('sharpening').checked = s.sharpening;
    document.getElementById('sharpenMethod').value = s.sharpen_method;
    const str = s.unsharp_strength || 1.5;
    document.getElementById('sharpenStrength').value = str;
    document.getElementById('sharpenValue').textContent = str;
}

// ─── Sliders ───
function setupSliders() {
    const bind = (sid, did) => {
        const s = document.getElementById(sid), d = document.getElementById(did);
        if (s && d) s.addEventListener('input', () => d.textContent = s.value);
    };
    bind('dehazeOmega', 'omegaValue');
    bind('claheClip', 'claheValue');
    bind('sharpenStrength', 'sharpenValue');
}

// ─── Presets ───
function setActivePreset(name) {
    currentPreset = name;
    ['Auto', 'Mild', 'Strong', 'Custom'].forEach(p => {
        const btn = document.getElementById('preset' + p);
        if (btn) btn.classList.toggle('btn-active', p.toLowerCase() === name);
    });
}

function applyPreset(preset) {
    setActivePreset(preset);

    if (preset === 'auto' && autoSettings) {
        applyAutoSettings(autoSettings);
        return;
    }

    if (preset === 'custom') return; // user adjusts manually

    const sets = {
        mild: {
            noise_reduction: true, noise_method: 'bilateral',
            color_correction: true, color_method: 'gray_world', red_compensation: true,
            dehazing: true, dehaze_omega: 0.7,
            contrast_enhancement: true, contrast_method: 'clahe', clahe_clip: 2.0,
            sharpening: false, sharpen_method: 'unsharp', unsharp_strength: 1.0,
        },
        strong: {
            noise_reduction: true, noise_method: 'nlm',
            color_correction: true, color_method: 'histogram_stretch', red_compensation: true,
            dehazing: true, dehaze_omega: 1.0,
            contrast_enhancement: true, contrast_method: 'clahe', clahe_clip: 6.0,
            sharpening: true, sharpen_method: 'unsharp', unsharp_strength: 2.5,
        },
    };

    if (sets[preset]) applyAutoSettings(sets[preset]);
}

// ─── Gather Settings ───
function gatherSettings() {
    return {
        noise_reduction: document.getElementById('noiseReduction').checked,
        noise_method: document.getElementById('noiseMethod').value,
        color_correction: document.getElementById('colorCorrection').checked,
        color_method: document.getElementById('colorMethod').value,
        red_compensation: document.getElementById('redCompensation').checked,
        dehazing: document.getElementById('dehazing').checked,
        dehaze_omega: parseFloat(document.getElementById('dehazeOmega').value),
        contrast_enhancement: document.getElementById('contrastEnhancement').checked,
        contrast_method: document.getElementById('contrastMethod').value,
        clahe_clip: parseFloat(document.getElementById('claheClip').value),
        sharpening: document.getElementById('sharpening').checked,
        sharpen_method: document.getElementById('sharpenMethod').value,
        unsharp_strength: parseFloat(document.getElementById('sharpenStrength').value),
    };
}

// ─── Enhance ───
async function enhanceImage() {
    if (!currentFile && !currentSamplePath) { alert('Please select an image first'); return; }

    const btn = document.getElementById('enhanceBtn');
    btn.disabled = true;
    document.getElementById('loadingOverlay').style.display = 'flex';
    document.getElementById('loadingTitle').textContent = 'Enhancing your image...';
    document.getElementById('loadingSubtitle').textContent = 'Applying image processing techniques';

    const settings = gatherSettings();

    try {
        let res;
        if (currentFile) {
            const formData = new FormData();
            formData.append('image', currentFile);
            formData.append('settings', JSON.stringify(settings));
            res = await fetch('/api/enhance', { method: 'POST', body: formData });
        } else {
            res = await fetch('/api/enhance-sample', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ samplePath: currentSamplePath, settings }),
            });
        }

        const data = await res.json();
        if (data.error) { alert('Error: ' + data.error); return; }
        displayResults(data);
    } catch (e) { alert('Enhancement failed: ' + e.message); }
    finally {
        btn.disabled = false;
        document.getElementById('loadingOverlay').style.display = 'none';
    }
}

// ─── Display Results ───
function displayResults(data) {
    const section = document.getElementById('resultsSection');
    section.style.display = 'block';

    document.getElementById('originalImage').src = 'data:image/jpeg;base64,' + data.original;
    document.getElementById('enhancedImage').src = 'data:image/jpeg;base64,' + data.enhanced;
    enhancedDataUrl = 'data:image/jpeg;base64,' + data.enhanced;

    const m = data.metrics;
    document.getElementById('metricsGrid').innerHTML = `
        <div class="metric-card">
            <div class="metric-label">PSNR</div>
            <div class="metric-value">${m.psnr} dB</div>
            <div class="metric-detail">Peak Signal-to-Noise Ratio</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">SSIM</div>
            <div class="metric-value">${m.ssim}</div>
            <div class="metric-detail">Structural Similarity</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Colorfulness</div>
            <div class="metric-value ${m.colorfulness_after > m.colorfulness_before ? 'metric-improved' : ''}">${m.colorfulness_after}</div>
            <div class="metric-detail">Before: ${m.colorfulness_before}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Contrast</div>
            <div class="metric-value ${m.contrast_after > m.contrast_before ? 'metric-improved' : ''}">${m.contrast_after}</div>
            <div class="metric-detail">Before: ${m.contrast_before}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Entropy</div>
            <div class="metric-value">${m.entropy_after}</div>
            <div class="metric-detail">Before: ${m.entropy_before}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Processing Time</div>
            <div class="metric-value">${data.processing_time}s</div>
            <div class="metric-detail">Total pipeline time</div>
        </div>
    `;

    const stepNames = {
        noise_reduction: '🔇 Noise Reduction',
        color_correction: '🎨 Color Correction',
        dehazing: '🌫️ Dehazing',
        contrast_enhancement: '🔆 Contrast',
        sharpening: '🔍 Sharpening',
    };

    document.getElementById('stepsGrid').innerHTML = Object.entries(data.steps).map(([key, base64]) => `
        <div class="step-card" onclick="showModal('data:image/jpeg;base64,${base64}')">
            <img src="data:image/jpeg;base64,${base64}" alt="${stepNames[key] || key}">
            <div class="step-name">${stepNames[key] || key}</div>
        </div>
    `).join('');

    section.scrollIntoView({ behavior: 'smooth' });
}

// ─── Modal ───
function showModal(src) {
    const ov = document.createElement('div');
    ov.className = 'modal-overlay';
    ov.innerHTML = `<img src="${src}" alt="Full view">`;
    ov.addEventListener('click', () => ov.remove());
    document.body.appendChild(ov);
}

// ─── Download ───
function downloadEnhanced() {
    if (!enhancedDataUrl) return;
    const a = document.createElement('a');
    a.href = enhancedDataUrl;
    a.download = 'enhanced_underwater.jpg';
    a.click();
}

// ─── Reset ───
function resetAll() {
    currentFile = null; currentSamplePath = null; enhancedDataUrl = null; autoSettings = null;
    document.getElementById('fileInput').value = '';
    document.getElementById('settingsPanel').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('analysisBanner').style.display = 'none';
    document.querySelectorAll('.sample-card').forEach(c => c.classList.remove('selected'));
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
