"""
Game Window module for Fighting Game Combo Detector.

This module contains the main Pygame window and rendering logic.
"""

from .components import (
    DirectionalButton,
    ComboDisplay,
    InputHistory,
    ComboList,
    ChargeIndicator
)
import pygame
import sys
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, '..')


class GameWindow:
    """
    Main game window that handles rendering and event processing.

    This class creates the Pygame window and manages all UI components.
    It also handles keyboard input and communicates with the GameController.
    """

    # Window settings
    WIDTH = 1200
    HEIGHT = 750
    FPS = 60
    TITLE = "Fighting Game Combo Detector - State Machine"

    # Color scheme (Dark cyberpunk theme)
    BG_COLOR = (15, 15, 25)
    GRID_COLOR = (25, 25, 40)

    # Key mappings - Only arrow keys (no WASD)
    KEY_MAP = {
        pygame.K_UP: 'UP',
        pygame.K_DOWN: 'DOWN',
        pygame.K_LEFT: 'LEFT',
        pygame.K_RIGHT: 'RIGHT',
        pygame.K_SPACE: 'SPACE'
    }

    def __init__(self, controller):
        """
        Initialize the game window.

        Args:
            controller: GameController instance for input handling
        """
        pygame.init()
        pygame.display.set_caption(self.TITLE)

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.controller = controller

        # Setup callbacks
        self.controller.set_combo_callback(self._on_combo_detected)
        self.controller.set_input_callback(self._on_input)
        self.controller.set_timeout_callback(self._on_timeout)
        self.controller.set_freeze_end_callback(self._on_freeze_end)
        self.controller.set_combo_cancelled_callback(self._on_combo_cancelled)

        # Initialize components
        self._init_components()

        # Track pressed keys for button visualization
        self.pressed_keys = set()

    def _init_components(self) -> None:
        """Initialize all UI components."""
        from combo_definitions import get_all_combos

        # Directional buttons layout (center of screen)
        btn_size = 80
        btn_spacing = 10
        center_x = 450
        center_y = 350

        self.buttons = {
            'UP': DirectionalButton(
                center_x, center_y - btn_size - btn_spacing,
                btn_size, 'UP'
            ),
            'DOWN': DirectionalButton(
                center_x, center_y + btn_spacing,
                btn_size, 'DOWN'
            ),
            'LEFT': DirectionalButton(
                center_x - btn_size - btn_spacing, center_y - btn_size // 2 + btn_spacing // 2,
                btn_size, 'LEFT'
            ),
            'RIGHT': DirectionalButton(
                center_x + btn_size + btn_spacing, center_y - btn_size // 2 + btn_spacing // 2,
                btn_size, 'RIGHT'
            ),
            'SPACE': DirectionalButton(
                center_x - btn_size, center_y + btn_size + btn_spacing * 3,
                btn_size * 3, 'SPACE'
            )
        }
        # Adjust space button height
        self.buttons['SPACE'].height = btn_size // 2

        # Combo display (top center)
        self.combo_display = ComboDisplay(150, 30, 650, 120)

        # Input history (below buttons)
        self.input_history = InputHistory(150, 560, 650, 80)

        # Combo list (right side)
        self.combo_list = ComboList(850, 30, 330, 630, get_all_combos())

        # Charge indicator (below space button)
        self.charge_indicator = ChargeIndicator(
            center_x - btn_size - 20,
            center_y + btn_size + btn_spacing * 3 + btn_size // 2 + 20,
            btn_size * 3 + 40, 80
        )

        # State info display
        self.font_small = None
        self.font_title = None

    def _on_combo_detected(self, combo_name: str, is_charged: bool) -> None:
        """Callback when a combo is detected."""
        self.combo_display.show_combo(combo_name, is_charged)

    def _on_input(self, key: str) -> None:
        """Callback when input is received."""
        history = self.controller.get_display_history()
        self.input_history.set_history(history)

    def _on_timeout(self) -> None:
        """Callback when timeout occurs."""
        self.input_history.set_history([])

    def _on_freeze_end(self) -> None:
        """Callback when freeze state ends."""
        self.input_history.set_history([])

    def _on_combo_cancelled(self) -> None:
        """Callback when combo is cancelled (held space too long)."""
        self.input_history.set_history([])
        self.combo_display.show_cancelled()

    def _update_space_button_state(self) -> None:
        """Update the space button enabled state based on controller state."""
        space_available = self.controller.is_space_available()
        self.buttons['SPACE'].set_enabled(space_available)

    def handle_events(self) -> None:
        """Process all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key in self.KEY_MAP:
                    # Don't process input if frozen (except for SPACE check in controller)
                    if self.controller.is_frozen:
                        continue

                    key = self.KEY_MAP[event.key]

                    # For SPACE, check if it's available
                    if key == 'SPACE' and not self.controller.is_space_available():
                        continue

                    self.pressed_keys.add(key)

                    # Update button visual
                    if key in self.buttons:
                        self.buttons[key].set_pressed(True)

                    # Process input
                    self.controller.process_key_down(key)

            elif event.type == pygame.KEYUP:
                if event.key in self.KEY_MAP:
                    key = self.KEY_MAP[event.key]
                    self.pressed_keys.discard(key)

                    # Update button visual
                    if key in self.buttons:
                        self.buttons[key].set_pressed(False)

                    # Process key release (important for SPACE)
                    self.controller.process_key_up(key)

    def update(self) -> None:
        """Update all game logic and components."""
        # Update controller
        self.controller.update()

        # Update space button enabled state
        self._update_space_button_state()

        # Update timeout progress
        if not self.controller.is_frozen:
            timeout_remaining = self.controller.get_time_until_timeout()
            self.input_history.set_timeout_progress(
                timeout_remaining / self.controller.TIMEOUT)
        else:
            # During freeze, show full bar
            self.input_history.set_timeout_progress(1.0)

        # Update charge indicator with zone info
        charge_progress = self.controller.get_charge_progress()
        charge_zone = self.controller.get_charge_zone()
        self.charge_indicator.set_charge(charge_progress, charge_zone)

        # Update components
        self.combo_display.update()
        for button in self.buttons.values():
            button.update()

    def _draw_background(self) -> None:
        """Draw the background with grid pattern."""
        self.screen.fill(self.BG_COLOR)

        # Draw subtle grid
        for x in range(0, self.WIDTH, 40):
            pygame.draw.line(self.screen, self.GRID_COLOR,
                             (x, 0), (x, self.HEIGHT))
        for y in range(0, self.HEIGHT, 40):
            pygame.draw.line(self.screen, self.GRID_COLOR,
                             (0, y), (self.WIDTH, y))

    def _draw_instructions(self) -> None:
        """Draw control instructions."""
        if self.font_small is None:
            self.font_small = pygame.font.Font(None, 24)
            self.font_title = pygame.font.Font(None, 32)

        # Instructions panel
        panel_x = 20
        panel_y = 680

        instructions = [
            "Kontrol: Arrow Keys | SPACE = Execute | ESC = Keluar",
            "Hold SPACE: <2s = Normal | 2-3s = SUPER | >3s = Cancel"
        ]

        for i, text in enumerate(instructions):
            rendered = self.font_small.render(text, True, (100, 100, 140))
            self.screen.blit(rendered, (panel_x, panel_y + i * 22))

    def render(self) -> None:
        """Render all components to the screen."""
        self._draw_background()

        # Draw components
        self.combo_display.draw(self.screen)
        self.input_history.draw(self.screen)
        self.combo_list.draw(self.screen)

        # Draw buttons
        for button in self.buttons.values():
            button.draw(self.screen)

        # Draw charge indicator
        self.charge_indicator.draw(self.screen)

        # Draw instructions
        self._draw_instructions()

        # Draw title
        if self.font_title:
            title = self.font_title.render(
                "FIGHTING GAME COMBO DETECTOR", True, (200, 200, 255))
            title_rect = title.get_rect(centerx=450, y=5)
            self.screen.blit(title, title_rect)

        pygame.display.flip()

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.FPS)

        pygame.quit()
