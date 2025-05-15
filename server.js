const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3000;

// Middleware untuk menyajikan file statis dari folder 'uploads'
app.use('/uploads', express.static('uploads')); // <-- Tambahkan ini
app.use(express.static('public'));

// Setup Multer untuk menangani upload file
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'uploads/');
    },
    filename: function (req, file, cb) {
        cb(null, Date.now() + path.extname(file.originalname)); // Append extension
    }
});

const upload = multer({ storage: storage });

// Serve static files from the "public" directory
app.use(express.static('public'));

// Route untuk upload video
app.post('/upload', upload.single('video'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ message: 'No file uploaded' });
    }
    res.json({ message: 'File uploaded successfully!', file: req.file });
});

// Route untuk mengambil daftar video
app.get('/videos', (req, res) => {
    fs.readdir('uploads/', (err, files) => {
        if (err) {
            console.error("Error membaca folder uploads:", err); // <-- Debug error
            return res.status(500).json({ error: 'Gagal membaca file' });
        }
        // Filter hanya file video (contoh: .mp4)
        const videoFiles = files.filter(file => {
            const ext = path.extname(file).toLowerCase();
            return ['.mp4', '.mov', '.avi'].includes(ext);
        });
        res.json({ files: videoFiles });
    });
});

// Jalankan server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});