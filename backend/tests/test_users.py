def test_get_me(client, test_user):
    user, token = test_user
    
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_get_me_unauthorized(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 403


def test_change_password(client, test_user):
    user, token = test_user
    
    response = client.post(
        "/api/v1/users/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "old_password": "test123",
            "new_password": "newpassword123"
        }
    )
    assert response.status_code == 200
    assert "Password changed successfully" in response.text


def test_change_password_wrong_old(client, test_user):
    user, token = test_user
    
    response = client.post(
        "/api/v1/users/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "old_password": "wrongpassword",
            "new_password": "newpassword123"
        }
    )
    assert response.status_code == 400
    assert "Incorrect old password" in response.text


def test_get_my_key(client, test_user):
    user, token = test_user
    
    response = client.get(
        "/api/v1/users/my-key",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "activation_key" in response.json()


def test_renew_key(client, test_user):
    user, token = test_user
    
    response = client.post(
        "/api/v1/users/renew-key",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "activation_key" in response.json()
    assert "expires_at" in response.json()