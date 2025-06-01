// index.js - MULLER SUSPENDER X1 Complete Image System
const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const { createWorker } = require('tesseract.js');
const sharp = require('sharp');
const app = express();
const port = process.env.PORT || 3000;

// Configuration
const UPLOAD_DIR = './uploads';
const GALLERY_DIR = './gallery';
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/gif'];

// Ensure directories exist
[UPLOAD_DIR, GALLERY_DIR].forEach(dir => {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
});

// Multer setup for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOAD_DIR),
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname);
    cb(null, `muller-${Date.now()}${ext}`);
  }
});

const upload = multer({ 
  storage,
  fileFilter: (req, file, cb) => {
    cb(null, ALLOWED_TYPES.includes(file.mimetype));
  }
});

// ======================
// 🖼️ IMAGE ROUTES
// ======================

// 1. Upload Endpoint
app.post('/upload', upload.single('image'), (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'No image uploaded' });
  
  res.json({ 
    success: true,
    url: `/images/${req.file.filename}`,
    preview: `/api/preview/${req.file.filename}?size=300`
  });
});

// 2. Gallery Endpoint
app.get('/api/gallery', (req, res) => {
  fs.readdir(GALLERY_DIR, (err, files) => {
    if (err) return res.status(500).json({ error: err.message });
    
    const images = files.filter(f => 
      ['.jpg', '.jpeg', '.png', '.gif'].includes(path.extname(f).toLowerCase())
    ).map(img => ({
      name: path.basename(img, path.extname(img)),
      url: `/gallery/${img}`,
      thumb: `/api/thumb/${img}`
    }));
    
    res.json(images);
  });
});

// 3. OCR Endpoint
app.post('/api/ocr', upload.single('image'), async (req, res) => {
  const worker = await createWorker('eng');
  const { data: { text } } = await worker.recognize(req.file.path);
  await worker.terminate();
  
  res.json({ text });
});

// 4. Filter Endpoint
app.get('/api/filter', async (req, res) => {
  const { image, filter } = req.query;
  const validFilters = ['blur', 'grayscale', 'invert', 'sepia'];
  
  if (!validFilters.includes(filter)) {
    return res.status(400).json({ error: 'Invalid filter' });
  }

  try {
    let processor = sharp(path.join(UPLOAD_DIR, image));
    
    switch(filter) {
      case 'blur': processor = processor.blur(5); break;
      case 'grayscale': processor = processor.grayscale(); break;
      case 'invert': processor = processor.negate(); break;
      case 'sepia': processor = processor.modulate({
        saturation: 0.5,
        brightness: 0.8
      }); break;
    }
    
    res.set('Content-Type', 'image/jpeg');
    return processor.jpeg().pipe(res);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ======================
// 🖼️ IMAGE PROCESSING
// ======================

// Thumbnail Generator
app.get('/api/thumb/:image', (req, res) => {
  sharp(path.join(GALLERY_DIR, req.params.image))
    .resize(200, 200)
    .toBuffer()
    .then(data => {
      res.set('Content-Type', 'image/jpeg');
      res.send(data);
    })
    .catch(err => res.status(404).send('Image not found'));
});

// Preview Generator
app.get('/api/preview/:image', (req, res) => {
  const size = parseInt(req.query.size) || 300;
  
  sharp(path.join(UPLOAD_DIR, req.params.image))
    .resize(size)
    .toBuffer()
    .then(data => {
      res.set('Content-Type', 'image/jpeg');
      res.send(data);
    })
    .catch(err => res.status(404).send('Image not found'));
});

// ======================
// 🚀 SERVER START
// ======================
app.use('/images', express.static(UPLOAD_DIR));
app.use('/gallery', express.static(GALLERY_DIR));

app.listen(port, () => {
  console.log(`MULLER SUSPENDER X1 Image Server running on port ${port}`);
  console.log(`📁 Uploads: ${path.resolve(UPLOAD_DIR)}`);
  console.log(`🖼️ Gallery: ${path.resolve(GALLERY_DIR)}`);
});
