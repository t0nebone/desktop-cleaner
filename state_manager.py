#!/usr/bin/env python3
"""
CLI utility for managing Desktop Cleaner persistence state.
Allows users to view, clear, export, and import their state data.
"""

import argparse
import json
import sys
from pathlib import Path
from persistence_manager import PersistenceManager


def print_summary(persistence_manager: PersistenceManager):
    """Print a summary of the current state."""
    summary = persistence_manager.get_handled_items_summary()
    session_count = persistence_manager.get_session_count()
    
    print("=== Desktop Cleaner State Summary ===")
    print(f"Sessions run: {session_count}")
    print(f"Items left on desktop: {summary['left']}")
    print(f"Items moved to folders: {summary['moved']}")
    print(f"Items moved to trash: {summary['trashed']}")
    print(f"Total items handled: {sum(summary.values())}")
    print()
    
    # Show iterator state
    items, current_index = persistence_manager.load_iterator_state()
    if items:
        print(f"Iterator state: {current_index + 1}/{len(items)} items")
        print(f"Current item: {Path(items[current_index]).name if current_index < len(items) else 'N/A'}")
    else:
        print("No iterator state saved")


def print_detailed_items(persistence_manager: PersistenceManager):
    """Print detailed information about all handled items."""
    items = persistence_manager.get_handled_items_list()
    
    if not items:
        print("No items have been handled yet.")
        return
    
    print("=== Handled Items Details ===")
    
    # Sort by timestamp
    items.sort(key=lambda x: x.get('timestamp', ''))
    
    for item in items:
        print(f"File: {item.get('filename', 'Unknown')}")
        print(f"  Action: {item.get('action', 'Unknown')}")
        print(f"  Original path: {item.get('original_path', 'Unknown')}")
        if item.get('destination'):
            print(f"  Moved to: {item.get('destination')}")
        print(f"  Timestamp: {item.get('timestamp', 'Unknown')}")
        print()


def clear_state(persistence_manager: PersistenceManager, what: str):
    """Clear specific parts of the state."""
    if what == "all":
        persistence_manager.clear_state()
        print("All state data cleared.")
    elif what == "handled":
        persistence_manager.clear_handled_items()
        print("Handled items data cleared.")
    elif what == "iterator":
        persistence_manager.save_iterator_state([], 0)
        print("Iterator state cleared.")
    else:
        print(f"Unknown clear target: {what}")
        print("Valid options: all, handled, iterator")


def export_state(persistence_manager: PersistenceManager, export_path: str):
    """Export state to a file."""
    if persistence_manager.export_state(export_path):
        print(f"State exported to: {export_path}")
    else:
        print("Failed to export state.")


def import_state(persistence_manager: PersistenceManager, import_path: str):
    """Import state from a file."""
    if persistence_manager.import_state(import_path):
        print(f"State imported from: {import_path}")
    else:
        print("Failed to import state.")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Manage Desktop Cleaner persistence state",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python state_manager.py summary              # Show state summary
  python state_manager.py list                # List all handled items
  python state_manager.py clear all           # Clear all state data
  python state_manager.py clear handled       # Clear only handled items
  python state_manager.py export backup.json  # Export state to file
  python state_manager.py import backup.json  # Import state from file
        """
    )
    
    parser.add_argument(
        'command',
        choices=['summary', 'list', 'clear', 'export', 'import'],
        help='Action to perform'
    )
    
    parser.add_argument(
        'target',
        nargs='?',
        help='Target for the command (required for clear, export, import)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.command in ['clear', 'export', 'import'] and not args.target:
        print(f"Error: {args.command} command requires a target argument")
        parser.print_help()
        sys.exit(1)
    
    # Initialize persistence manager
    try:
        persistence_manager = PersistenceManager()
    except Exception as e:
        print(f"Error initializing persistence manager: {e}")
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == 'summary':
            print_summary(persistence_manager)
        
        elif args.command == 'list':
            print_detailed_items(persistence_manager)
        
        elif args.command == 'clear':
            clear_state(persistence_manager, args.target)
        
        elif args.command == 'export':
            export_state(persistence_manager, args.target)
        
        elif args.command == 'import':
            import_state(persistence_manager, args.target)
    
    except Exception as e:
        print(f"Error executing command: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
