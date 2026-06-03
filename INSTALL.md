# 🚦 Smart Traffic Bandung - Installation & Run Guide

## 📋 Prerequisites

Pastikan Anda sudah install:
- **Python 3.9+** - https://python.org
- **Node.js 18+** - https://nodejs.org
- **MySQL 8.0+** - https://dev.mysql.com/downloads/
- **Git** (optional) - https://git-scm.com

## ⚙️ Instalasi Step-by-Step

### 1️⃣ Persiapan Database

```bash
# Login ke MySQL
mysql -u root -p

# Create database
CREATE DATABASE smart_traffic_bandung;

# Verify
SHOW DATABASES;
SHOW CREATE DATABASE smart_traffic_bandung;

# Exit
EXIT;
```

### 2️⃣ Setup Backend

**Terminal 1:**
```bash
# Navigate ke backend
cd tugas-smartcity/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup .env
cp .env.example .env

# Edit .env if needed (opsional jika default sudah sesuai)
# nano .env  (macOS/Linux)
# notepad .env  (Windows)

# Start backend server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend akan berjalan di: **http://localhost:8000**
✅ API Docs di: **http://localhost:8000/docs**

### 3️⃣ Setup Frontend

**Terminal 2 (baru):**
```bash
# Navigate ke frontend
cd tugas-smartcity/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

✅ Frontend akan berjalan di: **http://localhost:5173**

### 4️⃣ Buka Dashboard

**Browser:**
```
http://localhost:5173
```

Dashboard siap digunakan! 🎉

---

## 🚀 Quick Start (otomatis)

Jika ingin semua setup otomatis:

### macOS/Linux:
```bash
cd tugas-smartcity

# Make script executable
chmod +x setup.sh

# Run setup
./setup.sh

# Kemudian jalankan services
chmod +x start.sh
./start.sh
```

### Windows:
```bash
cd tugas-smartcity

# Run setup batch file
setup.bat

# Kemudian jalankan services
start.bat
```

---

## 🐳 Docker Setup (Alternative)

Jika sudah install Docker:

```bash
# Navigate ke project root
cd tugas-smartcity

# Build dan start semua services
docker-compose up -d

# Tunggu ~30 detik untuk database ready

# Akses services
Frontend: http://localhost:5173
Backend: http://localhost:8000
API Docs: http://localhost:8000/docs

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

---

## ✅ Verify Installation

### Check Backend

```bash
# Terminal:
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","service":"Smart Traffic Bandung API"}
```

### Check Frontend

Buka browser: http://localhost:5173
Seharusnya melihat dashboard dengan map dan CCTV list.

### Check Database

```bash
mysql -u root -p
USE smart_traffic_bandung;
SHOW TABLES;
# Seharusnya ada: cctvs, traffic_analysis
```

---

## 🔧 Configuration

### Backend (.env)

Jika perlu customize, edit `backend/.env`:

```env
# Database connection
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=smart_traffic_bandung
MYSQL_PORT=3306

# API Server
API_PORT=8000

# API Bandung
BANDUNG_API_URL=https://pelindung.bandung.go.id:8443/api/cek

# Frontend CORS
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# AI Configuration
CONFIDENCE_THRESHOLD=0.5
VEHICLE_CLASSES=["car", "motorcycle", "bus", "truck"]

# Traffic Status Thresholds (LANCAR < 40, PADAT 40-70, MACET > 70)
LANCAR_THRESHOLD=40
PADAT_THRESHOLD=70
```

---

## 🎯 Usage

### Dashboard Features

1. **📍 Map View**
   - Menampilkan semua CCTV di peta
   - Klik marker untuk select CCTV
   - Warna marker menunjukkan status

2. **📸 CCTV List**
   - List semua CCTV yang tersedia
   - Click untuk select dan analyze
   - Auto update status setiap 10 detik

3. **📹 Live Stream**
   - Real-time video dari CCTV
   - Autoplay saat CCTV dipilih
   - Support HLS format (.m3u8)

4. **📊 Traffic Analysis**
   - Jumlah kendaraan terdeteksi
   - Status lalu lintas (Hijau/Kuning/Merah)
   - Breakdown per jenis kendaraan
   - Confidence score

5. **🔄 Auto Refresh**
   - Toggle untuk auto update setiap 5 detik
   - Manual update dengan button "Analyze Now"

### Traffic Status Meaning

- 🟢 **LANCAR** (Green): < 40 kendaraan
- 🟡 **PADAT** (Yellow): 40-70 kendaraan
- 🔴 **MACET** (Red): > 70 kendaraan

---

## 🐛 Troubleshooting

### Problem: "Cannot connect to MySQL"

```bash
# Solution: Check if MySQL running
# macOS:
mysql.server start

# Linux:
sudo systemctl start mysql

# Windows: Start MySQL service from Services
```

### Problem: "Port 8000 already in use"

```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use different port:
python -m uvicorn app.main:app --port 8001
```

### Problem: "YOLO model not found"

```bash
# Download model manually
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

# This will download ~6MB model
```

### Problem: "No CCTV data showing"

```bash
# Check API Bandung connectivity
curl https://pelindung.bandung.go.id:8443/api/cek

# If error, API might be down. Try with mock data:
# Edit backend/app/routes/cctv.py and use mock_data
```

### Problem: "Video not playing"

- Check if stream URL is valid (try in VLC)
- Check if m3u8 file is accessible
- Check browser console for HLS errors

---

## 📊 API Endpoints

### CCTV Management
```bash
# Get all CCTV
GET /cctv

# Get CCTV detail
GET /cctv/{id}

# Analyze CCTV
GET /analyze/{id}

# Get history
GET /analyze/history/{id}?hours=24

# Get latest for all
GET /analyze/latest
```

Lihat [API_TESTING.md](API_TESTING.md) untuk detail lengkap.

---

## 🛑 Stopping Services

### Manual Stop

```bash
# Terminal 1 (Backend): Ctrl+C
# Terminal 2 (Frontend): Ctrl+C
# Terminal 3 (MySQL): mysql.server stop  (macOS)
```

### Docker Stop

```bash
docker-compose down
```

---

## 📚 Additional Resources

- [Full README](README.md) - Complete documentation
- [API Testing](API_TESTING.md) - API examples
- [Quick Reference](QUICK_REFERENCE.md) - Commands cheatsheet
- [Setup Guide](setup.md) - Database setup details
- [Docker Guide](DOCKER.md) - Docker instructions

---

## ✨ Features

### Backend ✅
- ✅ Fetch CCTV dari API Bandung
- ✅ YOLO v8 AI detection
- ✅ MySQL database
- ✅ RESTful API dengan Swagger docs
- ✅ CORS enabled
- ✅ Error handling & logging
- ✅ Database caching

### Frontend ✅
- ✅ Modern React dashboard
- ✅ Interactive Leaflet map
- ✅ HLS video streaming
- ✅ Real-time traffic status
- ✅ Auto-refresh polling
- ✅ Vehicle breakdown
- ✅ Responsive design
- ✅ Tailwind CSS styling

---

## 🎓 Next Steps

1. **Explore API** - Cek http://localhost:8000/docs
2. **Monitor Dashboard** - Lihat traffic in real-time
3. **Check History** - Lihat traffic trends
4. **Customize** - Edit thresholds di .env
5. **Deploy** - Gunakan Docker untuk production

---

## 📞 Support

Jika ada masalah:
1. Check logs di terminal
2. Lihat section Troubleshooting
3. Check API connectivity
4. Verify semua services running
5. Check .env configuration

---

**Happy Monitoring! 🚦**

Version: 1.0.0
Last Updated: 2024
