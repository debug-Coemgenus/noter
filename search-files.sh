#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Set defaults if not defined
NOTES_DIR=${NOTES_DIR:-./notes}
NOTES_EDITOR=${NOTES_EDITOR:-vim}

# Check if notes directory exists
if [ ! -d "$NOTES_DIR" ]; then
    echo "Notes directory not found: $NOTES_DIR"
    exit 1
fi

# Use find to get all .txt files and pipe to fzf
selected_file=$(find "$NOTES_DIR" -name '*.txt' -type f | fzf --prompt='Select file: ')

# If a file was selected, open it in the editor
if [ -n "$selected_file" ]; then
    "$NOTES_EDITOR" "$selected_file"
fi