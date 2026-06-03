import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

// Create custom HTML markers
const createCustomIcon = (status) => {
  const colors = {
    LANCAR: '#10b981',
    PADAT: '#f59e0b',
    MACET: '#ef4444',
  };

  const labels = {
    LANCAR: '✓',
    PADAT: '⚠',
    MACET: '✕',
  };

  const color = colors[status] || '#6b7280';
  const label = labels[status] || '●';

  const html = `
    <div style="
      display: flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      background-color: ${color};
      border: 2px solid white;
      border-radius: 50%;
      font-size: 16px;
      font-weight: bold;
      color: white;
      text-shadow: 0 1px 2px rgba(0,0,0,0.3);
      cursor: pointer;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    ">
      ${label}
    </div>
  `;

  return L.divIcon({
    html,
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32],
    className: 'custom-marker'
  });
};

export const MapView = ({ cctvs, selectedCCTVId, onSelectCCTV, trafficStatus }) => {
  const bandungCenter = [-6.9147, 107.6098];

  if (!cctvs || cctvs.length === 0) {
    return (
      <div className="w-full h-96 bg-gray-100 rounded-lg flex items-center justify-center text-gray-500">
        Loading map...
      </div>
    );
  }

  return (
    <MapContainer
      center={bandungCenter}
      zoom={13}
      style={{ height: '24rem', width: '100%' }}
      className="rounded-lg"
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; OpenStreetMap contributors'
      />

      {cctvs.map((cctv) => {
        const status = trafficStatus?.[cctv.id]?.status || 'PENDING';
        const isSelected = selectedCCTVId === cctv.id;

        return (
          <Marker
            key={cctv.id}
            position={[cctv.lat, cctv.lng]}
            icon={createCustomIcon(status)}
            eventHandlers={{
              click: () => onSelectCCTV(cctv.id),
            }}
          >
            <Popup>
              <div className={`p-2 ${isSelected ? 'border-2 border-blue-500' : ''}`}>
                <p className="font-semibold text-sm">{cctv.cctv_name}</p>
                <p className="text-xs text-gray-600">
                  Lat: {cctv.lat.toFixed(4)}, Lng: {cctv.lng.toFixed(4)}
                </p>
                <p className={`text-xs mt-1 font-bold ${
                  status === 'LANCAR' ? 'text-green-600' :
                  status === 'PADAT' ? 'text-yellow-600' :
                  'text-red-600'
                }`}>
                  Status: {status}
                </p>
                {trafficStatus?.[cctv.id]?.vehicle_count !== undefined && (
                  <p className="text-xs text-gray-600">
                    Kendaraan: {trafficStatus[cctv.id].vehicle_count}
                  </p>
                )}
              </div>
            </Popup>
          </Marker>
        );
      })}
    </MapContainer>
  );
};

export default MapView;