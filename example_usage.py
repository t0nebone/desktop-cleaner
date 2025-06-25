#!/usr/bin/env python3
"""
Example usage of the DesktopItemIterator class.
Shows how to integrate it into a desktop management application.
"""

from desktop_item_iterator import DesktopItemIterator
from pathlib import Path


def simple_desktop_browser():
    """
    Simple example showing how to use the DesktopItemIterator
    for browsing desktop items.
    """
    print("Desktop Item Browser")
    print("===================")
    
    # Initialize the iterator
    iterator = DesktopItemIterator()
    
    if iterator.get_item_count() == 0:
        print("No items found on desktop.")
        return
    
    print(f"Found {iterator.get_item_count()} items on desktop.")
    print("Commands: (n)ext, (p)revious, (c)urrent, (r)eset, (q)uit")
    print()
    
    # Show initial item
    current = iterator.current()
    if current:
        print(f"Current: {Path(current).name}")
        print(f"Path: {current}")
        print(f"Position: {iterator.get_current_index() + 1}/{iterator.get_item_count()}")
    
    # Simple interactive loop
    while True:
        command = input("\nEnter command: ").lower().strip()
        
        if command in ['q', 'quit']:
            break
        elif command in ['n', 'next']:
            next_item = iterator.next()
            if next_item:
                print(f"Next: {Path(next_item).name}")
                print(f"Position: {iterator.get_current_index() + 1}/{iterator.get_item_count()}")
            else:
                print("Already at the last item.")
        elif command in ['p', 'prev', 'previous']:
            prev_item = iterator.prev()
            if prev_item:
                print(f"Previous: {Path(prev_item).name}")
                print(f"Position: {iterator.get_current_index() + 1}/{iterator.get_item_count()}")
            else:
                print("Already at the first item.")
        elif command in ['c', 'current']:
            current = iterator.current()
            if current:
                print(f"Current: {Path(current).name}")
                print(f"Path: {current}")
                print(f"Position: {iterator.get_current_index() + 1}/{iterator.get_item_count()}")
        elif command in ['r', 'reset']:
            iterator.reset()
            current = iterator.current()
            if current:
                print(f"Reset to first item: {Path(current).name}")
                print(f"Position: {iterator.get_current_index() + 1}/{iterator.get_item_count()}")
        else:
            print("Unknown command. Use: (n)ext, (p)revious, (c)urrent, (r)reset, (q)uit")


def batch_processing_example():
    """
    Example showing how to process all desktop items in a batch.
    """
    print("\nBatch Processing Example")
    print("========================")
    
    iterator = DesktopItemIterator()
    
    if iterator.get_item_count() == 0:
        print("No items to process.")
        return
    
    # Process each item
    file_types = {}
    total_size = 0
    
    # Reset to start
    iterator.reset()
    
    for i in range(iterator.get_item_count()):
        current_path = iterator.current()
        if current_path:
            path_obj = Path(current_path)
            
            # Count file types
            if path_obj.is_file():
                suffix = path_obj.suffix.lower() or 'no_extension'
                file_types[suffix] = file_types.get(suffix, 0) + 1
                
                # Get file size
                try:
                    total_size += path_obj.stat().st_size
                except OSError:
                    pass  # Skip files we can't access
            else:
                file_types['directory'] = file_types.get('directory', 0) + 1
        
        # Move to next item (except for the last one)
        if i < iterator.get_item_count() - 1:
            iterator.next()
    
    # Report results
    print(f"Processed {iterator.get_item_count()} items")
    print(f"Total size: {total_size / (1024*1024):.2f} MB")
    print("\nFile type breakdown:")
    for file_type, count in sorted(file_types.items()):
        print(f"  {file_type}: {count}")


if __name__ == "__main__":
    # Run the simple browser
    simple_desktop_browser()
    
    # Run batch processing example
    batch_processing_example()
