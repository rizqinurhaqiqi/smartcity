# Smart Traffic Bandung - Quick Reference

## Directory Structure

```
tugas-smartcity/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # Entry point
│   │   ├── config.py          # Settings
│   │   ├── routes/
│   │   │   ├── cctv.py
│   │   │   ├── analysis.py
│   │   │   └── health.py
│   │   ├── services/
│   │   │   ├── cctv_service.py
│   │   │   └── database_service.py
│   │   ├── ai/
│   │   │   └── yolo_detector.py
│   │   └── models/
│   │       ├── database.py
│   │       └── schemas.py
│   ├── requirements.txt
│   ├── .env
│   ├── .gitignore
│   └── Dockerfile
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── main.jsx
│   │   ├── pages/
│   │   │   └── Dashboard.jsx
│   │   ├── components/
│   │   │   ├── VideoStream.jsx
│   │   │   ├── TrafficStatusPanel.jsx
│   │   │   ├── MapView.jsx
│   │   │   └── CCTVList.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   └── styles/
│   │       └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── .gitignore
│   └── Dockerfile
├── docker-compose.yml
├── setup.sh
├── setup.bat
├── start.sh
├── README.md
├── setup.md
├── API_TESTING.md
└── DOCKER.md
```

## Commands Cheatsheet

### Backend

```bash
# Setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Development
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Interactive shell
python -c "from app.config import settings; print(settings.DATABASE_URL)"
```

### Frontend

```bash
# Setup
cd frontend
npm install

# Development
npm run dev

# Build
npm run build

# Preview
npm run preview
```

### Database

```bash
# Connect to MySQL
mysql -u root -p

# List databases
SHOW DATABASES;

# Use database
USE smart_traffic_bandung;

# List tables
SHOW TABLES;

# View structure
DESCRIBE cctvs;
DESCRIBE traffic_analysis;
```

### Docker

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Rebuild images
docker-compose build --no-cache
```

## Key URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| API ReDoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/health |

## Environment Variables

### Backend (.env)

```env
# Database
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=smart_traffic_bandung

# API
API_PORT=8000
BANDUNG_API_URL=https://pelindung.bandung.go.id:8443/api/cek

# AI
CONFIDENCE_THRESHOLD=0.5

# Traffic Thresholds
LANCAR_THRESHOLD=40
PADAT_THRESHOLD=70
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/cctv` | Get all CCTVs |
| GET | `/cctv/{id}` | Get CCTV detail |
| GET | `/analyze/{id}` | Analyze traffic |
| GET | `/analyze/history/{id}` | Get history |
| GET | `/analyze/latest` | Get latest for all |

## Performance Optimization

### Frontend
- Use React.memo for components
- Lazy load video stream
- Debounce map interactions
- Cache CCTV list

### Backend
- Cache results 30 seconds
- Use connection pooling
- Optimize YOLO model (nano version)
- Index database queries

### Database
- Add indexes on frequently queried columns
- Archive old data
- Use pagination for queries

## Troubleshooting

### Backend Issues
| Problem | Solution |
|---------|----------|
| 502 Bad Gateway | Backend not running on port 8000 |
| CORS Error | Check CORS_ORIGINS in .env |
| Database Connection | Check MySQL running and credentials |
| YOLO Model Not Found | Run `from ultralytics import YOLO; YOLO('yolov8n.pt')` |

### Frontend Issues
| Problem | Solution |
|---------|----------|
| Cannot reach API | Check backend URL in api.js |
| Video not playing | Check if m3u8 stream is valid |
| Map not loading | Check internet connection |
| High memory usage | Disable auto-refresh, reduce polling |

### Database Issues
| Problem | Solution |
|---------|----------|
| Connection refused | Start MySQL: `mysql.server start` |
| Database doesn't exist | Run setup.md instructions |
| Out of disk space | Archive old data, increase storage |

## Development Tips

1. **Enable Debug Mode**
   ```python
   # In app/main.py
   app = FastAPI(debug=True)
   ```

2. **Mock API Response** (for testing without internet)
   ```python
   # In cctv_service.py
   def fetch_all_cctv(self):
       return self.get_mock_data()  # Return test data
   ```

3. **Local Video Testing**
   ```bash
   # Use local video file as stream
   streamUrl = "file:///path/to/video.mp4"
   ```

4. **Monitor Database**
   ```sql
   -- Check query performance
   SHOW PROCESSLIST;
   
   -- Check table sizes
   SELECT table_name, ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
   FROM information_schema.tables
   WHERE table_schema = 'smart_traffic_bandung';
   ```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [YOLO Documentation](https://docs.ultralytics.com/)
- [Leaflet Documentation](https://leafletjs.com/)
- [HLS.js Documentation](https://github.com/video-dev/hls.js/)

## License

MIT License - Free to use for any purpose
