// index.js - Complete Standalone Version
const http = require('http');
const fs = require('fs');
const path = require('path');
const querystring = require('querystring');

// ======================
// 🛠 CONFIGURATION
// ======================
const PORT = 3000;
const UPLOAD_DIR = './uploads';
const GALLERY_DIR = './gallery';

// Create directories if they don't exist
[UPLOAD_DIR, GALLERY_DIR].forEach(dir => {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
});

// ======================
// 🌟 EXPRESS-LIKE SERVER
// ======================
const server = http.createServer(async (req, res) => {
  // Route handler
  const route = req.url.split('?')[0];
  const params = querystring.parse(req.url.split('?')[1]);

  try {
    // 🖼️ Image Upload
    if (route === '/upload' && req.method === 'POST') {
      let body = '';
      req.on('data', chunk => body += chunk);
      req.on('end', () => {
        const base64Data = body.replace(/^data:image\/\w+;base64,/, '');
        const filename = `muller-${Date.now()}.jpg`;
        fs.writeFileSync(path.join(UPLOAD_DIR, filename), base64Data, 'base64');
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
          success: true, 
          url: `/image/${filename}` 
        }));
      });
      return;
    }

    // 🏞️ Gallery List
    if (route === '/api/gallery' && req.method === 'GET') {
      const files = fs.readdirSync(GALLERY_DIR).filter(f => 
        ['.jpg','.jpeg','.png'].includes(path.extname(f).toLowerCase())
      );
      
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(files.map(f => ({
        name: path.basename(f, path.extname(f)),
        url: `/gallery/${f}`
      }))));
      return;
    }

    // 📜 Serve Image Files
    if (route.startsWith('/image/') || route.startsWith('/gallery/')) {
      const dir = route.startsWith('/image/') ? UPLOAD_DIR : GALLERY_DIR;
      const filepath = path.join(dir, route.split('/').pop());
      
      if (fs.existsSync(filepath)) {
        const image = fs.readFileSync(filepath);
        res.writeHead(200, { 'Content-Type': 'image/jpeg' });
        res.end(image, 'binary');
      } else {
        res.writeHead(404);
        res.end('Image not found');
      }
      return;
    }

    // Default response
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>MULLER SUSPENDER X1</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 40px; }
          .upload-box { border: 2px dashed #ccc; padding: 20px; text-align: center; }
        </style>
      </head>
      <body>
        <h1>MULLER SUSPENDER X1 Image Server</h1>
        <div class="upload-box">
          <h3>🖼️ Image Upload</h3>
          <input type="file" id="imageInput" accept="image/*">
          <button onclick="uploadImage()">Upload</button>
          <div id="result"></div>
        </div>
        <script>
          async function uploadImage() {
            const file = document.getElementById('imageInput').files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = async (e) => {
              const res = await fetch('/upload', {
                method: 'POST',
                body: e.target.result
              });
              const data = await res.json();
              document.getElementById('result').innerHTML = 
                \`<p>Uploaded: <a href="\${data.url}" target="_blank">View</a></p>\`;
            };
            reader.readAsDataURL(file);
          }
        </script>
      </body>
      </html>
    `);

  } catch (err) {
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: err.message }));
  }
});

// ======================
// 🚀 START SERVER
// ======================
server.listen(PORT, () => {
  console.log(`
  ███╗   ███╗██╗   ██╗██╗     ██╗  ██╗███████╗
  ████╗ ████║██║   ██║██║     ██║  ██║██╔════╝
  ██╔████╔██║██║   ██║██║     ███████║█████╗  
  ██║╚██╔╝██║██║   ██║██║     ██╔══██║██╔══╝  
  ██║ ╚═╝ ██║╚██████╔╝███████╗██║  ██║███████╗
  ╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝
  SUSPENDER X1 Image Server running on port ${PORT}
  `);
  console.log(`📁 Uploads: ${path.resolve(UPLOAD_DIR)}`);
  console.log(`🖼️ Gallery: ${path.resolve(GALLERY_DIR)}`);
});
