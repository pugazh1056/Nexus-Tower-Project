from typing import Optional
from app.config import settings

supabase_client = None


def get_supabase():
    global supabase_client
    if supabase_client is None:
        url = settings.supabase_url or ""
        key = settings.supabase_secret_key or settings.supabase_key or ""
        if not url or not key or "placeholder" in url or "placeholder" in key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be configured.")
        try:
            from supabase import create_client
            supabase_client = create_client(url, key)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Supabase client: {e}")
    return supabase_client

