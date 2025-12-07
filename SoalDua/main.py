"""
Fighting Game Combo Detector - Main Entry Point

A state machine implementation for detecting fighting game combos.
This program demonstrates the use of a Trie-based state machine to
efficiently detect multiple combo sequences with timing constraints.

Features:
- 10 different combo sequences
- 1 second timeout between inputs
- Charged combo (hold SPACE for 2-3 seconds)
- Visual feedback with Pygame GUI
- 0.5 second freeze after successful combo

Controls:
- Arrow keys (Up/Down/Left/Right): Directional input
- SPACE: Execute combo (only available at final input, hold 2-3s for super)
- R: Reset
- ESC: Exit

Author: Assignment Automata Team
"""

from combo_definitions import print_combo_list
from gui.game_window import GameWindow
from game_controller import GameController
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Main entry point for the application."""
    print("=" * 60)
    print("FIGHTING GAME COMBO DETECTOR")
    print("State Machine Implementation")
    print("=" * 60)
    print()

    # Print combo list to console
    print_combo_list()

    print("\nKontrol:")
    print("  - Arrow Keys (Up/Down/Left/Right): Input arah")
    print("  - SPACE: Execute kombo (hanya tersedia di input terakhir)")
    print("  - ESC: Keluar")
    print()
    print("Hold SPACE:")
    print("  - < 2 detik: Combo biasa")
    print("  - 2-3 detik: SUPER Combo!")
    print("  - > 3 detik: Combo dibatalkan")
    print()
    print("Catatan:")
    print("  - Timeout antar input adalah 1 detik (timer freeze saat hold SPACE)")
    print("  - SPACE hanya bisa ditekan saat sudah di input terakhir")
    print("  - Setelah combo berhasil, ada freeze 0.5 detik")
    print()
    print("Memulai GUI...")
    print("-" * 60)

    # Initialize controller
    controller = GameController()

    # Initialize and run game window
    window = GameWindow(controller)
    window.run()

    print()
    print("Terima kasih telah menggunakan Fighting Game Combo Detector!")
    print("=" * 60)


if __name__ == "__main__":
    main()
