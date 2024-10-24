from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from models import db, User, Product
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
jwt = JWTManager(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"msg": "Username and password are required"}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username, password=password).first()
    if user:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200

    return jsonify({"msg": "Invalid credentials"}), 401

@app.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    products = Product.query.all()
    return jsonify([{'id': p.id, 'title': p.title, 'description': p.description, 'price': p.price} for p in products])

@app.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    price = data.get('price')

    new_product = Product(title=title, description=description, price=price)
    db.session.add(new_product)
    db.session.commit()

    return jsonify({"msg": "Product created successfully"}), 201

@app.route('/products/<int:id>', methods=['PUT'])
@jwt_required()
def update_product(id):
    product = Product.query.get(id)
    if product is None:
        return abort(404)

    data = request.get_json()
    product.title = data.get('title', product.title)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)

    db.session.commit()
    return jsonify({"msg": "Product updated successfully"}), 200

@app.route('/products/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    product = Product.query.get(id)
    if product is None:
        return abort(404)

    db.session.delete(product)
    db.session.commit()
    return jsonify({"msg": "Product deleted successfully."}), 200

if __name__ == '__main__':
    app.run(debug=True)
