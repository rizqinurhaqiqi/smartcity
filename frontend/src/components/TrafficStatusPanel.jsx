import React from 'react';

const getStatusColor = (status) => {
  switch (status) {
    case 'LANCAR':
      return 'bg-green-100 border-green-500 text-green-700';
    case 'PADAT':
      return 'bg-yellow-100 border-yellow-500 text-yellow-700';
    case 'MACET':
      return 'bg-red-100 border-red-500 text-red-700';
    default:
      return 'bg-gray-100 border-gray-500 text-gray-700';
  }
};

const getStatusDot = (status) => {
  switch (status) {
    case 'LANCAR':
      return 'bg-traffic-green';
    case 'PADAT':
      return 'bg-traffic-yellow';
    case 'MACET':
      return 'bg-traffic-red';
    default:
      return 'bg-gray-500';
  }
};

export const TrafficStatusPanel = ({ analysis, loading, error }) => {
  if (error) {
    return (
      <div className="bg-red-50 rounded-lg shadow p-6 border-l-4 border-red-500">
        <div className="flex items-start gap-4">
          <div className="text-3xl">❌</div>
          <div>
            <h3 className="font-semibold text-red-700 text-lg">Analisis Gagal</h3>
            <p className="text-red-600 mt-1">{error}</p>
            <p className="text-red-500 text-sm mt-3">
              ℹ️ Kemungkinan: CCTV tidak terdaftar atau stream URL tidak valid
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-center py-8">
          <div className="text-center">
            <div className="mb-4 flex justify-center">
              <div className="relative w-12 h-12">
                <div className="absolute inset-0 rounded-full border-4 border-gray-200"></div>
                <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-blue-500 animate-spin"></div>
              </div>
            </div>
            <p className="text-gray-600 font-medium">🔍 Menganalisis Traffic...</p>
            <p className="text-gray-500 text-sm mt-2">Mendeteksi kendaraan dengan YOLO</p>
          </div>
        </div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="bg-gray-50 rounded-lg shadow p-6 text-center text-gray-500 border-2 border-dashed border-gray-300">
        <p className="text-lg">👆 Pilih CCTV untuk analisis</p>
        <p className="text-sm mt-2">Klik marker di map atau item di list</p>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow p-6 border-l-4 ${getStatusColor(analysis.status)}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">{analysis.cctv_name}</h3>
        <span className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${getStatusDot(analysis.status)}`}></div>
          <span className="font-bold text-lg">{analysis.status}</span>
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div className="bg-gray-50 p-4 rounded">
          <p className="text-gray-600 text-sm">Total Kendaraan</p>
          <p className="text-2xl font-bold">{analysis.vehicle_count}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded">
          <p className="text-gray-600 text-sm">Mobil</p>
          <p className="text-2xl font-bold">{analysis.car_count}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded">
          <p className="text-gray-600 text-sm">Motor</p>
          <p className="text-2xl font-bold">{analysis.motorcycle_count}</p>
        </div>
        <div className="bg-gray-50 p-4 rounded">
          <p className="text-gray-600 text-sm">Bus</p>
          <p className="text-2xl font-bold">{analysis.bus_count}</p>
        </div>
      </div>

      <div className="flex items-center justify-between text-sm text-gray-600">
        <span>Confidence Score: {(analysis.confidence_score * 100).toFixed(1)}%</span>
        {analysis.timestamp && (
          <span>
            {new Date(analysis.timestamp).toLocaleTimeString('id-ID')}
          </span>
        )}
      </div>
    </div>
  );
};

export default TrafficStatusPanel;  