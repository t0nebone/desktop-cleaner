from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFileIconProvider, QDialog, QScrollArea, QPushButton, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont, QIcon, QCursor
from PyQt5.QtCore import QFileInfo, Qt, pyqtSignal
import os
from pathlib import Path
from datetime import datetime


class ClickablePreviewLabel(QLabel):
    """A clickable label that shows a larger preview when clicked."""
    clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.original_image = None
        self.file_path = None
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.original_image:
            self.show_large_preview()
        super().mousePressEvent(event)
    
    def show_large_preview(self):
        """Show a larger preview in a dialog window."""
        if not self.original_image:
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Large Preview - {os.path.basename(self.file_path)}")
        dialog.setModal(True)
        dialog.resize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Scroll area for the large image
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setAlignment(Qt.AlignCenter)
        
        # Create label with larger image
        large_label = QLabel()
        large_label.setPixmap(self.original_image.scaled(600, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        large_label.setAlignment(Qt.AlignCenter)
        scroll_area.setWidget(large_label)
        
        layout.addWidget(scroll_area)
        
        # Close button
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.close)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        dialog.exec_()

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

class ImagePreview:
    def __init__(self, file_path):
        self.file_path = file_path

    def get_preview(self):
        try:
            pixmap = QPixmap(self.file_path)
            if pixmap.isNull():
                widget = QLabel("Image preview not available")
                widget.setAlignment(Qt.AlignCenter)
                return widget, "Failed to load image"
            
            scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            widget = QLabel()
            widget.setPixmap(scaled_pixmap)
            widget.setAlignment(Qt.AlignCenter)
            
            # Get image metadata
            file_info = Path(self.file_path).stat()
            size_mb = file_info.st_size / (1024 * 1024)
            modified = datetime.fromtimestamp(file_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            metadata = f"Image: {pixmap.width()}x{pixmap.height()}\nSize: {size_mb:.2f} MB\nModified: {modified}"
            
            return widget, metadata
        except Exception as e:
            widget = QLabel(f"Error loading image: {str(e)}")
            widget.setAlignment(Qt.AlignCenter)
            return widget, f"Error: {str(e)}"

class PDFPreview:
    def __init__(self, file_path):
        self.file_path = file_path

    def get_preview(self):
        if not HAS_PYMUPDF:
            widget = QLabel("PDF preview not available\nPyMuPDF not installed")
            widget.setAlignment(Qt.AlignCenter)
            return widget, "PyMuPDF not installed"
        
        try:
            doc = fitz.open(self.file_path)
            if len(doc) == 0:
                widget = QLabel("PDF is empty")
                widget.setAlignment(Qt.AlignCenter)
                return widget, "Empty PDF file"
            
            page = doc[0]
            pix = page.get_pixmap()
            image = QPixmap()
            image.loadFromData(pix.tobytes())
            
            if image.isNull():
                widget = QLabel("PDF preview not available")
                widget.setAlignment(Qt.AlignCenter)
                return widget, "Failed to render PDF page"
            
            # Create larger preview (doubled size)
            scaled_image = image.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            widget = ClickablePreviewLabel()
            widget.setPixmap(scaled_image)
            widget.setAlignment(Qt.AlignCenter)
            widget.setToolTip("Click to view larger preview")
            widget.setStyleSheet("border: 1px solid #ccc; padding: 5px; background-color: white;")
            
            # Store original image for larger preview
            widget.original_image = image
            widget.file_path = self.file_path
            
            # Get PDF metadata
            file_info = Path(self.file_path).stat()
            size_mb = file_info.st_size / (1024 * 1024)
            modified = datetime.fromtimestamp(file_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            metadata = f"PDF: {len(doc)} pages\nSize: {size_mb:.2f} MB\nModified: {modified}"
            
            doc.close()
            return widget, metadata
            
        except Exception as e:
            widget = QLabel(f"Error loading PDF: {str(e)}")
            widget.setAlignment(Qt.AlignCenter)
            return widget, f"Error: {str(e)}"

class TextPreview:
    def __init__(self, file_path, lines=10):
        self.file_path = file_path
        self.lines = lines

    def get_preview(self):
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            content = None
            encoding_used = None
            
            for encoding in encodings:
                try:
                    with open(self.file_path, 'r', encoding=encoding) as file:
                        lines = file.readlines()[:self.lines]
                        content = ''.join(lines)
                        encoding_used = encoding
                        break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                widget = QLabel("Cannot read text file (encoding issues)")
                widget.setAlignment(Qt.AlignCenter)
                return widget, "Encoding not supported"
            
            # Limit content length for display
            if len(content) > 1000:
                content = content[:1000] + "..."
            
            widget = QLabel(content)
            widget.setFont(QFont("Courier", 9))
            widget.setWordWrap(True)
            widget.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            
            # Get file metadata
            file_info = Path(self.file_path).stat()
            size_kb = file_info.st_size / 1024
            modified = datetime.fromtimestamp(file_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            metadata = f"Text file ({encoding_used})\nSize: {size_kb:.1f} KB\nModified: {modified}"
            
            return widget, metadata
            
        except Exception as e:
            widget = QLabel(f"Error reading file: {str(e)}")
            widget.setAlignment(Qt.AlignCenter)
            return widget, f"Error: {str(e)}"

class DirectoryPreview:
    def __init__(self, dir_path):
        self.dir_path = dir_path

    def get_preview(self):
        try:
            entries = os.listdir(self.dir_path)
            
            # Create a widget with folder icon and file list
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setSpacing(10)
            layout.setContentsMargins(15, 15, 15, 15)
            
            # Add folder icon
            icon_provider = QFileIconProvider()
            file_info_qt = QFileInfo(self.dir_path)
            icon = icon_provider.icon(file_info_qt)
            
            icon_label = QLabel()
            icon_label.setPixmap(icon.pixmap(64, 64))
            icon_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(icon_label)
            
            # Directory name
            dir_name = os.path.basename(self.dir_path) or "Desktop"
            name_label = QLabel(dir_name)
            name_label.setFont(QFont("SF Pro Display", 14, QFont.Bold))
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setStyleSheet("color: #333; margin-bottom: 5px;")
            layout.addWidget(name_label)
            
            if not entries:
                empty_label = QLabel("Empty directory")
                empty_label.setAlignment(Qt.AlignCenter)
                empty_label.setStyleSheet("color: #999; font-style: italic;")
                layout.addWidget(empty_label)
                return widget, "Directory is empty"
            
            # Item count
            count_label = QLabel(f"{len(entries)} items")
            count_label.setFont(QFont("SF Pro Display", 11))
            count_label.setAlignment(Qt.AlignCenter)
            count_label.setStyleSheet("color: #666; margin-bottom: 10px;")
            layout.addWidget(count_label)
            
            # Sort and limit entries
            entries.sort()
            display_entries = entries[:20]  # Show fewer items for cleaner look
            
            # File list with modern styling
            if display_entries:
                file_list_text = []
                for entry in display_entries:
                    entry_path = os.path.join(self.dir_path, entry)
                    if os.path.isdir(entry_path):
                        file_list_text.append(f"📁 {entry}")
                    else:
                        file_list_text.append(f"📄 {entry}")
                
                if len(entries) > 20:
                    file_list_text.append(f"\n⋯ and {len(entries) - 20} more items")
                
                content = '\n'.join(file_list_text)
                
                files_label = QLabel(content)
                files_label.setFont(QFont("SF Pro Text", 10))
                files_label.setWordWrap(True)
                files_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
                files_label.setStyleSheet("""
                    color: #444;
                    background-color: #f8f9fa;
                    border: 1px solid #e9ecef;
                    border-radius: 6px;
                    padding: 10px;
                    line-height: 1.4;
                """)
                files_label.setMaximumHeight(200)
                layout.addWidget(files_label)
            
            layout.addStretch()
            
            # Get directory metadata
            file_info = Path(self.dir_path).stat()
            modified = datetime.fromtimestamp(file_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            metadata = f"Directory: {len(entries)} items\nModified: {modified}"
            
            return widget, metadata
            
        except PermissionError:
            widget = QLabel("🔒 Permission denied")
            widget.setAlignment(Qt.AlignCenter)
            widget.setStyleSheet("color: #dc3545; font-size: 14px;")
            return widget, "Access denied to directory"
        except Exception as e:
            widget = QLabel(f"❌ Error reading directory: {str(e)}")
            widget.setAlignment(Qt.AlignCenter)
            widget.setStyleSheet("color: #dc3545; font-size: 12px;")
            return widget, f"Error: {str(e)}"

class GenericPreview:
    def __init__(self, file_path):
        self.file_path = file_path

    def get_preview(self):
        try:
            icon_provider = QFileIconProvider()
            file_info_qt = QFileInfo(self.file_path)
            icon = icon_provider.icon(file_info_qt)
            pixmap = icon.pixmap(64, 64)

            widget = QLabel()
            widget.setPixmap(pixmap)
            widget.setAlignment(Qt.AlignCenter)
            
            # Get file metadata
            file_info = Path(self.file_path).stat()
            size_bytes = file_info.st_size
            
            # Format file size
            if size_bytes < 1024:
                size_str = f"{size_bytes} bytes"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.1f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
            else:
                size_str = f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
            
            modified = datetime.fromtimestamp(file_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            file_type = Path(self.file_path).suffix.upper() or "Unknown"
            
            metadata = f"Type: {file_type} file\nSize: {size_str}\nModified: {modified}"
            
            return widget, metadata
            
        except Exception as e:
            widget = QLabel("?")
            widget.setAlignment(Qt.AlignCenter)
            widget.setFont(QFont("Arial", 24))
            return widget, f"Error: {str(e)}"

