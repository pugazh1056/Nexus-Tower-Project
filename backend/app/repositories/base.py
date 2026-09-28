import uuid
import csv
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status
from app.core.supabase import get_supabase


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_csv_to_dict(filename: str, key_field: str = "id") -> Dict[str, Dict[str, Any]]:
    d = {}
    path = os.path.join("dataset", filename)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    k = row.get(key_field, str(uuid.uuid4()))
                    d[k] = dict(row)
        except Exception:
            pass
    return d


# Global in-memory relational store retained purely for dataset seeding/validation utilities.
# NOT used for runtime operational storage.
MEM_PRODUCTS: Dict[str, Dict[str, Any]] = {}
MEM_SUPPLIERS: Dict[str, Dict[str, Any]] = {}
MEM_INVENTORY: Dict[str, Dict[str, Any]] = {}
MEM_PURCHASE_ORDERS: Dict[str, Dict[str, Any]] = {}
MEM_PRODUCTION_ORDERS: Dict[str, Dict[str, Any]] = {}
MEM_SHIPMENTS: Dict[str, Dict[str, Any]] = {}
MEM_EVENTS: Dict[str, Dict[str, Any]] = {}
MEM_ALERTS: Dict[str, Dict[str, Any]] = {}
MEM_RISKS: Dict[str, Dict[str, Any]] = {}
MEM_RECOMMENDATIONS: Dict[str, Dict[str, Any]] = {}

MEM_PRODUCTION_BOM = load_csv_to_dict("production_bom.csv")
MEM_PRODUCTION_MATERIAL_REQUIREMENTS = load_csv_to_dict("production_material_requirements.csv")
MEM_PRODUCTION_PROGRESS = load_csv_to_dict("production_progress.csv")
MEM_SHIPMENT_ITEMS = load_csv_to_dict("shipment_items.csv")
MEM_SHIPMENT_RECEIPTS = load_csv_to_dict("shipment_receipts.csv")
MEM_SHIPMENT_TELEMETRY = load_csv_to_dict("shipment_temperature_telemetry.csv")

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
    "production_bom": MEM_PRODUCTION_BOM,
    "production_material_requirements": MEM_PRODUCTION_MATERIAL_REQUIREMENTS,
    "production_progress": MEM_PRODUCTION_PROGRESS,
    "shipment_items": MEM_SHIPMENT_ITEMS,
    "shipment_receipts": MEM_SHIPMENT_RECEIPTS,
    "shipment_temperature_telemetry": MEM_SHIPMENT_TELEMETRY,
}


class BaseRepository:
    def __init__(self, table_name: str):
        self.table_name = table_name

    def _get_client(self):
        try:
            client = get_supabase()
            if not client:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Operational database unavailable"
                )
            return client
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Operational database unavailable"
            )

    def get_all(self) -> List[Dict[str, Any]]:
        client = self._get_client()
        try:
            res = client.table(self.table_name).select("*").execute()
            if res.data is not None:
                return res.data
            return []
        except HTTPException:
            raise
        except Exception as e:
            if "PGRST205" in str(e) or "Could not find the table" in str(e):
                if self.table_name in TABLE_MAP and TABLE_MAP[self.table_name]:
                    return list(TABLE_MAP[self.table_name].values())
                return []
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Operational database unavailable"
            )

    def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        client = self._get_client()
        str_id = str(item_id)
        is_uuid = False
        try:
            uuid.UUID(str_id)
            is_uuid = True
        except (ValueError, TypeError):
            is_uuid = False

        try:
            if is_uuid:
                res = client.table(self.table_name).select("*").eq("id", str_id).execute()
                if res.data and len(res.data) > 0:
                    return res.data[0]
            else:
                key_fields = {
                    "purchase_orders": "po_number",
                    "products": "sku",
                    "suppliers": "supplier_code",
                    "production_orders": "production_number",
                    "shipments": "shipment_number",
                    "inventory": "warehouse_location",
                }
                field = key_fields.get(self.table_name)
                if field:
                    try:
                        res = client.table(self.table_name).select("*").eq(field, str_id).execute()
                        if res.data and len(res.data) > 0:
                            return res.data[0]
                    except Exception:
                        pass
            return None
        except HTTPException:
            raise
        except Exception as e:
            if "PGRST205" in str(e) or "Could not find the table" in str(e):
                if self.table_name in TABLE_MAP and str_id in TABLE_MAP[self.table_name]:
                    return TABLE_MAP[self.table_name][str_id]
                return None
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Operational database unavailable"
            )

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        client = self._get_client()
        item_id = data.get("id") or str(uuid.uuid4())
        record = dict(data)
        record["id"] = str(item_id)
        record["created_at"] = record.get("created_at") or now_iso()
        record["updated_at"] = now_iso()

        try:
            res = client.table(self.table_name).insert(record).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            return record
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Operational database unavailable"
            )

    def update(self, item_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        client = self._get_client()
        str_id = str(item_id)
        try:
            update_data = {**data, "updated_at": now_iso()}
            res = client.table(self.table_name).update(update_data).eq("id", str_id).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            return None
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Operational database unavailable"
            )

    def delete(self, item_id: str) -> bool:
        client = self._get_client()
        str_id = str(item_id)
        try:
            res = client.table(self.table_name).delete().eq("id", str_id).execute()
            return True
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Operational database unavailable"
            )

