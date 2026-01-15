-- Add priority field to brancher_todos table
-- Priority levels: 1=low, 2=medium, 3=high

ALTER TABLE brancher_todos
ADD COLUMN priority INTEGER DEFAULT 2 CHECK (priority >= 1 AND priority <= 3);

-- Update existing todos to have medium priority
UPDATE brancher_todos SET priority = 2 WHERE priority IS NULL;

-- Add comment to the column for documentation
COMMENT ON COLUMN brancher_todos.priority IS 'Priority level: 1=low, 2=medium, 3=high';