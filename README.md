# Smart Traffic Bandung - Fullstack System

Sistem monitoring lalu lintas real-time untuk Bandung yang mengintegrasikan backend Python FastAPI dengan frontend React JS. Menggunakan data CCTV dari API Bandung dan AI detection dengan YOLO untuk mendeteksi kendaraan.

## 🚀 Fitur Utama

### Backend (Python FastAPI)
- ✅ Fetch data CCTV dari API Bandung secara real-time
- ✅ Deteksi kendaraan menggunakan YOLO v8
- ✅ Analisis status traffic (LANCAR/PADAT/MACET)
- ✅ Database MySQL untuk menyimpan history
- ✅ REST API dengan dokumentasi Swagger
- ✅ CORS enabled untuk React frontend

### Frontend (React JS + Vite)
- ✅ Dashboard modern dengan Tailwind CSS
- ✅ Live streaming video HLS
- ✅ Interactive map dengan Leaflet
- ✅ Real-time traffic status display
- ✅ Auto-refresh data setiap 5 detik
- ✅ Responsive design (mobile & desktop)
- ✅ Vehicle count breakdown (mobil, motor, bus, truk)

## 📋 Struktur Project

```
tugas-smartcity/
├── backend/
│   ├── app/
│   │   ├── main.py              # Entry point FastAPI
│   │   ├── config.py            # Settings & configuration
│   │   ├── routes/
│   │   │   ├── cctv.py         # CCTV endpoints
│   │   │   ├── analysis.py     # Traffic analysis endpoints
│   │   │   └── health.py       # Health check
│   │   ├── services/
│   │   │   ├── cctv_service.py      # CCTV API integration
│   │   │   └── database_service.py  # Database operations
│   │   ├── ai/
│   │   │   └── yolo_detector.py     # YOLO detection engine
│   │   └── models/
│   │       ├── database.py      # SQLAlchemy models
│   │       └── schemas.py       # Pydantic schemas
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── main.jsx             # React entry point
│   │   ├── pages/
│   │   │   └── Dashboard.jsx    # Main dashboard page
│   │   ├── components/
│   │   │   ├── VideoStream.jsx      # Video streaming component
│   │   │   ├── TrafficStatusPanel.jsx  # Status display
│   │   │   ├── MapView.jsx         # Interactive map
│   │   │   └── CCTVList.jsx        # CCTV list
│   │   ├── services/
│   │   │   └── api.js           # API client with axios
│   │   └── styles/
│   │       └── index.css        # Global styles
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
└── README.md
```

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- MySQL 8.0+
- pip, npm

### Backend Setup

1. **Buka terminal di folder backend**
```bash
cd tugas-smartcity/backend
```

2. **Buat virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# atau
venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variable**
```bash
cp .env.example .env
```

Edit file `.env` dan sesuaikan dengan konfigurasi MySQL Anda:
```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=smart_traffic_bandung
MYSQL_PORT=3306

API_PORT=8000
BANDUNG_API_URL=https://pelindung.bandung.go.id:8443/api/cek
```

5. **Setup MySQL Database**
```bash
# Login ke MySQL
mysql -u root -p

# Buat database
CREATE DATABASE smart_traffic_bandung;
EXIT;
```

6. **Jalankan backend**
```bash
# Development mode (reload otomatis)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend akan berjalan di **http://localhost:8000**

API documentation tersedia di **http://localhost:8000/docs**

### Frontend Setup

1. **Buka terminal baru di folder frontend**
```bash
cd tugas-smartcity/frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Jalankan development server**
```bash
npm run dev
```

Frontend akan berjalan di **http://localhost:5173**

## 🔌 API Endpoints

### CCTV Endpoints

**GET /cctv**
- Fetch semua CCTV dari API Bandung
- Response: List CCTV dengan lokasi dan stream URL
```json
[
  {
    "id": 1,
    "cctv_name": "CCTV Pendopo",
    "lat": -6.9147,
    "lng": 107.6098,
    "stream_cctv": "http://..../stream.m3u8",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

**GET /cctv/{cctv_id}**
- Get detail CCTV by ID

### Traffic Analysis Endpoints

**GET /analyze/{cctv_id}**
- Analyze traffic dari CCTV tertentu
- Response:
```json
{
  "cctv_name": "CCTV Pendopo",
  "cctv_id": "1",
  "vehicle_count": 35,
  "status": "LANCAR",
  "car_count": 20,
  "motorcycle_count": 12,
  "bus_count": 2,
  "truck_count": 1,
  "confidence_score": 0.87,
  "timestamp": "2024-01-01T10:30:00"
}
```

**GET /analyze/history/{cctv_id}?hours=24**
- Get traffic analysis history

**GET /analyze/latest**
- Get latest traffic status untuk semua CCTV

### Health Check

**GET /health**
- Service health check status

## 🎓 Cara Menggunakan

### 1. Lihat Dashboard
Buka browser ke **http://localhost:5173**

### 2. Pilih CCTV
- Klik CCTV di sidebar atau marker di map
- Video stream akan otomatis diputar
- Analisis traffic akan dimulai

### 3. Monitoring Traffic
- **Hijau (LANCAR)**: ≤ 40 kendaraan
- **Kuning (PADAT)**: 40-70 kendaraan  
- **Merah (MACET)**: > 70 kendaraan

### 4. Auto Refresh
- Aktifkan "Auto Refresh" untuk update setiap 5 detik
- Manual refresh dengan button "Analyze Now"

## 🔍 Traffic Status Logic

```
if vehicle_count > 70:
    status = "MACET" (RED)
elif vehicle_count >= 40:
    status = "PADAT" (YELLOW)
else:
    status = "LANCAR" (GREEN)
```

## 🤖 AI Detection

Sistem menggunakan YOLO v8 Nano untuk:
- Deteksi kendaraan dari video stream
- Klasifikasi tipe kendaraan:
  - Car (mobil)
  - Motorcycle (motor)
  - Bus
  - Truck (truk)

Frame di-capture setiap 2 detik, dan rata-rata dihitung untuk hasil akurat.

## 🗄️ Database Schema

### CCTV Table
```sql
CREATE TABLE cctvs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cctv_id VARCHAR(100) UNIQUE,
    cctv_name VARCHAR(255),
    lat FLOAT,
    lng FLOAT,
    stream_url TEXT,
    dinas VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Traffic Analysis Table
```sql
CREATE TABLE traffic_analysis (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cctv_id VARCHAR(100),
    cctv_name VARCHAR(255),
    vehicle_count INT,
    car_count INT,
    motorcycle_count INT,
    bus_count INT,
    truck_count INT,
    status VARCHAR(20),
    confidence_score FLOAT,
    created_at TIMESTAMP
);
```

## 🐛 Troubleshooting

### Backend Error: "Cannot open stream"
- **Solusi**: Check API Bandung masih aktif. Coba ping https://pelindung.bandung.go.id:8443/api/cek

### Frontend tidak bisa connect ke backend
- **Solusi**: 
  - Pastikan backend running di http://localhost:8000
  - Check CORS setting di `.env`
  - Browser console untuk error message

### YOLO Model slow/error
- **Solusi**: 
  - Download ulang model: `from ultralytics import YOLO; YOLO("yolov8n.pt")`
  - Gunakan model nano (yolov8n.pt) untuk performa optimal
  - Pastikan GPU support jika tersedia

### MySQL Connection Error
- **Solusi**:
  - Pastikan MySQL service running
  - Check credentials di `.env`
  - Buat database terlebih dahulu

## 🎯 Optional Features (Bonus)

Sudah terimplementasi:
- ✅ Database history
- ✅ Chart-ready data structure
- ✅ Responsive design
- ✅ Auto-refresh dengan polling

Bisa ditambahkan:
- 🔲 WebSocket untuk real-time tanpa polling
- 🔲 Alert notification (email/SMS saat MACET)
- 🔲 Dashboard grafik dengan Chart.js
- 🔲 Export report
- 🔲 User authentication

## 📊 Performance Tips

1. **Reduce Frame Interval**: Ubah `frame_interval=2` di backend jadi lebih besar untuk performa lebih cepat
2. **Cache Results**: Backend sudah cache 30 detik
3. **Model Size**: Gunakan yolov8n.pt (nano) untuk performa optimal
4. **Database**: Add index ke `traffic_analysis.cctv_id` untuk query lebih cepat

## 📚 Dependencies

### Backend
- FastAPI: Web framework
- OpenCV: Video processing
- YOLO: Object detection
- SQLAlchemy: ORM
- MySQL Connector: Database driver

### Frontend
- React: UI library
- Vite: Build tool
- Tailwind CSS: Styling
- Axios: HTTP client
- Leaflet: Maps
- HLS.js: Video streaming

## 🤝 Contributing

Untuk development lebih lanjut:
1. Fork project
2. Buat feature branch
3. Commit changes
4. Push ke branch
5. Buat Pull Request

## 📝 License

MIT License - Bebas digunakan untuk tujuan apapun

## 👨‍💻 Author

Smart Traffic Bandung - Real-time Traffic Monitoring System

---

**Catatan**: Project ini menggunakan data CCTV publik dari API Bandung. Pastikan selalu mengikuti terms of service dari API tersebut.
