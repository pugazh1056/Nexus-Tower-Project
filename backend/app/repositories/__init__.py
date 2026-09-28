from .base import BaseRepository

product_repo = BaseRepository("products")
supplier_repo = BaseRepository("suppliers")
inventory_repo = BaseRepository("inventory")
purchase_order_repo = BaseRepository("purchase_orders")
production_order_repo = BaseRepository("production_orders")
production_bom_repo = BaseRepository("production_bom")
production_material_requirements_repo = BaseRepository("production_material_requirements")
production_progress_repo = BaseRepository("production_progress")
shipment_repo = BaseRepository("shipments")
shipment_items_repo = BaseRepository("shipment_items")
shipment_receipts_repo = BaseRepository("shipment_receipts")
shipment_telemetry_repo = BaseRepository("shipment_temperature_telemetry")
event_repo = BaseRepository("events")
alert_repo = BaseRepository("alerts")
risk_repo = BaseRepository("risks")
recommendation_repo = BaseRepository("recommendations")

__all__ = [
    "BaseRepository",
    "product_repo",
    "supplier_repo",
    "inventory_repo",
    "purchase_order_repo",
    "production_order_repo",
    "production_bom_repo",
    "production_material_requirements_repo",
    "production_progress_repo",
    "shipment_repo",
    "shipment_items_repo",
    "shipment_receipts_repo",
    "shipment_telemetry_repo",
    "event_repo",
    "alert_repo",
    "risk_repo",
    "recommendation_repo",
]
