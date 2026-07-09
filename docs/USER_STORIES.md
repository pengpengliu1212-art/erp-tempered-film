# ERP 钢化膜电商 — User Stories (PM)

> **Owner**: PM (lobsterai-team 7 角色)
> **Dispatched**: 2026-07-09 by GM
> **Brief**: 老板要"测试团队跑通"——MVP 钢化膜电商 ERP

## User Stories

### US-001: 列出商品 (PM)
- **as a** 商店运营
- **i want** 列出所有钢化膜商品（含库存）
- **so that** 我能快速查看当前 SKU 列表
- **AC**: GET /api/products 返回 200 + JSON 数组

### US-002: 添加钢化膜 SKU (Coder)
- **as a** 商店运营
- **i want** 添加新钢化膜 SKU（含尺寸/材质/价格）
- **so that** 上架新产品
- **AC**: POST /api/products + JSON body → 201 + 新 ID

### US-003: 查单个商品 (Coder)
- **as a** 客户/运营
- **i want** 按 ID 查商品
- **so that** 看详情
- **AC**: GET /api/products/{id} → 200 + 完整对象

### US-004: 更新库存 (Coder)
- **as a** 商店运营
- **i want** 修改商品库存数
- **so that** 反映实际库存
- **AC**: PATCH /api/products/{id}/stock + {qty} → 200 + 更新后对象

### US-005: 下订单 (Coder)
- **as a** 客户
- **i want** 下单（含自动扣库存）
- **so that** 买钢化膜
- **AC**: POST /api/orders + {product_id, qty} → 201 + 库存自动减

### US-006: 库存不足拒绝订单 (QA)
- **as a** 系统
- **i want** 库存不足时拒绝订单
- **so that** 不超卖
- **AC**: POST /api/orders + qty > stock → 400 + 错误信息

### US-007: 列出订单 (Coder)
- **as a** 商店运营
- **i want** 列出所有订单
- **so that** 查历史
- **AC**: GET /api/orders → 200 + JSON 数组

### US-008: 库存查询 (Coder)
- **as a** 商店运营
- **i want** 查当前库存（按商品）
- **so that** 知道哪些 SKU 要补
- **AC**: GET /api/products/low-stock?threshold=10 → 200 + 低库存列表

## Out of Scope (v0.1.0)

- 客户管理（user table）
- 支付集成
- 发货流程
- 报表
- 多语言
- 钢化膜材质分类（HDPE/玻璃/陶瓷）

## Acceptance Threshold

- 所有 8 个 AC 在 `pytest` 中通过
- 6 角色 sandbox smoke test 全 OK
- CI green on `main` branch
