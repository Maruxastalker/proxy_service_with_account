from PyQt5.QtCore import QThread, pyqtSignal
from services.websocket_service import WebSocketService
import time


class WebSocketThread(QThread):
    status_received = pyqtSignal(dict)
    
    def __init__(self, user_id: int, token: str):
        super().__init__()
        self.user_id = user_id
        self.token = token
        self.ws_service = None
        self.running = True
    
    def run(self):
        self.ws_service = WebSocketService(self.user_id, self.token)
        
        def on_message(data):
            self.status_received.emit(data)
        
        self.ws_service.connect(on_message)
        
        # Периодически отправляем ping и запрос статуса
        last_status_request = 0
        while self.running and self.ws_service and self.ws_service.running:
            time.sleep(25)  # каждые 25 секунд
            if self.ws_service:
                self.ws_service.send_ping()
                
                # Раз в 2 минуты запрашиваем статус
                current_time = time.time()
                if current_time - last_status_request > 120:
                    self.ws_service.send_status_request()
                    last_status_request = current_time
    
    def stop(self):
        self.running = False
        if self.ws_service:
            self.ws_service.close()