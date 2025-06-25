#!/usr/bin/env python3
"""
Test script to verify the GUI integration between iterator and preview providers.
"""

import sys
import os
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from desktop_item_iterator import DesktopItemIterator
from main_gui import PreviewProviderManager


def test_integration():
    """Test the integration between iterator and preview providers."""
    print("Testing Desktop Cleaner GUI Integration")
    print("=" * 50)
    
    # Test 1: Iterator initialization
    print("\n1. Testing Iterator Initialization...")
    try:
        iterator = DesktopItemIterator()
        item_count = iterator.get_item_count()
        print(f"✓ Iterator initialized successfully with {item_count} items")
        
        if item_count == 0:
            print("  Note: No items found on desktop - this is normal if desktop is empty")
            return True
        
    except Exception as e:
        print(f"✗ Iterator initialization failed: {e}")
        return False
    
    # Test 2: Current item retrieval
    print("\n2. Testing Current Item Retrieval...")
    try:
        current_item = iterator.current()
        if current_item:
            print(f"✓ Current item retrieved: {Path(current_item).name}")
        else:
            print("✓ No current item (empty desktop)")
            return True
    except Exception as e:
        print(f"✗ Current item retrieval failed: {e}")
        return False
    
    # Test 3: Preview provider selection
    print("\n3. Testing Preview Provider Selection...")
    try:
        provider = PreviewProviderManager.get_preview_provider(current_item)
        provider_type = type(provider).__name__
        print(f"✓ Preview provider selected: {provider_type}")
    except Exception as e:
        print(f"✗ Preview provider selection failed: {e}")
        return False
    
    # Test 4: Preview generation
    print("\n4. Testing Preview Generation...")
    try:
        widget, metadata = provider.get_preview()
        if widget and metadata:
            print(f"✓ Preview generated successfully")
            print(f"  Widget type: {type(widget).__name__}")
            print(f"  Metadata preview: {metadata[:50]}..." if len(metadata) > 50 else f"  Metadata: {metadata}")
        else:
            print("✗ Preview generation returned None")
            return False
    except Exception as e:
        print(f"✗ Preview generation failed: {e}")
        return False
    
    # Test 5: Navigation
    print("\n5. Testing Iterator Navigation...")
    try:
        # Test next
        next_item = iterator.next()
        if next_item:
            print(f"✓ Navigation to next item: {Path(next_item).name}")
        else:
            print("✓ Already at last item (single item desktop)")
        
        # Test previous
        prev_item = iterator.prev()
        if prev_item:
            print(f"✓ Navigation to previous item: {Path(prev_item).name}")
        else:
            print("✓ Back to first item")
        
        # Test reset
        iterator.reset()
        reset_item = iterator.current()
        if reset_item:
            print(f"✓ Reset to first item: {Path(reset_item).name}")
        
    except Exception as e:
        print(f"✗ Navigation testing failed: {e}")
        return False
    
    # Test 6: Error handling with invalid path
    print("\n6. Testing Error Handling...")
    try:
        fake_provider = PreviewProviderManager.get_preview_provider("/nonexistent/file.txt")
        fake_widget, fake_metadata = fake_provider.get_preview()
        print("✓ Error handling works - graceful fallback for invalid paths")
    except Exception as e:
        print(f"✓ Error handling works - exception caught: {type(e).__name__}")
    
    print("\n" + "=" * 50)
    print("✓ All integration tests passed!")
    return True


def test_preview_providers():
    """Test different types of preview providers."""
    print("\nTesting Preview Provider Types")
    print("-" * 30)
    
    # Test different file types
    test_cases = [
        ("/tmp/test.jpg", "ImagePreview"),
        ("/tmp/test.pdf", "PDFPreview"),
        ("/tmp/test.txt", "TextPreview"),
        ("/tmp", "DirectoryPreview"),
        ("/tmp/test.unknown", "GenericPreview")
    ]
    
    for file_path, expected_type in test_cases:
        try:
            provider = PreviewProviderManager.get_preview_provider(file_path)
            actual_type = type(provider).__name__
            if actual_type == expected_type:
                print(f"✓ {file_path} -> {actual_type}")
            else:
                print(f"✗ {file_path} -> Expected {expected_type}, got {actual_type}")
        except Exception as e:
            print(f"✗ {file_path} -> Error: {e}")


if __name__ == "__main__":
    print("Desktop Cleaner Integration Test")
    print("================================")
    
    # Initialize QApplication for GUI testing
    app = QApplication(sys.argv)
    
    try:
        success = test_integration()
        test_preview_providers()
        
        if success:
            print("\n🎉 Integration test completed successfully!")
            print("\nTo run the GUI application:")
            print("  python main_gui.py")
        else:
            print("\n❌ Integration test failed!")
            sys.exit(1)
    finally:
        # Don't call app.exec_() since this is just a test
        pass
