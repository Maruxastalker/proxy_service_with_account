def test_get_all_vms(client, test_user, test_vm):
    user, token = test_user
    
    response = client.get(
        "/api/v1/admin/vms/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_create_vm(client, test_user):
    user, token = test_user
    
    response = client.post(
        "/api/v1/admin/vms/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "New Proxy",
            "host": "new.proxy.com",
            "port": 3128,
            "protocol": "http"
        }
    )
    
    assert response.status_code == 201
    assert response.json()["name"] == "New Proxy"
    assert response.json()["host"] == "new.proxy.com"


def test_delete_vm(client, test_user, test_vm):
    user, token = test_user
    vm_id = test_vm.id
    
    response = client.delete(
        f"/api/v1/admin/vms/{vm_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "VM deleted successfully" in response.text


def test_activate_key_success(client, test_user, test_vm):
    user, token = test_user
    
    key_response = client.get(
        "/api/v1/users/my-key",
        headers={"Authorization": f"Bearer {token}"}
    )
    activation_key = key_response.json()["activation_key"]
    
    response = client.post(
        "/api/v1/activate",
        headers={"Authorization": f"Bearer {token}"},
        json={"activation_key": activation_key}
    )
    assert response.status_code == 200
    assert "host" in response.json()
    assert "port" in response.json()
    assert "protocol" in response.json()


def test_activate_key_invalid(client, test_user):
    user, token = test_user
    
    response = client.post(
        "/api/v1/activate",
        headers={"Authorization": f"Bearer {token}"},
        json={"activation_key": "invalid-key-123"}
    )
    assert response.status_code == 403
    assert "Invalid activation key" in response.text


def test_disconnect(client, test_user, test_vm):
    user, token = test_user
    
    key_response = client.get(
        "/api/v1/users/my-key",
        headers={"Authorization": f"Bearer {token}"}
    )
    activation_key = key_response.json()["activation_key"]
    
    client.post(
        "/api/v1/activate",
        headers={"Authorization": f"Bearer {token}"},
        json={"activation_key": activation_key}
    )
    
    response = client.post(
        "/api/v1/disconnect",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "Disconnected" in response.text