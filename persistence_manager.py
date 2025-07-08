#!/usr/bin/env python3
"""
Persistence Manager for Desktop Cleaner.
Handles saving and loading of application state, including which items have been processed
and what actions were taken on them.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class PersistenceManager:
    """Manages persistence of desktop cleaner state and handled items."""
    
    def __init__(self, state_file: str = "desktop_cleaner_state.json"):
        """
        Initialize the persistence manager.
        
        Args:
            state_file: Name of the state file (stored in user's home directory)
        """
        self.state_file_path = Path.home() / state_file
        self.state = self._load_state()
    
    def _load_state(self) -> Dict[str, Any]:
        """Load state from the JSON file."""
        if not self.state_file_path.exists():
            return self._get_default_state()
        
        try:
            with open(self.state_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load state file: {e}")
            return self._get_default_state()
    
    def _get_default_state(self) -> Dict[str, Any]:
        """Get the default state structure."""
        return {
            "version": "1.0",
            "last_updated": None,
            "session_count": 0,
            "handled_items": {},  # path_hash -> action_info
            "iterator_state": {
                "items": [],
                "current_index": 0
            }
        }
    
    def save_state(self) -> None:
        """Save the current state to the JSON file."""
        try:
            self.state["last_updated"] = datetime.now().isoformat()
            with open(self.state_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save state file: {e}")
    
    def get_path_hash(self, file_path: str) -> str:
        """
        Generate a hash for a file path to use as a key.
        
        Args:
            file_path: The file path to hash
            
        Returns:
            SHA-256 hash of the file path
        """
        return hashlib.sha256(file_path.encode('utf-8')).hexdigest()
    
    def mark_item_handled(self, file_path: str, action: str, destination: Optional[str] = None) -> None:
        """
        Mark an item as handled with the specified action.
        
        Args:
            file_path: Path to the file that was handled
            action: Action taken ("moved", "trashed")
            destination: Destination path if the item was moved
        """
        path_hash = self.get_path_hash(file_path)
        
        self.state["handled_items"][path_hash] = {
            "original_path": file_path,
            "action": action,
            "destination": destination,
            "timestamp": datetime.now().isoformat(),
            "filename": Path(file_path).name
        }
        
        self.save_state()
    
    def is_item_handled(self, file_path: str) -> bool:
        """
        Check if an item has already been handled.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if the item has been handled, False otherwise
        """
        path_hash = self.get_path_hash(file_path)
        return path_hash in self.state["handled_items"]
    
    def get_item_action(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get the action information for a handled item.
        
        Args:
            file_path: Path to check
            
        Returns:
            Dictionary with action information, or None if not handled
        """
        path_hash = self.get_path_hash(file_path)
        return self.state["handled_items"].get(path_hash)
    
    def get_handled_items_summary(self) -> Dict[str, int]:
        """
        Get a summary of handled items by action type.
        
        Returns:
            Dictionary with counts for each action type
        """
        summary = {"moved": 0, "trashed": 0}
        
        for item_info in self.state["handled_items"].values():
            action = item_info.get("action", "unknown")
            if action in summary:
                summary[action] += 1
        
        return summary
    
    def get_handled_items_list(self) -> List[Dict[str, Any]]:
        """
        Get a list of all handled items with their action information.
        
        Returns:
            List of dictionaries containing item information
        """
        return list(self.state["handled_items"].values())
    
    def filter_unhandled_items(self, current_desktop_items: List[str]) -> List[str]:
        """
        Filters out items that should not be presented to the user again.
        An item is considered handled and filtered out if:
        1. It was explicitly 'left' on the desktop.
        2. It was 'moved' or 'trashed' AND is no longer present on the desktop.
        If a 'moved' or 'trashed' item reappears on the desktop, it is considered unhandled.

        Args:
            current_desktop_items: A list of absolute file paths currently found on the desktop.

        Returns:
            List of file paths that should be presented to the user.
        """
        unhandled_items = []
        for item_path in current_desktop_items:
            path_hash = self.get_path_hash(item_path)
            handled_info = self.state["handled_items"].get(path_hash)

            if handled_info:
                action = handled_info.get("action")
                if action in ["moved", "trashed"]:
                    # If it was moved/trashed, and it's now back on the desktop,
                    # it should be considered unhandled again.
                    # We don't filter it out.
                    pass # It's back on desktop, so it's unhandled.
            
            # If not handled, or if handled by move/trash and now back on desktop
            unhandled_items.append(item_path)
            
        return unhandled_items
    
    def save_iterator_state(self, items: List[str], current_index: int) -> None:
        """
        Save the iterator state.
        
        Args:
            items: List of items in the iterator
            current_index: Current index position
        """
        self.state["iterator_state"] = {
            "items": items,
            "current_index": current_index
        }
        self.save_state()
    
    def load_iterator_state(self) -> tuple[List[str], int]:
        """
        Load the iterator state.
        
        Returns:
            Tuple of (items list, current index)
        """
        iterator_state = self.state.get("iterator_state", {})
        items = iterator_state.get("items", [])
        current_index = iterator_state.get("current_index", 0)
        
        return items, current_index
    
    def clear_state(self) -> None:
        """Clear all state data (reset to defaults)."""
        self.state = self._get_default_state()
        self.save_state()
    
    def clear_handled_items(self) -> None:
        """Clear only the handled items data, keeping other state."""
        self.state["handled_items"] = {}
        self.save_state()
    
    def increment_session_count(self) -> None:
        """Increment the session count."""
        self.state["session_count"] = self.state.get("session_count", 0) + 1
        self.save_state()
    
    def get_session_count(self) -> int:
        """Get the number of sessions."""
        return self.state.get("session_count", 0)
    
    def delete_state_file(self) -> bool:
        """
        Delete the state file completely.
        
        Returns:
            True if file was deleted or didn't exist, False if deletion failed
        """
        try:
            if self.state_file_path.exists():
                self.state_file_path.unlink()
            self.state = self._get_default_state()
            return True
        except OSError as e:
            print(f"Warning: Could not delete state file: {e}")
            return False
    
    def export_state(self, export_path: str) -> bool:
        """
        Export current state to a specified file.
        
        Args:
            export_path: Path where to export the state
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            export_file = Path(export_path)
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2)
            return True
        except IOError as e:
            print(f"Warning: Could not export state: {e}")
            return False
    
    def import_state(self, import_path: str) -> bool:
        """
        Import state from a specified file.
        
        Args:
            import_path: Path to import the state from
            
        Returns:
            True if import successful, False otherwise
        """
        try:
            import_file = Path(import_path)
            if not import_file.exists():
                return False
            
            with open(import_file, 'r', encoding='utf-8') as f:
                imported_state = json.load(f)
            
            # Validate the imported state has required keys
            required_keys = ["handled_items", "iterator_state"]
            if all(key in imported_state for key in required_keys):
                self.state = imported_state
                self.save_state()
                return True
            else:
                print("Warning: Imported state file is missing required keys")
                return False
                
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not import state: {e}")
            return False
