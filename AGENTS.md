# Agent Learnings

Notes and patterns discovered while working on this codebase.

## Project-Specific Workflow

- **Do not start the brancher TUI** - The TUI does not work well in agent environments and accumulates running instances in the background. Let the user start it and ask them to check functionality.
- **Version management** - When updating the `brancher` command, increment the version in `BRANCHER_VERSION_HISTORY.md`. There's a built-in VERSION string in the command.
- **Feature parity** - When adding functionality to `tui.py`, remind the user to add parallel functionality to the CLI.

## Supabase MCP Tools

This project has access to Supabase MCP tools for direct database interaction. If you don't have access to these tools but they would be useful for your task, ask the user to enable them.

**Project ID:** `qouaegjyuitffqcmwfpe`

**Table Prefix:** All tables for this project use the `brancher_` prefix.

**Tables:**
- `brancher_todos` - Simple TODO list storage

**Available tools include:**
- `supabase_list_tables` - List tables in the database
- `supabase_execute_sql` - Run SQL queries
- `supabase_apply_migration` - Apply DDL migrations
- `supabase_get_advisors` - Check for security/performance issues
- `supabase_list_migrations` - View migration history
- `supabase_generate_typescript_types` - Generate TypeScript types from schema

## Supabase RLS (Row Level Security)

### Key Concepts

1. **RLS must be explicitly enabled** - Creating policies alone doesn't protect data. You must run:
   ```sql
   ALTER TABLE table_name ENABLE ROW LEVEL SECURITY;
   ```

2. **Policies only activate when RLS is enabled** - A common error is having policies defined but RLS disabled, which provides zero protection.

3. **Use `get_advisors` to check security** - The Supabase MCP tool `get_advisors` with type "security" will catch:
   - Tables with RLS disabled
   - Policies that exist but aren't active
   - Sensitive columns exposed without protection
   - Overly permissive policies (e.g., `USING (true)`)

### RLS Policy Patterns in This Codebase

**User-owned data pattern:**
```sql
CREATE POLICY table_policy ON public.table_name
    FOR ALL
    TO public
    USING (user_id = get_user_id_from_apikey() OR is_admin_apikey())
    WITH CHECK (user_id = get_user_id_from_apikey() OR is_admin_apikey());
```

**Inherited access pattern** (for tables without `user_id` that reference user-owned tables):
```sql
CREATE POLICY references_policy ON public.references
    FOR ALL
    TO public
    USING (
        EXISTS (
            SELECT 1 FROM public.captures c
            WHERE c.id = capture_id
            AND (c.user_id = get_user_id_from_apikey() OR is_admin_apikey())
        )
    );
```

**Sensitive tables (like `users`):**
- SELECT: Can be permissive if needed for lookups
- INSERT: Restrict to admin/system
- UPDATE: Own record or admin
- DELETE: Admin only

### Helper Functions

This codebase uses custom helper functions for RLS:
- `get_user_id_from_apikey()` - extracts user ID from API key header
- `is_admin_apikey()` - checks if current request has admin privileges

**Junction table pattern** (tables linking two user-owned entities):
```sql
CREATE POLICY capture_projects_policy ON public.capture_projects
    FOR ALL
    TO public
    USING (
        EXISTS (SELECT 1 FROM public.captures c WHERE c.id = capture_id
                AND (c.user_id = get_user_id_from_apikey() OR is_admin_apikey()))
        OR EXISTS (SELECT 1 FROM public.projects p WHERE p.id = project_id
                   AND (p.user_id = get_user_id_from_apikey() OR is_admin_apikey()))
    );
```

**Shared/global data pattern** (tables without `user_id` that are intentionally shared):
```sql
-- SELECT remains public for lookups
-- INSERT/UPDATE require authentication
CREATE POLICY tags_insert_policy ON public.tags
    FOR INSERT WITH CHECK (get_user_id_from_apikey() IS NOT NULL OR is_admin_apikey());
-- DELETE restricted to admin
CREATE POLICY tags_delete_policy ON public.tags
    FOR DELETE USING (is_admin_apikey());
```

### Common Gotchas

1. **Tables without `user_id`** - Need to join through related tables to determine ownership
2. **Junction tables** (e.g., `capture_projects`) - Check ownership of EITHER related entity (OR logic)
3. **Shared/global data** (e.g., `tags`) - Keep SELECT public, require auth for modifications, admin-only for DELETE
4. **`USING (true)` policies** - Only acceptable for SELECT; using it for INSERT/UPDATE/DELETE bypasses security

## Supabase Functions

### Search Path Security

Functions must have an immutable search_path to prevent injection attacks:

```sql
CREATE OR REPLACE FUNCTION public.generate_prefixed_id(prefix text)
RETURNS text
LANGUAGE plpgsql
SET search_path = ''  -- Critical: prevents search path manipulation
AS $function$
BEGIN
  RETURN prefix || '-' || encode(pg_catalog.gen_random_bytes(4), 'hex');
END;
$function$;
```

**Key points:**
- Always add `SET search_path = ''` to function definitions
- Use fully-qualified function names (e.g., `pg_catalog.gen_random_bytes()`) inside the function body
- The `get_advisors` tool will flag functions with mutable search paths
