import csv
import glob
import os
import re

DATASET_DIR = "dataset"

def run_checks():
    print("=" * 60)
    print("RUNNING COMPREHENSIVE DATASET VALIDATION")
    print("=" * 60)
    
    # Load all CSVs
    files = glob.glob(os.path.join(DATASET_DIR, "*.csv"))
    tables = {}
    for fpath in files:
        name = os.path.basename(fpath)
        with open(fpath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            tables[name] = list(reader)
        print(f"Loaded {name:35} : {len(tables[name])} rows")

    errors = []
    
    # 1. Check date formats
    date_regex = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    iso_timestamp_regex = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
    
    for name, rows in tables.items():
        for i, row in enumerate(rows):
            for col, val in row.items():
                if val == "":
                    continue
                if col.endswith("_date") or col in ("order_date", "start_date", "end_date", "request_date", "approval_date", "invoice_date", "payment_due_date", "payment_date", "receipt_date"):
                    if not date_regex.match(val):
                        errors.append(f"[{name} row {i+1}] Invalid date format in {col}: '{val}' (expected YYYY-MM-DD)")
                elif col in ("timestamp", "created_at"):
                    if not (iso_timestamp_regex.match(val) or date_regex.match(val)):
                        errors.append(f"[{name} row {i+1}] Invalid timestamp format in {col}: '{val}'")

    # 2. Check no negative quantities
    quantity_cols = ["quantity", "reserved_quantity", "available_quantity", "target_stock", "reorder_level",
                     "ordered_quantity", "shipped_quantity", "received_quantity", "accepted_quantity",
                     "rejected_quantity", "damaged_quantity", "planned_quantity", "produced_quantity",
                     "required_quantity", "available_inventory_quantity", "material_shortage",
                     "min_order_quantity", "monthly_capacity", "allocated_quantity", "available_capacity"]
    
    for name, rows in tables.items():
        for i, row in enumerate(rows):
            for col in quantity_cols:
                if col in row and row[col] != "":
                    try:
                        v = float(row[col])
                        if v < 0:
                            errors.append(f"[{name} row {i+1}] Negative quantity in {col}: {v}")
                    except ValueError:
                        errors.append(f"[{name} row {i+1}] Non-numeric quantity in {col}: '{row[col]}'")

    # 3. Check receipt logic (received >= accepted + rejected, accepted + rejected == received if fully accounted)
    if "shipment_receipts.csv" in tables:
        for i, row in enumerate(tables["shipment_receipts.csv"]):
            recv = float(row["received_quantity"])
            acc = float(row["accepted_quantity"])
            rej = float(row["rejected_quantity"])
            dam = float(row["damaged_quantity"])
            if acc + rej > recv:
                errors.append(f"[shipment_receipts.csv row {i+1}] accepted ({acc}) + rejected ({rej}) > received ({recv})")
            if dam > recv:
                errors.append(f"[shipment_receipts.csv row {i+1}] damaged ({dam}) > received ({recv})")

    # 4. Check temperature logic
    if "shipment_temperature_telemetry.csv" in tables:
        for i, row in enumerate(tables["shipment_temperature_telemetry.csv"]):
            temp = float(row["temperature"])
            tmin = float(row["min_allowed_temperature"])
            tmax = float(row["max_allowed_temperature"])
            is_exc = row["is_excursion"].strip().lower() in ("true", "1")
            
            excursion_detected = (temp < tmin or temp > tmax)
            if excursion_detected != is_exc:
                errors.append(f"[shipment_temperature_telemetry.csv row {i+1}] Excursion mismatch: temp={temp}, min={tmin}, max={tmax}, is_excursion={is_exc}")

    # 5. Foreign Key Integrity Checks
    product_ids = {r["id"] for r in tables["products.csv"]}
    supplier_ids = {r["id"] for r in tables["suppliers.csv"]}
    po_ids = {r["id"] for r in tables["purchase_orders.csv"]}
    shipment_ids = {r["id"] for r in tables["shipments.csv"]}
    prod_order_ids = {r["id"] for r in tables["production_orders.csv"]}
    
    # Check FKs in inventory.csv
    for r in tables["inventory.csv"]:
        if r["product_id"] not in product_ids:
            errors.append(f"[inventory.csv] Missing product_id: {r['product_id']}")
            
    # Check FKs in purchase_orders.csv
    for r in tables["purchase_orders.csv"]:
        if r["supplier_id"] not in supplier_ids:
            errors.append(f"[purchase_orders.csv] Missing supplier_id: {r['supplier_id']}")
            
    # Check FKs in purchase_order_items.csv
    for r in tables["purchase_order_items.csv"]:
        if r["purchase_order_id"] not in po_ids:
            errors.append(f"[purchase_order_items.csv] Missing purchase_order_id: {r['purchase_order_id']}")
        if r["product_id"] not in product_ids:
            errors.append(f"[purchase_order_items.csv] Missing product_id: {r['product_id']}")

    # Check FKs in shipments.csv
    for r in tables["shipments.csv"]:
        if r["purchase_order_id"] not in po_ids:
            errors.append(f"[shipments.csv] Missing purchase_order_id: {r['purchase_order_id']}")
        if r["supplier_id"] not in supplier_ids:
            errors.append(f"[shipments.csv] Missing supplier_id: {r['supplier_id']}")

    # Check FKs in shipment_items.csv
    for r in tables["shipment_items.csv"]:
        if r["shipment_id"] not in shipment_ids:
            errors.append(f"[shipment_items.csv] Missing shipment_id: {r['shipment_id']}")
        if r["product_id"] not in product_ids:
            errors.append(f"[shipment_items.csv] Missing product_id: {r['product_id']}")

    # Check FKs in shipment_receipts.csv
    for r in tables["shipment_receipts.csv"]:
        if r["shipment_id"] not in shipment_ids:
            errors.append(f"[shipment_receipts.csv] Missing shipment_id: {r['shipment_id']}")
        if r["purchase_order_id"] not in po_ids:
            errors.append(f"[shipment_receipts.csv] Missing purchase_order_id: {r['purchase_order_id']}")
        if r["product_id"] not in product_ids:
            errors.append(f"[shipment_receipts.csv] Missing product_id: {r['product_id']}")

    # Check FKs in shipment_temperature_telemetry.csv
    for r in tables["shipment_temperature_telemetry.csv"]:
        if r["shipment_id"] not in shipment_ids:
            errors.append(f"[shipment_temperature_telemetry.csv] Missing shipment_id: {r['shipment_id']}")

    # Check FKs in supplier_products.csv
    for r in tables["supplier_products.csv"]:
        if r["supplier_id"] not in supplier_ids:
            errors.append(f"[supplier_products.csv] Missing supplier_id: {r['supplier_id']}")
        if r["product_id"] not in product_ids:
            errors.append(f"[supplier_products.csv] Missing product_id: {r['product_id']}")

    # Check FKs in supplier_performance.csv
    for r in tables["supplier_performance.csv"]:
        if r["supplier_id"] not in supplier_ids:
            errors.append(f"[supplier_performance.csv] Missing supplier_id: {r['supplier_id']}")
        if r["purchase_order_id"] not in po_ids:
            errors.append(f"[supplier_performance.csv] Missing purchase_order_id: {r['purchase_order_id']}")

    # Check FKs in supplier_capacity.csv
    for r in tables["supplier_capacity.csv"]:
        if r["supplier_id"] not in supplier_ids:
            errors.append(f"[supplier_capacity.csv] Missing supplier_id: {r['supplier_id']}")
        if r["product_id"] not in product_ids:
            errors.append(f"[supplier_capacity.csv] Missing product_id: {r['product_id']}")

    # Check FKs in supplier_contracts.csv
    for r in tables["supplier_contracts.csv"]:
        if r["supplier_id"] not in supplier_ids:
            errors.append(f"[supplier_contracts.csv] Missing supplier_id: {r['supplier_id']}")

    # Check FKs in purchase_requisitions.csv
    for r in tables["purchase_requisitions.csv"]:
        if r["product_id"] not in product_ids:
            errors.append(f"[purchase_requisitions.csv] Missing product_id: {r['product_id']}")
        if r["purchase_order_id"] and r["purchase_order_id"] not in po_ids:
            errors.append(f"[purchase_requisitions.csv] Missing purchase_order_id: {r['purchase_order_id']}")

    # Check FKs in purchase_order_status_history.csv
    for r in tables["purchase_order_status_history.csv"]:
        if r["purchase_order_id"] not in po_ids:
            errors.append(f"[purchase_order_status_history.csv] Missing purchase_order_id: {r['purchase_order_id']}")

    # Check FKs in purchase_price_history.csv
    for r in tables["purchase_price_history.csv"]:
        if r["supplier_id"] not in supplier_ids:
            errors.append(f"[purchase_price_history.csv] Missing supplier_id: {r['supplier_id']}")
        if r["product_id"] not in product_ids:
            errors.append(f"[purchase_price_history.csv] Missing product_id: {r['product_id']}")

    # Check FKs in procurement_transactions.csv
    for r in tables["procurement_transactions.csv"]:
        if r["purchase_order_id"] not in po_ids:
            errors.append(f"[procurement_transactions.csv] Missing purchase_order_id: {r['purchase_order_id']}")

    # Check FKs in production_bom.csv
    for r in tables["production_bom.csv"]:
        if r["finished_product_id"] not in product_ids:
            errors.append(f"[production_bom.csv] Missing finished_product_id: {r['finished_product_id']}")
        if r["component_product_id"] not in product_ids:
            errors.append(f"[production_bom.csv] Missing component_product_id: {r['component_product_id']}")

    # Check FKs in production_material_requirements.csv
    for r in tables["production_material_requirements.csv"]:
        if r["production_order_id"] not in prod_order_ids:
            errors.append(f"[production_material_requirements.csv] Missing production_order_id: {r['production_order_id']}")
        if r["finished_product_id"] not in product_ids:
            errors.append(f"[production_material_requirements.csv] Missing finished_product_id: {r['finished_product_id']}")
        if r["component_product_id"] not in product_ids:
            errors.append(f"[production_material_requirements.csv] Missing component_product_id: {r['component_product_id']}")

    # Check FKs in production_progress.csv
    for r in tables["production_progress.csv"]:
        if r["production_order_id"] not in prod_order_ids:
            errors.append(f"[production_progress.csv] Missing production_order_id: {r['production_order_id']}")

    print("\n" + "=" * 60)
    if errors:
        print(f"FAILED: {len(errors)} errors found:")
        for err in errors:
            print(f"  - {err}")
    else:
        print("SUCCESS: ALL 18 CSV DATASETS PASSED 100% OF RELATIONAL AND DATA QUALITY CHECKS!")
    print("=" * 60)

if __name__ == "__main__":
    run_checks()
