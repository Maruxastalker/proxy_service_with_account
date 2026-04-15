import json
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox, QFrame, QGroupBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from services.api_service import APIService
from threads.websocket_thread import WebSocketThread


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_service = APIService()
        self.websocket_thread = None
        self.user_id = None
        self.token = None
        self.init_ui()
        self.load_styles()
    
    def init_ui(self):
        self.setWindowTitle("Proxy Desktop Client")
        self.setFixedSize(600, 700)
        self.setMinimumSize(550, 650)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        header_layout = QHBoxLayout()
        icon_label = QLabel("🖥️")
        icon_label.setObjectName("icon")
        title_label = QLabel("Proxy Desktop Client")
        title_label.setObjectName("title")
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setObjectName("line")
        main_layout.addWidget(line)
        
        auth_group = QGroupBox("🔐 Авторизация")
        auth_group.setObjectName("auth_group")
        auth_layout = QVBoxLayout(auth_group)
        auth_layout.setSpacing(12)
        
        token_label = QLabel("JWT Token")
        token_label.setObjectName("field_label")
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Вставьте JWT токен из веб-версии")
        self.token_input.setEchoMode(QLineEdit.Password)
        self.token_input.setObjectName("token_input")
        auth_layout.addWidget(token_label)
        auth_layout.addWidget(self.token_input)
        
        main_layout.addWidget(auth_group)
        
        key_group = QGroupBox("🔑 Ключ активации")
        key_group.setObjectName("key_group")
        key_layout = QVBoxLayout(key_group)
        key_layout.setSpacing(12)
        
        key_label = QLabel("Activation Key")
        key_label.setObjectName("field_label")
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Вставьте ключ из письма")
        self.key_input.setObjectName("key_input")
        key_layout.addWidget(key_label)
        key_layout.addWidget(self.key_input)
        
        main_layout.addWidget(key_group)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        self.connect_btn = QPushButton("Подключиться")
        self.connect_btn.setObjectName("connect_btn")
        self.connect_btn.setMinimumHeight(45)
        self.connect_btn.clicked.connect(self.on_connect)
        
        self.disconnect_btn = QPushButton("Отключиться")
        self.disconnect_btn.setObjectName("disconnect_btn")
        self.disconnect_btn.setMinimumHeight(45)
        self.disconnect_btn.clicked.connect(self.on_disconnect)
        self.disconnect_btn.setEnabled(False)
        
        buttons_layout.addWidget(self.connect_btn)
        buttons_layout.addWidget(self.disconnect_btn)
        main_layout.addLayout(buttons_layout)
        
        status_group = QGroupBox("📡 Статус подключения")
        status_group.setObjectName("status_group")
        status_layout = QVBoxLayout(status_group)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setObjectName("status_text")
        status_layout.addWidget(self.status_text)
        
        main_layout.addWidget(status_group)
        
        info_label = QLabel("💡 Как получить JWT токен: F12 → Application → localStorage → access_token")
        info_label.setObjectName("info_label")
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        # Добавляем приветственное сообщение
        self.status_text.append("🟢 Приложение готово к работе")
        self.status_text.append("➡️ Введите JWT токен и ключ активации")
    
    def load_styles(self):
        try:
            with open("ui/styles.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Style not loaded: {e}")
    
    def on_connect(self):
        token = self.token_input.text().strip()
        activation_key = self.key_input.text().strip()
        
        if not token:
            QMessageBox.warning(self, "Ошибка", "Введите JWT токен")
            return
        
        if not activation_key:
            QMessageBox.warning(self, "Ошибка", "Введите ключ активации")
            return
        
        self.token = token
        self.connect_btn.setEnabled(False)
        self.connect_btn.setText("Подключение...")
        self.status_text.append("")
        self.status_text.append("⏳ Отправка ключа на сервер...")
        
        try:
            response = self.api_service.activate_key(token, activation_key)
            
            if response["success"]:
                vm_info = response["data"]
                
                self.status_text.append("")
                self.status_text.append("✅ ПОДКЛЮЧЕНИЕ УСТАНОВЛЕНО")
                self.status_text.append("═" * 40)
                self.status_text.append(f"🌐 Хост:     {vm_info['host']}")
                self.status_text.append(f"🔌 Порт:     {vm_info['port']}")
                self.status_text.append(f"📡 Протокол: {vm_info['protocol']}")
                self.status_text.append("═" * 40)
                self.status_text.append("🟢 Статус: АКТИВНО")
                
                self.connect_btn.setText("Подключено")
                self.connect_btn.setEnabled(False)
                self.disconnect_btn.setEnabled(True)
                
                self.user_id = self.api_service.get_user_id_from_token(token)
                if self.user_id:
                    self.start_websocket()
                    self.status_text.append("🔌 WebSocket: соединение установлено")
            else:
                self.status_text.append(f"❌ Ошибка: {response['error']}")
                self.connect_btn.setText("Подключиться")
                self.connect_btn.setEnabled(True)
                
        except Exception as e:
            self.status_text.append(f"❌ Исключение: {str(e)}")
            self.connect_btn.setText("Подключиться")
            self.connect_btn.setEnabled(True)
    
    def on_disconnect(self):
        self.status_text.append("")
        self.status_text.append("⏹️ Отключение от прокси...")
        
        if self.user_id and self.token:
            try:
                self.api_service.disconnect(self.token)
                self.status_text.append("✅ Отключено успешно")
                self.status_text.append("🔴 Статус: ОТКЛЮЧЕНО")
                self.status_text.append("═" * 40)
            except Exception as e:
                self.status_text.append(f"⚠️ Ошибка при отключении: {e}")
        
        self.stop_websocket()
        self.connect_btn.setText("Подключиться")
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.user_id = None
    
    def start_websocket(self):
        if self.websocket_thread:
            self.websocket_thread.stop()
        
        self.websocket_thread = WebSocketThread(self.user_id, self.token)
        self.websocket_thread.status_received.connect(self.on_ws_status)
        self.websocket_thread.start()
    
    def stop_websocket(self):
        if self.websocket_thread:
            self.websocket_thread.stop()
            self.websocket_thread.wait()
            self.websocket_thread = None
            self.status_text.append("🔌 WebSocket: отключен")
    
    def on_ws_status(self, status_data):
        status = status_data.get("status", "")
        msg_type = status_data.get("type", "")
        
        if msg_type == "error" or status == "error":
            error_msg = status_data.get("error", "Неизвестная ошибка")
            self.status_text.append(f"❌ WebSocket ошибка: {error_msg}")
            self.status_text.append("🔴 Статус: ОШИБКА")
            
        elif status == "connected":
            vm_info = status_data.get("vm_info")
            if vm_info:
                self.status_text.append(f"🟢 WebSocket: подключен к {vm_info['host']}:{vm_info['port']}")
            else:
                self.status_text.append("🟢 WebSocket: соединение активно")
            self.status_text.append("🟢 Статус: ПОДКЛЮЧЕНО")
            
        elif status == "disconnected":
            self.status_text.append("🔴 WebSocket: соединение разорвано")
            self.status_text.append("🔴 Статус: ОТКЛЮЧЕНО")
            
        elif status == "no_free_vms":
            self.status_text.append("⚠️ WebSocket: нет свободных прокси-серверов")
            self.status_text.append("🟡 Статус: НЕТ СВОБОДНЫХ VM")
            
        elif msg_type == "heartbeat":
            pass
            
        elif msg_type == "pong":
            pass
            
        else:
            self.status_text.append(f"📡 WebSocket: {status_data}")