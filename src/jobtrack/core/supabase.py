from supabase import create_client
from ..config import settings

def get_supabase(use_service_key=False):
    """Get Supabase client with either anon key or service role key."""
    key = settings.SUPABASE_SECRET_KEY if use_service_key else settings.SUPABASE_KEY
    return create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=key
    )

def init_supabase_schema():
    """Initialize the database schema using service role key."""
    client = get_supabase(use_service_key=True)
    
    # Enable the UUID extension if not already enabled
    enable_uuid = """
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    """
    
    # Update users table schema
    create_users = """
    DROP TABLE IF EXISTS users CASCADE;
    
    CREATE TABLE users (
        id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
        email varchar UNIQUE NOT NULL,
        password varchar NOT NULL,
        full_name varchar NOT NULL,
        created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
        updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
    );
    """
    
    try:
        # Execute raw SQL queries
        client.query(enable_uuid).execute()
        client.query(create_users).execute()
        print("Successfully initialized database schema")
    except Exception as e:
        print(f"Error initializing schema: {e}")

# Initialize global client with anon key for regular operations
supabase_client = get_supabase()
