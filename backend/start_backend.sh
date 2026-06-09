#!/bin/bash
# ─────────────────────────────────────────────────────
# start_backend.sh — Jalankan backend Smart City
# Cara pakai: bash start_backend.sh
# ─────────────────────────────────────────────────────

cd "$(dirname "$0")"

echo "🚀 Memulai Smart City Backend..."

# Aktifkan virtual environment
if [ ! -d "venv" ]; then
  echo "❌ Virtual environment tidak ditemukan!"
  echo "   Jalankan dulu: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

source venv/bin/activate
echo "✅ Virtual environment aktif"

# Jalankan server
echo "🌐 Server berjalan di: http://0.0.0.0:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo "🔌 ESP32 endpoint: http://localhost:8000/esp32/status"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
