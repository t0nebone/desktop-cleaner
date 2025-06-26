import os
import json
from pathlib import Path
from typing import List, Optional
from persistence_manager import PersistenceManager


class DesktopItemIterator:
    """
    Iterator for desktop items that scans ~/Desktop once on initialization,
    filters out invisible/system files, and provides navigation methods.
    """
    
    def __init__(self):
        """Initialize the iterator by scanning the Desktop directory."""
        self.desktop_path = Path.home() / "Desktop"
        self.items: List[str] = []
        self.current_index: int = 0
        self.persistence_manager = PersistenceManager()
        self.load_state()  # Load previously saved state
        self._scan_desktop()
    
    def _scan_desktop(self) -> None:
        """
        Scan the Desktop directory and filter out invisible/system files.
        Filters out: .DS_Store, .localized, and all dotfiles (files starting with .)
        """
        if not self.desktop_path.exists():
            return
        
        try:
            # If we're doing a fresh scan (not loading from state), start with empty list
            if not hasattr(self, '_state_loaded_from_file') or not self._state_loaded_from_file:
                fresh_items = []
            else:
                # If state was loaded from file, don't rescan - just return
                return
            
            for item in self.desktop_path.iterdir():
                # Skip invisible/system files
                if self._should_skip_file(item.name):
                    continue
                
                # Store absolute path
                fresh_items.append(str(item.absolute()))
            
            # Sort items for consistent ordering
            fresh_items.sort()
            
            # Filter out already handled items for fresh scans
            self.items = self.persistence_manager.filter_unhandled_items(fresh_items)
            
        except PermissionError:
            print(f"Permission denied accessing {self.desktop_path}")
        except Exception as e:
            print(f"Error scanning desktop: {e}")
    
    def save_state(self) -> None:
        """Save the current state to a JSON file for persistence."""
        state_path = Path.home() / "desktop_cleaner_state.json"
        state_data = {
            "items": self.items,
            "current_index": self.current_index
        }
        with open(state_path, 'w') as f:
            json.dump(state_data, f)
    
    def load_state(self) -> None:
        """Load the iterator state from persistence manager."""
        items, current_index = self.persistence_manager.load_iterator_state()
        if items:
            # Filter out items that no longer exist
            existing_items = [item for item in items if Path(item).exists()]
            self.items = existing_items
            
            # Ensure index is valid: clamp between 0 and len-1, default to 0 if empty
            if existing_items:
                self.current_index = max(0, min(current_index, len(existing_items) - 1))
            else:
                self.current_index = 0
            
            self._state_loaded_from_file = True
        else:
            self.items = []
            self.current_index = 0
            self._state_loaded_from_file = False
    
    def _should_skip_file(self, filename: str) -> bool:
        """
        Determine if a file should be skipped based on filtering rules.
        
        Args:
            filename: The name of the file to check
            
        Returns:
            True if the file should be skipped, False otherwise
        """
        # Skip dotfiles (files starting with .)
        if filename.startswith('.'):
            return True
        
        # Skip specific system files
        system_files = {'.DS_Store', '.localized'}
        if filename in system_files:
            return True
        
        return False
    
    def next(self) -> Optional[str]:
        """
        Move to the next item and return its path.
        
        Returns:
            The absolute path of the next item, or None if at the end
        """
        if not self.items:
            return None
        
        # Ensure current index is valid before proceeding
        self._ensure_valid_index()
        
        if self.current_index < len(self.items) - 1:
            self.current_index += 1
            return self.items[self.current_index]
        
        return None
    
    def prev(self) -> Optional[str]:
        """
        Move to the previous item and return its path.
        
        Returns:
            The absolute path of the previous item, or None if at the beginning
        """
        if not self.items:
            return None
        
        # Ensure current index is valid before proceeding
        self._ensure_valid_index()
        
        if self.current_index > 0:
            self.current_index -= 1
            return self.items[self.current_index]
        
        return None
    
    def current(self) -> Optional[str]:
        """
        Get the current item without moving the index.
        
        Returns:
            The absolute path of the current item, or None if no items
        """
        if not self.items or self.current_index < 0 or self.current_index >= len(self.items):
            return None
        
        return self.items[self.current_index]
    
    def reset(self) -> None:
        """Reset the iterator to the first item."""
        self.current_index = 0
    
    def get_item_count(self) -> int:
        """Get the total number of items."""
        return len(self.items)
    
    def get_current_index(self) -> int:
        """Get the current index position."""
        return self.current_index
    
    def is_at_start(self) -> bool:
        """Check if iterator is at the first item."""
        return self.current_index == 0
    
    def is_at_end(self) -> bool:
        """Check if iterator is at the last item."""
        return self.current_index >= len(self.items) - 1 if self.items else True
    
    def __str__(self) -> str:
        """String representation of the iterator state."""
        if not self.items:
            return "DesktopItemIterator: No items found"
        
        current_item = Path(self.current()).name if self.current() else "None"
        return f"DesktopItemIterator: {self.current_index + 1}/{len(self.items)} - {current_item}"
    
    def __repr__(self) -> str:
        """Detailed representation of the iterator."""
        return f"DesktopItemIterator(items={len(self.items)}, index={self.current_index})"
    
    def current_item_path(self) -> Optional[str]:
        """Get the path of the current item for actions."""
        return self.current()
    
    def _ensure_valid_index(self) -> None:
        """
        Ensure the current_index is within valid bounds.
        This should be called after any operation that might invalidate the index.
        """
        if not self.items:
            self.current_index = 0
        elif self.current_index < 0:
            self.current_index = 0
        elif self.current_index >= len(self.items):
            self.current_index = len(self.items) - 1
