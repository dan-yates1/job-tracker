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
    
    try:
        # Create users table using the PostgREST API
        client.from_('users').select("*").limit(1).execute()
        print("Successfully verified database schema")
    except Exception as e:
        print(f"Error initializing schema: {e}")
        # If table doesn't exist, we need to create it through Supabase dashboard
        print("Please ensure the users table is created in your Supabase dashboard with the following schema:")
        print("""
        Table name: users
        Columns:
        - id: uuid (primary key, default: uuid_generate_v4())
        - email: varchar (unique, not null)
        - password: varchar (not null)
        - full_name: varchar (not null)
        - created_at: timestamptz (default: now(), not null)
        - updated_at: timestamptz (default: now(), not null)
        """)

# Initialize global client with anon key for regular operations
supabase_client = get_supabase()
