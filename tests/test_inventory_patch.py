import pytest

@pytest.fixture
def sample_product_id(client):
    response = client.post("/inventory", json={"name": "Test", "quantity": 10, "unit": "kg"})
    return response.json()["id"]

def test_patch_inventory_increase(client, sample_product_id):
    # Happy Path: Increase stock
    response = client.patch(f"/inventory/{sample_product_id}", json={"delta": 5})
    assert response.status_code == 200
    assert response.json()["quantity"] == 15

def test_patch_inventory_decrease(client, sample_product_id):
    # Happy Path: Decrease stock
    response = client.patch(f"/inventory/{sample_product_id}", json={"delta": -5})
    assert response.status_code == 200
    assert response.json()["quantity"] == 5

def test_patch_inventory_edge_case(client, sample_product_id):
    # Edge Case: Drop exactly to 0
    response = client.patch(f"/inventory/{sample_product_id}", json={"delta": -10})
    assert response.status_code == 200
    assert response.json()["quantity"] == 0

def test_patch_inventory_failure_negative(client, sample_product_id):
    # Failure Mode: Drop below 0 (business logic failure)
    response = client.patch(f"/inventory/{sample_product_id}", json={"delta": -15})
    assert response.status_code == 400
    assert "negativa" in response.json()["detail"].lower()

def test_patch_inventory_failure_not_found(client):
    # Failure Mode: Product not found
    response = client.patch("/inventory/fake-id", json={"delta": 5})
    assert response.status_code == 404
