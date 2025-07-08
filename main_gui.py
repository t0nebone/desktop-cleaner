#!/usr/bin/env python3
"""
Main GUI application for Desktop Cleaner.
Wires together the iterator and preview providers for a complete desktop management experience.
"""

import sys
import os
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStatusBar, QSplitter, QFrame, QScrollArea,
    QMessageBox, QProgressBar, QFileDialog, QMenuBar, QAction
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon

from desktop_item_iterator import DesktopItemIterator
from preview_provider import (
    ImagePreview, PDFPreview, TextPreview, DirectoryPreview, GenericPreview, SvgPreview, DocxPreview, RtfPreview, XlsxPreview
)
from persistence_manager import PersistenceManager
from send2trash import send2trash


class PreviewProviderManager:
    """Manages selection of appropriate preview provider based on file type."""
    
    @staticmethod
    def get_preview_provider(file_path: str):
        """
        Choose and return the appropriate preview provider for the given file.
        
        Args:
            file_path: Path to the file to preview
            
        Returns:
            Appropriate preview provider instance
        """
        path_obj = Path(file_path)
        
        # Check if it's a directory
        if path_obj.is_dir():
            return DirectoryPreview(file_path)
        
        # Get file extension
        extension = path_obj.suffix.lower()
        
        # Image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        if extension in image_extensions:
            return ImagePreview(file_path)
        
        # PDF files
        if extension == '.pdf':
            return PDFPreview(file_path)
        
        # SVG files
        if extension == '.svg':
            return SvgPreview(file_path)

        # Word documents
        if extension == '.docx':
            return DocxPreview(file_path)

        # RTF documents
        if extension in ['.rtf', '.rtfd']:
            return RtfPreview(file_path)

        # Excel spreadsheets
        if extension == '.xlsx':
            return XlsxPreview(file_path)

        # Text files
        text_extensions = {'.txt', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv', '.md', '.yml', '.yaml'}
        if extension in text_extensions:
            return TextPreview(file_path)
        
        # Excel spreadsheets
        if extension == '.xlsx':
            return XlsxPreview(file_path)

        # Try text preview for files with no extension or unknown extensions
        if not extension or extension not in image_extensions.union(text_extensions).union({'.pdf', '.svg', '.docx', '.rtf', '.rtfd', '.xlsx'}):
            try:
                # Attempt to preview as text, but catch errors
                test_preview = TextPreview(file_path)
                # If it doesn't raise an error during init, it's likely text-like
                return test_preview
            except Exception:
                # Fallback to GenericPreview if TextPreview fails
                pass

        # Default to generic preview
        return GenericPreview(file_path)


class DesktopCleanerGUI(QMainWindow):
    """Main GUI window for the Desktop Cleaner application."""
    
    def __init__(self):
        super().__init__()
        self.iterator = None
        self.current_preview_widget = None
        self.current_metadata = ""
        self.current_preview_file = None  # Track which file the preview is showing
        self.persistence_manager = PersistenceManager()
        self.persistence_manager.increment_session_count()
        
        self.init_ui()
        self.init_iterator()
        self.setup_keyboard_shortcuts()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Desktop Cleaner")
        self.setGeometry(100, 100, 1000, 700)
        
        # Set application icon (if available)
        try:
            self.setWindowIcon(QIcon("icon.png"))
        except:
            pass  # Icon file not found, continue without it
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main horizontal splitter
        main_splitter = QSplitter(Qt.Horizontal)
        central_widget.setLayout(QHBoxLayout())
        central_widget.layout().addWidget(main_splitter)
        
        # Left panel - Controls
        self.create_control_panel(main_splitter)
        
        # Right panel - Preview
        self.create_preview_panel(main_splitter)
        
        # Set splitter proportions (30% controls, 70% preview)
        main_splitter.setSizes([300, 700])
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.create_status_bar()
    
    def create_control_panel(self, parent):
        """Create the left control panel."""
        control_frame = QFrame()
        control_frame.setFrameStyle(QFrame.StyledPanel)
        control_layout = QVBoxLayout(control_frame)
        
        # Title
        title_label = QLabel("Desktop Items")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(title_label)
        
        # Current item info
        self.current_item_label = QLabel("No items found")
        self.current_item_label.setWordWrap(True)
        item_font = QFont()
        item_font.setPointSize(10)
        self.current_item_label.setFont(item_font)
        control_layout.addWidget(self.current_item_label)
        
        # Position info
        self.position_label = QLabel("Position: 0/0")
        position_font = QFont()
        position_font.setPointSize(9)
        self.position_label.setFont(position_font)
        control_layout.addWidget(self.position_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        control_layout.addWidget(self.progress_bar)
        
        # Navigation buttons
        button_layout = QVBoxLayout()
        
        self.prev_button = QPushButton("◀ Previous")
        self.prev_button.clicked.connect(self.prev_item)
        button_layout.addWidget(self.prev_button)
        
        self.next_button = QPushButton("Next ▶")
        self.next_button.clicked.connect(self.next_item)

        # Action buttons
        self.move_button = QPushButton("Move to Folder...")
        self.move_button.clicked.connect(self.move_to_folder)
        button_layout.addWidget(self.move_button)

        self.trash_button = QPushButton("Move to Trash")
        self.trash_button.clicked.connect(self.move_to_trash)
        button_layout.addWidget(self.trash_button)
        button_layout.addWidget(self.next_button)
        
        # Reset button
        self.reset_button = QPushButton("⟲ Reset to First")
        self.reset_button.clicked.connect(self.reset_iterator)
        button_layout.addWidget(self.reset_button)
        
        # Refresh button
        self.refresh_button = QPushButton("🔄 Refresh Desktop")
        self.refresh_button.clicked.connect(self.refresh_iterator)
        button_layout.addWidget(self.refresh_button)
        
        control_layout.addLayout(button_layout)
        control_layout.addStretch()
        
        parent.addWidget(control_frame)
    
    def create_preview_panel(self, parent):
        """Create the right preview panel."""
        preview_frame = QFrame()
        preview_frame.setFrameStyle(QFrame.StyledPanel)
        preview_layout = QVBoxLayout(preview_frame)
        
        # Preview title
        preview_title = QLabel("Preview")
        preview_font = QFont()
        preview_font.setPointSize(14)
        preview_font.setBold(True)
        preview_title.setFont(preview_font)
        preview_title.setAlignment(Qt.AlignCenter)
        preview_layout.addWidget(preview_title)
        
        # Scrollable preview area
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setAlignment(Qt.AlignCenter)
        
        # Default preview widget
        self.default_preview = QLabel("No item selected")
        self.default_preview.setAlignment(Qt.AlignCenter)
        default_font = QFont()
        default_font.setPointSize(12)
        self.default_preview.setFont(default_font)
        self.preview_scroll.setWidget(self.default_preview)
        
        preview_layout.addWidget(self.preview_scroll)
        
        # Metadata label
        self.metadata_label = QLabel("No metadata available")
        self.metadata_label.setWordWrap(True)
        metadata_font = QFont()
        metadata_font.setPointSize(9)
        self.metadata_label.setFont(metadata_font)
        self.metadata_label.setMaximumHeight(100)
        preview_layout.addWidget(self.metadata_label)
        
        parent.addWidget(preview_frame)
    
    def create_status_bar(self):
        """Create and configure the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status message
        self.status_message = QLabel("Ready")
        self.status_bar.addWidget(self.status_message)
        
        # Item count
        self.item_count_label = QLabel("Items: 0")
        self.status_bar.addPermanentWidget(self.item_count_label)
    
    def create_menu_bar(self):
        """Create the menu bar with state management options."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # State submenu
        state_menu = file_menu.addMenu('State Management')
        
        # Show state summary
        summary_action = QAction('Show Summary', self)
        summary_action.triggered.connect(self.show_state_summary)
        state_menu.addAction(summary_action)
        
        # Clear handled items
        clear_handled_action = QAction('Clear Handled Items', self)
        clear_handled_action.triggered.connect(self.clear_handled_items)
        state_menu.addAction(clear_handled_action)
        
        # Clear all state
        clear_all_action = QAction('Clear All State', self)
        clear_all_action.triggered.connect(self.clear_all_state)
        state_menu.addAction(clear_all_action)
        
        state_menu.addSeparator()
        
        # Export state
        export_action = QAction('Export State...', self)
        export_action.triggered.connect(self.export_state)
        state_menu.addAction(export_action)
        
        # Import state
        import_action = QAction('Import State...', self)
        import_action.triggered.connect(self.import_state)
        state_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def verify_file_integrity(self, file_path: str) -> bool:
        """Verify that the file shown in preview matches the current file."""
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                QMessageBox.critical(self, "File Not Found", f"The file no longer exists:\n{file_path}")
                return False
            
            # CRITICAL: Check if preview file matches current file
            if hasattr(self, 'current_preview_file') and self.current_preview_file:
                if self.current_preview_file != file_path:
                    QMessageBox.critical(
                        self, "File Mismatch Error", 
                        f"CRITICAL ERROR: Preview mismatch detected!\n\n"
                        f"Preview shows: {os.path.basename(self.current_preview_file)}\n"
                        f"But trying to move: {os.path.basename(file_path)}\n\n"
                        f"Operation cancelled for safety."
                    )
                    return False
            
            # Get file info for verification
            file_stat = os.stat(file_path)
            file_name = os.path.basename(file_path)
            
            # Show confirmation dialog with file details
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Question)
            msg.setWindowTitle("Confirm File Operation")
            msg.setText(f"You are about to move:\n\n{file_name}\n\nSize: {file_stat.st_size:,} bytes\nModified: {datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n\nIs this the correct file?")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.Yes)
            
            return msg.exec_() == QMessageBox.Yes
            
        except Exception as e:
            QMessageBox.warning(self, "Verification Error", f"Could not verify file: {e}")
            return False
    
    def move_to_folder(self):
        """Move the item to a selected folder."""
        if not self.iterator or not self.iterator.current_item_path():
            return
        
        current_item_path = self.iterator.current_item_path()
        
        # CRITICAL: Verify file integrity before moving
        if not self.verify_file_integrity(current_item_path):
            self.status_message.setText("Move cancelled - file verification failed")
            return
            
        # Open dialog to select a directory
        directory = QFileDialog.getExistingDirectory(self, "Select Folder")
        if directory:
            try:
                # Double-check the file still exists and matches
                if not os.path.exists(current_item_path):
                    self.handle_error("File no longer exists - it may have been moved or deleted")
                    return
                
                # Move the file to the selected directory
                shutil.move(current_item_path, directory)
                self.persistence_manager.mark_item_handled(current_item_path, "moved", directory)
                self.status_message.setText(f"Moved to {directory}")
                # Remove from iterator and advance
                self.remove_current_item_and_advance()
            except Exception as e:
                self.handle_error(f"Failed to move file: {e}")
        # Skip to next if user cancels (no action needed)

    def move_to_trash(self):
        """Move the item to trash."""
        if not self.iterator or not self.iterator.current_item_path():
            return
        
        current_item_path = self.iterator.current_item_path()
        
        # CRITICAL: Verify file integrity before moving to trash
        if not self.verify_file_integrity(current_item_path):
            self.status_message.setText("Trash operation cancelled - file verification failed")
            return
            
        try:
            # Double-check the file still exists and matches
            if not os.path.exists(current_item_path):
                self.handle_error("File no longer exists - it may have been moved or deleted")
                return
                
            send2trash(current_item_path)
            self.persistence_manager.mark_item_handled(current_item_path, "trashed")
            self.status_message.setText("Moved to trash")
            # Remove from iterator and advance
            self.remove_current_item_and_advance()
        except Exception as e:
            self.handle_error(f"Failed to move to trash: {e}")

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for navigation."""
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        
        # Arrow key navigation
        QShortcut(QKeySequence(Qt.Key_Left), self, self.prev_item)
        QShortcut(QKeySequence(Qt.Key_Right), self, self.next_item)
        QShortcut(QKeySequence(Qt.Key_Home), self, self.reset_iterator)
        QShortcut(QKeySequence(Qt.Key_F5), self, self.refresh_iterator)
    
    def init_iterator(self):
        """Initialize the desktop item iterator."""
        try:
            self.status_message.setText("Loading desktop items...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
            # Scan desktop and filter items
            desktop_path = Path.home() / "Desktop"
            all_desktop_items = []
            if desktop_path.exists():
                for item in desktop_path.iterdir():
                    if not self._should_skip_file(item.name):
                        all_desktop_items.append(str(item.absolute()))
            all_desktop_items.sort()
            
            # Filter out handled items using the persistence manager
            unhandled_items = self.persistence_manager.filter_unhandled_items(all_desktop_items)
            
            # Initialize iterator with the unhandled items
            self.iterator = DesktopItemIterator(unhandled_items)
            
            self.progress_bar.setVisible(False)
            
            # Update UI
            self.update_ui()
            self.load_current_preview()
            
            # Update status
            item_count = self.iterator.get_item_count()
            self.status_message.setText(f"Loaded {item_count} desktop items")
            self.item_count_label.setText(f"Items: {item_count}")
            
            if item_count == 0:
                self.status_message.setText("No items found on desktop")
            
        except Exception as e:
            self.handle_error(f"Failed to load desktop items: {e}")

    def _should_skip_file(self, filename: str) -> bool:
        """
        Determine if a file should be skipped based on filtering rules.
        Moved from DesktopItemIterator to centralize logic.
        """
        # Skip dotfiles (files starting with .)
        if filename.startswith('.'):
            return True
        
        # Skip specific system files
        system_files = {'.DS_Store', '.localized'}
        if filename in system_files:
            return True
        
        return False
    
    def update_ui(self):
        """Update the UI elements based on current iterator state."""
        if not self.iterator:
            return
        
        current_path = self.iterator.current()
        item_count = self.iterator.get_item_count()
        current_index = self.iterator.get_current_index()
        
        # Update current item label
        if current_path:
            item_name = Path(current_path).name
            self.current_item_label.setText(f"Current: {item_name}")
        else:
            self.current_item_label.setText("No items found")
        
        # Update position label
        if item_count > 0:
            self.position_label.setText(f"Position: {current_index + 1}/{item_count}")
        else:
            self.position_label.setText("Position: 0/0")
        
        # Update button states
        self.prev_button.setEnabled(not self.iterator.is_at_start() and item_count > 0)
        self.next_button.setEnabled(not self.iterator.is_at_end() and item_count > 0)
        self.reset_button.setEnabled(item_count > 0)
    
    def load_current_preview(self):
        """Load and display preview for the current item."""
        if not self.iterator:
            return
        
        current_path = self.iterator.current()
        if not current_path:
            self.show_default_preview()
            return
        
        # INTEGRITY CHECK: Verify file still exists before showing preview
        if not os.path.exists(current_path):
            self.handle_preview_error(current_path, Exception("File no longer exists"))
            return
        
        try:
            self.status_message.setText("Loading preview...")
            
            # Get appropriate preview provider
            provider = PreviewProviderManager.get_preview_provider(current_path)
            
            # Get preview widget and metadata
            preview_widget, metadata = provider.get_preview()
            
            # Update preview
            if preview_widget:
                self.preview_scroll.setWidget(preview_widget)
                self.current_preview_widget = preview_widget
                # Store current file path for verification
                self.current_preview_file = current_path
            else:
                self.show_default_preview()
            
            # Update metadata
            self.metadata_label.setText(metadata if metadata else "No metadata available")
            self.current_metadata = metadata
            
            self.status_message.setText("Preview loaded")
            
        except Exception as e:
            self.handle_preview_error(current_path, e)
    
    def show_default_preview(self):
        """Show default preview when no item is selected or preview fails."""
        self.preview_scroll.setWidget(self.default_preview)
        self.metadata_label.setText("No metadata available")
        self.current_preview_widget = None
        self.current_metadata = ""
        self.current_preview_file = None
    
    def handle_preview_error(self, file_path: str, error: Exception):
        """Handle preview loading errors gracefully."""
        error_label = QLabel(f"Preview not available\n\nFile: {Path(file_path).name}\nError: {str(error)}")
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setWordWrap(True)
        error_label.setStyleSheet("color: #666; font-style: italic;")
        
        self.preview_scroll.setWidget(error_label)
        self.metadata_label.setText(f"Error loading preview: {str(error)}")
        self.status_message.setText("Preview failed - using fallback")
    
    def handle_error(self, message: str):
        """Handle general application errors."""
        self.progress_bar.setVisible(False)
        self.status_message.setText("Error occurred")
        
        # Show error dialog
        QMessageBox.critical(self, "Error", message)
    
    def _save_current_iterator_state(self):
        """Saves the current state of the iterator to the persistence file."""
        if self.iterator:
            # Ensure index is valid before saving
            self.iterator._ensure_valid_index()
            items = self.iterator.items
            current_index = self.iterator.get_current_index()
            self.persistence_manager.save_iterator_state(items, current_index)
    
    def advance_to_next_item(self):
        """Advance to the next item without performing any action."""
        if not self.iterator:
            return
        
        next_path = self.iterator.next()
        if next_path:
            self.update_ui()
            self.load_current_preview()
            self._save_current_iterator_state()
            self.status_message.setText("Moved to next item")
        else:
            self.show_completion_dialog()
    
    def remove_current_item_and_advance(self):
        """Remove current item from iterator and advance to next."""
        if not self.iterator:
            return
        
        # Remove current item from the iterator's items list
        current_index = self.iterator.get_current_index()
        if 0 <= current_index < len(self.iterator.items):
            self.iterator.items.pop(current_index)
            
            # Ensure index remains valid after removal
            self.iterator._ensure_valid_index()
            
            # Update UI and load preview
            self.update_ui()
            self.load_current_preview()
            self._save_current_iterator_state()
            
            # Check if we've processed all items
            if not self.iterator.items:
                self.show_completion_dialog()
                
    def show_completion_dialog(self):
        """Show completion dialog when all items have been processed."""
        QMessageBox.information(
            self, 
            "Desktop Cleaning Complete", 
            "Congratulations! You have processed all items on your desktop.\n\n"
            "Your desktop is now organized!"
        )
        self.status_message.setText("All items processed")
    
    def next_item(self):
        """Navigate to the next item."""
        if not self.iterator:
            return
        
        next_path = self.iterator.next()
        if next_path:
            self.update_ui()
            self.load_current_preview()
            self._save_current_iterator_state()
            self.status_message.setText("Moved to next item")
        else:
            self.status_message.setText("Already at last item")
    
    def prev_item(self):
        """Navigate to the previous item."""
        if not self.iterator:
            return
        
        prev_path = self.iterator.prev()
        if prev_path:
            self.update_ui()
            self.load_current_preview()
            self._save_current_iterator_state()
            self.status_message.setText("Moved to previous item")
        else:
            self.status_message.setText("Already at first item")
    
    def reset_iterator(self):
        """Reset iterator to the first item."""
        if not self.iterator:
            return
        
        self.iterator.reset()
        self.update_ui()
        self.load_current_preview()
        self._save_current_iterator_state()
        self.status_message.setText("Reset to first item")
    
    def refresh_iterator(self):
        """Refresh the desktop iterator (re-scan desktop)."""
        self.status_message.setText("Refreshing desktop items...")
        try:
            # Re-initialize iterator
            self.init_iterator()
        except Exception as e:
            self.handle_error(f"Failed to refresh desktop items: {e}")
    
    def closeEvent(self, event):
        """Handle application close event."""
        # State is now saved on each navigation action, so no need to save on close.
        event.accept()
    
    def show_state_summary(self):
        """Show a dialog with the current state summary."""
        summary = self.persistence_manager.get_handled_items_summary()
        session_count = self.persistence_manager.get_session_count()
        
        message = f"""Desktop Cleaner State Summary:

Sessions run: {session_count}
Items moved to folders: {summary['moved']}
Items moved to trash: {summary['trashed']}
Total items handled: {sum(summary.values())}

State file location: {self.persistence_manager.state_file_path}"""
        
        QMessageBox.information(self, "State Summary", message)
    
    def clear_handled_items(self):
        """Clear only the handled items data."""
        reply = QMessageBox.question(
            self, 'Clear Handled Items',
            'This will clear the record of all handled items, allowing you to see them again.\n\nContinue?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.persistence_manager.clear_handled_items()
            QMessageBox.information(self, 'Success', 'Handled items data cleared.')
            # Refresh the iterator to show previously handled items
            self.refresh_iterator()
    
    def clear_all_state(self):
        """Clear all state data."""
        reply = QMessageBox.question(
            self, 'Clear All State',
            'This will clear ALL state data including handled items and iterator position.\n\nThis action cannot be undone. Continue?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.persistence_manager.clear_state()
            QMessageBox.information(self, 'Success', 'All state data cleared.')
            # Refresh the iterator
            self.refresh_iterator()
    
    def export_state(self):
        """Export state to a file."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            'Export State',
            'desktop_cleaner_backup.json',
            'JSON files (*.json);;All files (*)'
        )
        
        if filename:
            if self.persistence_manager.export_state(filename):
                QMessageBox.information(self, 'Success', f'State exported to {filename}')
            else:
                QMessageBox.warning(self, 'Error', 'Failed to export state')
    
    def import_state(self):
        """Import state from a file."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            'Import State',
            '',
            'JSON files (*.json);;All files (*)'
        )
        
        if filename:
            reply = QMessageBox.question(
                self, 'Import State',
                'This will replace your current state with the imported data.\n\nContinue?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.persistence_manager.import_state(filename):
                    QMessageBox.information(self, 'Success', f'State imported from {filename}')
                    # Refresh the iterator to reflect the imported state
                    self.refresh_iterator()
                else:
                    QMessageBox.warning(self, 'Error', 'Failed to import state')


def main():
    """Main application entry point."""
    # Set Qt environment variables to reduce font warnings
    import os
    os.environ['QT_LOGGING_RULES'] = 'qt.qpa.fonts.debug=false'
    
    app = QApplication(sys.argv)
    
    # Configure Qt font settings to avoid SF Pro Display warning
    from PyQt5.QtGui import QFontDatabase
    
    # Set font substitutions to prevent Qt from trying to use SF Pro Display
    QFont.insertSubstitution("SF Pro Display", "Helvetica")
    QFont.insertSubstitution(".SF NS Text", "Helvetica")
    QFont.insertSubstitution(".SF NS Display", "Helvetica")
    
    # Set a default font that's guaranteed to exist on macOS
    default_font = QFont()
    default_font.setFamily("Helvetica")
    default_font.setPointSize(13)  # Standard macOS size
    app.setFont(default_font)
    
    # Set application metadata
    app.setApplicationName("Desktop Cleaner")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Desktop Tools")
    
    # Create and show main window
    window = DesktopCleanerGUI()
    window.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
