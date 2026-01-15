"""Migration display script for Brancher database.

This script displays the SQL migrations that need to be run.
For Supabase, you'll need to execute these in the Supabase SQL Editor.
"""

import sys
from pathlib import Path


def display_migration(migration_file: Path) -> None:
    """Display a single migration file."""
    print(f"\n{'='*60}")
    print(f"MIGRATION: {migration_file.name}")
    print(f"{'='*60}")

    with open(migration_file, 'r') as f:
        sql = f.read()

    print(sql)
    print()


def main():
    """Display all pending migrations."""
    migrations_dir = Path("migrations")
    if not migrations_dir.exists():
        print("No migrations directory found.")
        return

    # Get all SQL files in migrations directory, sorted by name
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        print("No migration files found.")
        return

    print(f"Found {len(migration_files)} migration file(s)")
    print("Copy and paste the following SQL into your Supabase SQL Editor:")
    print()

    for migration_file in migration_files:
        display_migration(migration_file)


if __name__ == "__main__":
    main()