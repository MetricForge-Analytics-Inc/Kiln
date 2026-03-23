#!/bin/bash
# MetricForge Crucible Web UI Launcher
# Simple bash wrapper to start the Streamlit interface

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Starting MetricForge Crucible Web UI..."
echo "💡 Opening http://localhost:8501"
echo ""

cd "$SCRIPT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

# Check if Streamlit is installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "⚠️  Streamlit not found. Installing dependencies..."
    pip install -q streamlit streamlit-option-menu 2>/dev/null || {
        echo "❌ Failed to install dependencies. Running with full output:"
        pip install streamlit streamlit-option-menu
        exit 1
    }
    echo "✅ Dependencies installed!"
fi

# Run the web UI
python3 web_ui.py
