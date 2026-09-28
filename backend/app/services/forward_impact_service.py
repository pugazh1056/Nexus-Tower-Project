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
    shipment_receipts_repo,
)


class ForwardImpactService:
    def __init__(self):
        pass

    def analyze(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        event_id = event_data.get("event_id") or "EVT-FWD-001"
        event_type = str(event_data.get("event_type", "")).upper()
        source_domain = event_data.get("source_domain") or event_data.get("domain") or "Procurement"
        entity_type = str(event_data.get("entity_type", "")).lower()
        entity_id = event_data.get("entity_id") or ""
        data = event_data.get("data", {})

        impacts: List[Dict[str, Any]] = []

        try:
            if event_type == "SUPPLIER_DELAY" or entity_type in ["purchase_order", "supplier"]:
                pos = purchase_order_repo.get_all()
                target_po = None
                for po in pos:
                    if str(po.get("id")) == str(entity_id) or str(po.get("po_number")) == str(entity_id) or str(po.get("id")) == str(data.get("po_id")):
                        target_po = po
                        break
                if not target_po and pos:
                    target_po = pos[0]

                if target_po:
                    po_id = target_po.get("id")
                    po_number = target_po.get("po_number", "PO-UNKNOWN")
                    
                    shipments = shipment_repo.get_all()
                    linked_shipments = [s for s in shipments if str(s.get("purchase_order_id")) == str(po_id)]
                    for s in linked_shipments:
                        impacts.append({
                            "event_id": event_id,
                            "source_domain": source_domain,
                            "entity_type": entity_type,
                            "entity_id": entity_id or str(po_id),
                            "domain": "Logistics",
                            "entity_type_target": "shipment",
                            "entity_id_target": s.get("id"),
                            "impact": f"Shipment {s.get('shipment_number')} linked to purchase order {po_number} is affected by supplier delay, current status: {s.get('status')}.",
                            "evidence": {
                                "shipment_number": s.get("shipment_number"),
                                "status": s.get("status"),
                                "tracking_number": s.get("tracking_number"),
                                "po_number": po_number
                            }
                        })

                    po_items = target_po.get("items", [])
                    if not po_items:
                        try:
                            from app.core.supabase import get_supabase
                            client = get_supabase()
                            if client:
                                res = client.table("purchase_order_items").select("*").eq("purchase_order_id", str(po_id)).execute()
                                if res.data:
                                    po_items = res.data
                        except Exception:
                            pass

                    for item in po_items:
                        prod_id = item.get("product_id")
                        qty = item.get("quantity") or item.get("ordered_quantity", 0)
                        product = product_repo.get_by_id(prod_id) if prod_id else None
                        sku = product.get("sku", "UNKNOWN-SKU") if product else "UNKNOWN-SKU"

                        inventories = inventory_repo.get_all()
                        matching_inv = [inv for inv in inventories if str(inv.get("product_id")) == str(prod_id)]
                        for inv in matching_inv:
                            on_hand = float(inv.get("quantity", 0))
                            reserved = float(inv.get("reserved_quantity", 0))
                            available = on_hand - reserved
                            warehouse = inv.get("warehouse_location", "Main Warehouse")
                            impacts.append({
                                "event_id": event_id,
                                "source_domain": source_domain,
                                "entity_type": entity_type,
                                "entity_id": entity_id or str(po_id),
                                "domain": "Inventory",
                                "entity_type_target": "inventory",
                                "entity_id_target": inv.get("id"),
                                "impact": f"Inventory availability at {warehouse} for product SKU {sku} is {available} against pending order quantity {qty}.",
                                "evidence": {
                                    "product_sku": sku,
                                    "warehouse_location": warehouse,
                                    "quantity_on_hand": on_hand,
                                    "reserved_quantity": reserved,
                                    "available_quantity": available,
                                    "ordered_quantity": qty
                                }
                            })

                        mat_reqs = production_material_requirements_repo.get_all()
                        matching_reqs = [req for req in mat_reqs if str(req.get("component_product_id")) == str(prod_id) or str(req.get("finished_product_id")) == str(prod_id)]
                        for req in matching_reqs:
                            prod_order_id = req.get("production_order_id")
                            req_qty = float(req.get("required_quantity", 0))
                            avail_qty = float(req.get("available_inventory_quantity", 0))
                            shortage = float(req.get("material_shortage", 0))
                            
                            prod_order = production_order_repo.get_by_id(prod_order_id) if prod_order_id else None
                            prod_number = prod_order.get("production_number", "PROD-UNKNOWN") if prod_order else "PROD-UNKNOWN"

                            impacts.append({
                                "event_id": event_id,
                                "source_domain": source_domain,
                                "entity_type": entity_type,
                                "entity_id": entity_id or str(po_id),
                                "domain": "Production",
                                "entity_type_target": "production_order",
                                "entity_id_target": prod_order_id,
                                "impact": f"Production order {prod_number} requires material {sku} (required quantity {req_qty}), while inventory availability is {avail_qty} against required quantity with shortage {shortage}.",
                                "evidence": {
                                    "production_number": prod_number,
                                    "component_sku": sku,
                                    "required_quantity": req_qty,
                                    "available_inventory_quantity": avail_qty,
                                    "material_shortage": shortage
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
                    on_hand = float(target_inv.get("quantity", 0))
                    reserved = float(target_inv.get("reserved_quantity", 0))
                    available = on_hand - reserved

                    mat_reqs = production_material_requirements_repo.get_all()
                    matching_reqs = [req for req in mat_reqs if str(req.get("component_product_id")) == str(prod_id)]
                    for req in matching_reqs:
                        prod_order_id = req.get("production_order_id")
                        req_qty = float(req.get("required_quantity", 0))
                        prod_order = production_order_repo.get_by_id(prod_order_id) if prod_order_id else None
                        prod_number = prod_order.get("production_number", "PROD-UNKNOWN") if prod_order else "PROD-UNKNOWN"

                        impacts.append({
                            "event_id": event_id,
                            "source_domain": source_domain,
                            "entity_type": entity_type,
                            "entity_id": entity_id or str(target_inv.get("id")),
                            "domain": "Production",
                            "entity_type_target": "production_order",
                            "entity_id_target": prod_order_id,
                            "impact": f"Low stock for product {sku} (available inventory {available}) threatens production order {prod_number} requiring quantity {req_qty}.",
                            "evidence": {
                                "product_sku": sku,
                                "available_inventory": available,
                                "production_number": prod_number,
                                "required_quantity": req_qty
                            }
                        })

                    pos = purchase_order_repo.get_all()
                    for po in pos:
                        po_items = po.get("items", [])
                        for item in po_items:
                            if str(item.get("product_id")) == str(prod_id):
                                impacts.append({
                                    "event_id": event_id,
                                    "source_domain": source_domain,
                                    "entity_type": entity_type,
                                    "entity_id": entity_id or str(target_inv.get("id")),
                                    "domain": "Procurement",
                                    "entity_type_target": "purchase_order",
                                    "entity_id_target": po.get("id"),
                                    "impact": f"Stock depletion in {sku} links to upstream purchase order {po.get('po_number')} (status: {po.get('status')}).",
                                    "evidence": {
                                        "product_sku": sku,
                                        "po_number": po.get("po_number"),
                                        "po_status": po.get("status")
                                    }
                                })

            elif event_type == "PRODUCTION_DISRUPTION" or entity_type in ["production_order", "production"]:
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
                    prod_id = target_ord.get("product_id")
                    product = product_repo.get_by_id(prod_id) if prod_id else None
                    sku = product.get("sku", "UNKNOWN") if product else "UNKNOWN"

                    mat_reqs = production_material_requirements_repo.get_all()
                    matching_reqs = [req for req in mat_reqs if str(req.get("production_order_id")) == str(ord_id)]
                    for req in matching_reqs:
                        comp_prod_id = req.get("component_product_id")
                        comp_prod = product_repo.get_by_id(comp_prod_id) if comp_prod_id else None
                        comp_sku = comp_prod.get("sku", "UNKNOWN") if comp_prod else "UNKNOWN"
                        req_qty = float(req.get("required_quantity", 0))
                        avail_qty = float(req.get("available_inventory_quantity", 0))
                        shortage = float(req.get("material_shortage", 0))

                        impacts.append({
                            "event_id": event_id,
                            "source_domain": source_domain,
                            "entity_type": entity_type,
                            "entity_id": entity_id or str(ord_id),
                            "domain": "Inventory",
                            "entity_type_target": "inventory",
                            "entity_id_target": comp_prod_id,
                            "impact": f"Production disruption on order {ord_num} stems from component requirement for SKU {comp_sku}: inventory availability is {avail_qty} against required quantity {req_qty} (shortage: {shortage}).",
                            "evidence": {
                                "production_number": ord_num,
                                "component_sku": comp_sku,
                                "required_quantity": req_qty,
                                "available_inventory_quantity": avail_qty,
                                "material_shortage": shortage
                            }
                        })

                    shipments = shipment_repo.get_all()
                    for s in shipments:
                        s_items = shipment_items_repo.get_all()
                        matching_s_items = [si for si in s_items if str(si.get("shipment_id")) == str(s.get("id")) and str(si.get("product_id")) == str(prod_id)]
                        if matching_s_items:
                            impacts.append({
                                "event_id": event_id,
                                "source_domain": source_domain,
                                "entity_type": entity_type,
                                "entity_id": entity_id or str(ord_id),
                                "domain": "Logistics",
                                "entity_type_target": "shipment",
                                "entity_id_target": s.get("id"),
                                "impact": f"Production disruption in order {ord_num} impacts downstream shipment {s.get('shipment_number')} for product SKU {sku}.",
                                "evidence": {
                                    "production_number": ord_num,
                                    "shipment_number": s.get("shipment_number"),
                                    "product_sku": sku,
                                    "shipment_status": s.get("status")
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
                        impacts.append({
                            "event_id": event_id,
                            "source_domain": source_domain,
                            "entity_type": entity_type,
                            "entity_id": entity_id or str(ship_id),
                            "domain": "Procurement",
                            "entity_type_target": "purchase_order",
                            "entity_id_target": po_id,
                            "impact": f"Shipment disruption on {ship_num} affects linked purchase order {po_num} delivery schedule.",
                            "evidence": {
                                "shipment_number": ship_num,
                                "po_number": po_num,
                                "shipment_status": target_ship.get("status")
                            }
                        })

                    s_items = shipment_items_repo.get_all()
                    matching_si = [si for si in s_items if str(si.get("shipment_id")) == str(ship_id)]
                    for si in matching_si:
                        prod_id = si.get("product_id")
                        product = product_repo.get_by_id(prod_id) if prod_id else None
                        sku = product.get("sku", "UNKNOWN") if product else "UNKNOWN"
                        shipped_qty = si.get("shipped_quantity", 0)

                        impacts.append({
                            "event_id": event_id,
                            "source_domain": source_domain,
                            "entity_type": entity_type,
                            "entity_id": entity_id or str(ship_id),
                            "domain": "Inventory",
                            "entity_type_target": "product",
                            "entity_id_target": prod_id,
                            "impact": f"Shipment disruption on {ship_num} delays receipt of {shipped_qty} units of product SKU {sku} into inventory.",
                            "evidence": {
                                "shipment_number": ship_num,
                                "product_sku": sku,
                                "shipped_quantity": shipped_qty
                            }
                        })

        except Exception:
            pass

        if not impacts:
            return {
                "event_id": event_id,
                "analysis_type": "FORWARD",
                "status": "NO_SUPPORTED_RELATIONSHIP",
                "impacts": []
            }

        return {
            "event_id": event_id,
            "analysis_type": "FORWARD",
            "status": "COMPLETED",
            "impacts": impacts
        }


forward_impact_service = ForwardImpactService()
