import websocket
import json
import threading
from typing import Callable, Optional


class WebSocketService:
    def __init__(self, user_id: int, token: str):
        self.user_id = user_id
        self.token = token
        self.ws_url = f"ws://localhost:8000/ws/status/{user_id}?token={token}"
        self.ws = None
        self.running = False
        self.on_message_callback = None
        self.thread = None
    
    def connect(self, on_message: Callable):
        self.on_message_callback = on_message
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
    
    def _run(self):
        try:
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            self.ws.run_forever()
        except Exception as e:
            if self.on_message_callback:
                self.on_message_callback({
                    "type": "error", 
                    "status": "error",
                    "error": str(e)
                })
    
    def _on_open(self, ws):
        print(f"WebSocket connected for user {self.user_id}")
        ws.send("status")
    
    def _on_message(self, ws, message):
        if self.on_message_callback:
            try:
                data = json.loads(message)
                self.on_message_callback(data)
            except:
                pass
    
    def _on_error(self, ws, error):
        print(f"WebSocket error: {error}")
        if self.on_message_callback:
            self.on_message_callback({
                "type": "error",
                "status": "error",
                "error": str(error)
            })
    
    def _on_close(self, ws, close_status_code, close_msg):
        print(f"WebSocket closed: {close_status_code} - {close_msg}")
        self.running = False
        if self.on_message_callback:
            self.on_message_callback({
                "type": "close",
                "status": "disconnected"
            })
    
    def send_ping(self):
        if self.ws and self.running:
            try:
                self.ws.send("ping")
            except:
                pass
    
    def send_status_request(self):
        if self.ws and self.running:
            try:
                self.ws.send("status")
            except:
                pass
    
    def close(self):
        self.running = False
        if self.ws:
            self.ws.close()