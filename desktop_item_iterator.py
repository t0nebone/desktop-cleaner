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
        self.persistence_manager = PersistenceManager()
        
        # Scan the desktop for the current list of unhandled items
        self.items: List[str] = self._scan_and_filter_desktop()
        
        # Always start at the beginning of the list
        self.current_index: int = 0

    def _scan_and_filter_desktop(self) -> List[str]:
        """
        Scan the Desktop directory, filter out unwanted files, and then
        filter out items that have already been handled.
        """
        if not self.desktop_path.exists():
            return []
        
        try:
            # Scan all items on the desktop
            fresh_items = [
                str(item.absolute())
                for item in self.desktop_path.iterdir()
                if not self._should_skip_file(item.name)
            ]
            
            # Sort for consistent order
            fresh_items.sort()
            
            # Filter out items that have already been handled
            return self.persistence_manager.filter_unhandled_items(fresh_items)
            
        except PermissionError:
            print(f"Permission denied accessing {self.desktop_path}")
            return []
        except Exception as e:
            print(f"Error scanning desktop: {e}")
            return []

    def _determine_starting_index(self, saved_items: List[str], saved_index: int) -> int:
        """
        Determines the starting index for the new session.
        It tries to find the last viewed item from the previous session in the new list of items.
        """
        # Check if there was a valid saved state
        if not saved_items or not (0 <= saved_index < len(saved_items)):
            return 0  # No valid saved state, start from the beginning

        # Get the path of the item from the last session
        last_viewed_item_path = saved_items[saved_index]

        # Try to find that same item in the newly scanned list
        try:
            new_index = self.items.index(last_viewed_item_path)
            return new_index
        except ValueError:
            # The last viewed item is no longer in the list (e.g., deleted, or handled)
            return 0
    
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
