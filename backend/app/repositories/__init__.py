from .base import BaseRepository

product_repo = BaseRepository("products")
supplier_repo = BaseRepository("suppliers")
inventory_repo = BaseRepository("inventory")
purchase_order_repo = BaseRepository("purchase_orders")
production_order_repo = BaseRepository("production_orders")
shipment_repo = BaseRepository("shipments")
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
    "shipment_repo",
    "event_repo",
    "alert_repo",
    "risk_repo",
    "recommendation_repo",
]
