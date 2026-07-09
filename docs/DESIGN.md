# ERP 钢化膜电商 — Design (Architect)

> **Owner**: Architect
> **Dispatched**: 2026-07-09 by GM

## Stack (Architect's choice)

- **Backend**: FastAPI (Python 3.12)
  - Auto OpenAPI docs at /docs
  - Pydantic validation
  - Async-ready
- **DB**: SQLite (v0.1.0) → Postgres (v0.2.0)
  - SQLModel (SQLAlchemy + Pydantic)
  - One file: `erp.db` for dev, env-configurable
- **Tests**: pytest + httpx (for TestClient)
- **CI**: GitHub Actions
  - Python 3.12
  - pip install -r requirements.txt
  - pytest --maxfail=1
- **Frontend**: 0 (MVP 后端 only)
- **Container**: alpine:latest + Python 3.12
- **Git workflow**: dev branch + main + GH Actions

## 5-phase framework (per OpenClaw `system-design` skill)

1. **Requirements** (PM) — 8 user stories in `docs/USER_STORIES.md`
2. **High-Level Design** (Architect) — REST API + SQLite + Python
3. **Deep Dive** (Architect) — Models: Product, Order; Routes: products/, orders/
4. **Scale/Reliability** (DevOps) — MVP scale: 1-10 concurrent users
5. **Trade-off** (Architect) — Chose SQLite over Postgres for MVP simplicity

## Component Diagram

```
[curl/Postman] → [FastAPI on :8000] → [SQLModel] → [SQLite file]
                          ↓
                    [Pydantic schemas]
                          ↓
                  [/docs OpenAPI UI]
```

## API Endpoints (Architect's design)

| Method | Path | Purpose |
|---|---|---|
| GET    | /api/health | Health check (DevOps for CI) |
| GET    | /api/products | List all products (US-001) |
| POST   | /api/products | Add new product (US-002) |
| GET    | /api/products/{id} | Get product by ID (US-003) |
| PATCH  | /api/products/{id}/stock | Update stock (US-004) |
| GET    | /api/products/low-stock?threshold=N | List low-stock products (US-008) |
| POST   | /api/orders | Create order (US-005) |
| GET    | /api/orders | List orders (US-007) |

## Data Model (Data's design)

```sql
CREATE TABLE products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  sku TEXT UNIQUE NOT NULL,
  size TEXT NOT NULL,           -- e.g., "iPhone 15", "Galaxy S24"
  material TEXT NOT NULL,        -- e.g., "9H tempered glass", "matte"
  price_cents INTEGER NOT NULL,  -- store in cents to avoid float
  stock INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id INTEGER NOT NULL,
  qty INTEGER NOT NULL,
  total_cents INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',  -- pending/paid/cancelled
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (product_id) REFERENCES products(id)
);
```

## Trade-off Analysis

| Option | Pros | Cons | Decision |
|---|---|---|---|
| SQLite vs Postgres | Zero-setup, file-based, fast for MVP | Single-writer, no multi-DC | **SQLite (v0.1.0)** |
| SQLModel vs SQLAlchemy + Pydantic | Single-source models, less duplication | Newer, fewer examples | **SQLModel** |
| Alpine + Python 3.12 vs full Python image | Smaller (50MB vs 350MB) | More build steps | **alpine + Python 3.12** |
| GH Actions matrix (ubuntu/windows/macos) vs ubuntu-only | Cross-platform CI | Slower, more failures | **ubuntu-only for MVP** |

## Risk Register

| Risk | Mitigation |
|---|---|
| SQLite file conflicts in CI | Use tmpfs or per-test DB file |
| Price in cents (overflow) | Use INTEGER, not DECIMAL |
| Stock race conditions | Acceptable for MVP; v0.2 use SELECT FOR UPDATE |
| Foreign-key constraint failure on order | Pydantic validates product_id exists first |
