import pytest
import os
from fastapi.testclient import TestClient

# Mock the database file BEFORE importing the app
import api.db
# Use a temporary testing file
TEST_DB_FILE = "test_products.csv"
api.db.DB_FILE = TEST_DB_FILE

from api.app import app

@pytest.fixture(autouse=True)
def setup_teardown_db():
    # Setup: Initialize a clean test DB before each test
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
    api.db.init_db()
    
    yield  # Run the test
    
    # Teardown: Clean up the test DB after the test
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)

@pytest.fixture
def client():
    # Return the TestClient for FastAPI
    return TestClient(app)
