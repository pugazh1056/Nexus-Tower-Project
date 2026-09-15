# Nexus Tower: FMCG Supply Chain Operations Dataset

> **Upgraded Enterprise Shared Dataset Package for SNS Agent Workbench Integration**  
> *Primary Source of Truth: `backend/sql/002_demo_seed_data.sql` and `dataset/*.csv`*

---

## 1. Notice of Synthetic Demo Data

> **Notice**: All records, companies, orders, tracking codes, and IoT telemetry values in this package are **synthetic demonstration data** created strictly for benchmarking, algorithm validation, and SNS Agent Workbench system integration.

---

## 2. Dataset Overview & Architecture

This upgraded dataset package provides a comprehensive, relational operations foundation across four core supply chain domains:
1. **Procurement**: Supplier performance analytics, contracts, lead times, capacity limits, price histories, purchase requisitions, and financial transactions.
2. **Inventory**: Real-time warehouse balances, safety stock targets, shelf-life (FEFO) tracking, reserved stock, and stream events.
3. **Production**: Multi-tier Bill of Materials (BOM), shop floor material requirement calculations, line-level throughput tracking, and downtime telemetry.
4. **Logistics & Cold Chain**: Inbound shipment manifest lines, receiving inspection assays, defect/rejection tracking, and IoT reefer temperature telemetry with automated excursion flagging.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       NEXUS AGENT WORKBENCH ARCHITECTURE                                │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────┘
             │                                     │                                    │
             ▼                                     ▼                                    ▼
┌─────────────────────────┐           ┌─────────────────────────┐          ┌─────────────────────────┐
│    PROCUREMENT AGENT    │           │    PRODUCTION AGENT     │          │     LOGISTICS AGENT     │
│ ─────────────────────── │           │ ─────────────────────── │          │ ─────────────────────── │
│ • supplier_performance  │           │ • production_orders     │          │ • shipments             │
│ • supplier_products     │ ◄───────► │ • production_bom        │ ◄──────► │ • shipment_items        │
│ • supplier_capacity     │           │ • production_material_  │          │ • shipment_receipts     │
│ • supplier_contracts    │           │   requirements          │          │ • shipment_temperature_ │
│ • purchase_orders       │           │ • production_progress   │          │   telemetry             │
│ • purchase_order_items  │           └────────────┬────────────┘          └────────────┬────────────┘
│ • purchase_requisitions │                        │                                    │
│ • purchase_order_status_│                        ▼                                    ▼
│   history               │           ┌─────────────────────────┐          ┌─────────────────────────┐
│ • purchase_price_history│ ◄───────► │     INVENTORY AGENT     │ ◄──────► │   CROSS-DOMAIN EVENTS   │
│ • procurement_          │           │ ─────────────────────── │          │ ─────────────────────── │
│   transactions          │           │ • inventory.csv         │          │ • events.csv            │
└─────────────────────────┘           │ • inventory_events.csv  │          │ • inventory_events.csv  │
                                      │ • products.csv          │          └─────────────────────────┘
                                      └─────────────────────────┘
```

---

## 3. Complete File Catalog & Record Counts

| Category | File | Primary Key | Description | Record Count |
| :--- | :--- | :--- | :--- | :---: |
| **Master** | `products.csv` | `id` (UUID) | Master catalog of finished FMCG goods, raw feedstock, and packaging. Source of truth for `reorder_level`. | 8 |
| **Master** | `suppliers.csv` | `id` (UUID) | Directory of certified global raw material suppliers, packaging vendors, and carriers. | 8 |
| **Inventory** | `inventory.csv` | `id` (UUID) | Physical stock balances across cold storage hubs, dry bulk units, and distribution centers with `receiving_date`, `expiry_date`, and `target_stock`. | 8 |
| **Inventory** | `inventory_events.csv` | `event_id` (Text) | High-throughput inventory stream schema formatted for SNS Agent Workbench queues. | 3 |
| **Procurement** | `purchase_orders.csv` | `id` (UUID) | Inbound procurement orders with normalized original, revised, and actual delivery dates. | 11 |
| **Procurement** | `purchase_order_items.csv` | `id` (UUID) | Itemized line-item quantities, unit prices, and extended amounts. | 11 |
| **Procurement** | `supplier_products.csv` | `id` (Text) | Supplier product catalog, standard lead times, MOQs, unit prices, and tier classification (`primary` vs `backup`). | 12 |
| **Procurement** | `supplier_performance.csv` | `id` (Text) | Historical delivery logs, promised vs actual dates, lead-time variance, delivered vs accepted/rejected quantities. | 11 |
| **Procurement** | `supplier_capacity.csv` | `id` (Text) | Monthly vendor capacity ceilings, allocated quantities, available surge bandwidth, and maintenance windows. | 6 |
| **Procurement** | `supplier_contracts.csv` | `id` (Text) | Master supply agreements, payment terms (Net 30/45/LC), Incoterms, SLA minimums, and penalty clauses. | 6 |
| **Procurement** | `purchase_requisitions.csv` | `id` (Text) | Purchase requisition workflow (requested, urgency, approved by, linked purchase order). | 4 |
| **Procurement** | `purchase_order_status_history.csv` | `id` (Text) | Audit trail of PO lifecycle status changes with timestamps and reasons. | 7 |
| **Procurement** | `purchase_price_history.csv` | `id` (Text) | Effective unit price ranges and volume thresholds over time. | 8 |
| **Procurement** | `procurement_transactions.csv` | `id` (Text) | Invoices, payment due dates, settlement timestamps, and payment statuses. | 6 |
| **Production** | `production_orders.csv` | `id` (UUID) | Factory floor batch manufacturing runs, planned/actual dates, and line progress. | 3 |
| **Production** | `production_bom.csv` | `id` (Text) | Bill of Materials linking finished products to raw feedstock and packaging with scrap factors. | 5 |
| **Production** | `production_material_requirements.csv` | `id` (Text) | Material requirement explosion per production order against available inventory with shortage status. | 5 |
| **Production** | `production_progress.csv` | `id` (Text) | Real-time line telemetry, equipment IDs, run rates, progress percentage, and downtime causes. | 3 |
| **Logistics** | `shipments.csv` | `id` (UUID) | Normalized shipment tracking with carrier names, origin, destination, original ETA, revised ETA, and actual delivery date. | 6 |
| **Logistics** | `shipment_items.csv` | `id` (Text) | Itemized shipment manifests with ordered vs shipped quantities. | 6 |
| **Logistics** | `shipment_receipts.csv` | `id` (Text) | Receiving dock inspection logs with received, accepted, rejected, and damaged quantities. | 4 |
| **Logistics** | `shipment_temperature_telemetry.csv` | `id` (Text) | Cold-chain IoT temperature logs with min/max thresholds, excursion flags, and sensor locations. | 9 |
| **Telemetry** | `events.csv` | `id` (UUID) | Real-time telemetry audit events, sensor triggers, status shifts, and cross-domain alerts. | 5 |

---

## 4. Entity Relationship & Foreign Key Matrix

```
[suppliers] ──┬──< [supplier_products] >── [products] ──┬──< [inventory]
              ├──< [supplier_capacity] >── [products]   ├──< [production_bom] (component)
              ├──< [supplier_contracts]                 └──< [purchase_order_items]
              ├──< [supplier_performance] >── [purchase_orders]
              └──< [purchase_orders] ──┬──< [purchase_order_items] >── [products]
                                       ├──< [purchase_order_status_history]
                                       ├──< [procurement_transactions]
                                       └──< [shipments] ──┬──< [shipment_items] >── [products]
                                                          ├──< [shipment_receipts] >── [products]
                                                          └──< [shipment_temperature_telemetry]

[production_orders] ──┬──< [production_material_requirements] >── [products]
                      └──< [production_progress]
```

---

## 5. Agent Data Availability & Analytical Capabilities

### 1. Procurement Agent Capabilities
- **Reliability & On-Time Delivery Rate**: Calculated directly from `supplier_performance.csv` (`on_time_count / total_orders`).
- **Lead-Time Trend Analysis**: Computed from `supplier_performance.csv` (`actual_delivery_date - order_date` vs `standard_lead_time_days` in `supplier_products.csv`).
- **Defect & Rejection Rate**: Computed from `supplier_performance.csv` (`rejected_quantity / delivered_quantity`) and verified against `shipment_receipts.csv`.
- **Alternative / Backup Supplier Evaluation**: Evaluates backup suppliers (`supplier_products.tier == 'backup'`) with capacity in `supplier_capacity.csv` and existing framework agreements in `supplier_contracts.csv`.
- **Price Benchmarking & Inflation Tracking**: Historical pricing trajectories from `purchase_price_history.csv`.
- **Contract Compliance & Penalty Computation**: Late penalty rates evaluated against delay durations in `supplier_contracts.csv`.

### 2. Inventory Agent Capabilities
- **Stockout Runway Days**: `available_quantity / daily_burn_rate`.
- **Safety Stock Deficit**: `available_quantity < target_stock` (where `target_stock` is strictly bound to `products.reorder_level`).
- **Perishability & FEFO Sequencing**: `expiry_date` tracking across dairy (14-day window), juice (6 months), and biscuits (6 months).
- **Inbound Visibility**: Aggregating expected replenishment from `purchase_orders.csv` and `shipments.csv`.

### 3. Production Agent Capabilities
- **BOM Material Explosion**: Translates finished goods work orders into component feedstock demands via `production_bom.csv`.
- **Material Availability & Shortage Identification**: Ingests `production_material_requirements.csv` to flag blocking shortages (e.g. 795L shortage on Milk production order `PRD-MILK-202609`).
- **Line Throughput & Bottleneck Detection**: Real-time operating rate and downtime analysis from `production_progress.csv`.

### 4. Logistics Agent Capabilities
- **In-Transit Delay Tracking & SLA Penalties**: Normalized tracking via `shipments.csv` (`revised_delivery_date - original_expected_delivery_date`).
- **Cold-Chain Excursion Anomaly Detection**: Temperature readings in `shipment_temperature_telemetry.csv` flagged when `temperature < min_allowed_temperature` or `temperature > max_allowed_temperature`.
- **Receiving Discrepancies**: Dock inspection verification in `shipment_receipts.csv`.

---

## 6. End-to-End Operational Scenarios

### Scenario A: Biscuits Inventory Depletion
- **State**: `inventory.csv` shows Biscuits stock at 50 units vs target stock of 200 units.
- **Trigger**: `inventory_events.csv` (`EVT-INV-001`, `STOCK_LOW`) and `events.csv` (`66666666-7777-8888-9999-000000000001`).
- **Linkage**: Inbound replenishment `PO-002` / `SHP-2026-001` is delayed in transit.

### Scenario B: Milk Supplier Delivery Delay
- **State**: Supplier Dairy Pure Co confirmed 8-day delay on `PO-001` (`ccaa359c-72a7-4a9a-adde-abcad89cf171`), moving delivery from `2026-09-06` to `2026-09-14`.
- **Root Cause**: Compressor failure on carrier vehicle `SHP-2026-002` documented in `shipment_temperature_telemetry.csv` (temperatures spiked to 9.2°C).
- **Action**: Procurement Agent can evaluate backup supplier `Apex Dairy Farms` (`SUP-005`) in `supplier_products.csv`.

### Scenario C: Mango Juice Bottling Line Slowdown
- **State**: Production Order `PRD-MJ-202609` is running at 40% capacity on Bottling Line 2.
- **Verification**: `production_material_requirements.csv` confirms raw pulp is sufficient (300kg available vs 150kg required). `production_progress.csv` isolates the bottleneck to `EQ-NOZZLE-02` calibration failure.

### Scenario D: Biscuits Freight Rail Intermodal Delay
- **State**: Shipment `SHP-2026-001` (Carrier: Global Swift Logistics) carrying 250 packs of biscuit mix is halted at Chicago rail terminal with a 72-hour delay.
- **Dates**: Normalized original ETA `2026-09-15` &rarr; revised ETA `2026-09-18`.

### Scenario E: Cascading Multi-Domain Disruption (Compound Milk Crisis)
- **State**: Simultaneous depletion of Milk inventory (30L available vs 100L target), delayed inbound `PO-001` (8-day delay), and scheduled production run `PRD-MILK-202609` (requiring 840L feedstock with only 45L in silo).
- **Escalation**: Triggered `events.csv` (`66666666-7777-8888-9999-000000000005`), requiring cross-domain synchronization between Procurement, Inventory, Production, and Logistics agents.
