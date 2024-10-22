# tests/test_product.py
import pytest
from app.main import app
from app.database import get_db
from decimal import Decimal
from bson import ObjectId
import motor.motor_asyncio
from typing import AsyncGenerator, Generator
import pytest_asyncio
import httpx



# Mock database setup
@pytest_asyncio.fixture
async def mock_db() -> AsyncGenerator:
    test_client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")
    test_db = test_client.test_product_management
    
    async def override_get_db():
        yield test_db

    
    app.dependency_overrides[get_db] = override_get_db
    await test_db.client.drop_database("test_product_management")  # Ensure clean DB before test
    try:
        yield test_db
    finally:
        await test_db.client.drop_database("test_product_management")  # Cleanup after test
        app.dependency_overrides.clear()

# Test client setup
@pytest_asyncio.fixture
async def client() -> AsyncGenerator:
    async with httpx.AsyncClient(app=app) as c:
        yield c

# Test data fixtures
@pytest.fixture
def valid_product():
    return {
        "name": "Test Product",
        "category": "Test Category",
        "price": "99.99"
    }

@pytest.fixture
def product_list():
    return [
        {"name": "Budget Product", "category": "Electronics", "price": "10.00"},
        {"name": "Premium Product", "category": "Electronics", "price": "999.99"},
        {"name": "Mid-range Product", "category": "Home", "price": "49.99"},
        {"name": "Luxury Item", "category": "Fashion", "price": "1999.99"}
    ]

# CREATE Tests
@pytest.mark.asyncio
async def test_create_product_success(client, mock_db, valid_product):
    response = client.post("/api/v1/products/", json=valid_product)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == valid_product["name"]
    assert data["category"] == valid_product["category"]
    assert Decimal(data["price"]) == Decimal(valid_product["price"])
    assert "_id" in data

@pytest.mark.asyncio
async def test_create_product_invalid_price(client, mock_db, valid_product):
    valid_product["price"] = "-10.00"
    response = client.post("/api/v1/products/", json=valid_product)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_product_missing_fields(client, mock_db):
    response = client.post("/api/v1/products/", json={"name": "Incomplete Product"})
    assert response.status_code == 422

# READ Tests
@pytest.mark.asyncio
async def test_get_products_with_pagination(client, mock_db, product_list):
    # Create multiple products
    for product in product_list:
        client.post("/api/v1/products/", json=product)
    
    # Test with limit and skip
    response = client.get("/api/v1/products/?skip=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

@pytest.mark.asyncio
async def test_get_products_price_range(client, mock_db, product_list):
    # Create multiple products
    for product in product_list:
        client.post("/api/v1/products/", json=product)
    
    response = client.get("/api/v1/products/?min_price=100&max_price=1000")
    assert response.status_code == 200
    data = response.json()
    assert all(100 <= Decimal(p["price"]) <= 1000 for p in data)

@pytest.mark.asyncio
async def test_get_products_category_search(client, mock_db, product_list):
    # Create multiple products
    for product in product_list:
        client.post("/api/v1/products/", json=product)
    
    response = client.get("/api/v1/products/?category=Electronics")
    assert response.status_code == 200
    data = response.json()
    assert all("Electronics" in p["category"] for p in data)

# UPDATE Tests
@pytest.mark.asyncio
async def test_update_product_partial(client, mock_db, valid_product):
    # Create product
    create_response = client.post("/api/v1/products/", json=valid_product)
    product_id = create_response.json()["_id"]
    
    # Partial update - only price
    update_data = {"price": "149.99"}
    response = client.put(f"/api/v1/products/{product_id}", json=update_data)
    assert response.status_code == 200
    assert Decimal(response.json()["price"]) == Decimal("149.99")
    assert response.json()["name"] == valid_product["name"]  # Original name unchanged

@pytest.mark.asyncio
async def test_update_product_invalid_fields(client, mock_db, valid_product):
    # Create product
    create_response = client.post("/api/v1/products/", json=valid_product)
    product_id = create_response.json()["_id"]
    
    # Update with invalid field
    update_data = {"invalid_field": "value"}
    response = client.put(f"/api/v1/products/{product_id}", json=update_data)
    assert response.status_code == 422

# DELETE Tests
@pytest.mark.asyncio
async def test_delete_product_cascade(client, mock_db, valid_product):
    # Create product
    create_response = client.post("/api/v1/products/", json=valid_product)
    product_id = create_response.json()["_id"]
    
    # Delete product
    delete_response = client.delete(f"/api/v1/products/{product_id}")
    assert delete_response.status_code == 204
    
    # Verify product is gone
    get_response = client.get(f"/api/v1/products/{product_id}")
    assert get_response.status_code == 404

# Error Handling Tests
@pytest.mark.asyncio
async def test_invalid_object_id_formats(client, mock_db):
    invalid_ids = ["123", "invalid_id", "12345678901"]
    
    for invalid_id in invalid_ids:
        get_response = client.get(f"/api/v1/products/{invalid_id}")
        assert get_response.status_code == 400
        assert get_response.json()["detail"] == "Invalid product ID"
        
        delete_response = client.delete(f"/api/v1/products/{invalid_id}")
        assert delete_response.status_code == 400
        assert delete_response.json()["detail"] == "Invalid product ID"

@pytest.mark.asyncio
async def test_product_not_found_scenarios(client, mock_db):
    valid_but_nonexistent_id = str(ObjectId())
    
    # Test GET
    get_response = client.get(f"/api/v1/products/{valid_but_nonexistent_id}")
    assert get_response.status_code == 404
    
    # Test DELETE
    delete_response = client.delete(f"/api/v1/products/{valid_but_nonexistent_id}")
    assert delete_response.status_code == 404
    
    # Test UPDATE
    update_response = client.put(
        f"/api/v1/products/{valid_but_nonexistent_id}",
        json={"name": "Updated Name"}
    )
    assert update_response.status_code == 404