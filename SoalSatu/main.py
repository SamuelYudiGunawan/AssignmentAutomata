"""
PDA Expression Validator - Main Entry Point

A Pushdown Automata implementation for validating and converting
mathematical expressions between infix, postfix, and prefix notations.

Features:
- Validate expressions in infix, postfix, or prefix notation
- Convert between all three notation types
- Visual GUI with Pygame showing PDA states
- Step-by-step execution trace

Controls:
- Type expression in input field
- Select notation type from dropdown
- Click Validate or press Enter
- Use example buttons for quick testing

Author: Assignment Automata Team
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from expression_validator import (
    ExpressionValidator, NotationType,
    validate_infix, validate_postfix, validate_prefix
)
from expression_converter import (
    ExpressionConverter,
    infix_to_postfix, infix_to_prefix,
    postfix_to_infix, postfix_to_prefix,
    prefix_to_infix, prefix_to_postfix
)
from gui.main_window import MainWindow


def print_header():
    """Print application header."""
    print("=" * 65)
    print("  PDA EXPRESSION VALIDATOR & CONVERTER")
    print("  Pushdown Automata Implementation")
    print("=" * 65)
    print()


def print_examples():
    """Print example usage."""
    print("Notasi yang didukung:")
    print("  - Infix   : (3+4)*2, 5-3/1, ((2+3)*4)")
    print("  - Postfix : 3 4 + 2 *, 5 3 1 / -")
    print("  - Prefix  : * + 3 4 2, - 5 / 3 1")
    print()
    print("Operator yang didukung: +, -, *, /")
    print("Operand: digit angka (0-9)")
    print()


def run_cli_demo():
    """Run a command-line demonstration."""
    validator = ExpressionValidator()
    converter = ExpressionConverter()
    
    print("-" * 65)
    print("Demo CLI - Validasi dan Konversi")
    print("-" * 65)
    print()
    
    # Demo infix
    print("[1] Infix Expression: (3+4)*2")
    result = validate_infix("(3+4)*2")
    print(f"    Valid: {result.is_valid}")
    print(f"    Message: {result.message}")
    print(f"    → Postfix: {infix_to_postfix('(3+4)*2')}")
    print(f"    → Prefix:  {infix_to_prefix('(3+4)*2')}")
    print()
    
    # Demo postfix
    print("[2] Postfix Expression: 3 4 + 2 *")
    result = validate_postfix("3 4 + 2 *")
    print(f"    Valid: {result.is_valid}")
    print(f"    Message: {result.message}")
    print(f"    → Infix:  {postfix_to_infix('3 4 + 2 *')}")
    print(f"    → Prefix: {postfix_to_prefix('3 4 + 2 *')}")
    print()
    
    # Demo prefix
    print("[3] Prefix Expression: * + 3 4 2")
    result = validate_prefix("* + 3 4 2")
    print(f"    Valid: {result.is_valid}")
    print(f"    Message: {result.message}")
    print(f"    → Infix:   {prefix_to_infix('* + 3 4 2')}")
    print(f"    → Postfix: {prefix_to_postfix('* + 3 4 2')}")
    print()
    
    # Demo invalid expression
    print("[4] Invalid Infix: (3+4*2")
    result = validate_infix("(3+4*2")
    print(f"    Valid: {result.is_valid}")
    print(f"    Message: {result.message}")
    print()
    
    print("-" * 65)


def main():
    """Main entry point."""
    print_header()
    print_examples()
    
    # Run CLI demo
    run_cli_demo()
    
    print("Memulai GUI...")
    print("(Tekan ESC untuk keluar)")
    print()
    
    # Run GUI
    try:
        window = MainWindow()
        window.run()
    except Exception as e:
        print(f"Error menjalankan GUI: {e}")
        print("Pastikan Pygame terinstall: pip install pygame")
        return 1
    
    print()
    print("Terima kasih telah menggunakan PDA Expression Validator!")
    print("=" * 65)
    return 0


if __name__ == "__main__":
    sys.exit(main())

