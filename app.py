from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields

app = Flask(__name__)
api = Api(app, version="1.0", title="Inventory API",
          description="Warehouse Inventory Management API with Swagger")

ns = api.namespace("products", description="Product operations")

# Product Model for Swagger
product_model = api.model("Product", {
    "id": fields.Integer(readOnly=True, description="Product ID"),
    "name": fields.String(required=True, description="Product name"),
    "description": fields.String(required=True, description="Product description"),
    "stock_quantity": fields.Integer(required=True, description="Stock quantity"),
    "low_stock_threshold": fields.Integer(required=False, description="Low stock threshold"),
})

# In-memory DB
products = {}
current_id = 1


# Helper function
def get_product_or_404(pid):
    if pid not in products:
        api.abort(404, f"Product {pid} not found")
    return products[pid]


@ns.route("/")
class ProductList(Resource):
    @ns.marshal_list_with(product_model)
    def get(self):
        """List all products"""
        return list(products.values())

    @ns.expect([product_model])  # 👈 Expecting a list of products
    @ns.marshal_list_with(product_model, code=201)
    def post(self):
        """Create one or more products"""
        global current_id
        payload = api.payload

        # If a single product dict is sent, wrap it into a list
        if isinstance(payload, dict):
            payload = [payload]

        created = []
        for data in payload:
            data["id"] = current_id
            data["low_stock_threshold"] = data.get("low_stock_threshold", 5)
            products[current_id] = data
            created.append(data)
            current_id += 1

        return created, 201


@ns.route("/<int:pid>")
@ns.response(404, "Product not found")
class Product(Resource):
    @ns.marshal_with(product_model)
    def get(self, pid):
        """Get a product by ID"""
        return get_product_or_404(pid)

    @ns.expect(product_model)
    @ns.marshal_with(product_model)
    def put(self, pid):
        """Update product details"""
        product = get_product_or_404(pid)
        data = api.payload
        product.update(data)
        if product["stock_quantity"] < 0:
            api.abort(400, "Stock quantity cannot be negative")
        return product

    def delete(self, pid):
        """Delete a product"""
        get_product_or_404(pid)
        del products[pid]
        return {"message": "Product deleted"}, 200


@ns.route("/<int:pid>/increase")
class IncreaseStock(Resource):
    def post(self, pid):
        """Increase stock"""
        product = get_product_or_404(pid)
        amount = request.json.get("amount", 0)
        product["stock_quantity"] += amount
        return product


@ns.route("/<int:pid>/decrease")
class DecreaseStock(Resource):
    def post(self, pid):
        """Decrease stock"""
        product = get_product_or_404(pid)
        amount = request.json.get("amount", 0)
        if product["stock_quantity"] < amount:
            api.abort(400, "Insufficient stock")
        product["stock_quantity"] -= amount
        return product


@ns.route("/low-stock")
class LowStock(Resource):
    def get(self):
        """List all products below low stock threshold"""
        low_stock = [p for p in products.values() if p["stock_quantity"] <= p["low_stock_threshold"]]
        return low_stock


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
