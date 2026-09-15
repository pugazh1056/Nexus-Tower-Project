import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers_procurement(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "m.vance@nexustower.internal", "password": "password123"},
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_inventory(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "s.chen@nexustower.internal", "password": "password123"},
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_production(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "k.novak@nexustower.internal", "password": "password123"},
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_logistics(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "d.morales@nexustower.internal", "password": "password123"},
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_admin(client):
    res = client.post(
        "/api/auth/login",
        json={"email": "ops-admin@nexustower.internal", "password": "password123"},
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
