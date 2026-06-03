import React, { useState } from 'react';

export const CCTVList = ({ cctvs, selectedCCTVId, onSelectCCTV, trafficStatus, loading }) => {
  const [searchQuery, setSearchQuery] = useState('');

  if (loading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="h-20 bg-gray-200 rounded animate-pulse"></div>
        ))}
      </div>
    );
  }

  if (!cctvs || cctvs.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No CCTV data available
      </div>
    );
  }

  // Filter CCTV berdasarkan search query
  const filteredCCTVs = cctvs.filter((cctv) =>
    cctv.cctv_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    cctv.id.toString().includes(searchQuery)
  );

  return (
    <div className="space-y-3">
      {/* Search Input */}
      <input
        type="text"
        placeholder="🔍 Cari CCTV..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      {/* CCTV List */}
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {filteredCCTVs.length === 0 ? (
          <div className="text-center py-4 text-gray-500 text-sm">
            Tidak ada CCTV yang cocok
          </div>
        ) : (
          filteredCCTVs.map((cctv) => {
            const status = trafficStatus?.[cctv.id]?.status;
            const isSelected = selectedCCTVId === cctv.id;

            const statusColors = {
              LANCAR: 'bg-green-100 border-green-500 text-green-700',
              PADAT: 'bg-yellow-100 border-yellow-500 text-yellow-700',
              MACET: 'bg-red-100 border-red-500 text-red-700',
            };

            const statusDots = {
              LANCAR: 'bg-traffic-green',
              PADAT: 'bg-traffic-yellow',
              MACET: 'bg-traffic-red',
            };

            // Show status only if analyzed
            const hasAnalysis = status !== undefined && status !== null;
            const displayStatus = hasAnalysis ? status : 'PENDING';

            return (
              <button
                key={cctv.id}
                onClick={() => onSelectCCTV(cctv.id)}
                className={`w-full p-4 rounded-lg border-2 transition-colors text-left ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50'
                    : `border-gray-200 bg-white hover:border-gray-300 ${
                        hasAnalysis ? statusColors[status] || 'bg-gray-50' : 'bg-gray-50'
                      }`
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h3 className="font-semibold text-sm truncate">{cctv.cctv_name}</h3>
                    <p className="text-xs text-gray-600">
                      {cctv.lat.toFixed(4)}, {cctv.lng.toFixed(4)}
                    </p>
                  </div>
                  {hasAnalysis && (
                    <div className="flex items-center gap-2 ml-2">
                      <div className={`w-3 h-3 rounded-full ${statusDots[status] || 'bg-gray-500'}`}></div>
                      <span className="font-bold text-sm whitespace-nowrap">{displayStatus}</span>
                    </div>
                  )}
                </div>
                {hasAnalysis && trafficStatus?.[cctv.id]?.vehicle_count !== undefined && (
                  <p className="text-xs text-gray-600 mt-2">
                    🚗 {trafficStatus[cctv.id].vehicle_count} kendaraan
                  </p>
                )}
                {!hasAnalysis && (
                  <p className="text-xs text-gray-500 mt-2">
                    ⏳ Belum dianalisis
                  </p>
                )}
              </button>
            );
          })
        )}
      </div>
    </div>
  );
};

export default CCTVList;