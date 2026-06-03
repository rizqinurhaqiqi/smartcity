import React, { useState, useEffect } from 'react';
import VideoStream from '../components/VideoStream';
import TrafficStatusPanel from '../components/TrafficStatusPanel';
import MapView from '../components/MapView';
import CCTVList from '../components/CCTVList';
import { cctvService, trafficService } from '../services/api';

export const Dashboard = () => {
  const [cctvs, setCCTVs] = useState([]);
  const [selectedCCTVId, setSelectedCCTVId] = useState(null);
  const [selectedCCTV, setSelectedCCTV] = useState(null);
  const [trafficStatus, setTrafficStatus] = useState({});
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [analysisError, setAnalysisError] = useState(null);
  const [loadingCCTVs, setLoadingCCTVs] = useState(true);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Fetch all CCTVs on mount
  useEffect(() => {
    fetchAllCCTVs();
  }, []);

  // Auto-refresh analysis every 5 seconds if selected
  useEffect(() => {
    if (!selectedCCTVId || !autoRefresh) return;

    const interval = setInterval(() => {
      analyzeTraffic(selectedCCTVId);
    }, 5000);

    return () => clearInterval(interval);
  }, [selectedCCTVId, autoRefresh]);

  // Update traffic status only for selected CCTV
  useEffect(() => {
    if (!selectedCCTVId) return;

    const updateStatus = async () => {
      try {
        const response = await trafficService.analyzeCCTV(selectedCCTVId);
        setTrafficStatus((prev) => ({
          [selectedCCTVId]: response.data,
        }));
      } catch (err) {
        console.error('Error fetching analysis:', err);
      }
    };

    updateStatus();
    const interval = setInterval(updateStatus, 10000); // Update every 10 seconds

    return () => clearInterval(interval);
  }, [selectedCCTVId]);

  const fetchAllCCTVs = async () => {
    try {
      setLoadingCCTVs(true);
      setError(null);
      const response = await cctvService.getAllCCTV();
      setCCTVs(response.data);
      // Don't auto-select - user must click marker
    } catch (err) {
      console.error('Error fetching CCTVs:', err);
      setError('Failed to load CCTV list. Make sure backend is running.');
    } finally {
      setLoadingCCTVs(false);
    }
  };

  const handleSelectCCTV = (cctvId) => {
    const cctv = cctvs.find((c) => c.id === cctvId);
    if (cctv) {
      console.log('Selected CCTV:', cctv);
      console.log('Stream URL:', cctv.stream_cctv || cctv.stream_url);
      setSelectedCCTVId(cctvId);
      setSelectedCCTV(cctv);
      setCurrentAnalysis(null); // Reset analysis dulu
      setAnalysisError(null); // Clear error juga
      analyzeTraffic(cctvId); // Baru analyze
    }
  };

  const analyzeTraffic = async (cctvId) => {
    try {
      setLoadingAnalysis(true);
      setAnalysisError(null);
      const response = await trafficService.analyzeCCTV(cctvId);
      setCurrentAnalysis(response.data);

      // Update traffic status
      setTrafficStatus((prev) => ({
        ...prev,
        [cctvId]: response.data,
      }));
    } catch (err) {
      console.error('Error analyzing traffic:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Gagal menganalisis traffic';
      setAnalysisError(errorMessage);
      setCurrentAnalysis(null);
    } finally {
      setLoadingAnalysis(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                🚦 Smart Traffic Bandung
              </h1>
              <p className="text-gray-600 text-sm mt-1">
                Real-time Traffic Monitoring System
              </p>
            </div>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="w-4 h-4"
                />
                <span className="text-sm font-medium text-gray-700">
                  Auto Refresh
                </span>
              </label>
              {error && (
                <div className="text-red-600 text-sm bg-red-50 px-3 py-2 rounded">
                  ⚠️ {error}
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Map Section */}
        <div className="mb-8 bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4">📍 CCTV Locations</h2>
          <MapView
            cctvs={cctvs}
            selectedCCTVId={selectedCCTVId}
            onSelectCCTV={handleSelectCCTV}
            trafficStatus={trafficStatus}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Sidebar - CCTV List */}
          <div className="lg:col-span-1 bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold mb-4">📸 CCTV List</h2>
            <button
              onClick={fetchAllCCTVs}
              className="w-full mb-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition text-sm"
            >
              Refresh List
            </button>
            <CCTVList
              cctvs={cctvs}
              selectedCCTVId={selectedCCTVId}
              onSelectCCTV={handleSelectCCTV}
              trafficStatus={trafficStatus}
              loading={loadingCCTVs}
            />
          </div>

          {/* Main Content - Video & Analysis */}
          <div className="lg:col-span-2 space-y-6">
            {/* Video Stream */}
            {selectedCCTV && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-xl font-bold mb-4">📹 Live Stream</h2>
                <div className="bg-black rounded-lg overflow-hidden">
                  {selectedCCTV.stream_url ? (
                    <VideoStream
                      streamUrl={`http://localhost:8000/cctv/stream/${selectedCCTV.id}`}
                      cctvName={selectedCCTV.cctv_name}
                      originalUrl={selectedCCTV.stream_url}
                    />
                  ) : (
                    <div className="h-64 bg-gray-900 flex items-center justify-center text-gray-400 text-center p-4">
                      <div>
                        <p className="text-lg mb-2">ℹ️ Tidak ada stream</p>
                        <p className="text-sm text-gray-500">stream_url field kosong atau undefined</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Traffic Status */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold">📊 Traffic Analysis</h2>
                {selectedCCTV && (
                  <button
                    onClick={() => analyzeTraffic(selectedCCTVId)}
                    disabled={loadingAnalysis}
                    className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400 transition text-sm"
                  >
                    {loadingAnalysis ? 'Analyzing...' : 'Analyze Now'}
                  </button>
                )}
              </div>
              <TrafficStatusPanel
                analysis={currentAnalysis}
                loading={loadingAnalysis}
                error={analysisError}
              />
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 text-center text-gray-600 text-sm">
          <p>
            Smart Traffic Bandung © 2024 | Backend Server: http://localhost:8000
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Dashboard;