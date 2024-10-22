# tests/test_product.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import ProductCreate, ProductUpdate
from bson import ObjectId

client = TestClient(app)

@pytest.fixture(scope="module")
def sample_product():
    return {
        "name": "Test Product",
        "description": "This is a test product.",
        "price": 99.99,
        "category": "Test Category"
    }

@pytest.fixture(scope="module")
async def created_product(sample_product):
    response = client.post("/api/v1/products/", json=sample_product)
    assert response.status_code == 201
    return response.json()

def test_create_product(sample_product):
    response = client.post("/api/v1/products/", json=sample_product)
    assert response.status_code == 201
    assert response.json()["name"] == sample_product["name"]
    assert response.json()["description"] == sample_product["description"]

def test_create_product_duplicate(created_product):
    response = client.post("/api/v1/products/", json=created_product)
    assert response.status_code == 400
    assert response.json()["detail"] == "Product with this name already exists"

def test_get_products():
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_product_by_id(created_product):
    product_id = created_product["_id"]
    response = client.get(f"/api/v1/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["name"] == created_product["name"]

def test_get_product_by_id_not_found():
    response = client.get(f"/api/v1/products/{ObjectId()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

def test_update_product_by_id(created_product):
    product_id = created_product["_id"]
    update_data = ProductUpdate(name="Updated Product", price=79.99)
    response = client.put(f"/api/v1/products/{product_id}", json=update_data.dict())
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Product"
    assert response.json()["price"] == "79.99"

def test_update_product_with_duplicate_name(created_product):
    # First create another product
    another_product = {
        "name": "Another Product",
        "description": "Another test product.",
        "price": 49.99,
        "category": "Another Category"
    }
    client.post("/api/v1/products/", json=another_product)
    
    # Attempt to update created_product to the name of another_product
    update_data = ProductUpdate(name="Another Product")
    response = client.put(f"/api/v1/products/{created_product['_id']}", json=update_data.dict())
    assert response.status_code == 400
    assert response.json()["detail"] == "Product with this name already exists"

def test_delete_product_by_id(created_product):
    product_id = created_product["_id"]
    response = client.delete(f"/api/v1/products/{product_id}")
    assert response.status_code == 204

def test_delete_product_not_found():
    response = client.delete(f"/api/v1/products/{ObjectId()}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"
