# Brancher Version History

## 1.1.0
- Added priority system (1=low, 2=medium, 3=high)
- CLI: `brancher add --priority` - Add todo with priority
- CLI: `brancher priority` - Change todo priority
- CLI: `brancher stats` - Show priority breakdown statistics
- TUI: Priority display with color coding (high=red, medium=yellow, low=dim)
- TUI: Priority selector when adding new todos
- TUI: Priority change shortcut (p key)
- TUI: Sort by priority (high first) then by creation date
- Database: Added priority column to brancher_todos table

## 1.0.0
- Initial release
- CLI: `brancher list` - List todos
- CLI: `brancher add` - Add a todo
- CLI: `brancher complete` - Mark todo as complete
- CLI: `brancher uncomplete` - Mark todo as incomplete
- CLI: `brancher delete` - Delete a todo
- TUI: Interactive todo list with keyboard shortcuts
