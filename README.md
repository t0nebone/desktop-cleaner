# Desktop Cleaner

Desktop Cleaner is a comprehensive desktop management application providing an intuitive interface for organizing and previewing desktop files. It supports smart previews, enhanced PDF viewing, and robust file operations with verification and modern styling for a seamless user experience.

![Desktop Cleaner Demo](demo/desktop-cleaner-demo.gif)

## Features

- **Enhanced PDF Previews**: Larger, clickable PDF previews with full-size view
- **Modern Directory Previews**: Styled previews with folder icons and emojis
- **Verified File Operations**: Ensures displayed preview matches the selected file before move/trash
- **Smart Previews**: Image, PDF, text file, and directory previews with detailed metadata
- **Persistent State**: Remembers handled items across sessions
- **Native macOS Dialogs**: User-friendly operations with confirmation and error dialogs
- **Smooth Navigation**: Keyboard and mouse navigation with real-time UI updates
- **Comprehensive Error Handling**: For permission issues and missing files

## Quick Start

### Prerequisites
- Python 3.7+ (tested with Python 3.13.2)
- macOS, Windows, or Linux (optimized for macOS)
- Git (for cloning the repository)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd desktop-cleaner
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   
   # On macOS/Linux:
   source .venv/bin/activate
   
   # On Windows:
   .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Launch Application

```bash
python main_gui.py
```

## Screenshots

### Main Interface
![Main Interface](demo/main-interface.png)
*Clean, intuitive interface with navigation controls on the left and live preview on the right*

### PDF Preview
![PDF Preview](demo/pdf-preview.png)
*Enhanced PDF previews with clickable thumbnails for full-size viewing*

### Directory Preview
![Directory Preview](demo/directory-preview.png)
*Modern directory previews with folder icons and file type indicators*

### File Operations
![File Operations](demo/file-operations.png)
*Safe file operations with verification dialogs and undo support*

2. **Application Features:**
   - Scans desktop, previews items, allows navigation.
   - Safely move items to folders or trash after verification.
   - Utilize mouse or keyboard shortcuts for smooth operation.

3. **Keyboard Shortcuts:**
   - `←` / `→`: Navigate between items
   - `Home`: Reset to first item
   - `F5`: Refresh desktop scan

4. **Enhanced Previews:**
   - **PDFs**: Click for larger view.
   - **Directories**: Modern styling with icons and emojis.

## Supported File Types

### Images
- **Formats**: JPEG, PNG, GIF, BMP, TIFF, WebP
- **Features**: Automatic scaling, EXIF metadata display, thumbnail generation
- **Limitations**: Very large images (>50MB) may load slowly

### Documents
- **PDF**: First-page preview, metadata extraction, clickable full-size view
- **Text**: Plain text, Python, JavaScript, HTML, CSS, JSON, XML, CSV, Markdown, YAML
- **Limitations**: Text files limited to first 1000 lines for performance

### Directories
- **Features**: File count, size summary, recent modification date
- **Preview**: Shows up to 20 files with type icons
- **Limitations**: Very large directories (>1000 items) show summary only

### Other Files
- **Generic Preview**: File icon, metadata (size, modified date, permissions)
- **Supported**: All file types with basic information display

## Demo

### Video Walkthrough
![Desktop Cleaner Walkthrough](demo/walkthrough.gif)

### Key Workflows

1. **Browse Desktop Items**
   - Launch application
   - Use arrow keys or navigation buttons
   - View real-time previews

2. **Organize Files**
   - Select "Move to Folder" for organization
   - Choose "Move to Trash" for deletion
   - "Leave on Desktop" to skip items

3. **Enhanced Previews**
   - Click PDF thumbnails for full-size view
   - View image metadata and properties
   - Browse directory contents inline

## Testing

To validate the application components and integration, run:
```bash
python test_gui_integration.py
python test_enhanced_previews.py
```

## Architecture

### Main Components

1. **DesktopItemIterator** (`desktop_item_iterator.py`)
   - Scans ~/Desktop on initialization
   - Filters out system/hidden files (.DS_Store, .localized, dotfiles)
   - Provides navigation methods (next, prev, current, reset)
   - Maintains current position and item count

2. **Preview Providers** (`preview_provider.py`)
   - `ImagePreview`: Displays scaled image thumbnails
   - `PDFPreview`: Renders first page of PDF documents
   - `TextPreview`: Shows file content with encoding detection
   - `DirectoryPreview`: Lists directory contents
   - `GenericPreview`: Shows file icon and metadata

3. **Main GUI** (`main_gui.py`)
   - `PreviewProviderManager`: Selects appropriate preview provider
   - `DesktopCleanerGUI`: Main window with navigation and preview panels
   - Keyboard shortcuts (Arrow keys, Home, F5)
   - Error handling and status updates

### Key Features Implemented

#### Window Load/Navigation Integration
- On application startup, automatically calls `iterator.current()` 
- Chooses appropriate preview provider based on file extension
- Injects preview widget into the right panel
- Updates status bar with current position and item count

#### Graceful Fallback System
- **Preview Failures**: Shows error message with fallback preview
- **Missing Dependencies**: Handles PyMuPDF absence gracefully  
- **File Access Errors**: Permission denied and file not found handling
- **Encoding Issues**: Multiple encoding attempts for text files
- **Empty Desktop**: Proper handling when no items are found

#### Status Bar Updates
- Current file name and position (e.g., "3/15")
- Loading states ("Loading preview...", "Preview loaded")
- Error states ("Preview failed - using fallback")
- Navigation feedback ("Moved to next item")

## Testing

The application includes comprehensive integration tests:

```bash
# Run the test suite
python test_gui_integration.py
```

Test coverage includes:
- Iterator initialization and item retrieval
- Preview provider selection logic
- Preview widget generation
- Navigation functionality
- Error handling with invalid paths
- Provider type verification

## Keyboard Shortcuts

- **Left Arrow**: Previous item
- **Right Arrow**: Next item  
- **Home**: Reset to first item
- **F5**: Refresh desktop items

## Error Handling

The application implements robust error handling:

### Preview Failures
- Invalid file paths → Generic "File not found" preview
- Corrupted images → "Image preview not available" message
- Missing PyMuPDF → "PDF preview not available" with install hint
- Permission denied → "Access denied" with clear messaging

### Iterator Errors
- Empty desktop → Proper UI state with disabled navigation
- Permission errors → Error dialog with details
- File system changes → Auto-refresh handles updates

### GUI Resilience
- Malformed widgets → Fallback to default preview
- Missing metadata → "No metadata available" placeholder
- Application errors → Status bar updates with error state

## File Structure

```
desktop-cleaner/
├── main_gui.py                 # Main GUI application
├── desktop_item_iterator.py    # Desktop scanning and navigation
├── preview_provider.py         # Preview widget providers
├── test_gui_integration.py     # Integration tests
├── test_iterator.py           # Iterator unit tests
├── example_usage.py           # Command-line usage examples
└── README.md                  # This documentation
```

## Performance Notes

### System Requirements
- **RAM**: Minimum 512MB available memory
- **Storage**: ~100MB for application and dependencies
- **Display**: Minimum 1024x768 resolution recommended

### Performance Optimizations
- **Image Scaling**: Automatic thumbnail generation for large images
- **PDF Rendering**: First-page only for quick previews
- **Directory Scanning**: Cached results with smart refresh
- **Memory Management**: Automatic cleanup of preview widgets

### Known Limitations

#### File Size Limits
- **Images**: Files over 50MB may load slowly
- **PDFs**: Complex PDFs with many layers may take 3-5 seconds to render
- **Text Files**: Only first 1000 lines displayed for performance

#### Platform-Specific
- **macOS**: Optimized with native file dialogs and trash integration
- **Windows**: Uses system trash, may require additional permissions
- **Linux**: Requires trash-cli for proper trash functionality

#### Dependencies
- **PyMuPDF**: Required for PDF previews (falls back to generic preview if missing)
- **Pillow**: Required for image processing (images show as generic if missing)
- **PyQt5**: Core dependency - application will not run without it

## Troubleshooting

### Common Issues

**Application won't start:**
```bash
# Check Python version
python --version

# Verify virtual environment
which python

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Preview not working:**
- Ensure file permissions allow reading
- Check if file type is supported
- Try refreshing with F5

**Performance issues:**
- Close other applications to free memory
- Reduce desktop file count
- Check available disk space

## Development Notes

### Design Decisions
- **Single-scan approach**: Iterator scans desktop once on init for performance
- **Provider pattern**: Modular preview system for easy extension
- **Graceful degradation**: Application works even with missing optional dependencies
- **Keyboard-first navigation**: Full keyboard support for accessibility

### Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Future Enhancements
- Custom preview layouts and themes
- Plugin system for additional file types
- Batch operation support
- Configuration file support
- Multi-language support

## License

This project is provided as-is for educational and personal use.
