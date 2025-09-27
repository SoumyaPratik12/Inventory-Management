# Inventory API (Flask + Swagger + Docker)

A backend API to manage products in a warehouse.

## 🚀 Features
- CRUD for products
- Stock increase/decrease with validation
- Low stock listing
- Swagger UI docs
- Dockerized for easy deployment
- Unit tests with pytest

## 🔧 Run Locally
```bash
docker build -t inventory-api .
docker run -d -p 5000:5000 --name inventory inventory-api
```

Now visit: [http://localhost:5000/](http://localhost:5000/)

## 🧪 Run Tests
```bash
docker run --rm inventory-api pytest
```
