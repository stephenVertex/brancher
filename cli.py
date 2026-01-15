"""CLI tool for brancher - Simple TODO management."""

import click
from supabase_client import get_supabase_client

# Version follows MAJOR.MINOR.PATCH
VERSION = "1.1.0"


@click.group()
@click.version_option(VERSION, "--version", "-V", prog_name="brancher")
def cli():
    """brancher - Simple TODO command-line interface."""
    pass


@cli.command("list")
@click.option(
    "--all", "-a", "show_all", is_flag=True, help="Show all todos including completed"
)
def list_todos(show_all: bool):
    """List all TODOs.

    By default shows only incomplete todos. Use --all to show completed todos too.

    Examples:

        brancher list

        brancher list --all
    """
    client = get_supabase_client()

    query = client.table("brancher_todos").select("*").order("created_at", desc=False)

    if not show_all:
        query = query.eq("completed", False)

    result = query.execute()

    if not result.data:
        if show_all:
            click.echo("No TODOs found.")
        else:
            click.echo("No incomplete TODOs. Use --all to see completed items.")
        return

    click.echo()
    click.echo(f"{'ID':<15} {'Status':<10} {'Priority':<10} {'Title'}")
    click.echo("-" * 70)

    for todo in result.data:
        todo_id = todo.get("id", "")
        title = todo.get("title", "")
        completed = todo.get("completed", False)
        priority = todo.get("priority", 2)
        status = "[x]" if completed else "[ ]"
        priority_text = {1: "Low", 2: "Medium", 3: "High"}.get(priority, "Medium")

        click.echo(f"{todo_id:<15} {status:<10} {priority_text:<10} {title}")

    click.echo()
    click.echo(f"Total: {len(result.data)} todo(s)")


@cli.command("add")
@click.argument("title")
@click.option(
    "--priority",
    "-p",
    type=click.IntRange(1, 3),
    default=2,
    help="Priority level: 1=low, 2=medium, 3=high (default: 2)"
)
def add_todo(title: str, priority: int):
    """Add a new TODO.

    Examples:

        brancher add "Buy groceries"

        brancher add "Finish the report"
    """
    client = get_supabase_client()

    result = (
        client.table("brancher_todos")
        .insert(
            {
                "title": title,
                "priority": priority,
            }
        )
        .execute()
    )

    if result.data:
        todo = result.data[0]
        click.echo(f"Added: {todo['id']} - {title}")
    else:
        click.echo("Failed to add TODO.", err=True)
        raise SystemExit(1)


@cli.command("complete")
@click.argument("todo_id")
def complete_todo(todo_id: str):
    """Mark a TODO as completed.

    Examples:

        brancher complete todo-abc123
    """
    client = get_supabase_client()

    result = (
        client.table("brancher_todos")
        .update(
            {
                "completed": True,
            }
        )
        .eq("id", todo_id)
        .execute()
    )

    if result.data:
        todo = result.data[0]
        click.echo(f"Completed: {todo['title']}")
    else:
        click.echo(f"TODO not found: {todo_id}", err=True)
        raise SystemExit(1)


@cli.command("uncomplete")
@click.argument("todo_id")
def uncomplete_todo(todo_id: str):
    """Mark a TODO as not completed.

    Examples:

        brancher uncomplete todo-abc123
    """
    client = get_supabase_client()

    result = (
        client.table("brancher_todos")
        .update(
            {
                "completed": False,
            }
        )
        .eq("id", todo_id)
        .execute()
    )

    if result.data:
        todo = result.data[0]
        click.echo(f"Uncompleted: {todo['title']}")
    else:
        click.echo(f"TODO not found: {todo_id}", err=True)
        raise SystemExit(1)


@cli.command("priority")
@click.argument("todo_id")
@click.argument("priority", type=click.IntRange(1, 3))
def set_priority(todo_id: str, priority: int):
    """Set the priority of a TODO.

    PRIORITY should be 1 (low), 2 (medium), or 3 (high).

    Examples:

        brancher priority todo-abc123 3

        brancher priority todo-def456 1
    """
    client = get_supabase_client()

    priority_text = {1: "Low", 2: "Medium", 3: "High"}.get(priority, "Medium")

    result = (
        client.table("brancher_todos")
        .update({"priority": priority})
        .eq("id", todo_id)
        .execute()
    )

    if result.data:
        todo = result.data[0]
        click.echo(f"Set priority to {priority_text}: {todo['title']}")
    else:
        click.echo(f"TODO not found: {todo_id}", err=True)
        raise SystemExit(1)


@cli.command("stats")
def show_stats():
    """Show TODO statistics including priority breakdown.

    Examples:

        brancher stats
    """
    client = get_supabase_client()

    # Get all todos
    result = client.table("brancher_todos").select("*").execute()

    if not result.data:
        click.echo("No TODOs found.")
        return

    total = len(result.data)
    completed = len([t for t in result.data if t.get("completed", False)])
    incomplete = total - completed

    # Priority breakdown
    priorities = {1: 0, 2: 0, 3: 0}
    for todo in result.data:
        priority = todo.get("priority", 2)
        priorities[priority] += 1

    click.echo()
    click.echo("TODO Statistics")
    click.echo("=" * 20)
    click.echo(f"Total:      {total}")
    click.echo(f"Completed:  {completed}")
    click.echo(f"Incomplete: {incomplete}")
    click.echo()
    click.echo("Priority Breakdown:")
    click.echo(f"  High (3):   {priorities[3]}")
    click.echo(f"  Medium (2): {priorities[2]}")
    click.echo(f"  Low (1):    {priorities[1]}")
    click.echo()


@cli.command("delete")
@click.argument("todo_id")
@click.confirmation_option(prompt="Are you sure you want to delete this TODO?")
def delete_todo(todo_id: str):
    """Delete a TODO.

    Examples:

        brancher delete todo-abc123
    """
    client = get_supabase_client()

    # Get the todo first
    check = client.table("brancher_todos").select("title").eq("id", todo_id).execute()
    if not check.data:
        click.echo(f"TODO not found: {todo_id}", err=True)
        raise SystemExit(1)

    title = check.data[0]["title"]

    result = client.table("brancher_todos").delete().eq("id", todo_id).execute()

    if result.data:
        click.echo(f"Deleted: {title}")
    else:
        click.echo(f"Failed to delete TODO: {todo_id}", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
