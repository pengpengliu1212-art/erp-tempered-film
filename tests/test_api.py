"""QA: API tests for all 8 user stories"""
from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    """US-000: Health check for CI smoke test."""
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_frontend_home(client: TestClient) -> None:
    """Frontend dashboard renders."""
    r = client.get("/")
    assert r.status_code == 200
    assert "ERP 钢化膜" in r.text


def test_list_products_empty(client: TestClient) -> None:
    """US-001: List products (empty initially)."""
    r = client.get("/api/products")
    assert r.status_code == 200
    assert r.json() == []


def test_create_product(client: TestClient) -> None:
    """US-002: Add new product SKU."""
    r = client.post(
        "/api/products",
        json={
            "name": "iPhone 15 钢化膜",
            "sku": "IP15-TG-001",
            "size": "iPhone 15",
            "material": "9H tempered glass",
            "price_cents": 2999,
            "stock": 100,
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["sku"] == "IP15-TG-001"
    assert data["stock"] == 100
    assert data["id"] > 0


def test_create_product_duplicate_sku(client: TestClient) -> None:
    """US-002 edge: duplicate SKU rejected."""
    payload = {
        "name": "Test",
        "sku": "DUP-001",
        "size": "iPhone 15",
        "material": "9H",
        "price_cents": 1000,
        "stock": 10,
    }
    assert client.post("/api/products", json=payload).status_code == 201
    r = client.post("/api/products", json=payload)
    assert r.status_code == 409


def test_get_product_by_id(client: TestClient) -> None:
    """US-003: Get product by ID."""
    create = client.post(
        "/api/products",
        json={
            "name": "Test",
            "sku": "TEST-003",
            "size": "iPhone 15",
            "material": "9H",
            "price_cents": 1000,
            "stock": 50,
        },
    )
    pid = create.json()["id"]
    r = client.get(f"/api/products/{pid}")
    assert r.status_code == 200
    assert r.json()["sku"] == "TEST-003"


def test_get_product_not_found(client: TestClient) -> None:
    """US-003 edge: 404 for missing ID."""
    r = client.get("/api/products/99999")
    assert r.status_code == 404


def test_update_stock(client: TestClient) -> None:
    """US-004: Update product stock."""
    create = client.post(
        "/api/products",
        json={
            "name": "Test",
            "sku": "STK-001",
            "size": "X",
            "material": "Y",
            "price_cents": 100,
            "stock": 10,
        },
    )
    pid = create.json()["id"]
    r = client.patch(f"/api/products/{pid}/stock?new_stock=200")
    assert r.status_code == 200
    assert r.json()["stock"] == 200


def test_create_order_decrements_stock(client: TestClient) -> None:
    """US-005: Order auto-decrements stock."""
    create = client.post(
        "/api/products",
        json={
            "name": "Test",
            "sku": "ORD-001",
            "size": "X",
            "material": "Y",
            "price_cents": 1000,
            "stock": 50,
        },
    )
    pid = create.json()["id"]
    r = client.post("/api/orders", json={"product_id": pid, "qty": 5})
    assert r.status_code == 201
    assert r.json()["total_cents"] == 5000
    # Stock should now be 45
    r2 = client.get(f"/api/products/{pid}")
    assert r2.json()["stock"] == 45


def test_create_order_insufficient_stock(client: TestClient) -> None:
    """US-006: Insufficient stock rejected."""
    create = client.post(
        "/api/products",
        json={
            "name": "Test",
            "sku": "ORD-002",
            "size": "X",
            "material": "Y",
            "price_cents": 1000,
            "stock": 3,
        },
    )
    pid = create.json()["id"]
    r = client.post("/api/orders", json={"product_id": pid, "qty": 10})
    assert r.status_code == 400
    assert "Insufficient stock" in r.json()["detail"]


def test_create_order_product_not_found(client: TestClient) -> None:
    """US-006 edge: nonexistent product rejected."""
    r = client.post("/api/orders", json={"product_id": 99999, "qty": 1})
    assert r.status_code == 404


def test_list_orders(client: TestClient) -> None:
    """US-007: List orders."""
    r = client.get("/api/orders")
    assert r.status_code == 200
    assert r.json() == []


def test_low_stock(client: TestClient) -> None:
    """US-008: Low stock query."""
    # Create 3 products with different stock
    for i, stock in enumerate([5, 50, 1], start=1):
        client.post(
            "/api/products",
            json={
                "name": f"P{i}",
                "sku": f"LS-{i:03d}",
                "size": "X",
                "material": "Y",
                "price_cents": 100,
                "stock": stock,
            },
        )
    r = client.get("/api/products/special/low-stock?threshold=10")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2  # stock 5 and 1 are <= 10
    skus = {p["sku"] for p in data}
    assert skus == {"LS-001", "LS-003"}
