#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
  export $(cat .env | grep -v '#' | xargs)
fi

# Set defaults if not defined
NOTES_DIR=${NOTES_DIR:-./notes}
NOTES_EDITOR=${NOTES_EDITOR:-vi}

# Check if notes directory exists
if [ ! -d "$NOTES_DIR" ]; then
  echo "Notes directory not found: $NOTES_DIR"
  exit 1
fi

# Use find and grep to search content within all .txt files and pipe to fzf
selected_line=$(find "$NOTES_DIR" -name '*.txt' -exec grep -Hn . {} \; | fzf --prompt='Search content: ' --delimiter=':' --preview='cat {1}')

# If a line was selected, extract the filename and line number, then open it in the editor
if [ -n "$selected_line" ]; then
  filename=$(echo "$selected_line" | cut -d':' -f1)
  line_number=$(echo "$selected_line" | cut -d':' -f2)
  "$NOTES_EDITOR" "+$line_number" "$filename"
fi

