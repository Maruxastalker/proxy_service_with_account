import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect


def test_websocket_connection_success(client, test_user):
    user, token = test_user
    
    with client.websocket_connect(f"/ws/status/{user.id}?token={token}") as websocket:
        data = websocket.receive_json()
        assert data["type"] == "connection_status"
        assert data["status"] in ["connected", "disconnected"]


def test_websocket_ping_pong(client, test_user):
    user, token = test_user
    
    with client.websocket_connect(f"/ws/status/{user.id}?token={token}") as websocket:
        
        initial = websocket.receive_json()
        assert initial["type"] == "connection_status"
        
        websocket.send_text("ping")
        
        response = websocket.receive_json()
        assert response["type"] == "pong"