"""
backend/telemetry_stream.py: Real-Time WebSocket Telemetry Stream Manager.
Broadcasts continuous simulated supply chain events (IoT sensor telemetry, GPS pings,
customs gate alerts, and RL agent state triggers) to subscribed WebSockets clients.
"""

import asyncio
import json
import random
import time
from typing import List, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    """
    Manages active WebSocket connections and broadcasts real-time telemetry frames.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.corridors = ["IN-MUM-TO-DXB", "IN-DEL-TO-JED", "IN-MAA-TO-DOH", "IN-NSI-TO-RUH"]
        self.carriers = ["delhivery", "xpressbees", "bluedart", "shadowfax"]

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_json(self, message: Dict[str, Any]):
        for connection in list(self.active_connections):
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                self.disconnect(connection)

    def generate_telemetry_event(self) -> Dict[str, Any]:
        """
        Synthesizes a live real-time supply chain sensor & transit telemetry event.
        """
        corridor = random.choice(self.corridors)
        carrier = random.choice(self.carriers)
        temp_c = round(random.uniform(2.0, 8.5) if random.random() > 0.15 else random.uniform(11.0, 16.0), 1)
        speed_knots = round(random.uniform(16.0, 24.5), 1)
        is_temp_excursion = temp_c > 8.0
        is_delayed = random.random() > 0.78

        return {
            "event_type": "TELEMETRY_FRAME",
            "timestamp": time.time(),
            "tracking_id": f"TRK-{random.randint(10000, 99999)}",
            "corridor": corridor,
            "carrier": carrier,
            "gps": {
                "latitude": round(random.uniform(18.0, 26.0), 4),
                "longitude": round(random.uniform(55.0, 75.0), 4)
            },
            "sensor_readings": {
                "container_temperature_c": temp_c,
                "temperature_status": "EXCURSION_ALERT" if is_temp_excursion else "OPTIMAL_COLD_CHAIN",
                "transit_speed_kmh": round(speed_knots * 1.852, 1),
                "vibration_g": round(random.uniform(0.1, 0.6), 2)
            },
            "risk_assessment": {
                "is_delayed": is_delayed,
                "delay_risk_score": round(random.uniform(0.70, 0.95) if is_delayed else random.uniform(0.05, 0.35), 2),
                "recommended_rl_action": "EXPEDITE_REROUTE" if is_delayed else "HOLD_STANDARD"
            }
        }


# Global Singleton Instance
ws_manager = ConnectionManager()
