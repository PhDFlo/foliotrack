"""
Portfolio Dashboard — Interactive Streamlit application for foliotrack.

Launch via the ``dash`` CLI entry point or by calling ``main()`` directly.
"""

import subprocess
import sys
from pathlib import Path


def main():
    """Launch the Streamlit dashboard."""
    app_path = Path(__file__).parent / "app.py"
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(app_path)],
        check=True,
    )
