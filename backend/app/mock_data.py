"""
Mock data untuk testing tanpa koneksi ke API Bandung
"""

MOCK_CCTVS = [
    {
        "id": "1",
        "cctv_name": "CCTV Pendopo",
        "lat": -6.9147,
        "lng": 107.6098,
        "stream_cctv": "http://example.com/stream1.m3u8",
        "dinas": "Dishub"
    },
    {
        "id": "2",
        "cctv_name": "CCTV Alun-Alun",
        "lat": -6.9175,
        "lng": 107.6090,
        "stream_cctv": "http://example.com/stream2.m3u8",
        "dinas": "Dishub"
    },
    {
        "id": "3",
        "cctv_name": "CCTV Jl. Braga",
        "lat": -6.9200,
        "lng": 107.6100,
        "stream_cctv": "http://example.com/stream3.m3u8",
        "dinas": "Dishub"
    },
    {
        "id": "4",
        "cctv_name": "CCTV Cikapundung",
        "lat": -6.9130,
        "lng": 107.6150,
        "stream_cctv": "http://example.com/stream4.m3u8",
        "dinas": "Dishub"
    },
    {
        "id": "5",
        "cctv_name": "CCTV Riau",
        "lat": -6.9250,
        "lng": 107.6050,
        "stream_cctv": "http://example.com/stream5.m3u8",
        "dinas": "Dishub"
    },
]

MOCK_ANALYSIS = {
    "1": {
        "cctv_name": "CCTV Pendopo",
        "vehicle_count": 35,
        "status": "LANCAR",
        "car_count": 20,
        "motorcycle_count": 12,
        "bus_count": 2,
        "truck_count": 1,
        "confidence_score": 0.87
    },
    "2": {
        "cctv_name": "CCTV Alun-Alun",
        "vehicle_count": 78,
        "status": "MACET",
        "car_count": 45,
        "motorcycle_count": 28,
        "bus_count": 4,
        "truck_count": 1,
        "confidence_score": 0.82
    },
    "3": {
        "cctv_name": "CCTV Jl. Braga",
        "vehicle_count": 52,
        "status": "PADAT",
        "car_count": 30,
        "motorcycle_count": 18,
        "bus_count": 3,
        "truck_count": 1,
        "confidence_score": 0.85
    },
}
