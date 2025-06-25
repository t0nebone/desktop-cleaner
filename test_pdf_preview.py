#!/usr/bin/env python3
"""
Test script to verify PDF preview functionality is working correctly.
"""

import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from preview_provider import PDFPreview

def test_pdf_preview():
    """Test PDF preview functionality."""
    
    # Find PDF files on desktop
    desktop_path = Path.home() / "Desktop"
    pdf_files = list(desktop_path.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found on desktop to test")
        return False
    
    print(f"Found {len(pdf_files)} PDF file(s) on desktop:")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file.name}")
    
    # Test the first PDF file
    test_pdf = pdf_files[0]
    print(f"\nTesting PDF preview for: {test_pdf.name}")
    
    try:
        preview = PDFPreview(str(test_pdf))
        widget, metadata = preview.get_preview()
        
        print("✅ PDF preview created successfully!")
        print(f"Metadata: {metadata}")
        
        # Check if it's a proper preview widget (not an error message)
        if hasattr(widget, 'pixmap') and widget.pixmap() is not None:
            print("✅ PDF preview has valid pixmap (image generated)")
            return True
        else:
            print("❌ PDF preview widget doesn't have valid pixmap")
            return False
            
    except Exception as e:
        print(f"❌ Error testing PDF preview: {e}")
        return False

def test_pymupdf_import():
    """Test if PyMuPDF is properly installed."""
    try:
        import fitz
        print("✅ PyMuPDF (fitz) imported successfully")
        print(f"PyMuPDF version: {fitz.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import PyMuPDF: {e}")
        return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    print("Testing PDF Preview Functionality")
    print("=" * 40)
    
    # Test PyMuPDF import
    if not test_pymupdf_import():
        sys.exit(1)
    
    print()
    
    # Test PDF preview
    if test_pdf_preview():
        print("\n🎉 PDF preview test passed!")
    else:
        print("\n💥 PDF preview test failed!")
        sys.exit(1)
