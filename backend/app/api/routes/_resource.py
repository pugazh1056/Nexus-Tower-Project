"""Factory for CRUD routers backed by a Supabase table."""

from fastapi import APIRouter, Depends, Response, status

from app.core.dependencies import get_current_user
from app.services.crud import create_row, delete_row, get_row, list_rows, update_row


def resource_router(prefix: str, tag: str, table: str) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=[tag])
    protected = [Depends(get_current_user)]

    @router.get("/", dependencies=protected)
    def list_resource() -> list[dict]:
        return list_rows(table)

    @router.get("/{resource_id}", dependencies=protected)
    def get_resource(resource_id: str) -> dict:
        return get_row(table, resource_id)

    @router.post("/", status_code=status.HTTP_201_CREATED, dependencies=protected)
    def create_resource(payload: dict) -> dict:
        return create_row(table, payload)

    @router.patch("/{resource_id}", dependencies=protected)
    def update_resource(resource_id: str, payload: dict) -> dict:
        return update_row(table, resource_id, payload)

    @router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=protected)
    def delete_resource(resource_id: str) -> Response:
        delete_row(table, resource_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router
