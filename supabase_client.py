"""Supabase client singleton for Brancher."""

import os
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

# Global singleton client
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get or create a Supabase client instance (singleton pattern)."""
    global _supabase_client

    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_API_KEY:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_API_KEY must be set in environment variables. "
                "Copy .env.example to .env and fill in your credentials."
            )

        _supabase_client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

    return _supabase_client


def reset_client():
    """Reset the client instance (useful for testing)."""
    global _supabase_client
    _supabase_client = None
