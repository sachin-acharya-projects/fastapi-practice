from fastapi import status
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/api/v1/health/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


def test_create_product() -> None:
    payload = {
        "label": "Test Product",
        "rate": 5,
        "quantity": 10,
    }
    response = client.post(
        "/api/v1/products/", data=payload, headers={"Content-Type": "application/json"}
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["label"] == payload["label"]
    assert response.json()["rate"] == payload["rate"]
    assert response.json()["quantity"] == payload["quantity"]
