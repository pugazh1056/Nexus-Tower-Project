import csv
import os

DATASET_DIR = "dataset"

def run_validation():
    print("=" * 60)
    print("VALIDATING PRODUCTION & LOGISTICS DATASET INTEGRITY")
    print("=" * 60)

    # 1. Load CSVs
    files = {
        "production_bom": "production_bom.csv",
        "production_material_requirements": "production_material_requirements.csv",
        "production_progress": "production_progress.csv",
        "shipment_items": "shipment_items.csv",
        "shipment_receipts": "shipment_receipts.csv",
        "shipment_temperature_telemetry": "shipment_temperature_telemetry.csv",
        "products": "products.csv",
        "production_orders": "production_orders.csv",
        "shipments": "shipments.csv",
        "purchase_orders": "purchase_orders.csv"
    }

    data = {}
    for key, fname in files.items():
        fpath = os.path.join(DATASET_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            data[key] = list(reader)
        print(f"Loaded {fname:38} : {len(data[key])} rows")

    errors = []

    product_ids = {r["id"] for r in data["products"]}
    prod_order_ids = {r["id"] for r in data["production_orders"]}
    shipment_ids = {r["id"] for r in data["shipments"]}
    po_ids = {r["id"] for r in data["purchase_orders"]}

    # 2. Validation Checks
    
    # Check production_bom
    for i, r in enumerate(data["production_bom"]):
        if r["finished_product_id"] not in product_ids:
            errors.append(f"[production_bom row {i+1}] Invalid finished_product_id: {r['finished_product_id']}")
        if r["component_product_id"] not in product_ids:
            errors.append(f"[production_bom row {i+1}] Invalid component_product_id: {r['component_product_id']}")
        if float(r["required_quantity_per_unit"]) < 0:
            errors.append(f"[production_bom row {i+1}] Negative required_quantity_per_unit")
        if float(r["scrap_factor"]) < 0:
            errors.append(f"[production_bom row {i+1}] Negative scrap_factor")

    # Check production_material_requirements
    for i, r in enumerate(data["production_material_requirements"]):
        if r["production_order_id"] not in prod_order_ids:
            errors.append(f"[production_material_requirements row {i+1}] Invalid production_order_id: {r['production_order_id']}")
        if r.get("component_product_id") and r["component_product_id"] not in product_ids:
            errors.append(f"[production_material_requirements row {i+1}] Invalid component_product_id: {r['component_product_id']}")
        if float(r["required_quantity"]) < 0 or float(r["available_inventory_quantity"]) < 0 or float(r["material_shortage"]) < 0:
            errors.append(f"[production_material_requirements row {i+1}] Negative quantity value")

    # Check production_progress
    for i, r in enumerate(data["production_progress"]):
        if r["production_order_id"] not in prod_order_ids:
            errors.append(f"[production_progress row {i+1}] Invalid production_order_id: {r['production_order_id']}")
        if float(r["planned_quantity"]) < 0 or float(r["produced_quantity"]) < 0 or float(r["production_rate"]) < 0:
            errors.append(f"[production_progress row {i+1}] Negative quantity/rate value")

    # Check shipment_items
    for i, r in enumerate(data["shipment_items"]):
        if r["shipment_id"] not in shipment_ids:
            errors.append(f"[shipment_items row {i+1}] Invalid shipment_id: {r['shipment_id']}")
        if r["product_id"] not in product_ids:
            errors.append(f"[shipment_items row {i+1}] Invalid product_id: {r['product_id']}")
        if float(r["ordered_quantity"]) < 0 or float(r["shipped_quantity"]) < 0:
            errors.append(f"[shipment_items row {i+1}] Negative quantity value")

    # Check shipment_receipts
    for i, r in enumerate(data["shipment_receipts"]):
        if r["shipment_id"] not in shipment_ids:
            errors.append(f"[shipment_receipts row {i+1}] Invalid shipment_id: {r['shipment_id']}")
        if r.get("purchase_order_id") and r["purchase_order_id"] not in po_ids:
            errors.append(f"[shipment_receipts row {i+1}] Invalid purchase_order_id: {r['purchase_order_id']}")
        if r["product_id"] not in product_ids:
            errors.append(f"[shipment_receipts row {i+1}] Invalid product_id: {r['product_id']}")
        recv = float(r["received_quantity"])
        acc = float(r["accepted_quantity"])
        rej = float(r["rejected_quantity"])
        dam = float(r["damaged_quantity"])
        if recv < 0 or acc < 0 or rej < 0 or dam < 0:
            errors.append(f"[shipment_receipts row {i+1}] Negative quantity in receipts")
        if acc + rej > recv:
            errors.append(f"[shipment_receipts row {i+1}] accepted + rejected > received")

    # Check shipment_temperature_telemetry
    for i, r in enumerate(data["shipment_temperature_telemetry"]):
        if r["shipment_id"] not in shipment_ids:
            errors.append(f"[shipment_temperature_telemetry row {i+1}] Invalid shipment_id: {r['shipment_id']}")
        temp = float(r["temperature"])
        tmin = float(r["min_allowed_temperature"])
        tmax = float(r["max_allowed_temperature"])
        is_exc = r["is_excursion"].strip().lower() in ("true", "1")
        excursion_detected = (temp < tmin or temp > tmax)
        if excursion_detected != is_exc:
            errors.append(f"[shipment_temperature_telemetry row {i+1}] Temperature excursion flag mismatch")

    print("=" * 60)
    if errors:
        print(f"VALIDATION FAILED WITH {len(errors)} ERRORS:")
        for err in errors:
            print(f" - {err}")
    else:
        print("SUCCESS: ALL 6 PRODUCTION & LOGISTICS TABLES & DATASETS PASSED ALL 10 VALIDATION CHECKS!")
    print("=" * 60)

if __name__ == "__main__":
    run_validation()
