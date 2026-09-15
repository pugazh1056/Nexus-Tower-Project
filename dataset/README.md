# Nexus Tower: FMCG Supply Chain Operations Dataset

> **Clean Shared Dataset Package for SNS Agent Workbench Integration**  
> *Source of Truth: `backend/sql/002_demo_seed_data.sql`*

---

## 1. Purpose of the Dataset

This dataset provides a standardized, normalized relational operations package designed for the **SNS Agent Workbench** team and autonomous supply chain agents. It captures real-world FMCG (Fast-Moving Consumer Goods) manufacturing and distribution dynamics across four core functional domains:

1. **Procurement Operations**: Supplier capacity, purchase orders, vendor delays, and emergency sourcing.
2. **Inventory Management**: Warehouse stock positions, safety stock floors, reserved allocations, and runway calculations.
3. **Production Scheduling**: Shop floor work orders, line throughput, machinery bottlenecks, and batch sequencing.
4. **Logistics & Dispatch**: Inbound/outbound freight tracking, intermodal delays, reefer transport, and corridor re-routing.

This dataset enables multi-agent orchestration, anomaly detection, automated root-cause analysis, and cross-domain prescriptive action generation.

> **Notice**: All records in this package are **synthetic demonstration data** created for benchmarking and system integration.

---

## 2. Table Catalog & Schema Descriptions

| File | Primary Key | Description | Record Count |
| :--- | :--- | :--- | :---: |
| `products.csv` | `id` (UUID) | Master catalog of finished FMCG goods and raw feedstock (Milk, Biscuits, Mango Juice). | 3 |
| `suppliers.csv` | `id` (UUID) | Directory of certified global raw material suppliers, packaging vendors, and freight carriers. | 4 |
| `inventory.csv` | `id` (UUID) | Physical stock balances across cold storage hubs, dry bulk units, and distribution centers. | 3 |
| `purchase_orders.csv` | `id` (UUID) | Inbound procurement orders, vendor assignment, commitment dates, and monetary totals. | 3 |
| `purchase_order_items.csv` | `id` (UUID) | Itemized line-item quantities, unit prices, and extended amounts linked to purchase orders. | 3 |
| `production_orders.csv` | `id` (UUID) | Factory floor batch manufacturing runs, planned/actual start dates, and line progress. | 3 |
| `shipments.csv` | `id` (UUID) | In-transit dispatches, telematics tracking numbers, origin/destination hubs, and carrier SLAs. | 3 |
| `events.csv` | `id` (UUID) | Real-time telemetry audit events, sensor triggers, status shifts, and domain alerts. | 5 |
| `inventory_events.csv` | `event_id` (Text) | High-throughput inventory stream schema formatted specifically for SNS Agent Workbench feeds. | 3 |

---

## 3. Foreign Key & Entity Relationship Matrix

All relationships in this dataset strictly reflect relational integrity:

```
[suppliers] <─── (supplier_id) ─── [purchase_orders] <─── (purchase_order_id) ─── [purchase_order_items]
     ▲                                   ▲                                                  │
     │                                   │ (purchase_order_id)                              │ (product_id)
     │ (supplier_id)                     │                                                  ▼
[shipments] ─────────────────────────────┘                                             [products]
                                                                                            ▲
[inventory] ─────────────── (product_id) ───────────────────────────────────────────────────┤
                                                                                            │ (product_id)
[production_orders] ─────── (product_id) ───────────────────────────────────────────────────┘

[events] ────────────────── (entity_id) ───> references [inventory | purchase_orders | production_orders | shipments]
[inventory_events] ──────── (entity_id) ───> references [products.sku]
```

### Relational References
- `inventory.product_id` &rarr; `products.id`
- `purchase_orders.supplier_id` &rarr; `suppliers.id`
- `purchase_order_items.purchase_order_id` &rarr; `purchase_orders.id`
- `purchase_order_items.product_id` &rarr; `products.id`
- `production_orders.product_id` &rarr; `products.id`
- `shipments.purchase_order_id` &rarr; `purchase_orders.id`
- `shipments.supplier_id` &rarr; `suppliers.id`
- `events.entity_id` &rarr; Referenced entity PK (`inventory.id`, `purchase_orders.id`, `production_orders.id`, `shipments.id`)
- `inventory_events.entity_id` &rarr; `products.sku`

---

## 4. The 5 Operational Disruption Scenarios

The dataset encodes 5 distinct supply chain operational disruption patterns:

### Scenario A: Low Inventory (Biscuits Stockout Risk)
- **Problem**: Retail demand has depleted packaged biscuit reserves below the minimum safety buffer.
- **Affected Records**:
  - `products.csv`: `6b9956f6-5c18-4fe3-9681-d4feaaed0a38` (`BIS-001`)
  - `inventory.csv`: `11111111-2222-3333-4444-555555555552` (Warehouse West - Available: 50 packs vs Reorder Level: 200 packs)
  - `events.csv`: `66666666-7777-8888-9999-000000000001` (`INVENTORY_DEPLETED`)
  - `inventory_events.csv`: `EVT-INV-001` (`STOCK_LOW`)

### Scenario B: Supplier Delay (Dairy Pure Co Feedstock Lag)
- **Problem**: Primary dairy vendor suffered refrigeration compressor failure, missing scheduled delivery date by 8 days.
- **Affected Records**:
  - `suppliers.csv`: `545e9817-ce6b-4a0f-9a6f-9b5b29041090` (`Dairy Pure Co` / `SUP-001`)
  - `purchase_orders.csv`: `ccaa359c-72a7-4a9a-adde-abcad89cf171` (`PO-001`, expected 2026-09-06)
  - `purchase_order_items.csv`: `40c6d1b9-5efb-47ba-8810-541c5b57a1fa` (100L raw milk)
  - `shipments.csv`: `d2e3f4a5-b6c7-4d8e-9f0a-1b2c3d4e5f6a` (`SHP-2026-002`, carrier `ColdRoute Express`)
  - `events.csv`: `66666666-7777-8888-9999-000000000002` (`SUPPLIER_DELAY_REPORTED`)

### Scenario C: Production Disruption (Bottling Line 2 Calibration Slowdown)
- **Problem**: Mango Juice Bottling Line 2 is throttled to 40% efficiency due to high-pressure flow sensor nozzle fault.
- **Affected Records**:
  - `products.csv`: `d6b6faf9-ecc3-40b6-94ef-51a80d2a5853` (`MJ-001`)
  - `production_orders.csv`: `f1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c` (`PRD-MJ-202609`, 120/500 produced)
  - `events.csv`: `66666666-7777-8888-9999-000000000003` (`PRODUCTION_SLOWDOWN_RECORDED`)

### Scenario D: Shipment Delay (Rail Hub Intermodal Congestion)
- **Problem**: Carrier `Global Swift Logistics` transporting baking ingredients is stranded at Chicago rail terminal with a 72-hour delay.
- **Affected Records**:
  - `suppliers.csv`: `7c89f1d2-3a45-4b67-89ef-0123456789ab` (`Golden Wheat Mills`)
  - `purchase_orders.csv`: `a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d` (`PO-002`)
  - `shipments.csv`: `c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f` (`SHP-2026-001`, tracking `TRK-SWIFT-8912`)
  - `events.csv`: `66666666-7777-8888-9999-000000000004` (`SHIPMENT_DELAY_DETECTED`)

### Scenario E: Cascading Multi-Domain Disruption (Compound Milk Crisis)
- **Problem**: Simultaneous milk warehouse buffer depletion and supplier freight delay creates an imminent shutdown of planned production order `PRD-MILK-202609`.
- **Affected Records**:
  - `inventory.csv`: `11111111-2222-3333-4444-555555555551` (Cold Hub Alpha - 30L available vs 100L reorder level)
  - `purchase_orders.csv`: `ccaa359c-72a7-4a9a-adde-abcad89cf171` (`PO-001`)
  - `production_orders.csv`: `d3c4d5e6-a7b8-4b9c-0d1e-2f3a4b5c6d7e` (`PRD-MILK-202609`, planned 800L)
  - `events.csv`: `66666666-7777-8888-9999-000000000005` (`CROSS_DOMAIN_DISRUPTION_RAISED`)
  - `inventory_events.csv`: `EVT-INV-002` (`STOCK_LOW`)

---

## 5. Domain Agent Playbooks

Autonomous agents operating within the SNS Agent Workbench can leverage this dataset according to their domain specializations:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        NEXUS CONTROL TOWER                             │
│                  (Cross-Domain Telemetry & Synthesis)                  │
└────────────────────────────────────────────────────────────────────────┘
       ▲                     ▲                    ▲                   ▲
       │                     │                    │                   │
┌──────────────┐      ┌──────────────┐     ┌──────────────┐    ┌──────────────┐
│ PROCUREMENT  │      │  INVENTORY   │     │  PRODUCTION  │    │  LOGISTICS   │
│    AGENT     │      │    AGENT     │     │    AGENT     │    │    AGENT     │
└──────────────┘      └──────────────┘     └──────────────┘    └──────────────┘
```

### 1. Procurement Agent
- **Input Feeds**: `purchase_orders.csv`, `suppliers.csv`, `events.csv` (`SUPPLIER_DELAY_REPORTED`).
- **Autonomous Behaviors**:
  - Detect vendor SLA violations and delivery variances.
  - Evaluate backup suppliers (e.g., split allocations or issue spot purchase orders).
  - Draft emergency purchase orders and compute expediting costs.

### 2. Inventory Agent
- **Input Feeds**: `inventory.csv`, `inventory_events.csv`, `products.csv`.
- **Autonomous Behaviors**:
  - Calculate active runway days (`available_quantity / daily_burn_rate`).
  - Flag critical stockout thresholds (`available_quantity < reorder_level`).
  - Propose inter-warehouse rebalances or safety stock threshold adjustments.

### 3. Production Agent
- **Input Feeds**: `production_orders.csv`, `inventory.csv`, `events.csv` (`PRODUCTION_SLOWDOWN_RECORDED`).
- **Autonomous Behaviors**:
  - Track batch progress against planned completion dates.
  - Detect line bottleneck anomalies and throughput drops.
  - Re-sequence factory work orders to prioritize unaffected production lines.

### 4. Logistics Agent
- **Input Feeds**: `shipments.csv`, `purchase_orders.csv`, `events.csv` (`SHIPMENT_DELAY_DETECTED`).
- **Autonomous Behaviors**:
  - Ingest carrier GPS coordinates and ETAs.
  - Identify transit corridor delays and estimated SLA penalty exposure.
  - Authorize expedited hot-shot trucking charters or bypass rail terminals.

---

## 6. Integration Checklist for SNS Agent Workbench

1. **Ingestion**: Import CSV files into agent vector/relational memories or local SQLite/DuckDB engines.
2. **Event Streaming**: Use `events.csv` and `inventory_events.csv` as mock event queues to trigger agent workflows.
3. **Evaluation**: Compare generated agent recommendations against target mitigations (order split, route switch, schedule rebalance).
