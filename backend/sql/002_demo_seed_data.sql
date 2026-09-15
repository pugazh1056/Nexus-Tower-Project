-- =============================================================================
-- Nexus Tower: FMCG Supply Chain Operations Cockpit
-- Comprehensive Demo Seed Dataset (Milk, Biscuits, Mango Juice)
-- =============================================================================
-- This script safely seeds realistic relational operational data across:
--   A. Low Inventory Scenario
--   B. Supplier Delay Scenario
--   C. Production Disruption Scenario
--   D. Shipment Delay Scenario
--   E. Combined Multi-Domain Disruption Scenario
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. PRODUCTS (Milk, Biscuits, Mango Juice)
-- -----------------------------------------------------------------------------
INSERT INTO public.products (id, sku, name, description, category, unit, reorder_level, is_active, created_at, updated_at)
VALUES
  ('b462b2e9-4a83-4e3c-af52-dd87ab42d06d', 'MILK-001', 'Milk', 'Fresh pasteurized whole milk', 'Dairy', 'litre', 100.0, true, NOW(), NOW()),
  ('6b9956f6-5c18-4fe3-9681-d4feaaed0a38', 'BIS-001', 'Biscuits', 'Crunchy packaged tea biscuits', 'Snacks', 'pack', 200.0, true, NOW(), NOW()),
  ('d6b6faf9-ecc3-40b6-94ef-51a80d2a5853', 'MJ-001', 'Mango Juice', '100% natural premium mango nectar', 'Beverages', 'bottle', 150.0, true, NOW(), NOW())
ON CONFLICT (id) DO UPDATE SET
  name = EXCLUDED.name,
  description = EXCLUDED.description,
  category = EXCLUDED.category,
  unit = EXCLUDED.unit,
  reorder_level = EXCLUDED.reorder_level,
  is_active = EXCLUDED.is_active;

-- -----------------------------------------------------------------------------
-- 2. SUPPLIERS
-- -----------------------------------------------------------------------------
INSERT INTO public.suppliers (id, name, supplier_code, contact_person, email, phone, address, city, country, status, created_at, updated_at)
VALUES
  ('545e9817-ce6b-4a0f-9a6f-9b5b29041090', 'Dairy Pure Co', 'SUP-001', 'Marcus Vance', 'orders@dairypure.com', '+61-3-9821-4400', '12 Yarra Valley Way', 'Melbourne', 'Australia', 'active', NOW(), NOW()),
  ('7c89f1d2-3a45-4b67-89ef-0123456789ab', 'Golden Wheat Mills', 'SUP-002', 'Sarah Jenkins', 'procurement@goldenwheat.com', '+1-312-555-0192', '800 Industrial Blvd', 'Chicago', 'USA', 'active', NOW(), NOW()),
  ('8d90a2e3-4b56-4c78-90fa-1234567890bc', 'Tropical Sunshine Groves', 'SUP-003', 'Rajesh Sharma', 'export@tropicalgroves.in', '+91-22-2849-1120', '45 Orchard Estate', 'Mumbai', 'India', 'active', NOW(), NOW()),
  ('9e01b3f4-5c67-4d89-01ab-2345678901cd', 'Global Swift Logistics', 'SUP-004', 'Elena Rostova', 'dispatch@globalswift.sg', '+65-6789-2211', '10 Marina Terminal Road', 'Singapore', 'Singapore', 'active', NOW(), NOW())
ON CONFLICT (id) DO UPDATE SET
  name = EXCLUDED.name,
  supplier_code = EXCLUDED.supplier_code,
  contact_person = EXCLUDED.contact_person,
  email = EXCLUDED.email,
  phone = EXCLUDED.phone,
  city = EXCLUDED.city,
  country = EXCLUDED.country,
  status = EXCLUDED.status;

-- -----------------------------------------------------------------------------
-- 3. INVENTORY (Low Inventory Scenarios A & E)
-- -----------------------------------------------------------------------------
INSERT INTO public.inventory (id, product_id, warehouse_location, quantity, reserved_quantity, last_updated)
VALUES
  ('11111111-2222-3333-4444-555555555551', 'b462b2e9-4a83-4e3c-af52-dd87ab42d06d', 'Cold Hub Alpha - Bay 4', 45.0, 15.0, NOW()),
  ('11111111-2222-3333-4444-555555555552', '6b9956f6-5c18-4fe3-9681-d4feaaed0a38', 'Warehouse West - Aisle 12', 60.0, 10.0, NOW()),
  ('11111111-2222-3333-4444-555555555553', 'd6b6faf9-ecc3-40b6-94ef-51a80d2a5853', 'Beverage Distribution East', 350.0, 50.0, NOW())
ON CONFLICT (id) DO UPDATE SET
  quantity = EXCLUDED.quantity,
  reserved_quantity = EXCLUDED.reserved_quantity,
  warehouse_location = EXCLUDED.warehouse_location,
  last_updated = EXCLUDED.last_updated;

-- -----------------------------------------------------------------------------
-- 4. PURCHASE ORDERS & ITEMS (Supplier Delay Scenario B & Sourcing Scenario E)
-- -----------------------------------------------------------------------------
INSERT INTO public.purchase_orders (id, po_number, supplier_id, created_by, status, order_date, expected_delivery_date, total_amount, notes, created_at, updated_at)
VALUES
  ('ccaa359c-72a7-4a9a-adde-abcad89cf171', 'PO-001', '545e9817-ce6b-4a0f-9a6f-9b5b29041090', NULL, 'ordered', CURRENT_DATE - INTERVAL '11 days', CURRENT_DATE - INTERVAL '8 days', 5000.0, 'Raw Milk batch - Dairy Pure Co experiencing refrigerated tank delay', NOW(), NOW()),
  ('a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d', 'PO-002', '7c89f1d2-3a45-4b67-89ef-0123456789ab', NULL, 'ordered', CURRENT_DATE - INTERVAL '3 days', CURRENT_DATE + INTERVAL '4 days', 12500.0, 'Baking flour and biscuit mix consignment', NOW(), NOW()),
  ('b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e', 'PO-003', '8d90a2e3-4b56-4c78-90fa-1234567890bc', NULL, 'received', CURRENT_DATE - INTERVAL '14 days', CURRENT_DATE - INTERVAL '4 days', 8400.0, 'Alphonso Mango pulp concentrate delivery - verified and inspected', NOW(), NOW())
ON CONFLICT (id) DO UPDATE SET
  po_number = EXCLUDED.po_number,
  supplier_id = EXCLUDED.supplier_id,
  status = EXCLUDED.status,
  order_date = EXCLUDED.order_date,
  expected_delivery_date = EXCLUDED.expected_delivery_date,
  total_amount = EXCLUDED.total_amount,
  notes = EXCLUDED.notes;

INSERT INTO public.purchase_order_items (id, purchase_order_id, product_id, quantity, unit_price)
VALUES
  ('40c6d1b9-5efb-47ba-8810-541c5b57a1fa', 'ccaa359c-72a7-4a9a-adde-abcad89cf171', 'b462b2e9-4a83-4e3c-af52-dd87ab42d06d', 100.0, 50.0),
  ('22222222-3333-4444-5555-666666666662', 'a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d', '6b9956f6-5c18-4fe3-9681-d4feaaed0a38', 250.0, 50.0),
  ('22222222-3333-4444-5555-666666666663', 'b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e', 'd6b6faf9-ecc3-40b6-94ef-51a80d2a5853', 300.0, 28.0)
ON CONFLICT (id) DO UPDATE SET
  quantity = EXCLUDED.quantity,
  unit_price = EXCLUDED.unit_price;

-- -----------------------------------------------------------------------------
-- 5. PRODUCTION ORDERS (Production Disruption Scenario C & Production Planning)
-- -----------------------------------------------------------------------------
INSERT INTO public.production_orders (id, production_number, product_id, created_by, planned_quantity, produced_quantity, status, planned_start_date, planned_end_date, actual_start_date, actual_end_date, notes, created_at, updated_at)
VALUES
  ('f1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c', 'PRD-MJ-202609', 'd6b6faf9-ecc3-40b6-94ef-51a80d2a5853', NULL, 500.0, 120.0, 'in_progress', CURRENT_DATE - INTERVAL '2 days', CURRENT_DATE + INTERVAL '1 days', CURRENT_DATE - INTERVAL '2 days', NULL, 'Bottling Line 2 running at 40% capacity due to high-pressure nozzle calibration issue', NOW(), NOW()),
  ('e2b3c4d5-f6a7-4a8b-9c0d-1e2f3a4b5c6d', 'PRD-BIS-202609', '6b9956f6-5c18-4fe3-9681-d4feaaed0a38', NULL, 1000.0, 0.0, 'planned', CURRENT_DATE + INTERVAL '2 days', CURRENT_DATE + INTERVAL '6 days', NULL, NULL, 'High-volume biscuit packaging run scheduled following flour delivery', NOW(), NOW()),
  ('d3c4d5e6-a7b8-4b9c-0d1e-2f3a4b5c6d7e', 'PRD-MILK-202609', 'b462b2e9-4a83-4e3c-af52-dd87ab42d06d', NULL, 800.0, 0.0, 'planned', CURRENT_DATE + INTERVAL '3 days', CURRENT_DATE + INTERVAL '5 days', NULL, NULL, 'Awaiting raw pasteurization feedstock confirmation from PO-001', NOW(), NOW())
ON CONFLICT (id) DO UPDATE SET
  production_number = EXCLUDED.production_number,
  planned_quantity = EXCLUDED.planned_quantity,
  produced_quantity = EXCLUDED.produced_quantity,
  status = EXCLUDED.status,
  notes = EXCLUDED.notes;

-- -----------------------------------------------------------------------------
-- 6. SHIPMENTS (Shipment Delay Scenario D & Freight Tracking)
-- -----------------------------------------------------------------------------
INSERT INTO public.shipments (id, shipment_number, purchase_order_id, supplier_id, status, carrier_name, tracking_number, origin, destination, expected_delivery_date, actual_delivery_date, created_at, updated_at)
VALUES
  ('c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f', 'SHP-2026-001', 'a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d', '7c89f1d2-3a45-4b67-89ef-0123456789ab', 'delayed', 'Global Swift Logistics', 'TRK-SWIFT-8912', 'Chicago Central Freight Rail', 'Warehouse West Distribution', CURRENT_DATE - INTERVAL '1 days', NULL, NOW(), NOW()),
  ('d2e3f4a5-b6c7-4d8e-9f0a-1b2c3d4e5f6a', 'SHP-2026-002', 'ccaa359c-72a7-4a9a-adde-abcad89cf171', '545e9817-ce6b-4a0f-9a6f-9b5b29041090', 'delayed', 'ColdRoute Express', 'TRK-COLD-4401', 'Melbourne Cold Logistics Hub', 'Cold Hub Alpha - Bay 4', CURRENT_DATE - INTERVAL '8 days', NULL, NOW(), NOW()),
  ('e3f4a5b6-c7d8-4e9f-0a1b-2c3d4e5f6a7b', 'SHP-2026-003', 'b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e', '8d90a2e3-4b56-4c78-90fa-1234567890bc', 'delivered', 'Pacific Ocean Maritime', 'TRK-MAR-5520', 'Jawaharlal Nehru Port, Mumbai', 'Beverage Distribution East', CURRENT_DATE - INTERVAL '4 days', CURRENT_DATE - INTERVAL '4 days', NOW(), NOW())
ON CONFLICT (id) DO UPDATE SET
  shipment_number = EXCLUDED.shipment_number,
  status = EXCLUDED.status,
  carrier_name = EXCLUDED.carrier_name,
  tracking_number = EXCLUDED.tracking_number,
  expected_delivery_date = EXCLUDED.expected_delivery_date;

-- -----------------------------------------------------------------------------
-- 7. ALERTS (Scenarios A, B, C, D, E)
-- -----------------------------------------------------------------------------
INSERT INTO public.alerts (id, title, message, severity, entity_type, entity_id, is_read, created_for, created_at)
VALUES
  ('33333333-4444-5555-6666-777777777771', 'Low Inventory Alert: Biscuits', 'Stock level for Biscuits (BIS-001) is 50 available units, significantly below the reorder threshold of 200 units.', 'critical', 'inventory', '11111111-2222-3333-4444-555555555552', false, NULL, NOW() - INTERVAL '6 hours'),
  ('33333333-4444-5555-6666-777777777772', 'Supplier Dispatch Lag: Dairy Pure Co', 'PO-001 expected delivery was missed by 8 days. Supplier reports cooling compressor maintenance.', 'warning', 'purchase_order', 'ccaa359c-72a7-4a9a-adde-abcad89cf171', false, NULL, NOW() - INTERVAL '12 hours'),
  ('33333333-4444-5555-6666-777777777773', 'Production Line Slowdown: Bottling 2', 'Batch PRD-MJ-202609 is progressing at 40% nominal throughput due to nozzle flow sensor fault.', 'warning', 'production_order', 'f1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c', false, NULL, NOW() - INTERVAL '4 hours'),
  ('33333333-4444-5555-6666-777777777774', 'Shipment In-Transit Delay: SHP-2026-001', 'Carrier Global Swift Logistics reports rail intermodal hub congestion causing +72 hour delay on Biscuit ingredients.', 'warning', 'shipment', 'c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f', false, NULL, NOW() - INTERVAL '2 hours'),
  ('33333333-4444-5555-6666-777777777775', 'Cascading Supply Chain Disruption', 'Multi-tier impact: Milk raw material stockout risks shutting down planned production PRD-MILK-202609 within 48 hours.', 'critical', 'purchase_order', 'ccaa359c-72a7-4a9a-adde-abcad89cf171', false, NULL, NOW() - INTERVAL '1 hours')
ON CONFLICT (id) DO UPDATE SET
  title = EXCLUDED.title,
  message = EXCLUDED.message,
  severity = EXCLUDED.severity,
  is_read = EXCLUDED.is_read;

-- -----------------------------------------------------------------------------
-- 8. RISKS (Scenarios A, B, C, D, E)
-- -----------------------------------------------------------------------------
INSERT INTO public.risks (id, title, description, risk_type, probability, impact, risk_score, status, entity_type, entity_id, identified_by, created_at, updated_at)
VALUES
  ('44444444-5555-6666-7777-888888888881', 'Retail Biscuit Stockout Risk', 'Depleted warehouse inventory could cause unfilled grocery orders within 3 business days.', 'inventory', 0.85, 9.0, 7.65, 'open', 'product', '6b9956f6-5c18-4fe3-9681-d4feaaed0a38', NULL, NOW() - INTERVAL '6 hours', NOW()),
  ('44444444-5555-6666-7777-888888888882', 'Dairy Vendor Fulfillment Variance', 'Prolonged supplier delay on PO-001 threatens fresh milk bottling operational readiness.', 'procurement', 0.80, 8.5, 6.80, 'open', 'supplier', '545e9817-ce6b-4a0f-9a6f-9b5b29041090', NULL, NOW() - INTERVAL '12 hours', NOW()),
  ('44444444-5555-6666-7777-888888888883', 'Beverage Bottling Schedule Slip', 'Line 2 pump calibration delay risks spilling production into weekend premium labor shifts.', 'production', 0.60, 6.0, 3.60, 'open', 'production_order', 'f1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c', NULL, NOW() - INTERVAL '4 hours', NOW()),
  ('44444444-5555-6666-7777-888888888884', 'Intermodal Freight Delay Risk', 'Rail freight congestion may delay bakery production start date for batch PRD-BIS-202609.', 'logistics', 0.70, 7.5, 5.25, 'open', 'shipment', 'c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f', NULL, NOW() - INTERVAL '2 hours', NOW()),
  ('44444444-5555-6666-7777-888888888885', 'Cross-Domain Production Halting Risk', 'Simultaneous milk inventory depletion and carrier delay creates a critical multi-channel outage risk.', 'cross_domain', 0.90, 10.0, 9.00, 'open', 'purchase_order', 'ccaa359c-72a7-4a9a-adde-abcad89cf171', NULL, NOW() - INTERVAL '1 hours', NOW())
ON CONFLICT (id) DO UPDATE SET
  title = EXCLUDED.title,
  description = EXCLUDED.description,
  probability = EXCLUDED.probability,
  impact = EXCLUDED.impact,
  risk_score = EXCLUDED.risk_score,
  status = EXCLUDED.status;

-- -----------------------------------------------------------------------------
-- 9. RECOMMENDATIONS (Prescriptive Actions for Cockpit & Agents)
-- -----------------------------------------------------------------------------
INSERT INTO public.recommendations (id, title, description, recommendation_type, priority, entity_type, entity_id, status, generated_by, created_at, updated_at)
VALUES
  ('55555555-6666-7777-8888-999999999991', 'Issue Expedited PO for Biscuits', 'Generate an expedited emergency purchase order of 300 units of BIS-001 from Golden Wheat Mills.', 'procurement', 'high', 'product', '6b9956f6-5c18-4fe3-9681-d4feaaed0a38', 'pending', 'Nexus AI Engine', NOW() - INTERVAL '6 hours', NOW()),
  ('55555555-6666-7777-8888-999999999992', 'Engage Secondary Dairy Supplier', 'Split procurement order PO-001 and divert 150 litres to local co-op dairy to secure immediate production feedstock.', 'procurement', 'critical', 'purchase_order', 'ccaa359c-72a7-4a9a-adde-abcad89cf171', 'pending', 'Nexus AI Engine', NOW() - INTERVAL '11 hours', NOW()),
  ('55555555-6666-7777-8888-999999999993', 'Rebalance Production to Bottling Line 3', 'Re-route remaining 380 bottles of Mango Juice batch PRD-MJ-202609 to auxiliary line 3 during 2 PM shift change.', 'production', 'medium', 'production_order', 'f1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c', 'pending', 'Nexus AI Engine', NOW() - INTERVAL '3 hours', NOW()),
  ('55555555-6666-7777-8888-999999999994', 'Authorize Express Air Transit Re-route', 'Switch final 400km transit of shipment SHP-2026-001 to dedicated refrigerated truck charter to bypass rail blockade.', 'logistics', 'high', 'shipment', 'c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f', 'accepted', 'Nexus AI Engine', NOW() - INTERVAL '2 hours', NOW()),
  ('55555555-6666-7777-8888-999999999995', 'Execute Unified Cross-Domain Mitigation', 'Approve combined action: 1) Divert local dairy supply, 2) Reschedule PRD-MILK by 24h, 3) Allocate reserve inventory.', 'cross_domain', 'critical', 'purchase_order', 'ccaa359c-72a7-4a9a-adde-abcad89cf171', 'pending', 'Nexus AI Engine', NOW() - INTERVAL '1 hours', NOW())
ON CONFLICT (id) DO UPDATE SET
  title = EXCLUDED.title,
  description = EXCLUDED.description,
  priority = EXCLUDED.priority,
  status = EXCLUDED.status;

-- -----------------------------------------------------------------------------
-- 10. EVENTS (Telemetry Audit Stream & Domain Triggers)
-- -----------------------------------------------------------------------------
INSERT INTO public.events (id, event_type, entity_type, entity_id, actor_id, description, metadata, created_at)
VALUES
  ('66666666-7777-8888-9999-000000000001', 'INVENTORY_DEPLETED', 'inventory', '11111111-2222-3333-4444-555555555552', NULL, 'Biscuits stock level fell below critical reorder threshold (Current: 50, Reorder: 200)', '{"sku": "BIS-001", "quantity": 50, "location": "Warehouse West"}'::jsonb, NOW() - INTERVAL '6 hours'),
  ('66666666-7777-8888-9999-000000000002', 'SUPPLIER_DELAY_REPORTED', 'purchase_order', 'ccaa359c-72a7-4a9a-adde-abcad89cf171', NULL, 'Supplier Dairy Pure Co confirmed 8-day delivery delay on PO-001', '{"supplier": "Dairy Pure Co", "po_number": "PO-001", "delay_days": 8}'::jsonb, NOW() - INTERVAL '12 hours'),
  ('66666666-7777-8888-9999-000000000003', 'PRODUCTION_SLOWDOWN_RECORDED', 'production_order', 'f1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c', NULL, 'IoT telemetry detected 60% throughput drop on Bottling Line 2 for Mango Juice batch', '{"line": "Line 2", "batch": "PRD-MJ-202609", "current_efficiency": 0.40}'::jsonb, NOW() - INTERVAL '4 hours'),
  ('66666666-7777-8888-9999-000000000004', 'SHIPMENT_DELAY_DETECTED', 'shipment', 'c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f', NULL, 'GPS tracker reports carrier Global Swift Logistics halted at rail terminal hub', '{"shipment_number": "SHP-2026-001", "status": "delayed", "eta_delta_hours": 72}'::jsonb, NOW() - INTERVAL '2 hours'),
  ('66666666-7777-8888-9999-000000000005', 'CROSS_DOMAIN_DISRUPTION_RAISED', 'purchase_order', 'ccaa359c-72a7-4a9a-adde-abcad89cf171', NULL, 'Milk feedstock shortage escalated to production scheduling and sales fulfillment channels', '{"severity": "critical", "affected_orders": ["PO-001", "PRD-MILK-202609"]}'::jsonb, NOW() - INTERVAL '1 hours')
ON CONFLICT (id) DO UPDATE SET
  event_type = EXCLUDED.event_type,
  description = EXCLUDED.description,
  metadata = EXCLUDED.metadata;

-- -----------------------------------------------------------------------------
-- 11. INVENTORY_EVENTS (SNS Agent Workbench Telemetry Integration)
-- -----------------------------------------------------------------------------
INSERT INTO public.inventory_events (event_id, event_type, entity_id, current_stock, target_stock)
VALUES
  ('EVT-INV-001', 'STOCK_LOW', 'BIS-001', 50, 200),
  ('EVT-INV-002', 'STOCK_LOW', 'MILK-001', 30, 100),
  ('EVT-INV-003', 'STOCK_OPTIMAL', 'MJ-001', 300, 150)
ON CONFLICT (event_id) DO UPDATE SET
  event_type = EXCLUDED.event_type,
  entity_id = EXCLUDED.entity_id,
  current_stock = EXCLUDED.current_stock,
  target_stock = EXCLUDED.target_stock;
