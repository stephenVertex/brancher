# Keyboard navigation in TUI

Add vim-style j/k keyboard navigation to move up and down the TODO list.

## Requirements

- `j` moves selection down (next item)
- `k` moves selection up (previous item)
- Navigation should work globally (not just when list is focused)
- No wrap-around behavior (stop at first/last item)

## Implementation

Add key bindings to `BrancherApp.BINDINGS` in `tui.py`:
- `Binding("j", "cursor_down", "Down", show=False)`
- `Binding("k", "cursor_up", "Up", show=False)`

The `show=False` keeps the footer clean since arrow keys already work.

Implement the actions:
- `action_cursor_down()` - move ListView highlight to next item
- `action_cursor_up()` - move ListView highlight to previous item

## Testing

- Press `j` to move down the list
- Press `k` to move up the list
- Verify navigation stops at boundaries (doesn't wrap)
- Verify it works even when input field is focused
