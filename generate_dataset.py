import csv
import json
import os
import re

# Directory
DATASET_DIR = "dataset"
os.makedirs(DATASET_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. CORE ENTITY IDS (PRESERVED 100%)
# -----------------------------------------------------------------------------
# Finished Products
PROD_MILK_ID = "b462b2e9-4a83-4e3c-af52-dd87ab42d06d"
PROD_BISCUITS_ID = "6b9956f6-5c18-4fe3-9681-d4feaaed0a38"
PROD_MANGO_JUICE_ID = "d6b6faf9-ecc3-40b6-94ef-51a80d2a5853"

# Raw Materials & Components (for complete BOM & Inventory linking)
RAW_MILK_ID = "c5e6f7a8-1111-4b2c-8d3e-4f5a6b7c8d9e"
RAW_FLOUR_ID = "c5e6f7a8-2222-4b2c-8d3e-4f5a6b7c8d9e"
RAW_PULP_ID = "c5e6f7a8-3333-4b2c-8d3e-4f5a6b7c8d9e"
PKG_BOTTLE_ID = "c5e6f7a8-4444-4b2c-8d3e-4f5a6b7c8d9e"
PKG_WRAP_ID = "c5e6f7a8-5555-4b2c-8d3e-4f5a6b7c8d9e"

# Suppliers (4 Core Preserved + 4 Backup/Alternative)
SUP_DAIRY_PURE_ID = "545e9817-ce6b-4a0f-9a6f-9b5b29041090"        # SUP-001 Primary Milk
SUP_GOLDEN_WHEAT_ID = "7c89f1d2-3a45-4b67-89ef-0123456789ab"      # SUP-002 Primary Flour
SUP_TROPICAL_GROVES_ID = "8d90a2e3-4b56-4c78-90fa-1234567890bc"   # SUP-003 Primary Mango
SUP_GLOBAL_SWIFT_ID = "9e01b3f4-5c67-4d89-01ab-2345678901cd"      # SUP-004 Primary Logistics

SUP_APEX_DAIRY_ID = "a1b2c3d4-0005-4a7b-8c9d-0e1f2a3b4c5d"        # SUP-005 Backup Dairy
SUP_MIDWEST_GRAIN_ID = "a1b2c3d4-0006-4a7b-8c9d-0e1f2a3b4c5d"     # SUP-006 Backup Flour
SUP_RATNAGIRI_AGRO_ID = "a1b2c3d4-0007-4a7b-8c9d-0e1f2a3b4c5d"    # SUP-007 Backup Mango
SUP_PACIFIC_REEFER_ID = "a1b2c3d4-0008-4a7b-8c9d-0e1f2a3b4c5d"    # SUP-008 Backup Cold Reefer

# Inventory Core IDs
INV_MILK_ID = "11111111-2222-3333-4444-555555555551"
INV_BISCUITS_ID = "11111111-2222-3333-4444-555555555552"
INV_MANGO_JUICE_ID = "11111111-2222-3333-4444-555555555553"
INV_RAW_MILK_ID = "11111111-2222-3333-4444-555555555554"
INV_RAW_FLOUR_ID = "11111111-2222-3333-4444-555555555555"
INV_RAW_PULP_ID = "11111111-2222-3333-4444-555555555556"
INV_PKG_BOTTLE_ID = "11111111-2222-3333-4444-555555555557"
INV_PKG_WRAP_ID = "11111111-2222-3333-4444-555555555558"

# PO Core IDs
PO_001_ID = "ccaa359c-72a7-4a9a-adde-abcad89cf171"
PO_002_ID = "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
PO_003_ID = "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e"

# PO Item Core IDs
POI_001_ID = "40c6d1b9-5efb-47ba-8810-541c5b57a1fa"
POI_002_ID = "22222222-3333-4444-5555-666666666662"
POI_003_ID = "22222222-3333-4444-5555-666666666663"

# Production Orders Core IDs
PRD_MJ_ID = "f1a2b3c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c"
PRD_BIS_ID = "e2b3c4d5-f6a7-4a8b-9c0d-1e2f3a4b5c6d"
PRD_MILK_ID = "d3c4d5e6-a7b8-4b9c-0d1e-2f3a4b5c6d7e"

# Shipments Core IDs
SHP_001_ID = "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f"
SHP_002_ID = "d2e3f4a5-b6c7-4d8e-9f0a-1b2c3d4e5f6a"
SHP_003_ID = "e3f4a5b6-c7d8-4e9f-0a1b-2c3d4e5f6a7b"

# Events Core IDs
EVT_001_ID = "66666666-7777-8888-9999-000000000001"
EVT_002_ID = "66666666-7777-8888-9999-000000000002"
EVT_003_ID = "66666666-7777-8888-9999-000000000003"
EVT_004_ID = "66666666-7777-8888-9999-000000000004"
EVT_005_ID = "66666666-7777-8888-9999-000000000005"

def write_csv(filename, rows, fieldnames):
    filepath = os.path.join(DATASET_DIR, filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {filename:35} : {len(rows)} records")

# -----------------------------------------------------------------------------
# 1. products.csv
# -----------------------------------------------------------------------------
products = [
    {"id": PROD_MILK_ID, "sku": "MILK-001", "name": "Milk", "description": "Fresh pasteurized whole milk", "category": "Dairy", "unit": "litre", "reorder_level": 100.0, "is_active": True},
    {"id": PROD_BISCUITS_ID, "sku": "BIS-001", "name": "Biscuits", "description": "Crunchy packaged tea biscuits", "category": "Snacks", "unit": "pack", "reorder_level": 200.0, "is_active": True},
    {"id": PROD_MANGO_JUICE_ID, "sku": "MJ-001", "name": "Mango Juice", "description": "100% natural premium mango nectar", "category": "Beverages", "unit": "bottle", "reorder_level": 150.0, "is_active": True},
    {"id": RAW_MILK_ID, "sku": "RAW-MILK-01", "name": "Raw Pasteurization Feedstock", "description": "Grade A raw farm milk bulk tank feedstock", "category": "Raw Materials", "unit": "litre", "reorder_level": 500.0, "is_active": True},
    {"id": RAW_FLOUR_ID, "sku": "RAW-FLOUR-01", "name": "Premium Biscuit Flour Mix", "description": "Refined enriched wheat flour and leavening mix", "category": "Raw Materials", "unit": "kg", "reorder_level": 600.0, "is_active": True},
    {"id": RAW_PULP_ID, "sku": "RAW-PULP-01", "name": "Alphonso Mango Pulp Concentrate", "description": "Aseptic packed pure Alphonso mango puree", "category": "Raw Materials", "unit": "kg", "reorder_level": 300.0, "is_active": True},
    {"id": PKG_BOTTLE_ID, "sku": "PKG-BOT-01", "name": "500ml Aseptic Glass Bottles", "description": "Sterilized 500ml glass beverage bottles with caps", "category": "Packaging", "unit": "unit", "reorder_level": 1000.0, "is_active": True},
    {"id": PKG_WRAP_ID, "sku": "PKG-WRAP-01", "name": "Moisture-Barrier Biscuit Wrappers", "description": "BOPP printed moisture barrier wrapping film", "category": "Packaging", "unit": "roll", "reorder_level": 50.0, "is_active": True}
]
write_csv("products.csv", products, ["id", "sku", "name", "description", "category", "unit", "reorder_level", "is_active"])

# -----------------------------------------------------------------------------
# 2. suppliers.csv
# -----------------------------------------------------------------------------
suppliers = [
    {"id": SUP_DAIRY_PURE_ID, "name": "Dairy Pure Co", "supplier_code": "SUP-001", "contact_person": "Marcus Vance", "email": "orders@dairypure.com", "phone": "+61-3-9821-4400", "address": "12 Yarra Valley Way", "city": "Melbourne", "country": "Australia", "status": "active"},
    {"id": SUP_GOLDEN_WHEAT_ID, "name": "Golden Wheat Mills", "supplier_code": "SUP-002", "contact_person": "Sarah Jenkins", "email": "procurement@goldenwheat.com", "phone": "+1-312-555-0192", "address": "800 Industrial Blvd", "city": "Chicago", "country": "USA", "status": "active"},
    {"id": SUP_TROPICAL_GROVES_ID, "name": "Tropical Sunshine Groves", "supplier_code": "SUP-003", "contact_person": "Rajesh Sharma", "email": "export@tropicalgroves.in", "phone": "+91-22-2849-1120", "address": "45 Orchard Estate", "city": "Mumbai", "country": "India", "status": "active"},
    {"id": SUP_GLOBAL_SWIFT_ID, "name": "Global Swift Logistics", "supplier_code": "SUP-004", "contact_person": "Elena Rostova", "email": "dispatch@globalswift.sg", "phone": "+65-6789-2211", "address": "10 Marina Terminal Road", "city": "Singapore", "country": "Singapore", "status": "active"},
    {"id": SUP_APEX_DAIRY_ID, "name": "Apex Dairy Farms", "supplier_code": "SUP-005", "contact_person": "Liam O'Connor", "email": "contracts@apexdairy.com.au", "phone": "+61-3-5561-2200", "address": "400 Coastal Highway", "city": "Warrnambool", "country": "Australia", "status": "active"},
    {"id": SUP_MIDWEST_GRAIN_ID, "name": "Midwest Grain Corp", "supplier_code": "SUP-006", "contact_person": "David Miller", "email": "sales@midwestgrain.com", "phone": "+1-612-555-4920", "address": "1400 River Road", "city": "Minneapolis", "country": "USA", "status": "active"},
    {"id": SUP_RATNAGIRI_AGRO_ID, "name": "Ratnagiri Agro Exports", "supplier_code": "SUP-007", "contact_person": "Pooja Kulkarni", "email": "trade@ratnagiriagro.in", "phone": "+91-2352-224410", "address": "88 Port Wharf Road", "city": "Ratnagiri", "country": "India", "status": "active"},
    {"id": SUP_PACIFIC_REEFER_ID, "name": "Pacific Reefer Lines", "supplier_code": "SUP-008", "contact_person": "James MacLeod", "email": "ops@pacificreefer.com", "phone": "+61-2-9211-7788", "address": "25 Port Botany Way", "city": "Sydney", "country": "Australia", "status": "active"}
]
write_csv("suppliers.csv", suppliers, ["id", "name", "supplier_code", "contact_person", "email", "phone", "address", "city", "country", "status"])

# -----------------------------------------------------------------------------
# 3. inventory.csv
# -----------------------------------------------------------------------------
inventory = [
    {"id": INV_MILK_ID, "product_id": PROD_MILK_ID, "product_name": "Milk", "warehouse_location": "Cold Hub Alpha - Bay 4", "quantity": 45.0, "reserved_quantity": 15.0, "available_quantity": 30.0, "receiving_date": "2026-09-08", "expiry_date": "2026-09-22", "target_stock": 100.0},
    {"id": INV_BISCUITS_ID, "product_id": PROD_BISCUITS_ID, "product_name": "Biscuits", "warehouse_location": "Warehouse West - Aisle 12", "quantity": 60.0, "reserved_quantity": 10.0, "available_quantity": 50.0, "receiving_date": "2026-08-15", "expiry_date": "2027-02-15", "target_stock": 200.0},
    {"id": INV_MANGO_JUICE_ID, "product_id": PROD_MANGO_JUICE_ID, "product_name": "Mango Juice", "warehouse_location": "Beverage Distribution East", "quantity": 350.0, "reserved_quantity": 50.0, "available_quantity": 300.0, "receiving_date": "2026-09-01", "expiry_date": "2027-03-01", "target_stock": 150.0},
    {"id": INV_RAW_MILK_ID, "product_id": RAW_MILK_ID, "product_name": "Raw Pasteurization Feedstock", "warehouse_location": "Cold Hub Alpha - Silo 1", "quantity": 45.0, "reserved_quantity": 0.0, "available_quantity": 45.0, "receiving_date": "2026-09-08", "expiry_date": "2026-09-18", "target_stock": 500.0},
    {"id": INV_RAW_FLOUR_ID, "product_id": RAW_FLOUR_ID, "product_name": "Premium Biscuit Flour Mix", "warehouse_location": "Warehouse West - Silo 3", "quantity": 120.0, "reserved_quantity": 20.0, "available_quantity": 100.0, "receiving_date": "2026-08-10", "expiry_date": "2027-02-10", "target_stock": 600.0},
    {"id": INV_RAW_PULP_ID, "product_id": RAW_PULP_ID, "product_name": "Alphonso Mango Pulp Concentrate", "warehouse_location": "Beverage Distribution East - Cold Zone", "quantity": 350.0, "reserved_quantity": 50.0, "available_quantity": 300.0, "receiving_date": "2026-09-10", "expiry_date": "2027-03-10", "target_stock": 300.0},
    {"id": INV_PKG_BOTTLE_ID, "product_id": PKG_BOTTLE_ID, "product_name": "500ml Aseptic Glass Bottles", "warehouse_location": "Beverage Distribution East - Pallet Bay", "quantity": 2500.0, "reserved_quantity": 500.0, "available_quantity": 2000.0, "receiving_date": "2026-08-20", "expiry_date": "2028-08-20", "target_stock": 1000.0},
    {"id": INV_PKG_WRAP_ID, "product_id": PKG_WRAP_ID, "product_name": "Moisture-Barrier Biscuit Wrappers", "warehouse_location": "Warehouse West - Rack 4", "quantity": 80.0, "reserved_quantity": 10.0, "available_quantity": 70.0, "receiving_date": "2026-08-01", "expiry_date": "2028-08-01", "target_stock": 50.0}
]
write_csv("inventory.csv", inventory, ["id", "product_id", "product_name", "warehouse_location", "quantity", "reserved_quantity", "available_quantity", "receiving_date", "expiry_date", "target_stock"])

# -----------------------------------------------------------------------------
# 4. purchase_orders.csv
# -----------------------------------------------------------------------------
purchase_orders = [
    {"id": PO_001_ID, "po_number": "PO-001", "supplier_id": SUP_DAIRY_PURE_ID, "created_by": "USR-PROC-01", "status": "ordered", "priority": "high", "order_date": "2026-09-03", "original_expected_delivery_date": "2026-09-06", "revised_delivery_date": "2026-09-14", "actual_delivery_date": "", "total_amount": 5000.0, "notes": "Raw Milk batch - Dairy Pure Co experiencing refrigerated tank delay (8 days late)"},
    {"id": PO_002_ID, "po_number": "PO-002", "supplier_id": SUP_GOLDEN_WHEAT_ID, "created_by": "USR-PROC-02", "status": "ordered", "priority": "medium", "order_date": "2026-09-11", "original_expected_delivery_date": "2026-09-15", "revised_delivery_date": "2026-09-18", "actual_delivery_date": "", "total_amount": 12500.0, "notes": "Baking flour and biscuit mix consignment - freight delayed at Chicago rail terminal"},
    {"id": PO_003_ID, "po_number": "PO-003", "supplier_id": SUP_TROPICAL_GROVES_ID, "created_by": "USR-PROC-01", "status": "received", "priority": "medium", "order_date": "2026-08-31", "original_expected_delivery_date": "2026-09-10", "revised_delivery_date": "2026-09-10", "actual_delivery_date": "2026-09-10", "total_amount": 8400.0, "notes": "Alphonso Mango pulp concentrate delivery - verified, inspected, and received into inventory"},
    
    # Historical POs for Performance Analytics (On-Time Delivery, Defect Rates, Price Trends)
    {"id": "77777777-1111-4444-8888-000000000001", "po_number": "PO-2026-HIST-001", "supplier_id": SUP_DAIRY_PURE_ID, "created_by": "USR-PROC-01", "status": "received", "priority": "high", "order_date": "2026-06-01", "original_expected_delivery_date": "2026-06-04", "revised_delivery_date": "2026-06-04", "actual_delivery_date": "2026-06-04", "total_amount": 4800.0, "notes": "Historical regular dairy delivery - on time, perfect quality"},
    {"id": "77777777-1111-4444-8888-000000000002", "po_number": "PO-2026-HIST-002", "supplier_id": SUP_DAIRY_PURE_ID, "created_by": "USR-PROC-01", "status": "received", "priority": "high", "order_date": "2026-07-02", "original_expected_delivery_date": "2026-07-05", "revised_delivery_date": "2026-07-07", "actual_delivery_date": "2026-07-07", "total_amount": 4900.0, "notes": "Historical dairy order - 2 day weather delay"},
    {"id": "77777777-1111-4444-8888-000000000003", "po_number": "PO-2026-HIST-003", "supplier_id": SUP_DAIRY_PURE_ID, "created_by": "USR-PROC-01", "status": "received", "priority": "high", "order_date": "2026-08-01", "original_expected_delivery_date": "2026-08-04", "revised_delivery_date": "2026-08-04", "actual_delivery_date": "2026-08-04", "total_amount": 5000.0, "notes": "Historical dairy order - on time"},
    
    {"id": "77777777-1111-4444-8888-000000000004", "po_number": "PO-2026-HIST-004", "supplier_id": SUP_GOLDEN_WHEAT_ID, "created_by": "USR-PROC-02", "status": "received", "priority": "medium", "order_date": "2026-06-10", "original_expected_delivery_date": "2026-06-17", "revised_delivery_date": "2026-06-17", "actual_delivery_date": "2026-06-17", "total_amount": 12000.0, "notes": "Flour bulk delivery - on time"},
    {"id": "77777777-1111-4444-8888-000000000005", "po_number": "PO-2026-HIST-005", "supplier_id": SUP_GOLDEN_WHEAT_ID, "created_by": "USR-PROC-02", "status": "received", "priority": "medium", "order_date": "2026-07-15", "original_expected_delivery_date": "2026-07-22", "revised_delivery_date": "2026-07-22", "actual_delivery_date": "2026-07-22", "total_amount": 12200.0, "notes": "Flour bulk delivery - on time"},
    {"id": "77777777-1111-4444-8888-000000000006", "po_number": "PO-2026-HIST-006", "supplier_id": SUP_GOLDEN_WHEAT_ID, "created_by": "USR-PROC-02", "status": "received", "priority": "medium", "order_date": "2026-08-10", "original_expected_delivery_date": "2026-08-17", "revised_delivery_date": "2026-08-18", "actual_delivery_date": "2026-08-18", "total_amount": 12500.0, "notes": "Flour bulk delivery - 1 day rail siding delay"},
    
    {"id": "77777777-1111-4444-8888-000000000007", "po_number": "PO-2026-HIST-007", "supplier_id": SUP_TROPICAL_GROVES_ID, "created_by": "USR-PROC-01", "status": "received", "priority": "medium", "order_date": "2026-06-20", "original_expected_delivery_date": "2026-07-01", "revised_delivery_date": "2026-07-01", "actual_delivery_date": "2026-07-01", "total_amount": 8000.0, "notes": "Mango concentrate batch - on time"},
    {"id": "77777777-1111-4444-8888-000000000008", "po_number": "PO-2026-HIST-008", "supplier_id": SUP_TROPICAL_GROVES_ID, "created_by": "USR-PROC-01", "status": "received", "priority": "medium", "order_date": "2026-07-25", "original_expected_delivery_date": "2026-08-05", "revised_delivery_date": "2026-08-05", "actual_delivery_date": "2026-08-05", "total_amount": 8200.0, "notes": "Mango concentrate batch - on time"}
]
write_csv("purchase_orders.csv", purchase_orders, ["id", "po_number", "supplier_id", "created_by", "status", "priority", "order_date", "original_expected_delivery_date", "revised_delivery_date", "actual_delivery_date", "total_amount", "notes"])

# -----------------------------------------------------------------------------
# 5. purchase_order_items.csv
# -----------------------------------------------------------------------------
purchase_order_items = [
    {"id": POI_001_ID, "purchase_order_id": PO_001_ID, "product_id": PROD_MILK_ID, "quantity": 100.0, "unit_price": 50.0, "total_price": 5000.0},
    {"id": POI_002_ID, "purchase_order_id": PO_002_ID, "product_id": PROD_BISCUITS_ID, "quantity": 250.0, "unit_price": 50.0, "total_price": 12500.0},
    {"id": POI_003_ID, "purchase_order_id": PO_003_ID, "product_id": PROD_MANGO_JUICE_ID, "quantity": 300.0, "unit_price": 28.0, "total_price": 8400.0},
    
    # Historical PO Items
    {"id": "88888888-2222-5555-9999-000000000001", "purchase_order_id": "77777777-1111-4444-8888-000000000001", "product_id": PROD_MILK_ID, "quantity": 100.0, "unit_price": 48.0, "total_price": 4800.0},
    {"id": "88888888-2222-5555-9999-000000000002", "purchase_order_id": "77777777-1111-4444-8888-000000000002", "product_id": PROD_MILK_ID, "quantity": 100.0, "unit_price": 49.0, "total_price": 4900.0},
    {"id": "88888888-2222-5555-9999-000000000003", "purchase_order_id": "77777777-1111-4444-8888-000000000003", "product_id": PROD_MILK_ID, "quantity": 100.0, "unit_price": 50.0, "total_price": 5000.0},
    
    {"id": "88888888-2222-5555-9999-000000000004", "purchase_order_id": "77777777-1111-4444-8888-000000000004", "product_id": PROD_BISCUITS_ID, "quantity": 250.0, "unit_price": 48.0, "total_price": 12000.0},
    {"id": "88888888-2222-5555-9999-000000000005", "purchase_order_id": "77777777-1111-4444-8888-000000000005", "product_id": PROD_BISCUITS_ID, "quantity": 250.0, "unit_price": 48.8, "total_price": 12200.0},
    {"id": "88888888-2222-5555-9999-000000000006", "purchase_order_id": "77777777-1111-4444-8888-000000000006", "product_id": PROD_BISCUITS_ID, "quantity": 250.0, "unit_price": 50.0, "total_price": 12500.0},
    
    {"id": "88888888-2222-5555-9999-000000000007", "purchase_order_id": "77777777-1111-4444-8888-000000000007", "product_id": PROD_MANGO_JUICE_ID, "quantity": 300.0, "unit_price": 26.67, "total_price": 8000.0},
    {"id": "88888888-2222-5555-9999-000000000008", "purchase_order_id": "77777777-1111-4444-8888-000000000008", "product_id": PROD_MANGO_JUICE_ID, "quantity": 300.0, "unit_price": 27.33, "total_price": 8200.0}
]
write_csv("purchase_order_items.csv", purchase_order_items, ["id", "purchase_order_id", "product_id", "quantity", "unit_price", "total_price"])

# -----------------------------------------------------------------------------
# 6. shipments.csv (FIXED SHP-003 & Normalized Date Columns)
# -----------------------------------------------------------------------------
shipments = [
    {
        "id": SHP_001_ID,
        "shipment_number": "SHP-2026-001",
        "purchase_order_id": PO_002_ID,
        "supplier_id": SUP_GOLDEN_WHEAT_ID,
        "status": "delayed",
        "carrier_name": "Global Swift Logistics",
        "tracking_number": "TRK-SWIFT-8912",
        "origin": "Chicago Central Freight Rail",
        "destination": "Warehouse West Distribution",
        "original_expected_delivery_date": "2026-09-15",
        "revised_delivery_date": "2026-09-18",
        "actual_delivery_date": ""
    },
    {
        "id": SHP_002_ID,
        "shipment_number": "SHP-2026-002",
        "purchase_order_id": PO_001_ID,
        "supplier_id": SUP_DAIRY_PURE_ID,
        "status": "delayed",
        "carrier_name": "ColdRoute Express",
        "tracking_number": "TRK-COLD-4401",
        "origin": "Melbourne Cold Logistics Hub",
        "destination": "Cold Hub Alpha - Bay 4",
        "original_expected_delivery_date": "2026-09-06",
        "revised_delivery_date": "2026-09-14",
        "actual_delivery_date": ""
    },
    {
        "id": SHP_003_ID,
        "shipment_number": "SHP-2026-003",
        "purchase_order_id": PO_003_ID,
        "supplier_id": SUP_TROPICAL_GROVES_ID,
        "status": "delivered",
        "carrier_name": "Pacific Ocean Maritime",
        "tracking_number": "TRK-MAR-5520",
        "origin": "Jawaharlal Nehru Port, Mumbai",
        "destination": "Beverage Distribution East",
        "original_expected_delivery_date": "2026-09-10",
        "revised_delivery_date": "2026-09-10",
        "actual_delivery_date": "2026-09-10"
    },
    # Historical Shipments
    {
        "id": "99999999-3333-6666-aaaa-000000000001",
        "shipment_number": "SHP-2026-HIST-001",
        "purchase_order_id": "77777777-1111-4444-8888-000000000001",
        "supplier_id": SUP_DAIRY_PURE_ID,
        "status": "delivered",
        "carrier_name": "ColdRoute Express",
        "tracking_number": "TRK-COLD-3101",
        "origin": "Melbourne Cold Logistics Hub",
        "destination": "Cold Hub Alpha - Bay 4",
        "original_expected_delivery_date": "2026-06-04",
        "revised_delivery_date": "2026-06-04",
        "actual_delivery_date": "2026-06-04"
    },
    {
        "id": "99999999-3333-6666-aaaa-000000000002",
        "shipment_number": "SHP-2026-HIST-002",
        "purchase_order_id": "77777777-1111-4444-8888-000000000004",
        "supplier_id": SUP_GOLDEN_WHEAT_ID,
        "status": "delivered",
        "carrier_name": "Global Swift Logistics",
        "tracking_number": "TRK-SWIFT-6204",
        "origin": "Chicago Central Freight Rail",
        "destination": "Warehouse West Distribution",
        "original_expected_delivery_date": "2026-06-17",
        "revised_delivery_date": "2026-06-17",
        "actual_delivery_date": "2026-06-17"
    },
    {
        "id": "99999999-3333-6666-aaaa-000000000003",
        "shipment_number": "SHP-2026-HIST-003",
        "purchase_order_id": "77777777-1111-4444-8888-000000000007",
        "supplier_id": SUP_TROPICAL_GROVES_ID,
        "status": "delivered",
        "carrier_name": "Pacific Ocean Maritime",
        "tracking_number": "TRK-MAR-4109",
        "origin": "Jawaharlal Nehru Port, Mumbai",
        "destination": "Beverage Distribution East",
        "original_expected_delivery_date": "2026-07-01",
        "revised_delivery_date": "2026-07-01",
        "actual_delivery_date": "2026-07-01"
    }
]
write_csv("shipments.csv", shipments, [
    "id", "shipment_number", "purchase_order_id", "supplier_id", "status",
    "carrier_name", "tracking_number", "origin", "destination",
    "original_expected_delivery_date", "revised_delivery_date", "actual_delivery_date"
])

# -----------------------------------------------------------------------------
# 7. production_orders.csv
# -----------------------------------------------------------------------------
production_orders = [
    {
        "id": PRD_MJ_ID,
        "production_number": "PRD-MJ-202609",
        "product_id": PROD_MANGO_JUICE_ID,
        "created_by": "USR-PRD-01",
        "planned_quantity": 500.0,
        "produced_quantity": 120.0,
        "status": "in_progress",
        "planned_start_date": "2026-09-12",
        "planned_end_date": "2026-09-15",
        "actual_start_date": "2026-09-12",
        "actual_end_date": "",
        "notes": "Bottling Line 2 running at 40% capacity due to high-pressure nozzle calibration issue"
    },
    {
        "id": PRD_BIS_ID,
        "production_number": "PRD-BIS-202609",
        "product_id": PROD_BISCUITS_ID,
        "created_by": "USR-PRD-02",
        "planned_quantity": 1000.0,
        "produced_quantity": 0.0,
        "status": "planned",
        "planned_start_date": "2026-09-16",
        "planned_end_date": "2026-09-20",
        "actual_start_date": "",
        "actual_end_date": "",
        "notes": "High-volume biscuit packaging run scheduled following flour delivery"
    },
    {
        "id": PRD_MILK_ID,
        "production_number": "PRD-MILK-202609",
        "product_id": PROD_MILK_ID,
        "created_by": "USR-PRD-01",
        "planned_quantity": 800.0,
        "produced_quantity": 0.0,
        "status": "planned",
        "planned_start_date": "2026-09-17",
        "planned_end_date": "2026-09-19",
        "actual_start_date": "",
        "actual_end_date": "",
        "notes": "Awaiting raw pasteurization feedstock confirmation from PO-001"
    }
]
write_csv("production_orders.csv", production_orders, [
    "id", "production_number", "product_id", "created_by", "planned_quantity",
    "produced_quantity", "status", "planned_start_date", "planned_end_date",
    "actual_start_date", "actual_end_date", "notes"
])

# -----------------------------------------------------------------------------
# 8. events.csv
# -----------------------------------------------------------------------------
events = [
    {
        "id": EVT_001_ID,
        "event_type": "INVENTORY_DEPLETED",
        "entity_type": "inventory",
        "entity_id": INV_BISCUITS_ID,
        "actor_id": "SYSTEM_TRIGGER",
        "description": "Biscuits stock level fell below critical reorder threshold (Current: 50, Reorder: 200)",
        "metadata": json.dumps({"sku": "BIS-001", "quantity": 50, "location": "Warehouse West", "reorder_level": 200}),
        "created_at": "2026-09-14T15:15:39Z"
    },
    {
        "id": EVT_002_ID,
        "event_type": "SUPPLIER_DELAY_REPORTED",
        "entity_type": "purchase_order",
        "entity_id": PO_001_ID,
        "actor_id": "SYSTEM_CARRIER_INTEGRATION",
        "description": "Supplier Dairy Pure Co confirmed 8-day delivery delay on PO-001 (Original ETA: 2026-09-06, Revised ETA: 2026-09-14)",
        "metadata": json.dumps({"supplier": "Dairy Pure Co", "po_number": "PO-001", "delay_days": 8, "original_eta": "2026-09-06", "revised_eta": "2026-09-14"}),
        "created_at": "2026-09-14T09:15:39Z"
    },
    {
        "id": EVT_003_ID,
        "event_type": "PRODUCTION_SLOWDOWN_RECORDED",
        "entity_type": "production_order",
        "entity_id": PRD_MJ_ID,
        "actor_id": "IOT_SHOPFLOOR_AGENT",
        "description": "IoT telemetry detected 60% throughput drop on Bottling Line 2 for Mango Juice batch",
        "metadata": json.dumps({"line": "Bottling Line 2", "batch": "PRD-MJ-202609", "current_efficiency": 0.40, "target_efficiency": 1.0}),
        "created_at": "2026-09-14T17:15:39Z"
    },
    {
        "id": EVT_004_ID,
        "event_type": "SHIPMENT_DELAY_DETECTED",
        "entity_type": "shipment",
        "entity_id": SHP_001_ID,
        "actor_id": "GPS_TELEMATICS_FEED",
        "description": "GPS tracker reports carrier Global Swift Logistics halted at rail terminal hub, ETA delta: +72 hours (Revised ETA: 2026-09-18)",
        "metadata": json.dumps({"shipment_number": "SHP-2026-001", "status": "delayed", "eta_delta_hours": 72, "original_eta": "2026-09-15", "revised_eta": "2026-09-18"}),
        "created_at": "2026-09-14T19:15:39Z"
    },
    {
        "id": EVT_005_ID,
        "event_type": "CROSS_DOMAIN_DISRUPTION_RAISED",
        "entity_type": "purchase_order",
        "entity_id": PO_001_ID,
        "actor_id": "ORCHESTRATION_ENGINE",
        "description": "Milk feedstock shortage escalated to production scheduling and sales fulfillment channels",
        "metadata": json.dumps({"severity": "critical", "affected_orders": ["PO-001", "PRD-MILK-202609"], "root_cause": "Refrigeration breakdown at Dairy Pure Co"}),
        "created_at": "2026-09-14T20:15:39Z"
    }
]
write_csv("events.csv", events, ["id", "event_type", "entity_type", "entity_id", "actor_id", "description", "metadata", "created_at"])

# -----------------------------------------------------------------------------
# 9. inventory_events.csv
# -----------------------------------------------------------------------------
inventory_events = [
    {"event_id": "EVT-INV-001", "event_type": "STOCK_LOW", "entity_id": "BIS-001", "current_stock": 50, "target_stock": 200},
    {"event_id": "EVT-INV-002", "event_type": "STOCK_LOW", "entity_id": "MILK-001", "current_stock": 30, "target_stock": 100},
    {"event_id": "EVT-INV-003", "event_type": "STOCK_OPTIMAL", "entity_id": "MJ-001", "current_stock": 300, "target_stock": 150}
]
write_csv("inventory_events.csv", inventory_events, ["event_id", "event_type", "entity_id", "current_stock", "target_stock"])

# =============================================================================
# 10. NEW PROCUREMENT DATASETS
# =============================================================================

# supplier_products.csv (Mapping, MOQ, Lead Times, Alternative/Backup Tier)
supplier_products = [
    {"id": "sp-001", "supplier_id": SUP_DAIRY_PURE_ID, "product_id": PROD_MILK_ID, "tier": "primary", "standard_lead_time_days": 3, "min_order_quantity": 50.0, "unit_price": 50.0, "currency": "USD", "is_certified": True},
    {"id": "sp-002", "supplier_id": SUP_DAIRY_PURE_ID, "product_id": RAW_MILK_ID, "tier": "primary", "standard_lead_time_days": 3, "min_order_quantity": 100.0, "unit_price": 35.0, "currency": "USD", "is_certified": True},
    {"id": "sp-003", "supplier_id": SUP_APEX_DAIRY_ID, "product_id": PROD_MILK_ID, "tier": "backup", "standard_lead_time_days": 4, "min_order_quantity": 80.0, "unit_price": 52.5, "currency": "USD", "is_certified": True},
    {"id": "sp-004", "supplier_id": SUP_APEX_DAIRY_ID, "product_id": RAW_MILK_ID, "tier": "backup", "standard_lead_time_days": 4, "min_order_quantity": 150.0, "unit_price": 37.0, "currency": "USD", "is_certified": True},
    
    {"id": "sp-005", "supplier_id": SUP_GOLDEN_WHEAT_ID, "product_id": PROD_BISCUITS_ID, "tier": "primary", "standard_lead_time_days": 4, "min_order_quantity": 100.0, "unit_price": 50.0, "currency": "USD", "is_certified": True},
    {"id": "sp-006", "supplier_id": SUP_GOLDEN_WHEAT_ID, "product_id": RAW_FLOUR_ID, "tier": "primary", "standard_lead_time_days": 4, "min_order_quantity": 200.0, "unit_price": 25.0, "currency": "USD", "is_certified": True},
    {"id": "sp-007", "supplier_id": SUP_MIDWEST_GRAIN_ID, "product_id": PROD_BISCUITS_ID, "tier": "backup", "standard_lead_time_days": 5, "min_order_quantity": 150.0, "unit_price": 53.0, "currency": "USD", "is_certified": True},
    {"id": "sp-008", "supplier_id": SUP_MIDWEST_GRAIN_ID, "product_id": RAW_FLOUR_ID, "tier": "backup", "standard_lead_time_days": 5, "min_order_quantity": 250.0, "unit_price": 26.5, "currency": "USD", "is_certified": True},
    
    {"id": "sp-009", "supplier_id": SUP_TROPICAL_GROVES_ID, "product_id": PROD_MANGO_JUICE_ID, "tier": "primary", "standard_lead_time_days": 10, "min_order_quantity": 100.0, "unit_price": 28.0, "currency": "USD", "is_certified": True},
    {"id": "sp-010", "supplier_id": SUP_TROPICAL_GROVES_ID, "product_id": RAW_PULP_ID, "tier": "primary", "standard_lead_time_days": 10, "min_order_quantity": 150.0, "unit_price": 18.0, "currency": "USD", "is_certified": True},
    {"id": "sp-011", "supplier_id": SUP_RATNAGIRI_AGRO_ID, "product_id": PROD_MANGO_JUICE_ID, "tier": "backup", "standard_lead_time_days": 12, "min_order_quantity": 120.0, "unit_price": 29.5, "currency": "USD", "is_certified": True},
    {"id": "sp-012", "supplier_id": SUP_RATNAGIRI_AGRO_ID, "product_id": RAW_PULP_ID, "tier": "backup", "standard_lead_time_days": 12, "min_order_quantity": 200.0, "unit_price": 19.2, "currency": "USD", "is_certified": True}
]
write_csv("supplier_products.csv", supplier_products, ["id", "supplier_id", "product_id", "tier", "standard_lead_time_days", "min_order_quantity", "unit_price", "currency", "is_certified"])

# supplier_performance.csv (Historical Delivery Records for On-Time, Defect, and Delay Calculation)
supplier_performance = [
    # Dairy Pure Co (SUP-001) - Historically good, but severe current delay
    {"id": "perf-001", "supplier_id": SUP_DAIRY_PURE_ID, "purchase_order_id": "77777777-1111-4444-8888-000000000001", "order_date": "2026-06-01", "promised_delivery_date": "2026-06-04", "actual_delivery_date": "2026-06-04", "lead_time_days": 3, "delay_days": 0, "on_time_status": "ON_TIME", "delivered_quantity": 100.0, "accepted_quantity": 100.0, "rejected_quantity": 0.0, "defect_rate": 0.0, "inspection_notes": "Passed bacteriological and fat content testing"},
    {"id": "perf-002", "supplier_id": SUP_DAIRY_PURE_ID, "purchase_order_id": "77777777-1111-4444-8888-000000000002", "order_date": "2026-07-02", "promised_delivery_date": "2026-07-05", "actual_delivery_date": "2026-07-07", "lead_time_days": 5, "delay_days": 2, "on_time_status": "LATE", "delivered_quantity": 100.0, "accepted_quantity": 98.0, "rejected_quantity": 2.0, "defect_rate": 0.02, "inspection_notes": "Minor cap seal damage on 2 units"},
    {"id": "perf-003", "supplier_id": SUP_DAIRY_PURE_ID, "purchase_order_id": "77777777-1111-4444-8888-000000000003", "order_date": "2026-08-01", "promised_delivery_date": "2026-08-04", "actual_delivery_date": "2026-08-04", "lead_time_days": 3, "delay_days": 0, "on_time_status": "ON_TIME", "delivered_quantity": 100.0, "accepted_quantity": 100.0, "rejected_quantity": 0.0, "defect_rate": 0.0, "inspection_notes": "Passed all quality criteria"},
    {"id": "perf-004", "supplier_id": SUP_DAIRY_PURE_ID, "purchase_order_id": PO_001_ID, "order_date": "2026-09-03", "promised_delivery_date": "2026-09-06", "actual_delivery_date": "", "lead_time_days": 11, "delay_days": 8, "on_time_status": "CRITICAL_DELAY", "delivered_quantity": 0.0, "accepted_quantity": 0.0, "rejected_quantity": 0.0, "defect_rate": 0.0, "inspection_notes": "Refrigeration compressor breakdown in transport"},
    
    # Golden Wheat Mills (SUP-002) - Highly reliable supplier
    {"id": "perf-005", "supplier_id": SUP_GOLDEN_WHEAT_ID, "purchase_order_id": "77777777-1111-4444-8888-000000000004", "order_date": "2026-06-10", "promised_delivery_date": "2026-06-17", "actual_delivery_date": "2026-06-17", "lead_time_days": 7, "delay_days": 0, "on_time_status": "ON_TIME", "delivered_quantity": 250.0, "accepted_quantity": 250.0, "rejected_quantity": 0.0, "defect_rate": 0.0, "inspection_notes": "Flour moisture content verified at 13.5%"},
    {"id": "perf-006", "supplier_id": SUP_GOLDEN_WHEAT_ID, "purchase_order_id": "77777777-1111-4444-8888-000000000005", "order_date": "2026-07-15", "promised_delivery_date": "2026-07-22", "actual_delivery_date": "2026-07-22", "lead_time_days": 7, "delay_days": 0, "on_time_status": "ON_TIME", "delivered_quantity": 250.0, "accepted_quantity": 248.0, "rejected_quantity": 2.0, "defect_rate": 0.008, "inspection_notes": "Slight torn packaging on 2 cartons"},
    {"id": "perf-007", "supplier_id": SUP_GOLDEN_WHEAT_ID, "purchase_order_id": "77777777-1111-4444-8888-000000000006", "order_date": "2026-08-10", "promised_delivery_date": "2026-08-17", "actual_delivery_date": "2026-08-18", "lead_time_days": 8, "delay_days": 1, "on_time_status": "LATE", "delivered_quantity": 250.0, "accepted_quantity": 250.0, "rejected_quantity": 0.0, "defect_rate": 0.0, "inspection_notes": "Passed quality testing"},
    {"id": "perf-008", "supplier_id": SUP_GOLDEN_WHEAT_ID, "purchase_order_id": PO_002_ID, "order_date": "2026-09-11", "promised_delivery_date": "2026-09-15", "actual_delivery_date": "", "lead_time_days": 7, "delay_days": 3, "on_time_status": "TRANSIT_DELAY", "delivered_quantity": 0.0, "accepted_quantity": 0.0, "rejected_quantity": 0.0, "defect_rate": 0.0, "inspection_notes": "Carrier rail intermodal bottleneck in Chicago"},
    
    # Tropical Sunshine Groves (SUP-003) - Steady international supplier
    {"id": "perf-009", "supplier_id": SUP_TROPICAL_GROVES_ID, "purchase_order_id": "77777777-1111-4444-8888-000000000007", "order_date": "2026-06-20", "promised_delivery_date": "2026-07-01", "actual_delivery_date": "2026-07-01", "lead_time_days": 11, "delay_days": 0, "on_time_status": "ON_TIME", "delivered_quantity": 300.0, "accepted_quantity": 300.0, "rejected_quantity": 0.0, "defect_rate": 0.0, "inspection_notes": "Brix reading 16.2, pH 3.8"},
    {"id": "perf-010", "supplier_id": SUP_TROPICAL_GROVES_ID, "purchase_order_id": "77777777-1111-4444-8888-000000000008", "order_date": "2026-07-25", "promised_delivery_date": "2026-08-05", "actual_delivery_date": "2026-08-05", "lead_time_days": 11, "delay_days": 0, "on_time_status": "ON_TIME", "delivered_quantity": 300.0, "accepted_quantity": 300.0, "rejected_quantity": 0.0, "defect_rate": 0.0, "inspection_notes": "Aseptic packaging intact"},
    {"id": "perf-011", "supplier_id": SUP_TROPICAL_GROVES_ID, "purchase_order_id": PO_003_ID, "order_date": "2026-08-31", "promised_delivery_date": "2026-09-10", "actual_delivery_date": "2026-09-10", "lead_time_days": 10, "delay_days": 0, "on_time_status": "ON_TIME", "delivered_quantity": 300.0, "accepted_quantity": 300.0, "rejected_quantity": 0.0, "defect_rate": 0.0, "inspection_notes": "Passed full incoming laboratory assay"}
]
write_csv("supplier_performance.csv", supplier_performance, [
    "id", "supplier_id", "purchase_order_id", "order_date", "promised_delivery_date",
    "actual_delivery_date", "lead_time_days", "delay_days", "on_time_status",
    "delivered_quantity", "accepted_quantity", "rejected_quantity", "defect_rate", "inspection_notes"
])

# supplier_capacity.csv (Capacity, Monthly Limit, Surge Allowance)
supplier_capacity = [
    {"id": "cap-001", "supplier_id": SUP_DAIRY_PURE_ID, "product_id": PROD_MILK_ID, "period_month": "2026-09", "monthly_capacity": 5000.0, "allocated_quantity": 3800.0, "available_capacity": 1200.0, "max_surge_capacity": 6000.0, "maintenance_scheduled": "2026-09-25", "status": "constrained"},
    {"id": "cap-002", "supplier_id": SUP_APEX_DAIRY_ID, "product_id": PROD_MILK_ID, "period_month": "2026-09", "monthly_capacity": 6000.0, "allocated_quantity": 2500.0, "available_capacity": 3500.0, "max_surge_capacity": 7500.0, "maintenance_scheduled": "2026-10-10", "status": "optimal"},
    {"id": "cap-003", "supplier_id": SUP_GOLDEN_WHEAT_ID, "product_id": PROD_BISCUITS_ID, "period_month": "2026-09", "monthly_capacity": 10000.0, "allocated_quantity": 7200.0, "available_capacity": 2800.0, "max_surge_capacity": 12000.0, "maintenance_scheduled": "", "status": "optimal"},
    {"id": "cap-004", "supplier_id": SUP_MIDWEST_GRAIN_ID, "product_id": PROD_BISCUITS_ID, "period_month": "2026-09", "monthly_capacity": 8000.0, "allocated_quantity": 3000.0, "available_capacity": 5000.0, "max_surge_capacity": 9500.0, "maintenance_scheduled": "", "status": "optimal"},
    {"id": "cap-005", "supplier_id": SUP_TROPICAL_GROVES_ID, "product_id": PROD_MANGO_JUICE_ID, "period_month": "2026-09", "monthly_capacity": 8000.0, "allocated_quantity": 6000.0, "available_capacity": 2000.0, "max_surge_capacity": 9000.0, "maintenance_scheduled": "", "status": "optimal"},
    {"id": "cap-006", "supplier_id": SUP_RATNAGIRI_AGRO_ID, "product_id": PROD_MANGO_JUICE_ID, "period_month": "2026-09", "monthly_capacity": 6000.0, "allocated_quantity": 2000.0, "available_capacity": 4000.0, "max_surge_capacity": 7000.0, "maintenance_scheduled": "", "status": "optimal"}
]
write_csv("supplier_capacity.csv", supplier_capacity, [
    "id", "supplier_id", "product_id", "period_month", "monthly_capacity",
    "allocated_quantity", "available_capacity", "max_surge_capacity", "maintenance_scheduled", "status"
])

# supplier_contracts.csv (Contract terms, SLAs, penalty clauses)
supplier_contracts = [
    {"id": "cnt-001", "supplier_id": SUP_DAIRY_PURE_ID, "contract_number": "CTR-DP-2025", "title": "Fresh Dairy Bulk Supply Agreement", "start_date": "2025-01-01", "end_date": "2026-12-31", "payment_terms": "Net 30", "incoterms": "DDP", "late_penalty_rate_percent": 1.5, "min_sla_on_time_percent": 95.0, "auto_renew": True, "status": "active"},
    {"id": "cnt-002", "supplier_id": SUP_GOLDEN_WHEAT_ID, "contract_number": "CTR-GW-2025", "title": "Baking Flour Long-Term Sourcing MSA", "start_date": "2025-03-01", "end_date": "2027-02-28", "payment_terms": "Net 45", "incoterms": "FOB", "late_penalty_rate_percent": 1.0, "min_sla_on_time_percent": 92.0, "auto_renew": True, "status": "active"},
    {"id": "cnt-003", "supplier_id": SUP_TROPICAL_GROVES_ID, "contract_number": "CTR-TG-2025", "title": "Tropical Fruit Puree Import Agreement", "start_date": "2025-05-01", "end_date": "2027-04-30", "payment_terms": "Letter of Credit", "incoterms": "CIF", "late_penalty_rate_percent": 2.0, "min_sla_on_time_percent": 90.0, "auto_renew": False, "status": "active"},
    {"id": "cnt-004", "supplier_id": SUP_GLOBAL_SWIFT_ID, "contract_number": "CTR-GS-2026", "title": "Master Freight & Intermodal Transport Agreement", "start_date": "2026-01-01", "end_date": "2026-12-31", "payment_terms": "Net 30", "incoterms": "FCA", "late_penalty_rate_percent": 2.5, "min_sla_on_time_percent": 96.0, "auto_renew": True, "status": "active"},
    {"id": "cnt-005", "supplier_id": SUP_APEX_DAIRY_ID, "contract_number": "CTR-AD-2026", "title": "Secondary Dairy Contingency Framework Agreement", "start_date": "2026-02-01", "end_date": "2027-01-31", "payment_terms": "Net 30", "incoterms": "DDP", "late_penalty_rate_percent": 1.0, "min_sla_on_time_percent": 90.0, "auto_renew": True, "status": "standby"},
    {"id": "cnt-006", "supplier_id": SUP_MIDWEST_GRAIN_ID, "contract_number": "CTR-MG-2026", "title": "Secondary Grain Contingency Agreement", "start_date": "2026-02-01", "end_date": "2027-01-31", "payment_terms": "Net 30", "incoterms": "FOB", "late_penalty_rate_percent": 1.0, "min_sla_on_time_percent": 90.0, "auto_renew": True, "status": "standby"}
]
write_csv("supplier_contracts.csv", supplier_contracts, [
    "id", "supplier_id", "contract_number", "title", "start_date", "end_date",
    "payment_terms", "incoterms", "late_penalty_rate_percent", "min_sla_on_time_percent", "auto_renew", "status"
])

# purchase_requisitions.csv (Requisitions leading to POs)
purchase_requisitions = [
    {"id": "req-001", "requisition_number": "REQ-2026-089", "product_id": PROD_MILK_ID, "requested_by": "USR-INV-01", "department": "Dairy Operations", "requested_quantity": 100.0, "urgency": "critical", "request_date": "2026-09-02", "status": "approved", "approved_by": "USR-MGR-01", "approval_date": "2026-09-02", "purchase_order_id": PO_001_ID},
    {"id": "req-002", "requisition_number": "REQ-2026-090", "product_id": PROD_BISCUITS_ID, "requested_by": "USR-PRD-02", "department": "Snack Manufacturing", "requested_quantity": 250.0, "urgency": "medium", "request_date": "2026-09-10", "status": "approved", "approved_by": "USR-MGR-02", "approval_date": "2026-09-11", "purchase_order_id": PO_002_ID},
    {"id": "req-003", "requisition_number": "REQ-2026-085", "product_id": PROD_MANGO_JUICE_ID, "requested_by": "USR-INV-02", "department": "Beverage Bottling", "requested_quantity": 300.0, "urgency": "medium", "request_date": "2026-08-30", "status": "approved", "approved_by": "USR-MGR-01", "approval_date": "2026-08-31", "purchase_order_id": PO_003_ID},
    {"id": "req-004", "requisition_number": "REQ-2026-092", "product_id": RAW_MILK_ID, "requested_by": "USR-PRD-01", "department": "Dairy Operations", "requested_quantity": 500.0, "urgency": "critical", "request_date": "2026-09-14", "status": "pending_approval", "approved_by": "", "approval_date": "", "purchase_order_id": ""}
]
write_csv("purchase_requisitions.csv", purchase_requisitions, [
    "id", "requisition_number", "product_id", "requested_by", "department",
    "requested_quantity", "urgency", "request_date", "status", "approved_by", "approval_date", "purchase_order_id"
])

# purchase_order_status_history.csv (Audit trail of PO life-cycle)
purchase_order_status_history = [
    {"id": "posh-001", "purchase_order_id": PO_001_ID, "previous_status": "draft", "new_status": "approved", "changed_by": "USR-MGR-01", "timestamp": "2026-09-03T08:30:00Z", "reason": "Approved high-priority dairy replenishment"},
    {"id": "posh-002", "purchase_order_id": PO_001_ID, "previous_status": "approved", "new_status": "ordered", "changed_by": "USR-PROC-01", "timestamp": "2026-09-03T09:15:00Z", "reason": "Transmitted EDI purchase order to Dairy Pure Co"},
    {"id": "posh-003", "purchase_order_id": PO_001_ID, "previous_status": "ordered", "new_status": "delayed", "changed_by": "SYSTEM", "timestamp": "2026-09-14T09:15:39Z", "reason": "Supplier reported mechanical cooling breakdown (delay of 8 days)"},
    
    {"id": "posh-004", "purchase_order_id": PO_002_ID, "previous_status": "draft", "new_status": "approved", "changed_by": "USR-MGR-02", "timestamp": "2026-09-11T10:00:00Z", "reason": "Routine raw flour restocking approval"},
    {"id": "posh-005", "purchase_order_id": PO_002_ID, "previous_status": "approved", "new_status": "ordered", "changed_by": "USR-PROC-02", "timestamp": "2026-09-11T11:20:00Z", "reason": "Dispatched order confirmation to Golden Wheat Mills"},
    
    {"id": "posh-006", "purchase_order_id": PO_003_ID, "previous_status": "ordered", "new_status": "in_transit", "changed_by": "SYSTEM", "timestamp": "2026-09-02T14:00:00Z", "reason": "Vessel departed origin port Mumbai"},
    {"id": "posh-007", "purchase_order_id": PO_003_ID, "previous_status": "in_transit", "new_status": "received", "changed_by": "USR-WH-03", "timestamp": "2026-09-10T16:30:00Z", "reason": "Received, inspected, and verified at Beverage Distribution East"}
]
write_csv("purchase_order_status_history.csv", purchase_order_status_history, [
    "id", "purchase_order_id", "previous_status", "new_status", "changed_by", "timestamp", "reason"
])

# purchase_price_history.csv (Historical unit price changes)
purchase_price_history = [
    {"id": "pph-001", "supplier_id": SUP_DAIRY_PURE_ID, "product_id": PROD_MILK_ID, "effective_start_date": "2026-01-01", "effective_end_date": "2026-06-30", "unit_price": 48.0, "currency": "USD", "volume_threshold": 100.0},
    {"id": "pph-002", "supplier_id": SUP_DAIRY_PURE_ID, "product_id": PROD_MILK_ID, "effective_start_date": "2026-07-01", "effective_end_date": "2026-12-31", "unit_price": 50.0, "currency": "USD", "volume_threshold": 100.0},
    
    {"id": "pph-003", "supplier_id": SUP_GOLDEN_WHEAT_ID, "product_id": PROD_BISCUITS_ID, "effective_start_date": "2026-01-01", "effective_end_date": "2026-06-30", "unit_price": 48.0, "currency": "USD", "volume_threshold": 250.0},
    {"id": "pph-004", "supplier_id": SUP_GOLDEN_WHEAT_ID, "product_id": PROD_BISCUITS_ID, "effective_start_date": "2026-07-01", "effective_end_date": "2026-12-31", "unit_price": 50.0, "currency": "USD", "volume_threshold": 250.0},
    
    {"id": "pph-005", "supplier_id": SUP_TROPICAL_GROVES_ID, "product_id": PROD_MANGO_JUICE_ID, "effective_start_date": "2026-01-01", "effective_end_date": "2026-06-30", "unit_price": 26.67, "currency": "USD", "volume_threshold": 300.0},
    {"id": "pph-006", "supplier_id": SUP_TROPICAL_GROVES_ID, "product_id": PROD_MANGO_JUICE_ID, "effective_start_date": "2026-07-01", "effective_end_date": "2026-12-31", "unit_price": 28.0, "currency": "USD", "volume_threshold": 300.0},
    
    {"id": "pph-007", "supplier_id": SUP_APEX_DAIRY_ID, "product_id": PROD_MILK_ID, "effective_start_date": "2026-01-01", "effective_end_date": "2026-12-31", "unit_price": 52.5, "currency": "USD", "volume_threshold": 80.0},
    {"id": "pph-008", "supplier_id": SUP_MIDWEST_GRAIN_ID, "product_id": PROD_BISCUITS_ID, "effective_start_date": "2026-01-01", "effective_end_date": "2026-12-31", "unit_price": 53.0, "currency": "USD", "volume_threshold": 150.0}
]
write_csv("purchase_price_history.csv", purchase_price_history, [
    "id", "supplier_id", "product_id", "effective_start_date", "effective_end_date", "unit_price", "currency", "volume_threshold"
])

# procurement_transactions.csv (Invoice and payment tracking)
procurement_transactions = [
    {"id": "tx-001", "purchase_order_id": "77777777-1111-4444-8888-000000000001", "invoice_number": "INV-DP-9912", "invoice_date": "2026-06-04", "payment_due_date": "2026-07-04", "payment_date": "2026-07-02", "amount": 4800.0, "currency": "USD", "status": "paid", "payment_reference": "WIRE-20260702-01"},
    {"id": "tx-002", "purchase_order_id": "77777777-1111-4444-8888-000000000004", "invoice_number": "INV-GW-4410", "invoice_date": "2026-06-17", "payment_due_date": "2026-08-01", "payment_date": "2026-07-28", "amount": 12000.0, "currency": "USD", "status": "paid", "payment_reference": "ACH-20260728-44"},
    {"id": "tx-003", "purchase_order_id": "77777777-1111-4444-8888-000000000007", "invoice_number": "INV-TG-1029", "invoice_date": "2026-07-01", "payment_due_date": "2026-07-31", "payment_date": "2026-07-25", "amount": 8000.0, "currency": "USD", "status": "paid", "payment_reference": "LC-20260725-88"},
    {"id": "tx-004", "purchase_order_id": PO_003_ID, "invoice_number": "INV-TG-1890", "invoice_date": "2026-09-10", "payment_due_date": "2026-10-10", "payment_date": "2026-09-12", "amount": 8400.0, "currency": "USD", "status": "paid", "payment_reference": "LC-20260912-10"},
    {"id": "tx-005", "purchase_order_id": PO_001_ID, "invoice_number": "INV-DP-1044", "invoice_date": "2026-09-06", "payment_due_date": "2026-10-06", "payment_date": "", "amount": 5000.0, "currency": "USD", "status": "pending_delivery", "payment_reference": ""},
    {"id": "tx-006", "purchase_order_id": PO_002_ID, "invoice_number": "INV-GW-5190", "invoice_date": "2026-09-11", "payment_due_date": "2026-10-26", "payment_date": "", "amount": 12500.0, "currency": "USD", "status": "pending_delivery", "payment_reference": ""}
]
write_csv("procurement_transactions.csv", procurement_transactions, [
    "id", "purchase_order_id", "invoice_number", "invoice_date", "payment_due_date", "payment_date", "amount", "currency", "status", "payment_reference"
])

# =============================================================================
# 11. NEW PRODUCTION DATASETS
# =============================================================================

# production_bom.csv (Bill of Materials)
production_bom = [
    # Milk BOM (1 litre Finished Milk requires 1.05 L raw feedstock)
    {"id": "bom-001", "finished_product_id": PROD_MILK_ID, "component_product_id": RAW_MILK_ID, "component_name": "Raw Pasteurization Feedstock", "required_quantity_per_unit": 1.05, "unit": "litre", "scrap_factor": 0.05},
    
    # Biscuits BOM (1 pack Finished Biscuits requires 0.5 kg Flour mix and 1 wrapper)
    {"id": "bom-002", "finished_product_id": PROD_BISCUITS_ID, "component_product_id": RAW_FLOUR_ID, "component_name": "Premium Biscuit Flour Mix", "required_quantity_per_unit": 0.50, "unit": "kg", "scrap_factor": 0.02},
    {"id": "bom-003", "finished_product_id": PROD_BISCUITS_ID, "component_product_id": PKG_WRAP_ID, "component_name": "Moisture-Barrier Biscuit Wrappers", "required_quantity_per_unit": 0.01, "unit": "roll", "scrap_factor": 0.01},
    
    # Mango Juice BOM (1 bottle Finished Mango Juice requires 0.3 kg mango pulp and 1 glass bottle)
    {"id": "bom-004", "finished_product_id": PROD_MANGO_JUICE_ID, "component_product_id": RAW_PULP_ID, "component_name": "Alphonso Mango Pulp Concentrate", "required_quantity_per_unit": 0.30, "unit": "kg", "scrap_factor": 0.03},
    {"id": "bom-005", "finished_product_id": PROD_MANGO_JUICE_ID, "component_product_id": PKG_BOTTLE_ID, "component_name": "500ml Aseptic Glass Bottles", "required_quantity_per_unit": 1.00, "unit": "unit", "scrap_factor": 0.01}
]
write_csv("production_bom.csv", production_bom, [
    "id", "finished_product_id", "component_product_id", "component_name", "required_quantity_per_unit", "unit", "scrap_factor"
])

# production_material_requirements.csv (Order-specific material requirements & inventory availability)
production_material_requirements = [
    # PRD-MJ-202609 (Mango Juice: 500 bottles) -> Materials are SUFFICIENT (Pulp available: 300, Bottles available: 2000)
    {
        "id": "pmr-001",
        "production_order_id": PRD_MJ_ID,
        "finished_product_id": PROD_MANGO_JUICE_ID,
        "component_product_id": RAW_PULP_ID,
        "component_name": "Alphonso Mango Pulp Concentrate",
        "required_quantity": 150.0,
        "unit": "kg",
        "available_inventory_quantity": 300.0,
        "material_shortage": 0.0,
        "status": "sufficient"
    },
    {
        "id": "pmr-002",
        "production_order_id": PRD_MJ_ID,
        "finished_product_id": PROD_MANGO_JUICE_ID,
        "component_product_id": PKG_BOTTLE_ID,
        "component_name": "500ml Aseptic Glass Bottles",
        "required_quantity": 500.0,
        "unit": "unit",
        "available_inventory_quantity": 2000.0,
        "material_shortage": 0.0,
        "status": "sufficient"
    },
    
    # PRD-BIS-202609 (Biscuits: 1000 packs) -> Requires 500kg Flour mix, available is 100kg (Shortage: 400kg pending inbound PO-002 / SHP-001)
    {
        "id": "pmr-003",
        "production_order_id": PRD_BIS_ID,
        "finished_product_id": PROD_BISCUITS_ID,
        "component_product_id": RAW_FLOUR_ID,
        "component_name": "Premium Biscuit Flour Mix",
        "required_quantity": 500.0,
        "unit": "kg",
        "available_inventory_quantity": 100.0,
        "material_shortage": 400.0,
        "status": "delayed_inbound"
    },
    {
        "id": "pmr-004",
        "production_order_id": PRD_BIS_ID,
        "finished_product_id": PROD_BISCUITS_ID,
        "component_product_id": PKG_WRAP_ID,
        "component_name": "Moisture-Barrier Biscuit Wrappers",
        "required_quantity": 10.0,
        "unit": "roll",
        "available_inventory_quantity": 70.0,
        "material_shortage": 0.0,
        "status": "sufficient"
    },
    
    # PRD-MILK-202609 (Milk: 800 litres) -> Requires 840L Raw Milk, available is 45L (CRITICAL SHORTAGE: 795L pending delayed PO-001 / SHP-002)
    {
        "id": "pmr-005",
        "production_order_id": PRD_MILK_ID,
        "finished_product_id": PROD_MILK_ID,
        "component_product_id": RAW_MILK_ID,
        "component_name": "Raw Pasteurization Feedstock",
        "required_quantity": 840.0,
        "unit": "litre",
        "available_inventory_quantity": 45.0,
        "material_shortage": 795.0,
        "status": "critical_shortage"
    }
]
write_csv("production_material_requirements.csv", production_material_requirements, [
    "id", "production_order_id", "finished_product_id", "component_product_id", "component_name",
    "required_quantity", "unit", "available_inventory_quantity", "material_shortage", "status"
])

# production_progress.csv (Shop Floor Line Operations & Downtime Tracking)
production_progress = [
    {
        "id": "prog-001",
        "production_order_id": PRD_MJ_ID,
        "production_line": "Bottling Line 2",
        "equipment_id": "EQ-NOZZLE-02",
        "planned_quantity": 500.0,
        "produced_quantity": 120.0,
        "production_rate": 40.0,
        "progress_percentage": 24.0,
        "downtime_minutes": 180,
        "downtime_reason": "High-pressure filler nozzle calibration fault causing line speed throttling (40% operating capacity)",
        "planned_start_date": "2026-09-12",
        "planned_end_date": "2026-09-15",
        "actual_start_date": "2026-09-12",
        "actual_end_date": "",
        "status": "slowdown"
    },
    {
        "id": "prog-002",
        "production_order_id": PRD_BIS_ID,
        "production_line": "Baking & Packaging Line 1",
        "equipment_id": "EQ-OVEN-01",
        "planned_quantity": 1000.0,
        "produced_quantity": 0.0,
        "production_rate": 0.0,
        "progress_percentage": 0.0,
        "downtime_minutes": 0,
        "downtime_reason": "Scheduled staging - waiting for flour consignment clearance",
        "planned_start_date": "2026-09-16",
        "planned_end_date": "2026-09-20",
        "actual_start_date": "",
        "actual_end_date": "",
        "status": "planned"
    },
    {
        "id": "prog-003",
        "production_order_id": PRD_MILK_ID,
        "production_line": "Pasteurization Line 3",
        "equipment_id": "EQ-PAST-03",
        "planned_quantity": 800.0,
        "produced_quantity": 0.0,
        "production_rate": 0.0,
        "progress_percentage": 0.0,
        "downtime_minutes": 0,
        "downtime_reason": "Production hold - raw milk feedstock delivery delayed by supplier Dairy Pure Co",
        "planned_start_date": "2026-09-17",
        "planned_end_date": "2026-09-19",
        "actual_start_date": "",
        "actual_end_date": "",
        "status": "on_hold"
    }
]
write_csv("production_progress.csv", production_progress, [
    "id", "production_order_id", "production_line", "equipment_id", "planned_quantity",
    "produced_quantity", "production_rate", "progress_percentage", "downtime_minutes",
    "downtime_reason", "planned_start_date", "planned_end_date", "actual_start_date", "actual_end_date", "status"
])

# =============================================================================
# 12. NEW LOGISTICS DATASETS
# =============================================================================

# shipment_items.csv
shipment_items = [
    {"id": "si-001", "shipment_id": SHP_001_ID, "product_id": PROD_BISCUITS_ID, "ordered_quantity": 250.0, "shipped_quantity": 250.0, "unit": "pack"},
    {"id": "si-002", "shipment_id": SHP_002_ID, "product_id": PROD_MILK_ID, "ordered_quantity": 100.0, "shipped_quantity": 100.0, "unit": "litre"},
    {"id": "si-003", "shipment_id": SHP_003_ID, "product_id": PROD_MANGO_JUICE_ID, "ordered_quantity": 300.0, "shipped_quantity": 300.0, "unit": "bottle"},
    
    # Historical shipment items
    {"id": "si-004", "shipment_id": "99999999-3333-6666-aaaa-000000000001", "product_id": PROD_MILK_ID, "ordered_quantity": 100.0, "shipped_quantity": 100.0, "unit": "litre"},
    {"id": "si-005", "shipment_id": "99999999-3333-6666-aaaa-000000000002", "product_id": PROD_BISCUITS_ID, "ordered_quantity": 250.0, "shipped_quantity": 250.0, "unit": "pack"},
    {"id": "si-006", "shipment_id": "99999999-3333-6666-aaaa-000000000003", "product_id": PROD_MANGO_JUICE_ID, "ordered_quantity": 300.0, "shipped_quantity": 300.0, "unit": "bottle"}
]
write_csv("shipment_items.csv", shipment_items, ["id", "shipment_id", "product_id", "ordered_quantity", "shipped_quantity", "unit"])

# shipment_receipts.csv
shipment_receipts = [
    # Delivered SHP-003
    {
        "id": "rec-001",
        "shipment_id": SHP_003_ID,
        "purchase_order_id": PO_003_ID,
        "product_id": PROD_MANGO_JUICE_ID,
        "received_quantity": 300.0,
        "accepted_quantity": 300.0,
        "rejected_quantity": 0.0,
        "damaged_quantity": 0.0,
        "partial_delivery": False,
        "receipt_date": "2026-09-10",
        "inspector_notes": "All 300 bottles verified intact, seal intact, pH and brix verified within specification"
    },
    # Historical Receipts
    {
        "id": "rec-002",
        "shipment_id": "99999999-3333-6666-aaaa-000000000001",
        "purchase_order_id": "77777777-1111-4444-8888-000000000001",
        "product_id": PROD_MILK_ID,
        "received_quantity": 100.0,
        "accepted_quantity": 100.0,
        "rejected_quantity": 0.0,
        "damaged_quantity": 0.0,
        "partial_delivery": False,
        "receipt_date": "2026-06-04",
        "inspector_notes": "Cold-chain continuous log verified at 3.8C"
    },
    {
        "id": "rec-003",
        "shipment_id": "99999999-3333-6666-aaaa-000000000002",
        "purchase_order_id": "77777777-1111-4444-8888-000000000004",
        "product_id": PROD_BISCUITS_ID,
        "received_quantity": 250.0,
        "accepted_quantity": 250.0,
        "rejected_quantity": 0.0,
        "damaged_quantity": 0.0,
        "partial_delivery": False,
        "receipt_date": "2026-06-17",
        "inspector_notes": "Packaging clean and dry"
    },
    {
        "id": "rec-004",
        "shipment_id": "99999999-3333-6666-aaaa-000000000003",
        "purchase_order_id": "77777777-1111-4444-8888-000000000007",
        "product_id": PROD_MANGO_JUICE_ID,
        "received_quantity": 300.0,
        "accepted_quantity": 300.0,
        "rejected_quantity": 0.0,
        "damaged_quantity": 0.0,
        "partial_delivery": False,
        "receipt_date": "2026-07-01",
        "inspector_notes": "Passed inbound quality checks"
    }
]
write_csv("shipment_receipts.csv", shipment_receipts, [
    "id", "shipment_id", "purchase_order_id", "product_id", "received_quantity",
    "accepted_quantity", "rejected_quantity", "damaged_quantity", "partial_delivery",
    "receipt_date", "inspector_notes"
])

# shipment_temperature_telemetry.csv (IoT Cold-Chain Telemetry for Refrigerated Milk & Controlled Shipments)
shipment_temperature_telemetry = [
    # SHP-002: Refrigerated Milk (Nominal 2.0C - 6.0C) with EXCURSION due to compressor fault
    {"id": "tele-001", "shipment_id": SHP_002_ID, "timestamp": "2026-09-04T06:00:00Z", "temperature": 3.8, "min_allowed_temperature": 2.0, "max_allowed_temperature": 6.0, "is_excursion": False, "sensor_location": "Reefer Bay Zone A", "telemetry_notes": "Normal refrigerated cooling"},
    {"id": "tele-002", "shipment_id": SHP_002_ID, "timestamp": "2026-09-04T12:00:00Z", "temperature": 4.1, "min_allowed_temperature": 2.0, "max_allowed_temperature": 6.0, "is_excursion": False, "sensor_location": "Reefer Bay Zone A", "telemetry_notes": "Normal refrigerated cooling"},
    {"id": "tele-003", "shipment_id": SHP_002_ID, "timestamp": "2026-09-04T18:00:00Z", "temperature": 6.8, "min_allowed_temperature": 2.0, "max_allowed_temperature": 6.0, "is_excursion": True, "sensor_location": "Reefer Bay Zone A", "telemetry_notes": "WARNING: Compressor cycle oscillation detected"},
    {"id": "tele-004", "shipment_id": SHP_002_ID, "timestamp": "2026-09-05T00:00:00Z", "temperature": 8.5, "min_allowed_temperature": 2.0, "max_allowed_temperature": 6.0, "is_excursion": True, "sensor_location": "Reefer Bay Zone A", "telemetry_notes": "CRITICAL EXCURSION: Refrigeration compressor failed, vehicle routed to repair depot in Melbourne"},
    {"id": "tele-005", "shipment_id": SHP_002_ID, "timestamp": "2026-09-05T06:00:00Z", "temperature": 9.2, "min_allowed_temperature": 2.0, "max_allowed_temperature": 6.0, "is_excursion": True, "sensor_location": "Reefer Bay Zone A", "telemetry_notes": "CRITICAL EXCURSION: Secondary backup unit engaged, awaiting thermal re-stabilization"},
    {"id": "tele-006", "shipment_id": SHP_002_ID, "timestamp": "2026-09-06T12:00:00Z", "temperature": 4.5, "min_allowed_temperature": 2.0, "max_allowed_temperature": 6.0, "is_excursion": False, "sensor_location": "Reefer Bay Zone A", "telemetry_notes": "Thermal equilibrium restored, cargo batch quarantined for lab assay"},
    
    # SHP-003: Ambient Mango Juice Shipment (Nominal 10.0C - 30.0C)
    {"id": "tele-007", "shipment_id": SHP_003_ID, "timestamp": "2026-09-02T10:00:00Z", "temperature": 21.5, "min_allowed_temperature": 10.0, "max_allowed_temperature": 30.0, "is_excursion": False, "sensor_location": "Maritime Container Unit 1", "telemetry_notes": "Optimal ambient conditions"},
    {"id": "tele-008", "shipment_id": SHP_003_ID, "timestamp": "2026-09-06T10:00:00Z", "temperature": 22.1, "min_allowed_temperature": 10.0, "max_allowed_temperature": 30.0, "is_excursion": False, "sensor_location": "Maritime Container Unit 1", "telemetry_notes": "Optimal ambient conditions"},
    {"id": "tele-009", "shipment_id": SHP_003_ID, "timestamp": "2026-09-10T08:00:00Z", "temperature": 20.8, "min_allowed_temperature": 10.0, "max_allowed_temperature": 30.0, "is_excursion": False, "sensor_location": "Maritime Container Unit 1", "telemetry_notes": "Arrival dock temperature verified"}
]
write_csv("shipment_temperature_telemetry.csv", shipment_temperature_telemetry, [
    "id", "shipment_id", "timestamp", "temperature", "min_allowed_temperature",
    "max_allowed_temperature", "is_excursion", "sensor_location", "telemetry_notes"
])

print("\n--- ALL 18 DATASET CSV FILES SUCCESSFULLY GENERATED ---")
