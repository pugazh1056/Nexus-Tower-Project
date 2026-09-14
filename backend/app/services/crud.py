"""Small helpers for the Supabase-backed resource endpoints."""

from typing import Any

from fastapi import HTTPException, status

from app.core.dependencies import require_supabase


def list_rows(table: str) -> list[dict[str, Any]]:
    response = require_supabase().table(table).select("*").execute()
    return response.data or []


def get_row(table: str, row_id: str) -> dict[str, Any]:
    response = require_supabase().table(table).select("*").eq("id", row_id).limit(1).execute()
    if not response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{table.rstrip('s').title()} not found")
    return response.data[0]


def create_row(table: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = require_supabase().table(table).insert(payload).execute()
    if not response.data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create {table.rstrip('s')}")
    return response.data[0]


def update_row(table: str, row_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")
    response = require_supabase().table(table).update(payload).eq("id", row_id).execute()
    if not response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{table.rstrip('s').title()} not found")
    return response.data[0]


def delete_row(table: str, row_id: str) -> None:
    response = require_supabase().table(table).delete().eq("id", row_id).execute()
    if not response.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{table.rstrip('s').title()} not found")
