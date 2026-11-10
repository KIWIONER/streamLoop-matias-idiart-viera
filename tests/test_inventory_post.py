def test_create_product_happy_path(client):
    # Happy Path
    payload = {"name": "Café", "quantity": 20, "unit": "kg"}
    response = client.post("/inventory", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Café"
    assert "id" in data

def test_create_product_edge_case(client):
    # Edge Case: quantity 0
    payload = {"name": "Leche", "quantity": 0, "unit": "L"}
    response = client.post("/inventory", json=payload)
    assert response.status_code == 200
    assert response.json()["quantity"] == 0

def test_create_product_failure(client):
    # Failure Mode: Missing fields
    payload = {"name": "Café"}
    response = client.post("/inventory", json=payload)
    assert response.status_code == 422  # Unprocessable Entity (FastAPI validation)
