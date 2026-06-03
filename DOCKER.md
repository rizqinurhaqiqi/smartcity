# Smart Traffic Bandung - Docker Support

## Dockerfile for Backend
Dockerfile yang ada di `backend/Dockerfile` untuk membuild docker image

## Dockerfile for Frontend
Dockerfile yang ada di `frontend/Dockerfile` untuk membuild docker image

## Docker Compose
Untuk menjalankan semua service dengan docker:

```bash
docker-compose up -d
```

Services:
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- MySQL: localhost:3306
- PhpMyAdmin (optional): http://localhost:8080

## Konfigurasi

Edit `docker-compose.yml` untuk mengatur port dan environment variables.

## Build Images

```bash
# Build backend
docker build -t smart-traffic-backend ./backend

# Build frontend
docker build -t smart-traffic-frontend ./frontend
```

## Running Containers

```bash
# Backend
docker run -p 8000:8000 --env-file backend/.env smart-traffic-backend

# Frontend
docker run -p 5173:5173 smart-traffic-frontend
```

## Environment Variables

Setiap container membaca `.env` file untuk konfigurasi. Pastikan `.env` sudah ada sebelum menjalankan container.
