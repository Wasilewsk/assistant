import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Initializing Cortana...")

from app.gui import launch_gui

if __name__ == "__main__":
    launch_gui()
