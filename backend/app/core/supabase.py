from typing import Optional
from app.config import settings

supabase_client = None


def get_supabase():
    global supabase_client
    if supabase_client is None:
        try:
            from supabase import create_client
            url = settings.supabase_url or ""
            key = settings.supabase_key or ""
            if url and key and "placeholder" not in url and "placeholder" not in key:
                supabase_client = create_client(url, key)
            else:
                supabase_client = None
        except Exception:
            supabase_client = None
    return supabase_client
