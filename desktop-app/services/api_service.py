import requests
import json
import jwt
from typing import Dict, Any, Optional


class APIService:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
    
    def activate_key(self, token: str, activation_key: str) -> Dict[str, Any]:
        url = f"{self.base_url}/activate"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = {"activation_key": activation_key}
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json()
                }
            elif response.status_code == 503:
                return {
                    "success": False,
                    "error": "Нет свободных прокси-серверов"
                }
            elif response.status_code == 403:
                return {
                    "success": False,
                    "error": "Неверный или просроченный ключ"
                }
            else:
                return {
                    "success": False,
                    "error": f"Ошибка {response.status_code}: {response.text}"
                }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Не удалось подключиться к серверу"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def disconnect(self, token: str) -> bool:
        url = f"{self.base_url}/disconnect"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        try:
            response = requests.post(url, headers=headers, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_user_id_from_token(self, token: str) -> Optional[int]:
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            return int(payload.get("sub"))
        except:
            return None