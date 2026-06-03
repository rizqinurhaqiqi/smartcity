"""
Utility functions for Smart Traffic Bandung
"""

from enum import Enum
from typing import Dict, List


class TrafficStatus(str, Enum):
    """Traffic status enum"""
    LANCAR = "LANCAR"
    PADAT = "PADAT"
    MACET = "MACET"


class VehicleType(str, Enum):
    """Vehicle type enum"""
    CAR = "car"
    MOTORCYCLE = "motorcycle"
    BUS = "bus"
    TRUCK = "truck"


def determine_traffic_status(
    vehicle_count: int,
    lancar_threshold: int = 40,
    padat_threshold: int = 70
) -> str:
    """
    Determine traffic status based on vehicle count
    
    Args:
        vehicle_count: Number of vehicles detected
        lancar_threshold: Threshold for LANCAR (must be < this)
        padat_threshold: Threshold for MACET (must be > this)
        
    Returns:
        Traffic status: LANCAR, PADAT, or MACET
    """
    if vehicle_count > padat_threshold:
        return TrafficStatus.MACET.value
    elif vehicle_count >= lancar_threshold:
        return TrafficStatus.PADAT.value
    else:
        return TrafficStatus.LANCAR.value


def get_status_color(status: str) -> str:
    """Get color code for status"""
    colors = {
        TrafficStatus.LANCAR.value: "#10b981",  # Green
        TrafficStatus.PADAT.value: "#f59e0b",    # Yellow
        TrafficStatus.MACET.value: "#ef4444",    # Red
    }
    return colors.get(status, "#6b7280")  # Default gray


def calculate_traffic_score(
    vehicle_count: int,
    max_vehicles: int = 100
) -> float:
    """
    Calculate traffic congestion score (0-1)
    
    Args:
        vehicle_count: Number of vehicles
        max_vehicles: Maximum expected vehicles
        
    Returns:
        Score between 0 (free) and 1 (congested)
    """
    return min(vehicle_count / max_vehicles, 1.0)


def format_datetime(dt) -> str:
    """Format datetime to ISO string"""
    if dt is None:
        return None
    return dt.isoformat()


def validate_coordinates(lat: float, lng: float) -> bool:
    """
    Validate latitude and longitude
    
    Args:
        lat: Latitude (-90 to 90)
        lng: Longitude (-180 to 180)
        
    Returns:
        True if valid, False otherwise
    """
    return -90 <= lat <= 90 and -180 <= lng <= 180


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate approximate distance between two coordinates in kilometers
    Using simplified Haversine formula
    
    Args:
        lat1, lng1: First coordinate
        lat2, lng2: Second coordinate
        
    Returns:
        Distance in kilometers
    """
    from math import radians, cos, sin, asin, sqrt
    
    # Convert to radians
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Earth radius in kilometers
    
    return c * r


def group_vehicles_by_type(
    detections: Dict[str, int]
) -> Dict[str, str]:
    """
    Group vehicles and return human-readable format
    
    Args:
        detections: Dict with vehicle counts
        
    Returns:
        Formatted string
    """
    parts = []
    if detections.get("car", 0) > 0:
        parts.append(f"{detections['car']} mobil")
    if detections.get("motorcycle", 0) > 0:
        parts.append(f"{detections['motorcycle']} motor")
    if detections.get("bus", 0) > 0:
        parts.append(f"{detections['bus']} bus")
    if detections.get("truck", 0) > 0:
        parts.append(f"{detections['truck']} truk")
    
    return ", ".join(parts) or "Tidak ada kendaraan"


def log_analysis_result(
    cctv_name: str,
    vehicle_count: int,
    status: str,
    confidence: float
) -> str:
    """
    Create formatted log message for analysis result
    """
    return (
        f"[{cctv_name}] "
        f"Vehicles: {vehicle_count} | "
        f"Status: {status} | "
        f"Confidence: {confidence:.2%}"
    )
