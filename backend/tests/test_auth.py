def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "Nexus Tower"


def test_login_success(client):
    response = client.post(
        "/api/auth/login",
        json={"email": "m.vance@nexustower.internal", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "m.vance@nexustower.internal"
    assert data["user"]["role"] == "procurement"


def test_get_me(client, auth_headers_procurement):
    response = client.get("/api/auth/me", headers=auth_headers_procurement)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "m.vance@nexustower.internal"
    assert data["full_name"] == "Marcus Vance"


def test_unauthorized_access(client):
    response = client.get("/api/products/")
    assert response.status_code == 401


def test_logout(client):
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
