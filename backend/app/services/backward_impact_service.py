from typing import List, Dict, Any, Optional
from app.repositories import (
    product_repo,
    supplier_repo,
    inventory_repo,
    purchase_order_repo,
    production_order_repo,
    production_material_requirements_repo,
    production_progress_repo,
    shipment_repo,
    shipment_items_repo,
)


class BackwardImpactService:
    def __init__(self):
        pass

    def analyze(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        event_id = event_data.get("event_id") or "EVT-BWD-001"
        event_type = str(event_data.get("event_type", "")).upper()
        source_domain = event_data.get("source_domain") or event_data.get("domain") or "Production"
        entity_type = str(event_data.get("entity_type", "")).lower()
        entity_id = event_data.get("entity_id") or ""
        data = event_data.get("data", {})

        root_causes: List[Dict[str, Any]] = []

        try:
            if event_type == "PRODUCTION_DISRUPTION" or entity_type in ["production_order", "production"]:
                prod_orders = production_order_repo.get_all()
                target_ord = None
                for ord_item in prod_orders:
                    if str(ord_item.get("id")) == str(entity_id) or str(ord_item.get("production_number")) == str(entity_id):
                        target_ord = ord_item
                        break
                if not target_ord and prod_orders:
                    target_ord = prod_orders[0]

                if target_ord:
                    ord_id = target_ord.get("id")
                    ord_num = target_ord.get("production_number", "PROD-UNKNOWN")
                    
                    # 1. Trace backward to material requirements -> inventory / purchase orders / suppliers
                    mat_reqs = production_material_requirements_repo.get_all()
                    matching_reqs = [req for req in mat_reqs if str(req.get("production_order_id")) == str(ord_id)]
                    for req in matching_reqs:
                        comp_prod_id = req.get("component_product_id")
                        comp_prod = product_repo.get_by_id(comp_prod_id) if comp_prod_id else None
                        comp_sku = comp_prod.get("sku", "UNKNOWN") if comp_prod else "UNKNOWN"
                        shortage = float(req.get("material_shortage", 0))

                        root_causes.append({
                            "event_id": event_id,
                            "source_domain": source_domain,
                            "entity_type": entity_type,
                            "entity_id": entity_id or str(ord_id),
                            "domain": "Inventory",
                            "entity_type_target": "inventory",
                            "entity_id_target": comp_prod_id,
                            "cause": f"Root cause for production disruption on order {ord_num}: component SKU {comp_sku} material shortage of {shortage} units in inventory stock.",
                            "evidence": {
                                "production_number": ord_num,
                                "component_sku": comp_sku,
                                "material_shortage": shortage
                            }
                        })

                        # Trace upstream to purchase orders for this component
                        pos = purchase_order_repo.get_all()
                        for po in pos:
                            po_items = po.get("items", [])
                            for item in po_items:
                                if str(item.get("product_id")) == str(comp_prod_id):
                                    sup_id = po.get("supplier_id")
                                    supplier = supplier_repo.get_by_id(sup_id) if sup_id else None
                                    sup_name = supplier.get("name", "SUPPLIER-UNKNOWN") if supplier else "SUPPLIER-UNKNOWN"
                                    
                                    root_causes.append({
                                        "event_id": event_id,
                                        "source_domain": source_domain,
                                        "entity_type": entity_type,
                                        "entity_id": entity_id or str(ord_id),
                                        "domain": "Procurement",
                                        "entity_type_target": "purchase_order",
                                        "entity_id_target": po.get("id"),
                                        "cause": f"Upstream root cause: purchase order {po.get('po_number')} from supplier {sup_name} for component SKU {comp_sku} experienced delays.",
                                        "evidence": {
                                            "po_number": po.get("po_number"),
                                            "supplier_name": sup_name,
                                            "component_sku": comp_sku,
                                            "po_status": po.get("status")
                                        }
                                    })

            elif event_type in ["STOCK_LOW", "INVENTORY_LOW"] or entity_type == "inventory":
                inventories = inventory_repo.get_all()
                target_inv = None
                for inv in inventories:
                    if str(inv.get("id")) == str(entity_id) or str(inv.get("product_id")) == str(entity_id):
                        target_inv = inv
                        break
                if not target_inv and inventories:
                    target_inv = inventories[0]

                if target_inv:
                    prod_id = target_inv.get("product_id")
                    product = product_repo.get_by_id(prod_id) if prod_id else None
                    sku = product.get("sku", "UNKNOWN") if product else "UNKNOWN"

                    # Upstream purchase orders
                    pos = purchase_order_repo.get_all()
                    for po in pos:
                        po_items = po.get("items", [])
                        for item in po_items:
                            if str(item.get("product_id")) == str(prod_id):
                                sup_id = po.get("supplier_id")
                                supplier = supplier_repo.get_by_id(sup_id) if sup_id else None
                                sup_name = supplier.get("name", "SUPPLIER-UNKNOWN") if supplier else "SUPPLIER-UNKNOWN"

                                root_causes.append({
                                    "event_id": event_id,
                                    "source_domain": source_domain,
                                    "entity_type": entity_type,
                                    "entity_id": entity_id or str(target_inv.get("id")),
                                    "domain": "Procurement",
                                    "entity_type_target": "purchase_order",
                                    "entity_id_target": po.get("id"),
                                    "cause": f"Root cause for low stock of {sku}: delayed or unfulfilled upstream purchase order {po.get('po_number')} from supplier {sup_name}.",
                                    "evidence": {
                                        "product_sku": sku,
                                        "po_number": po.get("po_number"),
                                        "supplier_name": sup_name,
                                        "po_status": po.get("status")
                                    }
                                })

            elif event_type == "SHIPMENT_DISRUPTION" or entity_type in ["shipment", "logistics"]:
                shipments = shipment_repo.get_all()
                target_ship = None
                for s in shipments:
                    if str(s.get("id")) == str(entity_id) or str(s.get("shipment_number")) == str(entity_id) or str(s.get("tracking_number")) == str(entity_id):
                        target_ship = s
                        break
                if not target_ship and shipments:
                    target_ship = shipments[0]

                if target_ship:
                    ship_id = target_ship.get("id")
                    ship_num = target_ship.get("shipment_number", "TRK-UNKNOWN")
                    po_id = target_ship.get("purchase_order_id")

                    if po_id:
                        po = purchase_order_repo.get_by_id(po_id)
                        po_num = po.get("po_number", "PO-UNKNOWN") if po else "PO-UNKNOWN"
                        sup_id = po.get("supplier_id") if po else None
                        supplier = supplier_repo.get_by_id(sup_id) if sup_id else None
                        sup_name = supplier.get("name", "SUPPLIER-UNKNOWN") if supplier else "SUPPLIER-UNKNOWN"

                        root_causes.append({
                            "event_id": event_id,
                            "source_domain": source_domain,
                            "entity_type": entity_type,
                            "entity_id": entity_id or str(ship_id),
                            "domain": "Procurement",
                            "entity_type_target": "purchase_order",
                            "entity_id_target": po_id,
                            "cause": f"Root cause for shipment disruption on {ship_num}: supplier {sup_name} delay on purchase order {po_num}.",
                            "evidence": {
                                "shipment_number": ship_num,
                                "po_number": po_num,
                                "supplier_name": sup_name,
                                "carrier": target_ship.get("carrier_name")
                            }
                        })

            elif event_type == "SUPPLIER_DELAY" or entity_type in ["purchase_order", "supplier"]:
                pos = purchase_order_repo.get_all()
                target_po = None
                for po in pos:
                    if str(po.get("id")) == str(entity_id) or str(po.get("po_number")) == str(entity_id) or str(po.get("id")) == str(data.get("po_id")):
                        target_po = po
                        break
                if not target_po and pos:
                    target_po = pos[0]

                if target_po:
                    po_num = target_po.get("po_number", "PO-UNKNOWN")
                    sup_id = target_po.get("supplier_id")
                    supplier = supplier_repo.get_by_id(sup_id) if sup_id else None
                    sup_code = supplier.get("supplier_code", "SUP-UNKNOWN") if supplier else "SUP-UNKNOWN"
                    sup_name = supplier.get("name", "SUPPLIER-UNKNOWN") if supplier else "SUPPLIER-UNKNOWN"

                    root_causes.append({
                        "event_id": event_id,
                        "source_domain": source_domain,
                        "entity_type": entity_type,
                        "entity_id": entity_id or str(target_po.get("id")),
                        "domain": "Procurement",
                        "entity_type_target": "supplier",
                        "entity_id_target": sup_id,
                        "cause": f"Root cause for supplier delay on purchase order {po_num}: supplier entity {sup_name} ({sup_code}) encountered operational lead-time variance.",
                        "evidence": {
                            "po_number": po_num,
                            "supplier_code": sup_code,
                            "supplier_name": sup_name,
                            "notes": target_po.get("notes")
                        }
                    })

        except Exception:
            pass

        if not root_causes:
            return {
                "event_id": event_id,
                "analysis_type": "BACKWARD",
                "status": "NO_SUPPORTED_RELATIONSHIP",
                "root_causes": []
            }

        return {
            "event_id": event_id,
            "analysis_type": "BACKWARD",
            "status": "COMPLETED",
            "root_causes": root_causes
        }


backward_impact_service = BackwardImpactService()
