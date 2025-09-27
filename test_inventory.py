import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_create_product(client):
    response = client.post("/products/", json={
        "name": "Laptop",
        "description": "Dell XPS",
        "stock_quantity": 10
    })
    assert response.status_code == 201
    assert response.get_json()["name"] == "Laptop"

def test_increase_stock(client):
    client.post("/products/", json={
        "name": "Mouse",
        "description": "Logitech",
        "stock_quantity": 5
    })
    response = client.post("/products/2/increase", json={"amount": 3})
    assert response.status_code == 200
    assert response.get_json()["stock_quantity"] == 8

def test_decrease_stock_fail(client):
    response = client.post("/products/2/decrease", json={"amount": 20})
    assert response.status_code == 400
