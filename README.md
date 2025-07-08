# Desktop Cleaner

Desktop Cleaner is a PyQt5 application designed to help you efficiently organize and declutter your desktop. It provides rich, interactive previews for a wide range of file types (images, PDFs, documents, spreadsheets, SVGs, and more), allowing you to quickly decide whether to move items to specific folders or send them to trash. With persistent state management, it streamlines the process of maintaining an organized workspace.

## Features

- **Comprehensive Preview Support**: Interactive previews for images (JPG, PNG, GIF, etc.), PDFs, text files, directories, SVG, DOCX, XLSX, RTF, and RTFD formats.
- **Intelligent Unknown File Preview**: Attempts text preview for files without extensions or unrecognized types, with graceful fallback.
- **Streamlined Workflow**: Easily move items to custom folders or trash with verification.
- **Persistent State**: Remembers handled items across sessions (moved/trashed items are re-scanned if returned to desktop).
- **Keyboard Navigation**: Efficiently browse and manage files using keyboard shortcuts.
- **Always Shows All Desktop Items**: No hidden items; the application always displays all current desktop contents.

## Quick Start

### Prerequisites
- Python 3.7+
- Git

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd desktop-cleaner
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    
    # On macOS/Linux:
    source .venv/bin/activate
    
    # On Windows:
    .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Launch Application

```bash
python main_gui.py
```

## Keyboard Shortcuts

-   `←` / `→`: Navigate between items
-   `Home`: Reset to first item
-   `F5`: Refresh desktop scan

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.