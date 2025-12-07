"""
Combo Definitions for Fighting Game Combo Detector.

This module defines all the combo sequences and their corresponding names.
Each combo is defined as a tuple of (input_sequence, combo_name).

Input Symbols:
- 'RIGHT' (→): Right arrow
- 'LEFT' (←): Left arrow  
- 'UP' (↑): Up arrow
- 'DOWN' (↓): Down arrow
- 'SPACE': Space bar (combo finisher)
"""

from typing import List, Tuple

# Input symbol constants for better readability
RIGHT = 'RIGHT'
LEFT = 'LEFT'
UP = 'UP'
DOWN = 'DOWN'
SPACE = 'SPACE'

# Symbol display mapping for UI
SYMBOL_DISPLAY = {
    'RIGHT': '→',
    'LEFT': '←',
    'UP': '↑',
    'DOWN': '↓',
    'SPACE': '␣'
}

# Reverse mapping for display to symbol
DISPLAY_TO_SYMBOL = {v: k for k, v in SYMBOL_DISPLAY.items()}


def get_display_symbol(symbol: str) -> str:
    """Convert internal symbol to display character."""
    return SYMBOL_DISPLAY.get(symbol, symbol)


def get_sequence_display(sequence: List[str]) -> str:
    """Convert a sequence of symbols to display string."""
    return ' '.join(get_display_symbol(s) for s in sequence)


# ============================================================================
# COMBO DEFINITIONS
# ============================================================================
# Format: (input_sequence, combo_name)
# Each combo ends with SPACE as the finisher

COMBO_DEFINITIONS: List[Tuple[List[str], str]] = [
    # Combo 1: → → → Space = Hadoken
    ([RIGHT, RIGHT, RIGHT, SPACE], "Hadoken"),
    
    # Combo 2: ↑ ↓ ↑ → Space = Shoryuken
    ([UP, DOWN, UP, RIGHT, SPACE], "Shoryuken"),
    
    # Combo 3: ← → ← → Space = Tatsumaki
    ([LEFT, RIGHT, LEFT, RIGHT, SPACE], "Tatsumaki"),
    
    # Combo 4: ↑ ↑ ↓ → Space = Dragon Punch
    ([UP, UP, DOWN, RIGHT, SPACE], "Dragon Punch"),
    
    # Combo 5: → ↓ → → Space = Hurricane Kick
    ([RIGHT, DOWN, RIGHT, RIGHT, SPACE], "Hurricane Kick"),
    
    # Combo 6: → → → ↓ ↑ → Space = Giga Hadoken
    ([RIGHT, RIGHT, RIGHT, DOWN, UP, RIGHT, SPACE], "Giga Hadoken"),
    
    # Combo 7: → → ↓ → ↑ ↓ → Space = Ultra Shoryuken
    ([RIGHT, RIGHT, DOWN, RIGHT, UP, DOWN, RIGHT, SPACE], "Ultra Shoryuken"),
    
    # Combo 8: ↑ ↑ ↓ → → → → Space = Mega Tatsumaki
    ([UP, UP, DOWN, RIGHT, RIGHT, RIGHT, RIGHT, SPACE], "Mega Tatsumaki"),
    
    # Combo 9: ← ↑ → → ↓ ↑ → Space = Final Dragon Punch
    ([LEFT, UP, RIGHT, RIGHT, DOWN, UP, RIGHT, SPACE], "Final Dragon Punch"),
    
    # Combo 10: → → ↑ ↓ → ↑ → → Space = Ultimate Hurricane Kick
    ([RIGHT, RIGHT, UP, DOWN, RIGHT, UP, RIGHT, RIGHT, SPACE], "Ultimate Hurricane Kick"),
]


def get_all_combos() -> List[Tuple[List[str], str]]:
    """
    Get all combo definitions.
    
    Returns:
        List of tuples containing (input_sequence, combo_name)
    """
    return COMBO_DEFINITIONS.copy()


def get_combo_by_name(name: str) -> Tuple[List[str], str]:
    """
    Get a specific combo by its name.
    
    Args:
        name: The name of the combo to find
        
    Returns:
        Tuple of (input_sequence, combo_name) or None if not found
    """
    for sequence, combo_name in COMBO_DEFINITIONS:
        if combo_name.lower() == name.lower():
            return (sequence, combo_name)
    return None


def get_combo_count() -> int:
    """Get the total number of defined combos."""
    return len(COMBO_DEFINITIONS)


def print_combo_list() -> None:
    """Print all combos in a formatted table."""
    print("\n" + "=" * 60)
    print("DAFTAR KOMBO FIGHTING GAME")
    print("=" * 60)
    print(f"{'No':<4} {'Rangkaian Tombol':<30} {'Output Kombo':<20}")
    print("-" * 60)
    
    for i, (sequence, name) in enumerate(COMBO_DEFINITIONS, 1):
        seq_display = get_sequence_display(sequence)
        print(f"{i:<4} {seq_display:<30} {name:<20}")
    
    print("=" * 60)
    print(f"Total: {len(COMBO_DEFINITIONS)} kombos")
    print()


# For testing
if __name__ == "__main__":
    print_combo_list()

