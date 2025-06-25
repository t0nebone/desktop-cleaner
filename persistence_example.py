#!/usr/bin/env python3
"""
Example demonstrating the persistence functionality of Desktop Cleaner.
This script shows how the state is saved and restored across sessions.
"""

from persistence_manager import PersistenceManager
from desktop_item_iterator import DesktopItemIterator
import time
from pathlib import Path

def demonstrate_persistence():
    """Demonstrate the persistence feature."""
    print("=== Desktop Cleaner Persistence Demo ===\n")
    
    # Initialize persistence manager
    pm = PersistenceManager()
    
    print("1. Initial state:")
    summary = pm.get_handled_items_summary()
    print(f"   Items handled: {sum(summary.values())}")
    print(f"   Sessions: {pm.get_session_count()}")
    print()
    
    # Simulate handling some items
    print("2. Simulating user actions...")
    test_files = [
        ("/Users/test/Desktop/document.pdf", "moved", "/Users/test/Documents"),
        ("/Users/test/Desktop/photo.jpg", "left", None),
        ("/Users/test/Desktop/temp.txt", "trashed", None)
    ]
    
    for file_path, action, destination in test_files:
        pm.mark_item_handled(file_path, action, destination)
        print(f"   Handled: {Path(file_path).name} -> {action}")
        time.sleep(0.1)  # Small delay to show different timestamps
    
    print()
    
    # Show updated state
    print("3. Updated state:")
    summary = pm.get_handled_items_summary()
    print(f"   Items left: {summary['left']}")
    print(f"   Items moved: {summary['moved']}")
    print(f"   Items trashed: {summary['trashed']}")
    print(f"   Total handled: {sum(summary.values())}")
    print()
    
    # Show individual items
    print("4. Detailed item list:")
    items = pm.get_handled_items_list()
    for item in items:
        print(f"   {item['filename']}: {item['action']}")
        if item.get('destination'):
            print(f"      -> moved to: {item['destination']}")
        print(f"      -> timestamp: {item['timestamp']}")
    print()
    
    # Demonstrate filtering
    print("5. Filtering demonstration:")
    all_items = [item['original_path'] for item in items]
    all_items.append("/Users/test/Desktop/new_file.txt")  # Add a new item
    
    print(f"   All items: {len(all_items)}")
    unhandled = pm.filter_unhandled_items(all_items)
    print(f"   Unhandled items: {len(unhandled)}")
    print(f"   Unhandled: {[Path(p).name for p in unhandled]}")
    print()
    
    # Demonstrate iterator state saving
    print("6. Iterator state demo:")
    pm.save_iterator_state(all_items, 2)
    loaded_items, loaded_index = pm.load_iterator_state()
    print(f"   Saved {len(all_items)} items at index {2}")
    print(f"   Loaded {len(loaded_items)} items at index {loaded_index}")
    print()
    
    # Show export capability
    print("7. Export/Import demo:")
    export_path = "demo_backup.json"
    if pm.export_state(export_path):
        print(f"   State exported to: {export_path}")
        
        # Clear and import to demonstrate
        pm.clear_state()
        print("   State cleared")
        
        if pm.import_state(export_path):
            print("   State imported successfully")
            summary = pm.get_handled_items_summary()
            print(f"   Items after import: {sum(summary.values())}")
        
        # Clean up
        Path(export_path).unlink()
        print("   Cleanup completed")
    print()
    
    # Final cleanup
    print("8. Cleaning up demo data...")
    pm.clear_state()
    print("   Demo completed!\n")
    
    print("=== Summary ===")
    print("The persistence system provides:")
    print("• Automatic state saving after each action")
    print("• Resume capability across sessions")
    print("• Hash-based item tracking for privacy")
    print("• Export/import for backup and transfer")
    print("• CLI tools for advanced management")
    print("\nUse 'python state_manager.py --help' for CLI options")

if __name__ == "__main__":
    demonstrate_persistence()
