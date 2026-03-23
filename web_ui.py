#!/usr/bin/env python
"""
MetricForge Crucible Web UI Launcher

Run the Streamlit web interface for MetricForge Crucible.
"""

import subprocess
import sys
from pathlib import Path

def check_and_install_dependencies():
    """Check if Streamlit is installed, install if missing."""
    try:
        import streamlit
        return True
    except ImportError:
        print("⚠️  Streamlit not found. Installing dependencies...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", 
                 "streamlit>=1.28.0", "streamlit-option-menu>=0.3.0"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("✅ Dependencies installed!")
            return True
        except Exception as e:
            print(f"❌ Failed to install dependencies: {e}")
            print("   Try running: pip install -r requirements.txt")
            return False

def main():
    """Launch the Streamlit web UI."""
    
    # Check dependencies
    if not check_and_install_dependencies():
        sys.exit(1)
    
    # Get the path to the Streamlit app
    app_path = Path(__file__).parent / "src" / "metricforge" / "web" / "app.py"
    
    if not app_path.exists():
        print(f"Error: Could not find Streamlit app at {app_path}")
        sys.exit(1)
    
    print(f"🚀 Starting MetricForge Crucible Web UI...")
    print(f"\n💡 The web UI will open in your default browser.")
    print(f"   If it doesn't, navigate to: http://localhost:8501\n")
    
    # Launch Streamlit
    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(app_path)],
            cwd=Path(__file__).parent
        )
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Error launching Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
