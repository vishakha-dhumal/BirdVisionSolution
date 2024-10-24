import sys
import os
import pytest

# Add the app directory to sys.path so the test module can find app.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, User  # Now this should work

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for testing
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create the tables
        yield client
        with app.app_context():
            db.drop_all()  # Clean up the database after tests

def test_register(client):
    response = client.post('/register', json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 201
    assert response.get_json() == {"msg": "User created successfully"}

def test_login(client):
    # First, register a user
    client.post('/register', json={"username": "testuser", "password": "testpass"})
    
    # Now, try to log in
    response = client.post('/login', json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert 'access_token' in response.get_json()

def test_create_product(client):
    # Log in to get the token
    client.post('/register', json={"username": "testuser", "password": "testpass"})
    login_response = client.post('/login', json={"username": "testuser", "password": "testpass"})
    token = login_response.get_json()['access_token']

    # Create a product using the token
    response = client.post('/products', json={"title": "Test Product", "description": "Test Description", "price": 10.0},
                           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert response.get_json() == {"msg": "Product created successfully"}