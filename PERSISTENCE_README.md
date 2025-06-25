# Desktop Cleaner Persistence Feature

The Desktop Cleaner now includes a persistence and resume feature that allows you to quit and resume your desktop cleaning session later. This is especially useful for large desktops with many items.

## How It Works

The application automatically tracks:
- Which files/folders you've already handled
- What action you took for each item (left on desktop, moved to folder, or moved to trash)
- Your current position in the desktop items list

This information is stored in a JSON file in your home directory: `~/desktop_cleaner_state.json`

## Features

### Automatic State Saving
- The application automatically saves your progress after each action
- Your session count is tracked across runs
- The iterator position is saved when you close the application

### Resume Capability
- When you restart the application, it automatically loads your previous state
- Previously handled items are filtered out, so you only see new or unhandled items
- Your position in the list is restored

### State Management Menu
Access state management features through the **File > State Management** menu:

#### Show Summary
- Displays statistics about your cleaning sessions
- Shows counts of items left, moved, and trashed
- Shows the location of the state file

#### Clear Handled Items
- Clears the record of handled items, making them visible again
- Useful if you want to re-process items or made mistakes

#### Clear All State
- Completely resets the application state
- Clears both handled items and iterator position
- **Warning**: This action cannot be undone

#### Export State
- Save your current state to a backup file
- Useful for transferring state between computers or creating backups

#### Import State
- Restore state from a previously exported file
- Replaces your current state with the imported data

## Command Line State Management

For advanced users, a command-line utility `state_manager.py` is provided:

```bash
# Show state summary
python state_manager.py summary

# List all handled items with details
python state_manager.py list

# Clear all state data
python state_manager.py clear all

# Clear only handled items
python state_manager.py clear handled

# Export state to a backup file
python state_manager.py export my_backup.json

# Import state from a backup file
python state_manager.py import my_backup.json
```

## State File Format

The state file is stored in JSON format with the following structure:

```json
{
  "version": "1.0",
  "last_updated": "2024-01-15T10:30:00",
  "session_count": 5,
  "handled_items": {
    "file_hash_1": {
      "original_path": "/Users/you/Desktop/document.pdf",
      "action": "moved",
      "destination": "/Users/you/Documents",
      "timestamp": "2024-01-15T10:25:00",
      "filename": "document.pdf"
    }
  },
  "iterator_state": {
    "items": ["/Users/you/Desktop/file1.txt", "/Users/you/Desktop/file2.jpg"],
    "current_index": 1
  }
}
```

## Hash-Based Item Tracking

Items are tracked using SHA-256 hashes of their file paths. This approach:
- Ensures consistent identification across sessions
- Prevents path-based conflicts
- Maintains privacy (actual paths are hashed)

## Benefits

1. **Resume Anytime**: Stop and start your cleaning sessions without losing progress
2. **Skip Processed Items**: Never accidentally handle the same item twice
3. **Track Progress**: See how many items you've processed over time
4. **Backup State**: Export your progress for safekeeping
5. **Multiple Sessions**: Perfect for large desktops that take multiple sessions to clean

## Best Practices

1. **Regular Backups**: Export your state occasionally, especially before major cleaning sessions
2. **Clear When Needed**: Use "Clear Handled Items" if you want to reconsider previous decisions
3. **Check Summary**: Regularly check your progress with the state summary
4. **Multiple Computers**: Export/import state files to sync progress across devices

## Privacy and Security

- The state file is stored locally on your computer only
- File paths are hashed for privacy
- No personal data is transmitted or stored remotely
- The state file can be deleted at any time without affecting your actual files

## Troubleshooting

### State File Corruption
If the state file becomes corrupted:
1. Use "Clear All State" from the menu, or
2. Delete `~/desktop_cleaner_state.json` manually, or
3. Use `python state_manager.py clear all`

### Missing Items
If items aren't showing up:
1. Check if they were previously handled
2. Use "Show Summary" to see your statistics
3. Consider using "Clear Handled Items" to reset

### Performance
The state file is designed to be lightweight and fast, but with thousands of handled items, you might notice slight startup delays. Consider clearing old state data periodically.
