import aiohttp
import asyncio
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class CCTVService:
    """Service untuk fetch data CCTV dari API Bandung"""

    def __init__(self, api_url: str = "https://pelindung.bandung.go.id:8443/api/cek"):
        self.api_url = api_url
        self.timeout = aiohttp.ClientTimeout(total=30)

    async def fetch_all_cctv(self) -> List[dict]:
        """
        Fetch semua data CCTV dari API Bandung
        
        Returns:
            List of CCTV data with id, cctv_name, lat, lng, stream_cctv
        """
        try:
            # Disable SSL verification untuk development
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector, timeout=self.timeout) as session:
                async with session.get(self.api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_cctv_data(data)
                    else:
                        logger.error(f"API returned status {response.status}")
                        return []
        except asyncio.TimeoutError:
            logger.error("API request timeout")
            return []
        except Exception as e:
            logger.error(f"Error fetching CCTV data: {str(e)}")
            return []

    def _parse_cctv_data(self, raw_data: dict) -> List[dict]:
        """
        Parse raw data dari API Bandung ke format yang diinginkan
        
        Response structure expected:
        {
            "data": [
                {
                    "id": "...",
                    "cctv_name": "...",
                    "lat": ...,
                    "lng": ...,
                    "stream_cctv": "...",
                    "dinas": "..."
                }
            ]
        }
        """
        try:
            cctvs = []
            
            # Handle different response formats
            if isinstance(raw_data, dict):
                data_list = raw_data.get("data", []) or raw_data.get("cctvs", []) or [raw_data]
            elif isinstance(raw_data, list):
                data_list = raw_data
            else:
                data_list = []

            for item in data_list:
                if isinstance(item, dict):
                    cctv = {
                        "id": str(item.get("id", "")),
                        "cctv_name": item.get("cctv_name", item.get("name", "")),
                        "lat": float(item.get("lat", 0)),
                        "lng": float(item.get("lng", 0)),
                        "stream_cctv": item.get("stream_cctv", item.get("stream_url", "")),
                        "dinas": item.get("dinas", item.get("agency", "")),
                    }
                    if cctv["id"] and cctv["lat"] and cctv["lng"]:
                        cctvs.append(cctv)
            
            return cctvs
        except Exception as e:
            logger.error(f"Error parsing CCTV data: {str(e)}")
            return []

    async def fetch_cctv_by_id(self, cctv_id: str) -> Optional[dict]:
        """Fetch single CCTV by ID"""
        all_cctvs = await self.fetch_all_cctv()
        for cctv in all_cctvs:
            if cctv["id"] == cctv_id:
                return cctv
        return None


# Singleton instance
cctv_service = CCTVService()
