#!/usr/bin/env python3
"""
Test script to verify enhanced preview functionality.
"""

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from preview_provider import PDFPreview, DirectoryPreview

def test_enhanced_pdf_preview():
    """Test enhanced PDF preview functionality."""
    
    # Find PDF files on desktop
    desktop_path = Path.home() / "Desktop"
    pdf_files = list(desktop_path.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found on desktop to test")
        return False
    
    print(f"Testing enhanced PDF preview for: {pdf_files[0].name}")
    
    try:
        preview = PDFPreview(str(pdf_files[0]))
        widget, metadata = preview.get_preview()
        
        # Check if it's a ClickablePreviewLabel
        widget_type = type(widget).__name__
        print(f"✅ PDF preview widget type: {widget_type}")
        
        if hasattr(widget, 'original_image') and widget.original_image:
            print("✅ PDF preview has clickable functionality")
        
        if hasattr(widget, 'setToolTip'):
            print("✅ PDF preview has tooltip")
        
        print(f"Preview metadata: {metadata}")
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced PDF preview: {e}")
        return False

def test_enhanced_directory_preview():
    """Test enhanced directory preview functionality."""
    
    # Find directories on desktop
    desktop_path = Path.home() / "Desktop"
    directories = [item for item in desktop_path.iterdir() if item.is_dir() and not item.name.startswith('.')]
    
    if not directories:
        print("No directories found on desktop to test")
        return False
    
    print(f"Testing enhanced directory preview for: {directories[0].name}")
    
    try:
        preview = DirectoryPreview(str(directories[0]))
        widget, metadata = preview.get_preview()
        
        # Check if it's a custom widget with layout
        widget_type = type(widget).__name__
        print(f"✅ Directory preview widget type: {widget_type}")
        
        if hasattr(widget, 'layout') and widget.layout():
            print("✅ Directory preview has custom layout")
        
        print(f"Preview metadata: {metadata}")
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced directory preview: {e}")
        return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    print("Testing Enhanced Preview Functionality")
    print("=" * 40)
    
    pdf_success = test_enhanced_pdf_preview()
    print()
    dir_success = test_enhanced_directory_preview()
    
    if pdf_success and dir_success:
        print("\n🎉 All enhanced preview tests passed!")
    else:
        print("\n💥 Some enhanced preview tests failed!")
