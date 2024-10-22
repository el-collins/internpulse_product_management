# Product Management System API

A robust RESTful API for managing products, built with FastAPI and MongoDB. This system provides complete CRUD operations with advanced filtering capabilities for product management.

## 🚀 Features

- Create new products with duplicate name checking
- Retrieve products with flexible filtering options:
  - Name search (case-insensitive)
  - Category search (case-insensitive)
  - Price range filtering
- Update products with partial updates support
- Delete products
- Decimal price handling for precision
- Comprehensive error handling
- MongoDB integration
- Async/await implementation

## 📋 API Endpoints

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/products/` | Create a new product |
| GET | `/products/` | Get all products with optional filters |
| GET | `/products/{product_id}` | Get product by ID |
| PUT | `/products/{product_id}` | Update product by ID |
| DELETE | `/products/{product_id}` | Delete product by ID |

### Request/Response Examples

#### Create Product
```http
POST /products/
Content-Type: application/json

{
    "name": "Sample Product",
    "price": "29.99",
    "category": "Electronics"
}
```

Response:
```json
{
    "id": "507f1f77bcf86cd799439011",
    "name": "Sample Product",
    "price": "29.99",
    "category": "Electronics"
}
```

#### Get Products with Filters
```http
GET /products/?name=sample&category=electronics&min_price=20&max_price=100
```

## 🛠️ Technology Stack

- Python 3.9+
- FastAPI
- MongoDB
- Poetry (dependency management)
- Motor (async MongoDB driver)
- Pydantic (data validation)

## 🏗️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/product-management-api.git
cd product-management-api
```

2. Install Poetry if you haven't already:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies:
```bash
poetry install
```

## 📦 Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.9"
fastapi = "^0.104.0"
uvicorn = "^0.24.0"
motor = "^3.3.1"
pydantic = "^2.4.2"
python-dotenv = "^1.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.1"
httpx = "^0.25.0"
```

## 🚦 Running the Application

1. Set up your environment variables in `.env`:
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=products_db
```

2. Start the application:
```bash
poetry run uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

Interactive API documentation will be available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔍 Error Handling

The API implements standard HTTP status codes:

- `200`: Success
- `201`: Resource created
- `204`: No content (successful deletion)
- `400`: Bad request (invalid ID, duplicate name)
- `404`: Resource not found
- `422`: Validation error

Error Response Example:
```json
{
    "detail": "Product with this name already exists"
}
```

## 📚 Project Structure

```
product-management-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   └── routers/
│       └── products.py
├── tests/
│   ├── __init__.py
│   ├── test_products.py
│   └── conftest.py
├── pyproject.toml
├── poetry.lock
├── README.md
└── .env
```

## 💡 Implementation Notes

### Price Handling
- Prices are stored as strings in MongoDB to preserve decimal precision
- Automatic conversion between Decimal and string formats
- Validation ensures non-negative prices

### Search Features
- Case-insensitive search for name and category
- Price range filtering with optional minimum and maximum values
- Regular expression support for partial matches

### Data Validation
- Input validation using Pydantic models
- Automatic request body parsing and response serialization
- Comprehensive error messages for invalid inputs

## 🧪 Testing

Run the test suite:
```bash
poetry run pytest
```

With coverage:
```bash
poetry run pytest --cov=app tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Install dependencies with `poetry install`
4. Make your changes
5. Run tests with `poetry run pytest`
6. Format code with `poetry run black .`
7. Commit changes
8. Push to the branch
9. Open a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.