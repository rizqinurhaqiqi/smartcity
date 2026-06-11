import React, { useEffect, useRef, useState } from 'react';
import HLS from 'hls.js';

export const VideoStream = ({ streamUrl, cctvName, originalUrl }) => {
  const videoRef = useRef(null);
  const hlsRef = useRef(null);
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    console.log('=== VideoStream Component ===');
    console.log('Proxy URL:', streamUrl);
    console.log('Original URL:', originalUrl);
    console.log('cctvName:', cctvName);
    
    if (!streamUrl) {
      console.warn('No stream URL provided');
      setHasError(true);
      return;
    }

    console.log('Loading stream from proxy:', streamUrl);
    const video = videoRef.current;
    if (!video) return;

    setHasError(false);
    setIsLoading(true);

    try {
      // Deteksi tipe stream dari original URL
      // Stream dari pelindung.bandung.go.id semuanya adalah .m3u8 (HLS)
      const isHLS =
        originalUrl?.includes('.m3u8') ||
        originalUrl?.includes('.m3u') ||
        streamUrl?.includes('stream-manifest'); // proxy manifest endpoint = HLS
      
      console.log('Stream type - HLS:', isHLS);

      if (isHLS && HLS.isSupported()) {
        console.log('Using HLS player via proxy');
        const hls = new HLS({
          autoStartLoad: true,
          startPosition: -1,
          debug: false,
          enableWorker: false,
          lowLatencyMode: true,
          maxMaxBufferLength: 30,
        });

        hlsRef.current = hls;

        hls.on(HLS.Events.MANIFEST_PARSED, () => {
          console.log('HLS manifest parsed, starting playback');
          setIsLoading(false);
          video.play().catch(err => {
            console.log('Play error:', err);
            setHasError(true);
          });
        });

        hls.on(HLS.Events.ERROR, (event, data) => {
          console.error('HLS error:', event, data);
          if (data.fatal) {
            setHasError(true);
            setIsLoading(false);
          }
        });

        hls.on(HLS.Events.FRAG_LOADED, (event, data) => {
          console.log('Fragment loaded:', data.frag.url);
        });

        try {
          // Load from proxy URL
          hls.loadSource(streamUrl);
          hls.attachMedia(video);
        } catch (err) {
          console.error('Error loading HLS source:', err);
          setHasError(true);
          setIsLoading(false);
        }

        return () => {
          if (hls) {
            hls.destroy();
          }
        };
      } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        // Safari native HLS
        console.log('Using Safari native HLS');
        video.src = streamUrl;
        setIsLoading(false);
      } else {
        // Direct video stream (MPEG-TS, MP4, etc)
        console.log('Using direct video stream via proxy');
        video.src = streamUrl;
        setIsLoading(false);
      }

      video.addEventListener('canplay', () => {
        console.log('Video can play');
        setIsLoading(false);
      });

      video.addEventListener('error', (e) => {
        console.error('Video element error:', e);
        setHasError(true);
        setIsLoading(false);
      });

    } catch (err) {
      console.error('Video setup error:', err);
      setHasError(true);
      setIsLoading(false);
    }
  }, [streamUrl, originalUrl]);

  return (
    <div className="relative bg-black rounded-lg overflow-hidden">
      <video
        ref={videoRef}
        className="w-full h-64 bg-gray-900"
        autoPlay
        controls
        playsInline
        muted
        crossOrigin="anonymous"
      />
      
      {isLoading && (
        <div className="absolute inset-0 bg-gray-900 bg-opacity-75 flex items-center justify-center">
          <div className="text-center">
            <div className="mb-3 flex justify-center">
              <div className="relative w-8 h-8">
                <div className="absolute inset-0 rounded-full border-2 border-gray-600"></div>
                <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-blue-400 animate-spin"></div>
              </div>
            </div>
            <p className="text-gray-300 text-sm">Loading stream...</p>
          </div>
        </div>
      )}

      {hasError && (
        <div className="absolute inset-0 bg-gray-900 flex items-center justify-center">
          <div className="text-center text-gray-400 px-4">
            <p className="text-lg">📹 Video tidak tersedia</p>
            <p className="text-xs mt-2 break-all text-gray-500">
              {streamUrl || 'Tidak ada URL'}
            </p>
            <p className="text-xs mt-2 text-gray-600">
              Stream mungkin sedang offline atau ada error koneksi
            </p>
            <p className="text-xs mt-3 text-gray-700 bg-gray-800 p-2 rounded">
              Original: {originalUrl?.substring(0, 60)}...
            </p>
          </div>
        </div>
      )}

      {cctvName && (
        <div className="absolute top-2 left-2 bg-black bg-opacity-50 text-white px-3 py-1 rounded text-sm">
          {cctvName}
        </div>
      )}
    </div>
  );
};

export default VideoStream;