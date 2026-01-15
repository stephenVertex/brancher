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
)
from textual.binding import Binding
from textual import on

from supabase_client import get_supabase_client


class TodoItem(ListItem):
    """A single TODO item in the list."""

    def __init__(self, todo_id: str, title: str, completed: bool) -> None:
        super().__init__()
        self.todo_id = todo_id
        self.title = title
        self.completed = completed

    def compose(self) -> ComposeResult:
        status = "[x]" if self.completed else "[ ]"
        yield Label(f"{status} {self.title}")


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
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield ListView(id="todo-list")
        with Horizontal(id="input-area"):
            yield Input(placeholder="New TODO...", id="new-todo")
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
        title = input_field.value.strip()

        if not title:
            return

        client = get_supabase_client()
        result = (
            client.table("brancher_todos")
            .insert(
                {
                    "title": title,
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
