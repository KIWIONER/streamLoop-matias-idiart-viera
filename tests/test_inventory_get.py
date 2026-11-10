def test_get_inventory_empty(client):
    # Happy Path
    response = client.get("/inventory")
    assert response.status_code == 200
    assert response.json() == []

def test_get_inventory_with_items(client):
    # Happy Path
    client.post("/inventory", json={"name": "Test Item", "quantity": 10, "unit": "kg"})
    response = client.get("/inventory")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Item"

def test_get_alerts(client):
    # Happy Path
    client.post("/inventory", json={"name": "Low Stock", "quantity": 5, "unit": "kg"})
    client.post("/inventory", json={"name": "High Stock", "quantity": 50, "unit": "kg"})
    
    # threshold default is 10
    response = client.get("/inventory/alerts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Low Stock"

def test_get_alerts_edge_case(client):
    # Edge Case: threshold 0
    client.post("/inventory", json={"name": "Zero Stock", "quantity": 0, "unit": "kg"})
    response = client.get("/inventory/alerts", params={"threshold": 0})
    assert response.status_code == 200
    # Alerts are < threshold, so 0 is not < 0
    assert len(response.json()) == 0
