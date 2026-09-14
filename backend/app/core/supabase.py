from supabase import create_client, Client
from app.config import settings


def _create_client() -> Client | None:
    if not settings.supabase_url or not (
        settings.supabase_secret_key or settings.supabase_key
    ):
        return None
    return create_client(
        settings.supabase_url,
        settings.supabase_secret_key or settings.supabase_key,
    )


supabase: Client | None = _create_client()