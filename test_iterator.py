#!/usr/bin/env python3
"""
Test script for DesktopItemIterator class.
Demonstrates the functionality and verifies it works correctly.
"""

from desktop_item_iterator import DesktopItemIterator
from pathlib import Path


def test_desktop_iterator():
    """Test the DesktopItemIterator functionality."""
    print("Testing DesktopItemIterator...")
    print("=" * 50)
    
    # Initialize the iterator
    iterator = DesktopItemIterator()
    
    # Display basic info
    print(f"Total items found: {iterator.get_item_count()}")
    print(f"Current iterator state: {iterator}")
    print()
    
    # Show current item
    current = iterator.current()
    if current:
        print(f"Current item: {Path(current).name}")
        print(f"Full path: {current}")
    else:
        print("No items found")
        return
    
    print()
    print("Navigation test:")
    print("-" * 30)
    
    # Test navigation through first few items
    for i in range(min(5, iterator.get_item_count())):
        current = iterator.current()
        if current:
            print(f"Item {i+1}: {Path(current).name}")
        
        # Move to next item
        next_item = iterator.next()
        if not next_item:
            print("Reached end of items")
            break
    
    print()
    print("Backward navigation test:")
    print("-" * 30)
    
    # Test backward navigation
    for i in range(3):
        prev_item = iterator.prev()
        if prev_item:
            print(f"Previous item: {Path(prev_item).name}")
        else:
            print("At beginning of items")
            break
    
    print()
    print("Iterator state info:")
    print("-" * 30)
    print(f"Current index: {iterator.get_current_index()}")
    print(f"At start: {iterator.is_at_start()}")
    print(f"At end: {iterator.is_at_end()}")
    
    # Reset and show first item again
    iterator.reset()
    print(f"After reset - Current item: {Path(iterator.current()).name if iterator.current() else 'None'}")
    
    print()
    print("All items found (filtered):")
    print("-" * 30)
    iterator.reset()
    for i in range(iterator.get_item_count()):
        current = iterator.current()
        if current:
            print(f"{i+1:2d}. {Path(current).name}")
        if i < iterator.get_item_count() - 1:
            iterator.next()


if __name__ == "__main__":
    test_desktop_iterator()
