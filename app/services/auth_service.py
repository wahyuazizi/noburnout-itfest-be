# app/services/auth_service.py
from supabase import create_client, Client
from app.config import settings

# Initialize Supabase client
supabase_url: str = settings.supabase_url
supabase_key: str = settings.supabase_key
supabase: Client = create_client(supabase_url, supabase_key)

class AuthService:
    """Service for handling authentication with Supabase."""

    @staticmethod
    def get_supabase_client() -> Client:
        """Returns the Supabase client instance."""
        return supabase

auth_service = AuthService()
