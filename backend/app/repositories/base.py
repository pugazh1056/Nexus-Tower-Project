import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.core.supabase import get_supabase


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# Global in-memory relational store (seeded with realistic FMCG demo data)
MEM_PRODUCTS: Dict[str, Dict[str, Any]] = {
    "prod-milk-001": {
        "id": "a0000001-0000-0000-0000-000000000001",
        "sku": "MILK-001",
        "name": "Ultra-Pasteurized Whole Milk 1L",
        "description": "Grade A pasteurized whole milk, shelf-stable aseptic packaging",
        "category": "Dairy",
        "unit": "litre",
        "reorder_level": 14600,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    },
    "prod-bisc-002": {
        "id": "a0000001-0000-0000-0000-000000000002",
        "sku": "BISC-001",
        "name": "Farmhouse Butter Biscuits 200g",
        "description": "Crispy golden butter biscuits in moisture-barrier wrap",
        "category": "Bakery",
        "unit": "pack",
        "reorder_level": 5000,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    },
    "prod-juice-003": {
        "id": "a0000001-0000-0000-0000-000000000003",
        "sku": "JUICE-001",
        "name": "Alphonso Mango Nectar 1L",
        "description": "Premium Alphonso mango nectar, cold-filled aseptic carton",
        "category": "Beverages",
        "unit": "litre",
        "reorder_level": 8000,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    },
}

MEM_SUPPLIERS: Dict[str, Dict[str, Any]] = {
    "sup-001": {
        "id": "b0000001-0000-0000-0000-000000000001",
        "supplier_code": "SUP-001",
        "name": "Northern Valley Dairy Co-op",
        "contact_person": "Robert Lindqvist",
        "email": "procurement@northernvalleydairy.com",
        "phone": "+1-920-555-0142",
        "address": "402 Dairy Lane, Green Bay Hub",
        "city": "Green Bay",
        "country": "USA",
        "status": "active",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    },
    "sup-002": {
        "id": "b0000001-0000-0000-0000-000000000002",
        "supplier_code": "SUP-002",
        "name": "Golden Grain Mill & Bakery Supply",
        "contact_person": "Elena Rostova",
        "email": "orders@goldengrainmill.com",
        "phone": "+1-312-555-0188",
        "address": "1200 Industrial Pkwy",
        "city": "Chicago",
        "country": "USA",
        "status": "active",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    },
    "sup-003": {
        "id": "b0000001-0000-0000-0000-000000000003",
        "supplier_code": "SUP-003",
        "name": "Tropical Orchards Puree Ltd",
        "contact_person": "Rajesh Nair",
        "email": "supply@tropicalorchards.com",
        "phone": "+91-22-555-0199",
        "address": "Plot 45, APMC Market Hub",
        "city": "Mumbai",
        "country": "India",
        "status": "active",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    },
}

MEM_INVENTORY: Dict[str, Dict[str, Any]] = {
    "inv-001": {
        "id": "c0000001-0000-0000-0000-000000000001",
        "product_id": "a0000001-0000-0000-0000-000000000001",
        "location": "Cold Silo 04",
        "batch_number": "BATCH-MILK-2026-10",
        "quantity_on_hand": 6200.0,
        "quantity_reserved": 1200.0,
        "reorder_threshold": 14600.0,
        "unit": "litre",
        "expiration_date": "2026-11-05",
        "status": "critical_buffer_breach",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    },
    "inv-002": {
        "id": "c0000001-0000-0000-0000-000000000002",
        "product_id": "a0000001-0000-0000-0000-000000000002",
        "location": "Warehouse A - Dry Storage",
        "batch_number": "BATCH-BISC-2026-08",
        "quantity_on_hand": 4800.0,
        "quantity_reserved": 500.0,
        "reorder_threshold": 5000.0,
        "unit": "pack",
        "expiration_date": "2027-04-15",
        "status": "warning_low",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    },
    "inv-003": {
        "id": "c0000001-0000-0000-0000-000000000003",
        "product_id": "a0000001-0000-0000-0000-000000000003",
        "location": "Warehouse C - Chilled Juice Tank",
        "batch_number": "BATCH-JUICE-2026-04",
        "quantity_on_hand": 7900.0,
        "quantity_reserved": 1000.0,
        "reorder_threshold": 8000.0,
        "unit": "litre",
        "expiration_date": "2026-12-20",
        "status": "warning_low",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    },
}

MEM_PURCHASE_ORDERS: Dict[str, Dict[str, Any]] = {
    "po-001": {
        "id": "d0000001-0000-0000-0000-000000000001",
        "po_number": "PO-89110",
        "supplier_id": "b0000001-0000-0000-0000-000000000001",
        "status": "ordered",
        "total_amount": 12780.0,
        "order_date": "2026-10-20",
        "expected_delivery_date": "2026-10-24",
        "actual_delivery_date": None,
        "notes": "9,000L Grade A Raw Milk Reefer Tanker (Carrier delayed by blizzard)",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "items": [
            {
                "id": "d0000001-0000-0000-0001-000000000001",
                "purchase_order_id": "d0000001-0000-0000-0000-000000000001",
                "product_id": "a0000001-0000-0000-0000-000000000001",
                "quantity": 9000.0,
                "unit_price": 1.42,
                "total_price": 12780.0,
                "created_at": now_iso(),
            }
        ],
    },
    "po-002": {
        "id": "d0000001-0000-0000-0000-000000000002",
        "po_number": "PO-89112",
        "supplier_id": "b0000001-0000-0000-0000-000000000002",
        "status": "ordered",
        "total_amount": 8500.0,
        "order_date": "2026-10-21",
        "expected_delivery_date": "2026-10-26",
        "actual_delivery_date": None,
        "notes": "Bakery shortening and unbleached flour restock",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "items": [
            {
                "id": "d0000001-0000-0000-0001-000000000002",
                "purchase_order_id": "d0000001-0000-0000-0000-000000000002",
                "product_id": "a0000001-0000-0000-0000-000000000002",
                "quantity": 5000.0,
                "unit_price": 1.70,
                "total_price": 8500.0,
                "created_at": now_iso(),
            }
        ],
    },
}

MEM_PRODUCTION_ORDERS: Dict[str, Dict[str, Any]] = {
    "prod-ord-001": {
        "id": "e0000001-0000-0000-0000-000000000001",
        "order_number": "PROD-2026-401",
        "product_id": "a0000001-0000-0000-0000-000000000001",
        "target_quantity": 15000.0,
        "completed_quantity": 0.0,
        "status": "scheduled",
        "line_id": "Line 02 - Aseptic Bottling",
        "start_date": "2026-10-25T08:00:00Z",
        "end_date": "2026-10-26T18:00:00Z",
        "notes": "Scheduled whole milk bottling run; risk of raw milk feedstock starvation",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    },
    "prod-ord-002": {
        "id": "e0000001-0000-0000-0000-000000000002",
        "order_number": "PROD-2026-402",
        "product_id": "a0000001-0000-0000-0000-000000000002",
        "target_quantity": 20000.0,
        "completed_quantity": 8000.0,
        "status": "in_progress",
        "line_id": "Line 01 - Rotary Bakery",
        "start_date": "2026-10-24T06:00:00Z",
        "end_date": "2026-10-25T20:00:00Z",
        "notes": "Farmhouse butter biscuit high-speed oven run",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    },
}

MEM_SHIPMENTS: Dict[str, Dict[str, Any]] = {
    "ship-001": {
        "id": "f0000001-0000-0000-0000-000000000001",
        "tracking_number": "TRK-9021",
        "carrier": "Northern Logistics Reefer Fleet",
        "origin": "Green Bay Hub, WI",
        "destination": "Midwest Packaging Plant #04",
        "purchase_order_id": "d0000001-0000-0000-0000-000000000001",
        "status": "delayed",
        "estimated_delivery": "2026-10-27T14:15:00Z",
        "actual_delivery": None,
        "notes": "Severe weather detour (+72h delay across I-80 corridor)",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    },
    "ship-002": {
        "id": "f0000001-0000-0000-0000-000000000002",
        "tracking_number": "TRK-4402",
        "carrier": "SwiftFreight Midwest",
        "origin": "Mumbai / Chicago Gateway",
        "destination": "Regional Logistics DC #02",
        "purchase_order_id": None,
        "status": "in_transit",
        "estimated_delivery": "2026-10-26T10:00:00Z",
        "actual_delivery": None,
        "notes": "Mango juice aseptic containers in transit",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    },
}

MEM_EVENTS: Dict[str, Dict[str, Any]] = {
    "evt-001": {
        "id": "70000001-0000-0000-0000-000000000001",
        "event_type": "SHIPMENT_DELAYED",
        "domain": "logistics",
        "source": "telematics",
        "payload": {
            "tracking_number": "TRK-9021",
            "carrier": "Northern Logistics",
            "delay_hours": 72,
            "corridor": "I-80 Des Moines bypass",
        },
        "severity": "high",
        "created_at": now_iso(),
    },
    "evt-002": {
        "id": "70000001-0000-0000-0000-000000000002",
        "event_type": "INVENTORY_LOW",
        "domain": "inventory",
        "source": "scada_silo_sensors",
        "payload": {
            "product_sku": "MILK-001",
            "location": "Cold Silo 04",
            "current_volume": 6200,
            "safety_floor": 14600,
            "runway_hours": 38.2,
        },
        "severity": "critical",
        "created_at": now_iso(),
    },
}

MEM_ALERTS: Dict[str, Dict[str, Any]] = {
    "alt-001": {
        "id": "80000001-0000-0000-0000-000000000001",
        "title": "Raw Milk Buffer Breach Warning",
        "message": "Cold Silo 04 reserves (6,200L) will reach starvation floor within 38h 14m due to PO #89110 transit slip.",
        "severity": "CRITICAL",
        "domain": "inventory",
        "entity_type": "inventory",
        "entity_id": "c0000001-0000-0000-0000-000000000001",
        "status": "ACTIVE",
        "created_at": now_iso(),
        "resolved_at": None,
    },
    "alt-002": {
        "id": "80000001-0000-0000-0000-000000000002",
        "title": "Carrier Route Variance #TRK-9021",
        "message": "I-80 heavy blizzard advisory resulted in 72-hour detour around Des Moines.",
        "severity": "HIGH",
        "domain": "logistics",
        "entity_type": "shipment",
        "entity_id": "f0000001-0000-0000-0000-000000000001",
        "status": "ACTIVE",
        "created_at": now_iso(),
        "resolved_at": None,
    },
    "alt-003": {
        "id": "80000001-0000-0000-0000-000000000003",
        "title": "Production Line 02 Starvation Hazard",
        "message": "Bottling batch will be starved of raw milk feedstock without mitigation by tomorrow 08:00 CST.",
        "severity": "HIGH",
        "domain": "production",
        "entity_type": "production_order",
        "entity_id": "e0000001-0000-0000-0000-000000000001",
        "status": "ACTIVE",
        "created_at": now_iso(),
        "resolved_at": None,
    },
}

MEM_RISKS: Dict[str, Dict[str, Any]] = {
    "rsk-001": {
        "id": "90000001-0000-0000-0000-000000000001",
        "risk_code": "RSK-MILK-01",
        "title": "Raw Milk Inbound Stockout & Plant Line 02 Idle Risk",
        "description": "Feedstock starvation risks halting Packaging Line 02, causing 4,000 cases of unfilled customer commitments.",
        "category": "supply",
        "probability": 0.85,
        "impact_score": 8.5,
        "estimated_loss": 14200.0,
        "status": "IDENTIFIED",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    },
    "rsk-002": {
        "id": "90000001-0000-0000-0000-000000000002",
        "risk_code": "RSK-BISC-02",
        "title": "Supplier Lead-time Slip for Biscuit Shortening",
        "description": "Golden Grain Mill re-order lead time increased by 3 days due to milling line maintenance.",
        "category": "supply",
        "probability": 0.65,
        "impact_score": 6.0,
        "estimated_loss": 5100.0,
        "status": "MITIGATING",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    },
}

MEM_RECOMMENDATIONS: Dict[str, Dict[str, Any]] = {
    "rec-001": {
        "id": "a1000001-0000-0000-0000-000000000001",
        "telemetry_id": "EXC-8842-MILK",
        "title": "AI Prescriptive Mitigation: Dispatch Certified Partner SwiftReefer",
        "description": "Authorize dynamic re-route: Dispatch certified partner SwiftReefer from Green Bay Hub. Reallocates 9,000L fresh batch in 14 hours.",
        "action_type": "re_route_dispatch",
        "target_domain": "procurement",
        "mitigation_cost": 450.0,
        "net_protected_value": 13750.0,
        "confidence_score": 98.6,
        "status": "pending_authorization",
        "steps": [
            "Issue PO #89110-EXP to SwiftReefer Cold Chain",
            "Reserve Green Bay Bay 03 Loading Slot (T-2h)",
            "Update MES Bottling Line 02 Schedule to prevent sanitize cycle",
            "Transmit automated EDI 856 advance ship notice",
        ],
        "created_at": now_iso(),
    }
}

TABLE_MAP = {
    "products": MEM_PRODUCTS,
    "suppliers": MEM_SUPPLIERS,
    "inventory": MEM_INVENTORY,
    "purchase_orders": MEM_PURCHASE_ORDERS,
    "production_orders": MEM_PRODUCTION_ORDERS,
    "shipments": MEM_SHIPMENTS,
    "events": MEM_EVENTS,
    "alerts": MEM_ALERTS,
    "risks": MEM_RISKS,
    "recommendations": MEM_RECOMMENDATIONS,
}


class BaseRepository:
    def __init__(self, table_name: str):
        self.table_name = table_name

    def _get_mem_store(self) -> Dict[str, Dict[str, Any]]:
        return TABLE_MAP.get(self.table_name, {})

    def get_all(self) -> List[Dict[str, Any]]:
        supabase = get_supabase()
        if supabase:
            try:
                res = supabase.table(self.table_name).select("*").execute()
                if res.data:
                    return res.data
            except Exception:
                pass
        return list(self._get_mem_store().values())

    def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        supabase = get_supabase()
        str_id = str(item_id)
        if supabase:
            try:
                res = supabase.table(self.table_name).select("*").eq("id", str_id).execute()
                if res.data and len(res.data) > 0:
                    return res.data[0]
            except Exception:
                pass

        # In-memory search by id or key
        store = self._get_mem_store()
        for k, v in store.items():
            if str(v.get("id")) == str_id or k == str_id:
                return v
        return None

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        item_id = data.get("id") or str(uuid.uuid4())
        record = dict(data)
        record["id"] = str(item_id)
        record["created_at"] = record.get("created_at") or now_iso()
        record["updated_at"] = now_iso()

        supabase = get_supabase()
        if supabase:
            try:
                res = supabase.table(self.table_name).insert(record).execute()
                if res.data and len(res.data) > 0:
                    return res.data[0]
            except Exception:
                pass

        store = self._get_mem_store()
        store[record["id"]] = record
        return record

    def update(self, item_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        str_id = str(item_id)
        supabase = get_supabase()
        if supabase:
            try:
                update_data = {**data, "updated_at": now_iso()}
                res = supabase.table(self.table_name).update(update_data).eq("id", str_id).execute()
                if res.data and len(res.data) > 0:
                    return res.data[0]
            except Exception:
                pass

        store = self._get_mem_store()
        for k, v in store.items():
            if str(v.get("id")) == str_id or k == str_id:
                v.update(data)
                v["updated_at"] = now_iso()
                return v
        return None

    def delete(self, item_id: str) -> bool:
        str_id = str(item_id)
        supabase = get_supabase()
        if supabase:
            try:
                res = supabase.table(self.table_name).delete().eq("id", str_id).execute()
                if res.data:
                    return True
            except Exception:
                pass

        store = self._get_mem_store()
        target_key = None
        for k, v in store.items():
            if str(v.get("id")) == str_id or k == str_id:
                target_key = k
                break
        if target_key:
            del store[target_key]
            return True
        return False
