"""
UI Components for Fighting Game Combo Detector.

This module contains all the visual components used in the game window.
"""

import pygame
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
import math


class UIComponent(ABC):
    """
    Abstract base class for all UI components.

    All visual elements in the game should inherit from this class
    and implement the draw and update methods.
    """

    def __init__(self, x: int, y: int, width: int, height: int):
        """
        Initialize the UI component.

        Args:
            x: X position
            y: Y position
            width: Component width
            height: Component height
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the component to the surface."""
        pass

    def update(self) -> None:
        """Update component state (called each frame)."""
        pass

    def get_rect(self) -> pygame.Rect:
        """Get the bounding rectangle of this component."""
        return pygame.Rect(self.x, self.y, self.width, self.height)


class DirectionalButton(UIComponent):
    """
    Visual representation of a directional button (arrow or space).
    Shows pressed/released state with animation.
    Uses custom drawn arrows instead of Unicode characters.
    """

    # Color scheme - Cyberpunk/Neon style
    COLORS = {
        'UP': (255, 100, 150),      # Pink
        'DOWN': (100, 200, 255),    # Cyan
        'LEFT': (255, 200, 100),    # Gold
        'RIGHT': (150, 255, 150),   # Green
        'SPACE': (200, 150, 255)    # Purple
    }

    def __init__(self, x: int, y: int, size: int, direction: str):
        """
        Initialize a directional button.

        Args:
            x: X position
            y: Y position
            size: Button size (width and height)
            direction: 'UP', 'DOWN', 'LEFT', 'RIGHT', or 'SPACE'
        """
        super().__init__(x, y, size, size)
        self.direction = direction
        self.pressed = False
        self.press_time = 0
        self.glow_intensity = 0
        self.font = None
        self.enabled = True  # New: for disabling space button

    def set_pressed(self, pressed: bool) -> None:
        """Set the pressed state of the button."""
        self.pressed = pressed
        if pressed:
            self.glow_intensity = 1.0

    def set_enabled(self, enabled: bool) -> None:
        """Set whether the button is enabled."""
        self.enabled = enabled

    def update(self) -> None:
        """Update button animation state."""
        if not self.pressed and self.glow_intensity > 0:
            self.glow_intensity = max(0, self.glow_intensity - 0.05)

    def _draw_arrow(self, surface: pygame.Surface, center_x: int, center_y: int,
                    color: Tuple[int, int, int], size: int) -> None:
        """Draw an arrow pointing in the button's direction."""
        arrow_size = size // 3

        if self.direction == 'UP':
            points = [
                (center_x, center_y - arrow_size),
                (center_x - arrow_size, center_y + arrow_size // 2),
                (center_x + arrow_size, center_y + arrow_size // 2)
            ]
            pygame.draw.polygon(surface, color, points)
        elif self.direction == 'DOWN':
            points = [
                (center_x, center_y + arrow_size),
                (center_x - arrow_size, center_y - arrow_size // 2),
                (center_x + arrow_size, center_y - arrow_size // 2)
            ]
            pygame.draw.polygon(surface, color, points)
        elif self.direction == 'LEFT':
            points = [
                (center_x - arrow_size, center_y),
                (center_x + arrow_size // 2, center_y - arrow_size),
                (center_x + arrow_size // 2, center_y + arrow_size)
            ]
            pygame.draw.polygon(surface, color, points)
        elif self.direction == 'RIGHT':
            points = [
                (center_x + arrow_size, center_y),
                (center_x - arrow_size // 2, center_y - arrow_size),
                (center_x - arrow_size // 2, center_y + arrow_size)
            ]
            pygame.draw.polygon(surface, color, points)
        elif self.direction == 'SPACE':
            # Draw a horizontal bar for space
            bar_width = size // 2
            bar_height = size // 6
            rect = pygame.Rect(center_x - bar_width // 2, center_y - bar_height // 2,
                               bar_width, bar_height)
            pygame.draw.rect(surface, color, rect, border_radius=3)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the button with glow effect."""
        if not self.visible:
            return

        base_color = self.COLORS.get(self.direction, (200, 200, 200))

        # Dim color if disabled
        if not self.enabled:
            base_color = tuple(c // 4 for c in base_color)

        # Draw glow effect
        if self.glow_intensity > 0 and self.enabled:
            glow_size = int(self.width * 1.3)
            glow_surface = pygame.Surface(
                (glow_size, glow_size), pygame.SRCALPHA)
            glow_alpha = int(100 * self.glow_intensity)
            glow_color = (*base_color, glow_alpha)
            pygame.draw.circle(glow_surface, glow_color,
                               (glow_size // 2, glow_size // 2), glow_size // 2)
            surface.blit(glow_surface,
                         (self.x + self.width // 2 - glow_size // 2,
                          self.y + self.height // 2 - glow_size // 2))

        # Draw button background
        if self.pressed and self.enabled:
            bg_color = base_color
            border_color = (255, 255, 255)
        else:
            bg_color = tuple(c // 3 for c in base_color)
            border_color = base_color

        # Draw rounded rectangle
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, bg_color, rect, border_radius=10)
        pygame.draw.rect(surface, border_color, rect,
                         width=3, border_radius=10)

        # Draw arrow/symbol
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        symbol_color = (255, 255, 255) if (
            self.pressed and self.enabled) else base_color
        self._draw_arrow(surface, center_x, center_y, symbol_color, self.width)


class ComboDisplay(UIComponent):
    """
    Displays the detected combo with animation effects.
    """

    def __init__(self, x: int, y: int, width: int, height: int):
        """Initialize the combo display."""
        super().__init__(x, y, width, height)
        self.current_combo: Optional[str] = None
        self.is_charged: bool = False
        self.is_cancelled: bool = False
        self.display_time: float = 0
        self.animation_progress: float = 0
        self.font_large = None
        self.font_small = None
        self.is_frozen = False

    def show_combo(self, combo_name: str, is_charged: bool = False) -> None:
        """Display a detected combo."""
        self.current_combo = combo_name
        self.is_charged = is_charged
        self.is_cancelled = False
        self.display_time = 1
        self.animation_progress = 0
        self.is_frozen = True

    def show_cancelled(self) -> None:
        """Display combo cancelled message."""
        self.current_combo = "CANCELLED!"
        self.is_charged = False
        self.is_cancelled = True
        self.display_time = 1.0  # Show briefly
        self.animation_progress = 0
        self.is_frozen = False

    def is_displaying(self) -> bool:
        """Check if currently displaying a combo."""
        return self.display_time > 0

    def update(self) -> None:
        """Update display animation."""
        if self.display_time > 0:
            self.display_time -= 1/60  # Assume 60 FPS
            self.animation_progress = min(1.0, self.animation_progress + 0.1)
        else:
            self.current_combo = None
            self.animation_progress = 0
            self.is_frozen = False

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the combo display."""
        if not self.visible:
            return

        if self.font_large is None:
            self.font_large = pygame.font.Font(None, 72)
            self.font_small = pygame.font.Font(None, 36)

        # Draw background panel
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Highlight border when frozen
        if self.is_frozen:
            pygame.draw.rect(surface, (30, 30, 60), bg_rect, border_radius=15)
            border_color = (255, 215, 0) if self.is_charged else (
                100, 255, 200)
            pygame.draw.rect(surface, border_color, bg_rect,
                             width=3, border_radius=15)
        else:
            pygame.draw.rect(surface, (20, 20, 40), bg_rect, border_radius=15)
            pygame.draw.rect(surface, (100, 100, 150),
                             bg_rect, width=2, border_radius=15)

        if self.current_combo:
            # Determine colors based on state
            if self.is_cancelled:
                text_color = (255, 100, 100)  # Red
                glow_color = (200, 50, 50)
            elif self.is_charged:
                text_color = (255, 215, 0)  # Gold
                glow_color = (255, 200, 100)
            else:
                text_color = (100, 255, 200)  # Cyan
                glow_color = (50, 200, 150)

            # Scale animation
            scale = 0.5 + 0.5 * self.animation_progress

            # Render combo name
            text = self.font_large.render(self.current_combo, True, text_color)

            # Apply scale
            scaled_width = int(text.get_width() * scale)
            scaled_height = int(text.get_height() * scale)
            if scaled_width > 0 and scaled_height > 0:
                scaled_text = pygame.transform.scale(
                    text, (scaled_width, scaled_height))
                text_rect = scaled_text.get_rect(center=(self.x + self.width // 2,
                                                         self.y + self.height // 2))

                # Draw glow
                glow_surface = pygame.Surface(
                    (scaled_width + 20, scaled_height + 20), pygame.SRCALPHA)
                glow_text = self.font_large.render(
                    self.current_combo, True, (*glow_color, 100))
                scaled_glow = pygame.transform.scale(
                    glow_text, (scaled_width, scaled_height))
                glow_surface.blit(scaled_glow, (10, 10))
                surface.blit(
                    glow_surface, (text_rect.x - 10, text_rect.y - 10))

                surface.blit(scaled_text, text_rect)

            # Draw "SUPER!" indicator if charged
            if self.is_charged:
                super_text = self.font_small.render(
                    "CHARGED!", True, (255, 255, 100))
                super_rect = super_text.get_rect(center=(self.x + self.width // 2,
                                                         self.y + self.height - 30))
                surface.blit(super_text, super_rect)

            # Draw freeze timer
            freeze_text = self.font_small.render(
                f"({self.display_time:.1f}s)", True, (150, 150, 180))
            freeze_rect = freeze_text.get_rect(center=(self.x + self.width // 2,
                                                       self.y + 20))
            surface.blit(freeze_text, freeze_rect)
        else:
            # Show waiting message
            text = self.font_small.render(
                "Tekan tombol untuk membuat kombo!", True, (150, 150, 180))
            text_rect = text.get_rect(center=(self.x + self.width // 2,
                                              self.y + self.height // 2))
            surface.blit(text, text_rect)


class InputHistory(UIComponent):
    """
    Displays the recent input history and timing indicator.
    Uses drawn arrows instead of Unicode.
    """

    def __init__(self, x: int, y: int, width: int, height: int):
        """Initialize the input history display."""
        super().__init__(x, y, width, height)
        self.history: List[str] = []  # Now stores direction names, not symbols
        self.timeout_progress: float = 1.0
        self.font = None

    def set_history(self, history: List[str]) -> None:
        """Set the current input history (direction names)."""
        self.history = history.copy()

    def set_timeout_progress(self, progress: float) -> None:
        """Set the timeout progress (0.0 to 1.0)."""
        self.timeout_progress = progress

    def _draw_mini_arrow(self, surface: pygame.Surface, x: int, y: int,
                         direction: str, size: int = 20) -> int:
        """Draw a small arrow and return the width used."""
        color = {
            'UP': (255, 100, 150),
            'DOWN': (100, 200, 255),
            'LEFT': (255, 200, 100),
            'RIGHT': (150, 255, 150),
            'SPACE': (200, 150, 255)
        }.get(direction, (200, 200, 200))

        arrow_size = size // 2
        center_x = x + size // 2
        center_y = y

        if direction == 'UP':
            points = [
                (center_x, center_y - arrow_size),
                (center_x - arrow_size, center_y + arrow_size // 2),
                (center_x + arrow_size, center_y + arrow_size // 2)
            ]
            pygame.draw.polygon(surface, color, points)
        elif direction == 'DOWN':
            points = [
                (center_x, center_y + arrow_size),
                (center_x - arrow_size, center_y - arrow_size // 2),
                (center_x + arrow_size, center_y - arrow_size // 2)
            ]
            pygame.draw.polygon(surface, color, points)
        elif direction == 'LEFT':
            points = [
                (center_x - arrow_size, center_y),
                (center_x + arrow_size // 2, center_y - arrow_size),
                (center_x + arrow_size // 2, center_y + arrow_size)
            ]
            pygame.draw.polygon(surface, color, points)
        elif direction == 'RIGHT':
            points = [
                (center_x + arrow_size, center_y),
                (center_x - arrow_size // 2, center_y - arrow_size),
                (center_x - arrow_size // 2, center_y + arrow_size)
            ]
            pygame.draw.polygon(surface, color, points)
        elif direction == 'SPACE':
            # Draw a small bar
            rect = pygame.Rect(x, center_y - 3, size, 6)
            pygame.draw.rect(surface, color, rect, border_radius=2)

        return size + 8  # Return width used including spacing

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the input history and timing bar."""
        if not self.visible:
            return

        if self.font is None:
            self.font = pygame.font.Font(None, 48)

        # Draw background
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, (30, 30, 50), bg_rect, border_radius=10)
        pygame.draw.rect(surface, (80, 80, 120), bg_rect,
                         width=2, border_radius=10)

        # Draw label
        label_font = pygame.font.Font(None, 24)
        label = label_font.render("INPUT:", True, (150, 150, 180))
        surface.blit(label, (self.x + 10, self.y + 5))

        # Draw input history using arrows
        if self.history:
            arrow_x = self.x + 80
            arrow_y = self.y + self.height // 2
            for direction in self.history[-10:]:  # Show last 10 inputs
                arrow_x += self._draw_mini_arrow(surface,
                                                 arrow_x, arrow_y, direction, 25)

        # Draw timeout bar
        bar_width = self.width - 20
        bar_height = 6
        bar_x = self.x + 10
        bar_y = self.y + self.height - 12

        # Background bar
        pygame.draw.rect(surface, (50, 50, 70),
                         (bar_x, bar_y, bar_width, bar_height), border_radius=3)

        # Progress bar
        if self.timeout_progress > 0:
            progress_width = int(bar_width * self.timeout_progress)
            # Color changes from green to red as time runs out
            if self.timeout_progress > 0.5:
                color = (100, 255, 150)
            elif self.timeout_progress > 0.25:
                color = (255, 255, 100)
            else:
                color = (255, 100, 100)
            pygame.draw.rect(surface, color,
                             (bar_x, bar_y, progress_width, bar_height), border_radius=3)


class ComboList(UIComponent):
    """
    Displays the list of available combos with drawn arrows.
    """

    def __init__(self, x: int, y: int, width: int, height: int,
                 combos: List[Tuple[List[str], str]]):
        """
        Initialize the combo list.

        Args:
            combos: List of (sequence, name) tuples
        """
        super().__init__(x, y, width, height)
        self.combos = combos
        self.scroll_offset = 0
        self.font = None
        self.font_small = None

    def _draw_mini_arrow(self, surface: pygame.Surface, x: int, y: int,
                         direction: str, size: int = 14) -> int:
        """Draw a small arrow and return the width used."""
        color = {
            'UP': (255, 100, 150),
            'DOWN': (100, 200, 255),
            'LEFT': (255, 200, 100),
            'RIGHT': (150, 255, 150),
            'SPACE': (200, 150, 255)
        }.get(direction, (150, 150, 150))

        arrow_size = size // 2
        center_x = x + size // 2
        center_y = y

        if direction == 'UP':
            points = [
                (center_x, center_y - arrow_size),
                (center_x - arrow_size, center_y + arrow_size // 2),
                (center_x + arrow_size, center_y + arrow_size // 2)
            ]
            pygame.draw.polygon(surface, color, points)
        elif direction == 'DOWN':
            points = [
                (center_x, center_y + arrow_size),
                (center_x - arrow_size, center_y - arrow_size // 2),
                (center_x + arrow_size, center_y - arrow_size // 2)
            ]
            pygame.draw.polygon(surface, color, points)
        elif direction == 'LEFT':
            points = [
                (center_x - arrow_size, center_y),
                (center_x + arrow_size // 2, center_y - arrow_size),
                (center_x + arrow_size // 2, center_y + arrow_size)
            ]
            pygame.draw.polygon(surface, color, points)
        elif direction == 'RIGHT':
            points = [
                (center_x + arrow_size, center_y),
                (center_x - arrow_size // 2, center_y - arrow_size),
                (center_x - arrow_size // 2, center_y + arrow_size)
            ]
            pygame.draw.polygon(surface, color, points)
        elif direction == 'SPACE':
            # Draw a small bar
            rect = pygame.Rect(x, center_y - 2, size, 4)
            pygame.draw.rect(surface, color, rect, border_radius=1)

        return size + 4

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the combo list."""
        if not self.visible:
            return

        if self.font is None:
            self.font = pygame.font.Font(None, 28)
            self.font_small = pygame.font.Font(None, 22)

        # Draw background
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, (25, 25, 45), bg_rect, border_radius=10)
        pygame.draw.rect(surface, (70, 70, 100), bg_rect,
                         width=2, border_radius=10)

        # Draw title
        title = self.font.render("DAFTAR KOMBO", True, (255, 200, 100))
        title_rect = title.get_rect(
            centerx=self.x + self.width // 2, y=self.y + 10)
        surface.blit(title, title_rect)

        # Draw separator
        pygame.draw.line(surface, (70, 70, 100),
                         (self.x + 10, self.y + 40),
                         (self.x + self.width - 10, self.y + 40), 2)

        # Draw combo entries
        y_offset = 50
        for i, (sequence, name) in enumerate(self.combos):
            if y_offset > self.height - 30:
                break

            # Combo number
            num_text = self.font_small.render(f"{i+1}.", True, (150, 150, 180))
            surface.blit(num_text, (self.x + 10, self.y + y_offset))

            # Combo name
            name_color = (200, 200, 255)
            name_text = self.font_small.render(name, True, name_color)
            surface.blit(name_text, (self.x + 35, self.y + y_offset))

            # Sequence using arrows
            arrow_x = self.x + 10
            arrow_y = self.y + y_offset + 25
            for direction in sequence:
                arrow_x += self._draw_mini_arrow(surface,
                                                 arrow_x, arrow_y, direction, 14)

            y_offset += 48


class ChargeIndicator(UIComponent):
    """
    Visual indicator for the charged combo mechanic.
    Shows when space is being held and the charge progress.

    Zones:
    - normal (< 2s): Green - release for normal combo
    - charging (1.9-2s): Blue - very small dead zone
    - super (2-3s): Gold - release for SUPER combo
    - cancel (> 3s): Red - combo will be cancelled
    """

    # Zone thresholds as percentage of 3 seconds
    NORMAL_ZONE = 1.9 / 3.0    # 0 to ~63% (0-1.9s)
    CHARGING_ZONE = 2.0 / 3.0  # ~63% to 66% (1.9-2s) - very small dead zone
    SUPER_ZONE = 1.0           # 66% to 100% (2-3s)

    def __init__(self, x: int, y: int, width: int, height: int):
        """Initialize the charge indicator."""
        super().__init__(x, y, width, height)
        self.charge_progress: float = 0.0
        self.is_charging: bool = False
        self.charge_zone: str = 'none'
        self.font = None
        self.font_small = None

    def set_charge(self, progress: float, zone: str) -> None:
        """
        Set the current charge state.

        Args:
            progress: 0.0 to 1.0 (representing 0-3 seconds)
            zone: 'none', 'normal', 'charging', 'super', or 'cancel'
        """
        self.charge_progress = progress
        self.charge_zone = zone
        self.is_charging = zone != 'none'

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the charge indicator."""
        if not self.visible or not self.is_charging:
            return

        if self.font is None:
            self.font = pygame.font.Font(None, 28)
            self.font_small = pygame.font.Font(None, 20)

        # Draw background
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, (40, 40, 60), bg_rect, border_radius=8)

        # Draw charge bar
        bar_margin = 10
        bar_width = self.width - bar_margin * 2
        bar_height = 24
        bar_x = self.x + bar_margin
        bar_y = self.y + 35

        # Background bar with zone sections
        pygame.draw.rect(surface, (60, 60, 80),
                         (bar_x, bar_y, bar_width, bar_height), border_radius=5)

        # Draw zone backgrounds
        normal_width = int(bar_width * self.NORMAL_ZONE)
        charging_width = int(
            bar_width * (self.CHARGING_ZONE - self.NORMAL_ZONE))
        super_width = int(bar_width * (self.SUPER_ZONE - self.CHARGING_ZONE))

        # Zone background colors (dim)
        pygame.draw.rect(surface, (30, 60, 30),  # Dim green
                         (bar_x, bar_y, normal_width, bar_height), border_radius=5)
        pygame.draw.rect(surface, (30, 30, 60),  # Dim blue
                         (bar_x + normal_width, bar_y, charging_width, bar_height))
        pygame.draw.rect(surface, (60, 50, 20),  # Dim gold
                         (bar_x + normal_width + charging_width,
                          bar_y, super_width, bar_height),
                         border_radius=5)

        # Progress bar
        if self.charge_progress > 0:
            progress_width = int(bar_width * min(1.0, self.charge_progress))

            # Color based on zone
            if self.charge_zone == 'normal':
                color = (100, 255, 150)  # Green
            elif self.charge_zone == 'charging':
                color = (100, 150, 255)  # Blue
            elif self.charge_zone == 'super':
                color = (255, 215, 0)    # Gold
            else:  # cancel
                color = (255, 80, 80)    # Red

            pygame.draw.rect(surface, color,
                             (bar_x, bar_y, progress_width, bar_height), border_radius=5)

        # Draw zone markers
        marker1_x = bar_x + normal_width
        marker2_x = bar_x + normal_width + charging_width

        pygame.draw.line(surface, (150, 150, 150),
                         (marker1_x, bar_y - 3), (marker1_x, bar_y + bar_height + 3), 2)
        pygame.draw.line(surface, (255, 215, 0),
                         (marker2_x, bar_y - 3), (marker2_x, bar_y + bar_height + 3), 2)

        # Draw zone labels below bar
        labels_y = bar_y + bar_height + 5

        normal_label = self.font_small.render("<2s", True, (100, 200, 100))
        surface.blit(normal_label, (bar_x + normal_width // 2 -
                     normal_label.get_width() // 2, labels_y))

        super_label = self.font_small.render("2-3s", True, (255, 215, 0))
        super_x = bar_x + normal_width + charging_width + \
            super_width // 2 - super_label.get_width() // 2
        surface.blit(super_label, (super_x, labels_y))

        # Draw main label
        labels = {
            'normal': ("RELEASE = Normal Combo", (100, 255, 150)),
            'charging': ("Keep holding...", (150, 150, 200)),
            'super': ("RELEASE = SUPER COMBO!", (255, 215, 0)),
            'cancel': ("TOO LONG - CANCELLED!", (255, 80, 80))
        }

        label_text, label_color = labels.get(
            self.charge_zone, ("", (150, 150, 150)))
        text = self.font.render(label_text, True, label_color)
        text_rect = text.get_rect(
            centerx=self.x + self.width // 2, y=self.y + 8)
        surface.blit(text, text_rect)

        # Draw border
        border_colors = {
            'normal': (100, 255, 150),
            'charging': (100, 150, 255),
            'super': (255, 215, 0),
            'cancel': (255, 80, 80)
        }
        border_color = border_colors.get(self.charge_zone, (80, 80, 120))
        pygame.draw.rect(surface, border_color, bg_rect,
                         width=2, border_radius=8)
