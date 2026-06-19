import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Initializing Cortana...")

import pygame
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
except pygame.error:
    pass

from app.gui import launch_gui

if __name__ == "__main__":
    launch_gui()
