# Database dan Setup Guide

## MySQL Database Setup

### 1. Buat Database
```sql
CREATE DATABASE smart_traffic_bandung;
USE smart_traffic_bandung;
```

### 2. Schema Tables

Tabel `cctvs`:
```sql
CREATE TABLE cctvs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cctv_id VARCHAR(100) UNIQUE NOT NULL INDEX,
    cctv_name VARCHAR(255) NOT NULL,
    lat FLOAT NOT NULL,
    lng FLOAT NOT NULL,
    stream_url TEXT,
    dinas VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

Tabel `traffic_analysis`:
```sql
CREATE TABLE traffic_analysis (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cctv_id VARCHAR(100) NOT NULL INDEX,
    cctv_name VARCHAR(255),
    vehicle_count INT NOT NULL,
    car_count INT DEFAULT 0,
    motorcycle_count INT DEFAULT 0,
    bus_count INT DEFAULT 0,
    truck_count INT DEFAULT 0,
    status VARCHAR(20),
    confidence_score FLOAT,
    frame_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP INDEX
);
```

### 3. Create Indexes untuk Performance
```sql
CREATE INDEX idx_cctv_analysis ON traffic_analysis(cctv_id, created_at);
CREATE INDEX idx_analysis_timestamp ON traffic_analysis(created_at DESC);
```

## Environment Configuration

Copy `.env.example` menjadi `.env`:

```bash
cp .env.example .env
```

Edit sesuai konfigurasi lokal Anda:
```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=smart_traffic_bandung
MYSQL_PORT=3306

API_PORT=8000
BANDUNG_API_URL=https://pelindung.bandung.go.id:8443/api/cek

# Frontend CORS origins
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# AI Configuration
CONFIDENCE_THRESHOLD=0.5
VEHICLE_CLASSES=["car", "motorcycle", "bus", "truck"]

# Traffic Status Thresholds
LANCAR_THRESHOLD=40      # < 40 kendaraan = LANCAR
PADAT_THRESHOLD=70       # 40-70 kendaraan = PADAT (> 70 = MACET)
```

## Running Services

### Terminal 1: MySQL
```bash
# macOS dengan Homebrew
brew services start mysql

# Atau manual
mysql.server start
```

### Terminal 2: Backend
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 3: Frontend
```bash
cd frontend
npm run dev
```

Akses aplikasi di: http://localhost:5173

## Testing API

### Health Check
```bash
curl http://localhost:8000/health
```

### Get All CCTV
```bash
curl http://localhost:8000/cctv
```

### Analyze Traffic
```bash
curl http://localhost:8000/analyze/{cctv_id}
```

### Get Latest Analysis
```bash
curl http://localhost:8000/analyze/latest
```

## Database Queries Examples

### Get Latest Traffic Status per CCTV
```sql
SELECT 
    t1.* 
FROM traffic_analysis t1
WHERE (t1.cctv_id, t1.created_at) IN (
    SELECT cctv_id, MAX(created_at)
    FROM traffic_analysis
    GROUP BY cctv_id
);
```

### Get Traffic History Last 24 Hours
```sql
SELECT 
    cctv_name,
    DATE(created_at) as date,
    HOUR(created_at) as hour,
    AVG(vehicle_count) as avg_vehicles,
    MAX(vehicle_count) as max_vehicles,
    status
FROM traffic_analysis
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY cctv_name, DATE(created_at), HOUR(created_at)
ORDER BY created_at DESC;
```

### Get Peak Hours
```sql
SELECT 
    cctv_name,
    HOUR(created_at) as hour,
    AVG(vehicle_count) as avg_vehicles
FROM traffic_analysis
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY cctv_name, HOUR(created_at)
ORDER BY avg_vehicles DESC;
```

## Backup & Restore

### Backup Database
```bash
mysqldump -u root -p smart_traffic_bandung > smart_traffic_bandung_backup.sql
```

### Restore Database
```bash
mysql -u root -p smart_traffic_bandung < smart_traffic_bandung_backup.sql
```
