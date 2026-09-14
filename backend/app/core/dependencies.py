"""Shared authentication and authorization dependencies."""

from typing import Any, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase_auth.errors import AuthError

from app.core.supabase import supabase

bearer_scheme = HTTPBearer(auto_error=False)


def _require_client() -> Any:
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase is not configured",
        )
    return supabase


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    client = _require_client()
    try:
        response = client.auth.get_user(credentials.credentials)
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        ) from exc
    user = getattr(response, "user", None)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")

    user_data = user.model_dump() if hasattr(user, "model_dump") else vars(user)
    user_id = user_data.get("id")
    result = (
        client.table("profiles")
        .select("*, roles(*)")
        .eq("id", user_id)
        .limit(1)
        .execute()
    )
    profile = result.data[0] if result.data else {}
    related_role = profile.get("roles")
    if isinstance(related_role, list):
        related_role = related_role[0] if related_role else None
    role_name = related_role.get("name") if isinstance(related_role, dict) else None
    return {**user_data, **profile, "role_name": role_name}


def require_roles(*roles: str) -> Callable[..., dict[str, Any]]:
    def dependency(user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
        if user.get("role_name") not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return dependency


def require_supabase() -> Any:
    return _require_client()
