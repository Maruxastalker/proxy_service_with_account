import pytest


def test_register_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "password_confirm": "password123"
        }
    )
    assert response.status_code == 201
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_register_password_mismatch(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser2@example.com",
            "password": "password123",
            "password_confirm": "different"
        }
    )
    assert response.status_code == 400
    assert "Passwords do not match" in response.text


def test_register_duplicate_email(client, test_user):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "test123",
            "password_confirm": "test123"
        }
    )
    assert response.status_code == 400
    assert "Email already registered" in response.text


def test_login_success(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "test123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.text


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "password"
        }
    )
    assert response.status_code == 401