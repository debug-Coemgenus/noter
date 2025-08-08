#!/usr/bin/env python3

import json
import os
import sys
import signal
import readline
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def load_tasks():
    """Load tasks from tasks.json file."""
    with open('tasks.json', 'r') as f:
        return json.load(f)

def display_tasks(tasks):
    """Display tasks with zebra striping."""
    print("\nAvailable tasks:")
    for i, task in enumerate(tasks):
        if i % 2 == 0:
            # Even rows - white text on black background
            print(f"\033[37m\033[40m{task['prefix']} | {task['task']}\033[0m")
        else:
            # Odd rows - white text on dark gray background
            print(f"\033[37m\033[100m{task['prefix']} | {task['task']}\033[0m")
    print()

def get_timestamp():
    """Get current timestamp in d.m.YYYY HH.MM format."""
    now = datetime.now()
    return f"{now.day}.{now.month}.{now.year} {now.hour}.{now.minute:02d}"

def get_note_file_path():
    """Get the path for today's note file."""
    notes_dir = os.getenv('NOTES_DIR', './notes')
    now = datetime.now()
    
    # Create month.year directory
    month_year = f"{now.month}.{now.year}"
    month_dir = Path(notes_dir) / month_year
    month_dir.mkdir(parents=True, exist_ok=True)
    
    # Create day.month.year.txt file
    day_month_year = f"{now.day}.{now.month}.{now.year}"
    return month_dir / f"{day_month_year}.txt"

def save_note(prefix, task_name, note_content):
    """Save note to the appropriate file."""
    file_path = get_note_file_path()
    timestamp = get_timestamp()
    
    note_line = f"[{timestamp}] [{task_name}] {note_content}\n"
    
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(note_line)

def find_task_by_prefix(tasks, prefix):
    """Find task name by prefix."""
    for task in tasks:
        if task['prefix'] == prefix:
            return task['task']
    return None


def main():
    tasks = load_tasks()
    display_tasks(tasks)
    
    last_saved_input = ""
    
    def signal_handler(signum, frame):
        """Handle Ctrl+C - save current note if present, then exit."""
        nonlocal tasks, last_saved_input
        print()  # New line after ^C
        
        # Get the current input buffer from readline
        current_input = readline.get_line_buffer().strip()
        
        # Only save if it's different from the last saved input
        if current_input and current_input != last_saved_input:
            parts = current_input.split(' ', 1)
            if len(parts) >= 2:
                prefix = parts[0]
                note_content = parts[1]
                task_name = find_task_by_prefix(tasks, prefix)
                if task_name:
                    save_note(prefix, task_name, note_content)
                    print(f"Note saved: [{get_timestamp()}] [{task_name}] {note_content}")
        
        print("Exiting...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    while True:
        try:
            print("Usage: [PREFIX] [NOTE]")
            user_input = input("Enter note: ").strip()
            
            if not user_input:
                continue
            
            # Parse input
            parts = user_input.split(' ', 1)
            if len(parts) < 2:
                print("Please use format: PREFIX NOTE")
                continue
            
            prefix = parts[0]
            note_content = parts[1]
            
            # Find task name
            task_name = find_task_by_prefix(tasks, prefix)
            if not task_name:
                print(f"Unknown prefix: {prefix}")
                continue
            
            # Save note
            save_note(prefix, task_name, note_content)
            print(f"Note saved: [{get_timestamp()}] [{task_name}] {note_content}")
            
            # Track this input to prevent duplicate saves on Ctrl+C
            last_saved_input = user_input
            
        except EOFError:
            # Handle Ctrl+D
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Note taking application')
    parser.add_argument('-f', '--files', action='store_true', 
                       help='Search for filenames using fzf')
    parser.add_argument('-s', '--search', action='store_true',
                       help='Search for text within files using fzf')
    
    args = parser.parse_args()
    
    if args.files:
        subprocess.run(['./search-files.sh'])
    elif args.search:
        subprocess.run(['./search-content.sh'])
    else:
        main()
