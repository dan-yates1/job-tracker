from supabase import create_client, Client

from .config import settings

def get_supabase() -> Client:
    """Get Supabase client instance."""
    return create_client(settings.supabase_url, settings.supabase_key)

def init_supabase_schema():
    """Initialize Supabase database schema."""
    # This function will be called on application startup
    # to ensure all required tables and constraints exist
    pass  # We'll implement this later if needed
