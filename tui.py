"""Brancher TUI - Simple TODO terminal interface."""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Header,
    Footer,
    Static,
    Input,
    Button,
    ListView,
    ListItem,
    Label,
    Select,
)
from textual.binding import Binding
from textual import on

from supabase_client import get_supabase_client


class TodoItem(ListItem):
    """A single TODO item in the list."""

    def __init__(
        self, todo_id: str, title: str, completed: bool, priority: int = 2
    ) -> None:
        super().__init__()
        self.todo_id = todo_id
        self.title = title
        self.completed = completed
        self.priority = priority

    def compose(self) -> ComposeResult:
        status = "[x]" if self.completed else "[ ]"
        priority_text = {
            1: "[dim]L[/dim]",
            2: "[yellow]M[/yellow]",
            3: "[red]H[/red]",
        }.get(self.priority, "[yellow]M[/yellow]")
        text = f"{status} {priority_text} {self.title}"
        yield Label(text)


class BrancherApp(App):
    """Brancher TUI Application."""

    TITLE = "Brancher - TODO List"

    CSS = """
    Screen {
        layout: vertical;
    }

    #todo-list {
        height: 1fr;
        border: solid green;
    }

    #input-area {
        height: auto;
        padding: 1;
    }

    #new-todo {
        width: 1fr;
    }

    #add-btn {
        width: auto;
        margin-left: 1;
    }

    #status-bar {
        height: 1;
        background: $surface;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("space", "toggle_todo", "Toggle"),
        Binding("d", "delete_todo", "Delete"),
        Binding("a", "focus_input", "Add"),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("p", "change_priority", "Priority"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield ListView(id="todo-list")
        with Horizontal(id="input-area"):
            yield Input(placeholder="New TODO...", id="new-todo")
            yield Select(
                [("1", "Low"), ("2", "Medium"), ("3", "High")],
                value="2",
                id="priority-select",
                prompt="Priority",
            )
            yield Button("Add", id="add-btn", variant="primary")
        yield Static("", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Load todos on startup."""
        self.load_todos()

    def load_todos(self) -> None:
        """Load todos from database."""
        client = get_supabase_client()
        result = (
            client.table("brancher_todos")
            .select("*")
            .order("priority", desc=True)
            .order("created_at", desc=False)
            .execute()
        )

        list_view = self.query_one("#todo-list", ListView)
        list_view.clear()

        if result.data:
            for todo in result.data:
                list_view.append(
                    TodoItem(
                        todo_id=todo["id"],
                        title=todo["title"],
                        completed=todo["completed"],
                        priority=todo.get("priority", 2),
                    )
                )

        self.update_status(f"Loaded {len(result.data)} todos")

    def update_status(self, message: str) -> None:
        """Update the status bar."""
        status = self.query_one("#status-bar", Static)
        status.update(message)

    def action_refresh(self) -> None:
        """Refresh the todo list."""
        self.load_todos()

    def action_focus_input(self) -> None:
        """Focus the input field."""
        self.query_one("#new-todo", Input).focus()

    def action_cursor_down(self) -> None:
        """Move selection down in the todo list."""
        list_view = self.query_one("#todo-list", ListView)
        list_view.action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move selection up in the todo list."""
        list_view = self.query_one("#todo-list", ListView)
        list_view.action_cursor_up()

    def action_toggle_todo(self) -> None:
        """Toggle the selected todo's completed status."""
        list_view = self.query_one("#todo-list", ListView)
        if list_view.highlighted_child is None:
            return

        item = list_view.highlighted_child
        if not isinstance(item, TodoItem):
            return

        new_completed = not item.completed
        client = get_supabase_client()
        result = (
            client.table("brancher_todos")
            .update(
                {
                    "completed": new_completed,
                }
            )
            .eq("id", item.todo_id)
            .execute()
        )

        if result.data:
            self.update_status(
                f"{'Completed' if new_completed else 'Uncompleted'}: {item.title}"
            )
            self.load_todos()

    def action_delete_todo(self) -> None:
        """Delete the selected todo."""
        list_view = self.query_one("#todo-list", ListView)
        if list_view.highlighted_child is None:
            return

        item = list_view.highlighted_child
        if not isinstance(item, TodoItem):
            return

        client = get_supabase_client()
        result = (
            client.table("brancher_todos").delete().eq("id", item.todo_id).execute()
        )

        if result.data:
            self.update_status(f"Deleted: {item.title}")
            self.load_todos()

    def action_change_priority(self) -> None:
        """Change the priority of the selected todo."""
        list_view = self.query_one("#todo-list", ListView)
        if list_view.highlighted_child is None:
            return

        item = list_view.highlighted_child
        if not isinstance(item, TodoItem):
            return

        # Cycle through priorities: 1 -> 2 -> 3 -> 1
        new_priority = ((item.priority - 1 + 1) % 3) + 1

        client = get_supabase_client()
        result = (
            client.table("brancher_todos")
            .update({"priority": new_priority})
            .eq("id", item.todo_id)
            .execute()
        )

        if result.data:
            priority_text = {1: "Low", 2: "Medium", 3: "High"}.get(
                new_priority, "Medium"
            )
            self.update_status(f"Changed priority to {priority_text}: {item.title}")
            self.load_todos()

    @on(Input.Submitted, "#new-todo")
    def add_todo_on_enter(self, event: Input.Submitted) -> None:
        """Add todo when Enter is pressed in input."""
        self.add_new_todo()

    @on(Button.Pressed, "#add-btn")
    def add_todo_on_click(self, event: Button.Pressed) -> None:
        """Add todo when Add button is clicked."""
        self.add_new_todo()

    def add_new_todo(self) -> None:
        """Add a new todo from the input field."""
        input_field = self.query_one("#new-todo", Input)
        priority_select = self.query_one("#priority-select", Select)
        title = input_field.value.strip()
        priority = int(priority_select.value) if priority_select.value else 2

        if not title:
            return

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
            input_field.value = ""
            self.update_status(f"Added: {title}")
            self.load_todos()


def main():
    """Run the Brancher TUI application."""
    app = BrancherApp()
    app.run()


if __name__ == "__main__":
    main()
