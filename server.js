const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3333;

const UPLOADS = path.join(__dirname, 'uploads');
if (!fs.existsSync(UPLOADS)) fs.mkdirSync(UPLOADS);

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, UPLOADS);
  },
  filename: function (req, file, cb) {
    const address = (req.body.address || req.body.addr || req.query.address || 'unknown').replace(/[^a-zA-Z0-9_.-]/g, '_');
    cb(null, `${address}${path.extname(file.originalname) || '.jpg'}`);
  }
});
const upload = multer({ storage });

app.use('/uploads', express.static(UPLOADS));

// Upload avatar endpoint (keeps existing backend untouched)
app.post('/api/upload-avatar', upload.single('avatar'), (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'No file uploaded' });
  const address = req.body.address || req.body.addr || 'unknown';
  const url = `${req.protocol}://${req.get('host')}/uploads/${req.file.filename}`;
  return res.json({ address, url });
});

// Get avatar metadata for an address
app.get('/api/avatar/:address', (req, res) => {
  const address = req.params.address.replace(/[^a-zA-Z0-9_.-]/g, '_');
  const files = fs.readdirSync(UPLOADS).filter((f) => f.startsWith(address));
  if (files.length === 0) return res.status(404).json({ error: 'Not found' });
  const file = files[0];
  const url = `${req.protocol}://${req.get('host')}/uploads/${file}`;
  res.json({ address: req.params.address, url });
});

app.get('/', (req, res) => res.send('Axion local backend (avatars)'));

app.listen(PORT, () => console.log(`Backend running on http://localhost:${PORT}`));
