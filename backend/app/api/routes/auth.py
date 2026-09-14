"""Authentication and current-user routes."""

from fastapi import APIRouter, Depends, Response, status
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from supabase_auth.errors import AuthError

from app.core.dependencies import bearer_scheme, get_current_user, require_supabase
from app.schemas.common import AuthLogin, AuthRegister

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: AuthRegister) -> dict:
    try:
        response = require_supabase().auth.sign_up(
            {"email": payload.email, "password": payload.password, "options": {"data": {"full_name": payload.full_name}}}
        )
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Registration failed") from exc
    user = getattr(response, "user", None)
    session = getattr(response, "session", None)
    return {
        "user": user.model_dump() if hasattr(user, "model_dump") else user,
        "session": session.model_dump() if hasattr(session, "model_dump") else session,
    }


@router.post("/login")
def login(payload: AuthLogin) -> dict:
    try:
        response = require_supabase().auth.sign_in_with_password(
            {"email": payload.email, "password": payload.password}
        )
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials") from exc
    return response.model_dump() if hasattr(response, "model_dump") else response


@router.get("/me")
def current_user(user: dict = Depends(get_current_user)) -> dict:
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    _: dict = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Response:
    try:
        client = require_supabase()
        client.auth.set_session(credentials.credentials, "")
        client.auth.sign_out({"scope": "local"})
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed") from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
