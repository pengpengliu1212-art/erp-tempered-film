# PM dispatch: ERP 钢化膜 — User Stories

> **Owner**: PM (lobsterai-team, role 2-of-7)
> **Dispatched**: 2026-07-09 by GM
> **Customer**: 钢化膜 (tempered glass film) ecommerce operator
> **Brief**: 老板要求测试 7 角色 AI 软件公司能否交付一个真实可跑的钢化膜电商 ERP (MVP)
> **Version**: v0.1.0

All acceptance criteria below are **verifiable** — QA can pass/fail each one.

---

## User Stories

### US-001 — List products (钢化膜 SKU catalog)
- **as_a** 商店运营 (store operator)
- **i_want** 列出所有钢化膜商品（含库存与价格）
- **so_that** 我能快速查看当前 SKU 目录

**Acceptance criteria**
- **Given** 商品库中已有 ≥1 个 SKU
  **When** 调用 `GET /api/products`
  **Then** 返回 `200` + JSON 数组，每个元素含 `id, name, size, material, price, stock`
- **Given** 商品库为空
  **When** 调用 `GET /api/products`
  **Then** 返回 `200` + 空数组 `[]`（不报错）

---

### US-002 — Add new tempered glass SKU (size, material, price)
- **as_a** 商店运营
- **i_want** 添加新钢化膜 SKU（尺寸 / 材质 / 价格 / 初始库存）
- **so_that** 我能上架新产品

**Acceptance criteria**
- **Given** 一个合法 body `{name, size, material, price, stock}`
  **When** 调用 `POST /api/products`
  **Then** 返回 `201` + 含新分配 `id` 的完整对象
- **Given** body 缺失必填字段（如无 `price`）
  **When** 调用 `POST /api/products`
  **Then** 返回 `400` + 校验错误信息，且不创建记录

---

### US-003 — Get product by ID
- **as_a** 客户 / 运营
- **i_want** 按 ID 查询单个商品
- **so_that** 我能查看该 SKU 的详情

**Acceptance criteria**
- **Given** 存在 `id = X` 的商品
  **When** 调用 `GET /api/products/{X}`
  **Then** 返回 `200` + 该商品完整对象
- **Given** `id` 不存在
  **When** 调用 `GET /api/products/{id}`
  **Then** 返回 `404` + 错误信息

---

### US-004 — Update product stock
- **as_a** 商店运营
- **i_want** 修改指定商品的库存数量
- **so_that** 系统库存能反映实际盘点结果

**Acceptance criteria**
- **Given** 存在商品 `id = X`
  **When** 调用 `PATCH /api/products/{X}/stock` + `{qty: 50}`
  **Then** 返回 `200` + 更新后对象，且 `stock == 50`
- **Given** `qty` 为负数
  **When** 调用 `PATCH /api/products/{X}/stock`
  **Then** 返回 `400`，库存保持不变

---

### US-005 — Place order (auto-decrement stock)
- **as_a** 客户 (customer)
- **i_want** 对某个钢化膜 SKU 下单，并自动扣减库存
- **so_that** 我能完成购买且库存自动同步

**Acceptance criteria**
- **Given** 商品 `id = X` 当前 `stock = 10`
  **When** 调用 `POST /api/orders` + `{product_id: X, qty: 3}`
  **Then** 返回 `201` + 订单对象，且该商品 `stock` 变为 `7`
- **Given** 下单成功
  **When** 再次 `GET /api/products/{X}`
  **Then** 返回的 `stock` 与扣减结果一致（持久化生效）

---

### US-006 — Reject order on insufficient stock
- **as_a** 系统 (system on behalf of运营)
- **i_want** 当下单数量超过可用库存时拒绝订单
- **so_that** 避免超卖

**Acceptance criteria**
- **Given** 商品 `id = X` 当前 `stock = 2`
  **When** 调用 `POST /api/orders` + `{product_id: X, qty: 5}`
  **Then** 返回 `400` + 库存不足错误信息
- **Given** 上述被拒订单
  **When** 再次 `GET /api/products/{X}`
  **Then** `stock` 仍为 `2`（未被扣减），且无订单被创建

---

### US-007 — List orders (history)
- **as_a** 商店运营
- **i_want** 列出所有历史订单
- **so_that** 我能查看销售/履约历史

**Acceptance criteria**
- **Given** 已有 ≥1 笔成功订单
  **When** 调用 `GET /api/orders`
  **Then** 返回 `200` + JSON 数组，每笔含 `id, product_id, qty, created_at`
- **Given** 尚无任何订单
  **When** 调用 `GET /api/orders`
  **Then** 返回 `200` + 空数组 `[]`

---

### US-008 — Low-stock query (restocking alert)
- **as_a** 商店运营
- **i_want** 查询库存低于阈值的商品
- **so_that** 我能及时补货，避免断货

**Acceptance criteria**
- **Given** 商品库中有 `stock` 高于和低于阈值的 SKU
  **When** 调用 `GET /api/products/low-stock?threshold=10`
  **Then** 返回 `200` + 仅包含 `stock < 10` 的商品列表
- **Given** 未提供 `threshold`
  **When** 调用 `GET /api/products/low-stock`
  **Then** 使用默认阈值（如 `10`）并返回 `200`

---

## Out of Scope (NOT in v0.1.0)

- 客户/用户账户管理（user table、注册、登录、鉴权）
- 支付集成（收款、退款、对账）
- 发货 / 物流 / 履约流程与运单跟踪
- 报表、销售分析、图表看板
- 多语言 / 国际化
- 钢化膜材质分类体系与型号适配（机型匹配表）
- 促销 / 优惠券 / 购物车多商品下单
- 订单取消 / 退货 / 库存回补流程
- 前端 UI（本版仅交付 REST API）

---

## Acceptance Threshold (整体验收线)

- [ ] 全部 8 个用户故事的 AC 在 `pytest` 中通过
- [ ] 库存扣减 (US-005) 与超卖拒绝 (US-006) 有针对性回归测试
- [ ] sandbox smoke test 全部 OK
- [ ] CI 在 `main` 分支为 green
