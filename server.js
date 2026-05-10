const express = require('express');
const multer = require('multer');
const path = require('path');
const { execFile } = require('child_process');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 7860;

app.use(express.static('public'));
app.use(express.json({ limit: '50mb' }));

const upload = multer({
    dest: 'uploads/',
    limits: { fileSize: 20 * 1024 * 1024 },
    fileFilter: (req, file, cb) => {
        const ext = path.extname(file.originalname).toLowerCase();
        if (['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'].includes(ext)) {
            cb(null, true);
        } else {
            cb(new Error('Only image files are allowed'));
        }
    }
});

['uploads', 'sample_images'].forEach(dir => {
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
});

// Sample images
app.get('/api/samples', (req, res) => {
    const samplesDir = path.join(__dirname, 'sample_images');
    if (!fs.existsSync(samplesDir)) return res.json([]);
    const files = fs.readdirSync(samplesDir)
        .filter(f => /\.(jpg|jpeg|png|bmp|webp)$/i.test(f))
        .map(f => ({
            name: f.replace(/\.[^.]+$/, '').replace(/[_-]/g, ' '),
            path: `/sample_images/${f}`
        }));
    res.json(files);
});

app.use('/sample_images', express.static('sample_images'));

// Auto-analyze image (uploaded file)
app.post('/api/analyze', upload.single('image'), (req, res) => {
    if (!req.file) return res.status(400).json({ error: 'No image' });
    const imagePath = path.resolve(req.file.path);
    const python = process.platform === 'win32' ? 'python' : 'python3';

    execFile(python, [
        path.join(__dirname, 'app.py'), '--analyze', imagePath
    ], { maxBuffer: 10 * 1024 * 1024 }, (error, stdout, stderr) => {
        try { fs.unlinkSync(imagePath); } catch (e) { }
        if (error) return res.status(500).json({ error: 'Analysis failed', details: stderr });
        try { res.json(JSON.parse(stdout)); }
        catch (e) { res.status(500).json({ error: 'Parse error' }); }
    });
});

// Auto-analyze sample image
app.post('/api/analyze-sample', express.json(), (req, res) => {
    const fullPath = path.join(__dirname, req.body.samplePath);
    if (!fs.existsSync(fullPath)) return res.status(404).json({ error: 'Not found' });
    const python = process.platform === 'win32' ? 'python' : 'python3';

    execFile(python, [
        path.join(__dirname, 'app.py'), '--analyze', fullPath
    ], { maxBuffer: 10 * 1024 * 1024 }, (error, stdout, stderr) => {
        if (error) return res.status(500).json({ error: 'Analysis failed', details: stderr });
        try { res.json(JSON.parse(stdout)); }
        catch (e) { res.status(500).json({ error: 'Parse error' }); }
    });
});

// Enhance uploaded image
app.post('/api/enhance', upload.single('image'), (req, res) => {
    if (!req.file) return res.status(400).json({ error: 'No image uploaded' });
    const imagePath = path.resolve(req.file.path);
    const settings = req.body.settings ? JSON.parse(req.body.settings) : {};
    const python = process.platform === 'win32' ? 'python' : 'python3';

    execFile(python, [
        path.join(__dirname, 'app.py'), imagePath, JSON.stringify(settings)
    ], { maxBuffer: 100 * 1024 * 1024 }, (error, stdout, stderr) => {
        try { fs.unlinkSync(imagePath); } catch (e) { }
        if (error) return res.status(500).json({ error: 'Processing failed', details: stderr });
        try { res.json(JSON.parse(stdout)); }
        catch (e) { res.status(500).json({ error: 'Failed to parse result' }); }
    });
});

// Enhance sample image
app.post('/api/enhance-sample', express.json(), (req, res) => {
    const { samplePath, settings } = req.body;
    const fullPath = path.join(__dirname, samplePath);
    if (!fs.existsSync(fullPath)) return res.status(404).json({ error: 'Sample not found' });
    const python = process.platform === 'win32' ? 'python' : 'python3';

    execFile(python, [
        path.join(__dirname, 'app.py'), fullPath, JSON.stringify(settings || {})
    ], { maxBuffer: 100 * 1024 * 1024 }, (error, stdout, stderr) => {
        if (error) return res.status(500).json({ error: 'Processing failed', details: stderr });
        try { res.json(JSON.parse(stdout)); }
        catch (e) { res.status(500).json({ error: 'Failed to parse result' }); }
    });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`🌊 AquaClear server running at http://localhost:${PORT}`);
});
