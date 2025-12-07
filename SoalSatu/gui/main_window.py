"""
Main Window for PDA Expression Validator GUI.

This module provides the main application window that integrates
all UI components for expression validation and conversion.
"""

from expression_converter import ExpressionConverter, ConversionResult
from expression_validator import (
    ExpressionValidator, NotationType, ValidationResult
)
import pygame
import sys
from typing import Optional

from .components import (
    Colors, FontManager, Label, Button, InputField, Dropdown,
    Panel, ValidationPanel, ConversionPanel, StateVisualizer,
    ToggleButtonGroup
)

# Import from parent directory
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MainWindow:
    """
    Main application window for the PDA Expression Validator.

    Provides a modern GUI for:
    - Input and validation of mathematical expressions
    - Conversion between infix, postfix, and prefix notations
    - Visualization of PDA states during validation
    """

    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    FPS = 60

    def __init__(self):
        """Initialize the main window."""
        pygame.init()
        pygame.display.set_caption("PDA Expression Validator & Converter")

        self.screen = pygame.display.set_mode(
            (self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        )
        self.clock = pygame.time.Clock()
        self.running = True

        # Initialize font manager
        FontManager.init()

        # Initialize validators and converters
        self.validator = ExpressionValidator()
        self.converter = ExpressionConverter()

        # Current state
        self.current_notation = NotationType.INFIX
        self.last_validation: Optional[ValidationResult] = None

        # Initialize UI components
        self._init_components()

    def _init_components(self):
        """Initialize all UI components."""
        # Title
        self.title_label = Label(
            40, 30, "PDA Expression Validator",
            font_name='title', color=Colors.ACCENT_PRIMARY
        )

        self.subtitle_label = Label(
            40, 75, "Validate and convert mathematical expressions using Pushdown Automata",
            font_name='body', color=Colors.TEXT_SECONDARY
        )

        # Input section - increased height to accommodate better spacing
        self.input_panel = Panel(40, 120, 720, 180, "Expression Input", 20)

        self.notation_label = Label(60, 175, "Notation:", font_name='body')

        self.notation_buttons = ToggleButtonGroup(
            180, 168,
            options=["Infix", "Postfix", "Prefix"],
            selected_index=0,
            on_change=self._on_notation_change,
            button_width=100, button_height=36, spacing=12
        )

        self.expression_label = Label(60, 240, "Expression:", font_name='body')

        self.expression_input = InputField(
            180, 233, 400, 44,
            placeholder="Enter expression (e.g., (3+4)*2)",
            on_submit=self._on_validate
        )

        self.validate_button = Button(
            600, 233, 140, 44,
            "Validate", on_click=self._on_validate,
            style='primary'
        )

        # Quick examples panel
        self.examples_panel = Panel(780, 120, 380, 180, "Quick Examples", 20)

        self.example_buttons = [
            Button(800, 175, 160, 36, "(3+4)*2",
                   on_click=lambda: self._set_example("(3+4)*2", 0), style='secondary'),
            Button(980, 175, 160, 36, "((5-3)*2)+1",
                   on_click=lambda: self._set_example("((5-3)*2)+1", 0), style='secondary'),
            Button(800, 220, 160, 36, "3 4 + 2 *",
                   on_click=lambda: self._set_example("3 4 + 2 *", 1), style='secondary'),
            Button(980, 220, 160, 36, "* + 3 4 2",
                   on_click=lambda: self._set_example("* + 3 4 2", 2), style='secondary'),
        ]

        # Validation results panel
        self.validation_panel = ValidationPanel(40, 320, 560, 260)

        # Conversion results panel
        self.conversion_panel = ConversionPanel(620, 320, 540, 260)

        # State visualizer
        self.state_visualizer = StateVisualizer(40, 600, 1120, 180)

        # Clear button
        self.clear_button = Button(
            1040, 75, 120, 36, "Clear All",
            on_click=self._on_clear, style='secondary'
        )

        # Status bar
        self.status_label = Label(
            40, self.WINDOW_HEIGHT - 35,
            "Ready - Enter an expression and click Validate",
            font_name='small', color=Colors.TEXT_MUTED
        )

        # Collect all components for event handling
        self.components = [
            self.notation_buttons,
            self.expression_input,
            self.validate_button,
            self.clear_button,
            self.validation_panel,
            self.conversion_panel,
        ] + self.example_buttons

    def _on_notation_change(self, index: int, value: str):
        """Handle notation type change."""
        notation_map = {
            0: NotationType.INFIX,
            1: NotationType.POSTFIX,
            2: NotationType.PREFIX
        }
        self.current_notation = notation_map.get(index, NotationType.INFIX)

        placeholders = {
            NotationType.INFIX: "Enter expression (e.g., (3+4)*2)",
            NotationType.POSTFIX: "Enter expression (e.g., 3 4 + 2 *)",
            NotationType.PREFIX: "Enter expression (e.g., * + 3 4 2)"
        }
        self.expression_input.placeholder = placeholders[self.current_notation]

        self.status_label.set_text(f"Notation changed to {value}")

    def _set_example(self, expression: str, notation_index: int):
        """Set an example expression."""
        self.notation_buttons.set_selected(notation_index)
        self._on_notation_change(
            notation_index, self.notation_buttons.options[notation_index])
        self.expression_input.set_text(expression)
        self._on_validate()

    def _on_validate(self, text: str = None):
        """Handle validation button click or enter key."""
        expression = text if text else self.expression_input.text

        if not expression.strip():
            self.status_label.set_text("Please enter an expression")
            return

        # Validate
        result = self.validator.validate(expression, self.current_notation)
        self.last_validation = result

        # Update validation panel
        self.validation_panel.set_result(
            result.is_valid,
            result.message,
            result.execution_trace
        )

        # Update state visualizer
        pda = self.validator.get_pda(self.current_notation)
        if pda:
            self.state_visualizer.set_pda_data(pda.get_diagram_data())
            self.state_visualizer.set_current_state(result.final_state)

        # If valid, also convert to other notations
        if result.is_valid:
            self._perform_conversions(expression)
            self.status_label.set_text(f"✓ Expression validated successfully")
        else:
            self.conversion_panel.clear()
            self.status_label.set_text(
                f"✗ Validation failed: {result.message}")

    def _perform_conversions(self, expression: str):
        """Convert valid expression to all notations."""
        results = self.converter.convert_to_all(
            expression, self.current_notation)

        self.conversion_panel.set_results(
            infix=results[NotationType.INFIX].result_expression,
            postfix=results[NotationType.POSTFIX].result_expression,
            prefix=results[NotationType.PREFIX].result_expression
        )

    def _on_clear(self):
        """Clear all inputs and results."""
        self.expression_input.clear()
        self.validation_panel.clear()
        self.conversion_panel.clear()
        self.state_visualizer.states = []
        self.last_validation = None
        self.status_label.set_text("Cleared - Ready for new expression")

    def _handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return

            # Pass events to components
            for component in self.components:
                if component.handle_event(event):
                    break

    def _update(self, dt: float):
        """Update components."""
        for component in self.components:
            component.update(dt)
        self.state_visualizer.update(dt)

    def _draw(self):
        """Draw all components."""
        # Clear screen with background
        self.screen.fill(Colors.BG_DARK)

        # Draw gradient accent line at top
        for i in range(4):
            alpha = 255 - i * 60
            color = tuple(min(255, c + 50 - i * 15)
                          for c in Colors.ACCENT_PRIMARY)
            pygame.draw.line(self.screen, color, (0, i),
                             (self.WINDOW_WIDTH, i))

        # Draw title and subtitle
        self.title_label.draw(self.screen)
        self.subtitle_label.draw(self.screen)

        # Draw panels
        self.input_panel.draw(self.screen)
        self.examples_panel.draw(self.screen)

        # Draw input components
        self.notation_label.draw(self.screen)
        self.notation_buttons.draw(self.screen)
        self.expression_label.draw(self.screen)
        self.expression_input.draw(self.screen)
        self.validate_button.draw(self.screen)
        self.clear_button.draw(self.screen)

        # Draw example buttons
        for btn in self.example_buttons:
            btn.draw(self.screen)

        # Draw result panels
        self.validation_panel.draw(self.screen)
        self.conversion_panel.draw(self.screen)

        # Draw state visualizer
        self.state_visualizer.draw(self.screen)

        # Draw status bar
        pygame.draw.rect(self.screen, Colors.BG_MEDIUM,
                         pygame.Rect(0, self.WINDOW_HEIGHT - 50, self.WINDOW_WIDTH, 50))
        self.status_label.draw(self.screen)

        # Update display
        pygame.display.flip()

    def run(self):
        """Run the main application loop."""
        while self.running:
            dt = self.clock.tick(self.FPS) / 1000.0

            self._handle_events()
            self._update(dt)
            self._draw()

        pygame.quit()
