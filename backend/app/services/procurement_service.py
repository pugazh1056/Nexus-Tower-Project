import uuid
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timezone
from app.repositories import purchase_order_repo
from app.schemas.purchase_order import (
    PurchaseOrderStatus,
    VALID_PO_TRANSITIONS,
)
from app.services.event_service import event_service
from app.services.alert_service import alert_service


class ProcurementService:
    def __init__(self):
        self.repo = purchase_order_repo

    def get_all(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        pos = self.repo.get_all()
        if status:
            pos = [p for p in pos if str(p.get("status", "")).lower() == status.lower()]
        return sorted(pos, key=lambda x: str(x.get("created_at") or ""), reverse=True)

    def get_by_id(self, po_id: str | UUID) -> Optional[Dict[str, Any]]:
        return self.repo.get_by_id(str(po_id))

    def create_purchase_order(self, po_in: Any) -> Dict[str, Any]:
        data = po_in.model_dump() if hasattr(po_in, "model_dump") else dict(po_in)
        data["supplier_id"] = str(data["supplier_id"])
        
        # Calculate totals
        items = data.pop("items", []) or []
        total_amount = 0.0
        processed_items = []
        for it in items:
            item_data = it.model_dump() if hasattr(it, "model_dump") else dict(it)
            item_data["id"] = str(uuid.uuid4())
            item_data["product_id"] = str(item_data["product_id"])
            qty = float(item_data.get("quantity", 0))
            price = float(item_data.get("unit_price", 0))
            subtotal = round(qty * price, 2)
            item_data["line_total"] = subtotal
            total_amount += subtotal
            processed_items.append(item_data)

        data["total_amount"] = round(total_amount, 2)
        data["status"] = PurchaseOrderStatus.DRAFT.value
        data["items"] = processed_items

        created = self.repo.create(data)
        for it in created.get("items", []):
            it["po_id"] = created["id"]

        event_service.create_event({
            "event_type": "PO_CREATED",
            "source_service": "procurement",
            "entity_id": created["id"],
            "payload": {
                "po_number": created.get("po_number"),
                "total_amount": created.get("total_amount"),
            },
        })

        return created

    def update_purchase_order(
        self, po_id: str | UUID, po_update: Any
    ) -> Optional[Dict[str, Any]]:
        current = self.get_by_id(po_id)
        if not current:
            return None

        data = po_update.model_dump(exclude_unset=True) if hasattr(po_update, "model_dump") else dict(po_update)
        
        # Enforce deterministic state transitions
        if "status" in data and data["status"]:
            target_status_val = data["status"].value if hasattr(data["status"], "value") else str(data["status"]).lower()
            current_status_val = current.get("status", PurchaseOrderStatus.DRAFT.value)
            if hasattr(current_status_val, "value"):
                current_status_val = current_status_val.value
            current_status_val = str(current_status_val).lower()

            target_status = PurchaseOrderStatus(target_status_val)
            current_status = PurchaseOrderStatus(current_status_val)

            if target_status != current_status:
                allowed_transitions = VALID_PO_TRANSITIONS.get(current_status, [])
                if target_status not in allowed_transitions:
                    allowed_names = [s.value for s in allowed_transitions]
                    raise ValueError(
                        f"Cannot transition PO from '{current_status.value}' to '{target_status.value}'. Allowed transitions: {allowed_names}"
                    )

            data["status"] = target_status.value

            # Trigger operational events based on status
            if target_status == PurchaseOrderStatus.ORDERED:
                event_service.create_event({
                    "event_type": "PO_ORDERED",
                    "source_service": "procurement",
                    "entity_id": str(po_id),
                    "payload": {"po_number": current.get("po_number")},
                })
            elif target_status == PurchaseOrderStatus.RECEIVED:
                data["actual_delivery_date"] = datetime.now(timezone.utc).isoformat()
                event_service.create_event({
                    "event_type": "PO_RECEIVED",
                    "source_service": "procurement",
                    "entity_id": str(po_id),
                    "payload": {"po_number": current.get("po_number")},
                })

        updated = self.repo.update(str(po_id), data)
        return updated

    def delete_purchase_order(self, po_id: str | UUID) -> bool:
        current = self.get_by_id(po_id)
        if not current:
            return False
        curr_status = str(current.get("status", "")).lower()
        if curr_status not in [PurchaseOrderStatus.DRAFT.value, PurchaseOrderStatus.CANCELLED.value]:
            raise ValueError(f"Cannot delete purchase order in '{curr_status}' status. Only draft or cancelled POs can be deleted.")
        return self.repo.delete(str(po_id))


procurement_service = ProcurementService()
