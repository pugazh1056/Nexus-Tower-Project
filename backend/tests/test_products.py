def test_list_products(client, auth_headers_procurement):
    response = client.get("/api/products/", headers=auth_headers_procurement)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    skus = [p["sku"] for p in data]
    assert "MILK-001" in skus


def test_create_and_get_product(client, auth_headers_admin):
    new_product = {
        "sku": "TEST-CHOC-01",
        "name": "Belgian Dark Chocolate Bar 100g",
        "description": "70% cocoa artisanal chocolate",
        "category": "Confectionery",
        "unit": "bar",
        "reorder_level": 2500,
    }
    create_res = client.post("/api/products/", json=new_product, headers=auth_headers_admin)
    assert create_res.status_code == 201
    prod_data = create_res.json()
    prod_id = prod_data["id"]
    assert prod_data["sku"] == "TEST-CHOC-01"

    # Get by ID
    get_res = client.get(f"/api/products/{prod_id}", headers=auth_headers_admin)
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Belgian Dark Chocolate Bar 100g"

    # Update product
    update_res = client.put(
        f"/api/products/{prod_id}",
        json={"name": "Premium Belgian Dark Chocolate Bar 100g", "reorder_level": 3000},
        headers=auth_headers_admin,
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Premium Belgian Dark Chocolate Bar 100g"


def test_supplier_delay_reporting(client, auth_headers_procurement):
    sups_res = client.get("/api/suppliers/", headers=auth_headers_procurement)
    assert sups_res.status_code == 200
    suppliers = sups_res.json()
    assert len(suppliers) >= 1
    sup_id = suppliers[0]["id"]

    delay_res = client.post(
        f"/api/suppliers/{sup_id}/report-delay",
        json={"delay_days": 4, "reason": "Severe freeze at regional transit hub"},
        headers=auth_headers_procurement,
    )
    assert delay_res.status_code == 200
    data = delay_res.json()
    assert data["status"] == "delay_recorded"
    assert data["delay_days"] == 4
