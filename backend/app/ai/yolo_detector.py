import cv2
import numpy as np
from typing import Dict, List, Optional
import logging
from ultralytics import YOLO
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Thread pool untuk processing yang berat
executor = ThreadPoolExecutor(max_workers=2)


class YOLODetector:
    """Service untuk deteksi kendaraan menggunakan YOLO"""

    def __init__(self, model_name: str = "yolov8n.pt"):
        """
        Initialize YOLO detector
        
        Args:
            model_name: Model YOLO yang digunakan (default: nano untuk performa)
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
        self.vehicle_classes = ["car", "motorcycle", "bus", "truck"]
        self.coco_class_ids = {
            2: "car",
            3: "motorcycle",
            5: "bus",
            7: "truck",
        }

    def _load_model(self):
        """Load YOLO model"""
        try:
            logger.info(f"Loading YOLO model: {self.model_name}")
            self.model = YOLO(self.model_name)
            logger.info("YOLO model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading YOLO model: {str(e)}")

    async def detect_vehicles_from_stream(
        self,
        stream_url: str,
        frame_interval: int = 2,
        max_frames: int = 10,
    ) -> Dict:
        """
        Deteksi kendaraan dari video stream
        
        Args:
            stream_url: URL m3u8 atau RTSP stream
            frame_interval: Interval dalam detik untuk capture frame
            max_frames: Maximum frames untuk di-process
            
        Returns:
            Dict dengan vehicle_count dan status
        """
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                executor,
                self._process_stream,
                stream_url,
                frame_interval,
                max_frames,
            )
            return result
        except Exception as e:
            logger.error(f"Error detecting vehicles from stream: {str(e)}")
            return {
                "vehicle_count": 0,
                "car_count": 0,
                "motorcycle_count": 0,
                "bus_count": 0,
                "truck_count": 0,
                "status": "ERROR",
                "confidence_score": 0.0,
            }

    def _process_stream(self, stream_url: str, frame_interval: int, max_frames: int) -> Dict:
        """Process video stream (blocking operation)"""
        try:
            cap = cv2.VideoCapture(stream_url)
            
            if not cap.isOpened():
                logger.error(f"Cannot open stream: {stream_url}")
                return self._get_empty_result()

            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_skip = max(1, int(fps * frame_interval)) if fps > 0 else 30

            total_vehicles = {
                "car": 0,
                "motorcycle": 0,
                "bus": 0,
                "truck": 0,
            }
            total_detections = 0
            confidence_sum = 0.0
            frame_count = 0

            while frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break

                # Skip frames sesuai interval
                if frame_count % frame_skip == 0:
                    detection = self._detect_vehicles_in_frame(frame)
                    
                    for vehicle_type, count in detection["vehicles"].items():
                        total_vehicles[vehicle_type] += count
                    
                    total_detections += detection["total_count"]
                    confidence_sum += detection["avg_confidence"]

                frame_count += 1

            cap.release()

            # Calculate average
            avg_confidence = (
                confidence_sum / frame_count if frame_count > 0 else 0.0
            )
            avg_vehicles = (
                total_detections / frame_count if frame_count > 0 else 0
            )

            return {
                "vehicle_count": int(avg_vehicles),
                "car_count": int(total_vehicles["car"] / max(frame_count, 1)),
                "motorcycle_count": int(total_vehicles["motorcycle"] / max(frame_count, 1)),
                "bus_count": int(total_vehicles["bus"] / max(frame_count, 1)),
                "truck_count": int(total_vehicles["truck"] / max(frame_count, 1)),
                "status": self._determine_status(int(avg_vehicles)),
                "confidence_score": float(avg_confidence),
            }

        except Exception as e:
            logger.error(f"Error processing stream: {str(e)}")
            return self._get_empty_result()

    def _detect_vehicles_in_frame(self, frame: np.ndarray) -> Dict:
        """Deteksi kendaraan dalam single frame"""
        try:
            if self.model is None:
                return self._get_empty_detection()

            # Resize frame untuk faster processing
            h, w = frame.shape[:2]
            if w > 1280:
                scale = 1280 / w
                frame = cv2.resize(frame, (1280, int(h * scale)))

            results = self.model(frame, conf=0.5, verbose=False)

            vehicles = {
                "car": 0,
                "motorcycle": 0,
                "bus": 0,
                "truck": 0,
            }
            total_count = 0
            confidence_scores = []

            if results and len(results) > 0:
                result = results[0]
                
                if result.boxes is not None:
                    for box in result.boxes:
                        class_id = int(box.cls)
                        confidence = float(box.conf)
                        
                        # Map COCO class IDs ke vehicle types
                        if class_id in self.coco_class_ids:
                            vehicle_type = self.coco_class_ids[class_id]
                            vehicles[vehicle_type] += 1
                            total_count += 1
                            confidence_scores.append(confidence)

            avg_confidence = (
                np.mean(confidence_scores) if confidence_scores else 0.0
            )

            return {
                "vehicles": vehicles,
                "total_count": total_count,
                "avg_confidence": float(avg_confidence),
            }

        except Exception as e:
            logger.error(f"Error detecting vehicles in frame: {str(e)}")
            return self._get_empty_detection()

    def _determine_status(self, vehicle_count: int) -> str:
        """
        Determine traffic status berdasarkan jumlah kendaraan
        
        - > 70: MACET
        - 40-70: PADAT
        - < 40: LANCAR
        """
        if vehicle_count > 70:
            return "MACET"
        elif vehicle_count >= 40:
            return "PADAT"
        else:
            return "LANCAR"

    def _get_empty_detection(self) -> Dict:
        """Return empty detection result"""
        return {
            "vehicles": {
                "car": 0,
                "motorcycle": 0,
                "bus": 0,
                "truck": 0,
            },
            "total_count": 0,
            "avg_confidence": 0.0,
        }

    def _get_empty_result(self) -> Dict:
        """Return empty result"""
        return {
            "vehicle_count": 0,
            "car_count": 0,
            "motorcycle_count": 0,
            "bus_count": 0,
            "truck_count": 0,
            "status": "ERROR",
            "confidence_score": 0.0,
        }


# Singleton instance
yolo_detector = YOLODetector()
