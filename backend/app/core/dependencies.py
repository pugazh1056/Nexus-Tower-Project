from typing import List, Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.supabase import get_supabase
import base64
import json

oauth2_scheme = HTTPBearer(auto_error=False)


# Known seed profiles for local testing & development
DEFAULT_PROFILES = {
    "m.vance@nexustower.internal": {
        "id": "usr-proc-01",
        "email": "m.vance@nexustower.internal",
        "full_name": "Marcus Vance",
        "role": "procurement",
        "role_name": "procurement",
    },
    "s.chen@nexustower.internal": {
        "id": "usr-invt-02",
        "email": "s.chen@nexustower.internal",
        "full_name": "Sarah Chen",
        "role": "inventory",
        "role_name": "inventory",
    },
    "k.novak@nexustower.internal": {
        "id": "usr-prod-03",
        "email": "k.novak@nexustower.internal",
        "full_name": "Klaus Novak",
        "role": "production",
        "role_name": "production",
    },
    "d.morales@nexustower.internal": {
        "id": "usr-logs-04",
        "email": "d.morales@nexustower.internal",
        "full_name": "Diego Morales",
        "role": "logistics",
        "role_name": "logistics",
    },
    "ops-admin@nexustower.internal": {
        "id": "usr-root-05",
        "email": "ops-admin@nexustower.internal",
        "full_name": "Nexus Operations Admin",
        "role": "admin",
        "role_name": "admin",
    },
}


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode a bearer token (Supabase JWT or internal token)."""
    if not token:
        return None
    try:
        # Check if internal mock token
        if token.startswith("nexus_jwt_"):
            parts = token.split("_")
            if len(parts) >= 3:
                email = base64.b64decode(parts[2]).decode("utf-8")
                if email in DEFAULT_PROFILES:
                    return DEFAULT_PROFILES[email]
                return {
                    "id": f"usr-{abs(hash(email)) % 10000}",
                    "email": email,
                    "full_name": email.split("@")[0].replace(".", " ").title(),
                    "role": "procurement",
                    "role_name": "procurement",
                }

        # Check if standard JWT
        parts = token.split(".")
        if len(parts) == 3:
            payload_b64 = parts[1]
            padded = payload_b64 + "=" * ((4 - len(payload_b64) % 4) % 4)
            data = json.loads(base64.urlsafe_b64decode(padded).decode("utf-8"))
            email = data.get("email", "")
            return {
                "id": data.get("sub", data.get("id", "usr-jwt")),
                "email": email,
                "full_name": data.get("user_metadata", {}).get("full_name") or email.split("@")[0],
                "role": data.get("role", "procurement"),
                "role_name": data.get("role", "procurement"),
            }
    except Exception:
        pass
    return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(oauth2_scheme)
) -> Dict[str, Any]:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    supabase = get_supabase()

    if supabase:
        try:
            user_response = supabase.auth.get_user(token)
            if user_response and user_response.user:
                u = user_response.user
                # Fetch profile / role
                prof_res = supabase.table("profiles").select("*, roles(name)").eq("id", u.id).execute()
                role_name = "procurement"
                full_name = u.email.split("@")[0]
                if prof_res.data and len(prof_res.data) > 0:
                    p = prof_res.data[0]
                    full_name = p.get("full_name", full_name)
                    r = p.get("roles")
                    if isinstance(r, dict):
                        role_name = r.get("name", "procurement")
                    elif isinstance(r, str):
                        role_name = r
                return {
                    "id": str(u.id),
                    "email": u.email,
                    "full_name": full_name,
                    "role": role_name,
                    "role_name": role_name,
                }
        except Exception:
            pass

    # Fallback to token decoder
    user = decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_roles(allowed_roles: List[str]):
    async def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = (current_user.get("role_name") or current_user.get("role") or "").lower()
        allowed = [r.lower() for r in allowed_roles]
        if "admin" in allowed and user_role == "admin":
            return current_user
        if user_role not in allowed and "admin" != user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted for role '{user_role}'. Allowed roles: {allowed_roles}",
            )
        return current_user

    return role_checker
