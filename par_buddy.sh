#!/bin/bash

# Par Buddy GUI Launcher Script
# This script launches the Par Buddy GUI application

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory to ensure relative imports work
cd "$SCRIPT_DIR"

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    # Check if python points to Python 3
    PYTHON_VERSION=$(python -c "import sys; print(sys.version_info.major)")
    if [ "$PYTHON_VERSION" = "3" ]; then
        PYTHON_CMD="python"
    else
        echo "Error: Python 3 is required but not found."
        echo "Please install Python 3 or ensure 'python3' command is available."
        exit 1
    fi
else
    echo "Error: Python is not installed or not in PATH."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Check if required files exist
if [ ! -f "par_buddy_gui.py" ]; then
    echo "Error: par_buddy_gui.py not found in current directory."
    echo "Please ensure you're running this script from the correct directory."
    exit 1
fi

if [ ! -f "par_buddy.py" ]; then
    echo "Error: par_buddy.py not found in current directory."
    echo "This file is required for the GUI to function properly."
    exit 1
fi

# Launch the GUI application
echo "Starting Par Buddy GUI..."
echo "Using Python: $PYTHON_CMD"
echo "Working directory: $SCRIPT_DIR"
echo ""

# Execute the GUI application
exec "$PYTHON_CMD" par_buddy_gui.py "$@"
