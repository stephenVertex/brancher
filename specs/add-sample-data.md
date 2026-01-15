# Create sample data

Use the CLI to populate the database with sample data.
Make the sample data about George Costanza making a list of things to do for his 'Summer of George'.

## Plan

1. Run `uv sync` to ensure dependencies are installed
2. Add each todo item using the `brancher add` command
3. Verify the data with `brancher list`

## Commands to execute

```bash
uv run brancher add "Read a book from beginning to end"
uv run brancher add "Play frolf (frisbee golf)"
uv run brancher add "Take a nap from 1pm to 4pm"
uv run brancher add "Eat a block of cheese the size of a car battery"
uv run brancher add "Learn to play guitar"
uv run brancher add "Watch daytime TV in bathrobe"
uv run brancher add "Avoid getting a job for 3 months"
uv run brancher add "Perfect the art of doing nothing"
```

## Verification

```bash
uv run brancher list
```

Expected output: 8 todos related to George's summer plans.
