"""
GUI Components for PDA Expression Validator.

Reusable UI components built with Pygame for the expression
validator and converter application.
"""

import pygame
from typing import List, Tuple, Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum


# Color palette - Modern dark theme with teal accents
class Colors:
    """Color definitions for the UI."""
    # Background colors
    BG_DARK = (18, 18, 24)
    BG_MEDIUM = (28, 28, 36)
    BG_LIGHT = (38, 38, 48)
    BG_PANEL = (32, 32, 42)
    
    # Accent colors
    ACCENT_PRIMARY = (0, 188, 180)      # Teal
    ACCENT_SECONDARY = (255, 107, 107)  # Coral
    ACCENT_SUCCESS = (80, 200, 120)     # Green
    ACCENT_ERROR = (255, 82, 82)        # Red
    ACCENT_WARNING = (255, 193, 7)      # Amber
    
    # Text colors
    TEXT_PRIMARY = (240, 240, 245)
    TEXT_SECONDARY = (160, 160, 175)
    TEXT_MUTED = (100, 100, 115)
    TEXT_DARK = (40, 40, 50)
    
    # State colors
    STATE_INITIAL = (100, 149, 237)     # Cornflower blue
    STATE_NORMAL = (150, 150, 165)
    STATE_ACCEPT = (80, 200, 120)       # Green
    STATE_ERROR = (255, 82, 82)         # Red
    STATE_CURRENT = (255, 215, 0)       # Gold
    
    # Border colors
    BORDER_DEFAULT = (60, 60, 75)
    BORDER_FOCUS = (0, 188, 180)
    BORDER_ERROR = (255, 82, 82)


class FontManager:
    """Manages fonts for the application."""
    
    _fonts: Dict[str, pygame.font.Font] = {}
    _initialized = False
    
    @classmethod
    def init(cls):
        """Initialize fonts."""
        if cls._initialized:
            return
        
        pygame.font.init()
        
        # Try to load modern fonts, fallback to system fonts
        font_names = ['Consolas', 'Monaco', 'Menlo', 'DejaVu Sans Mono', 'monospace']
        
        cls._fonts['title'] = pygame.font.SysFont('Segoe UI', 32, bold=True)
        cls._fonts['heading'] = pygame.font.SysFont('Segoe UI', 24, bold=True)
        cls._fonts['body'] = pygame.font.SysFont('Segoe UI', 18)
        cls._fonts['small'] = pygame.font.SysFont('Segoe UI', 14)
        cls._fonts['mono'] = pygame.font.SysFont('Consolas', 16)
        cls._fonts['mono_small'] = pygame.font.SysFont('Consolas', 14)
        cls._fonts['button'] = pygame.font.SysFont('Segoe UI', 16, bold=True)
        
        cls._initialized = True
    
    @classmethod
    def get(cls, name: str) -> pygame.font.Font:
        """Get a font by name."""
        if not cls._initialized:
            cls.init()
        return cls._fonts.get(name, cls._fonts['body'])


@dataclass
class Rect:
    """Rectangle helper class."""
    x: int
    y: int
    width: int
    height: int
    
    def to_pygame(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def contains(self, point: Tuple[int, int]) -> bool:
        px, py = point
        return (self.x <= px <= self.x + self.width and 
                self.y <= py <= self.y + self.height)


class Component:
    """Base class for all UI components."""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = Rect(x, y, width, height)
        self.visible = True
        self.enabled = True
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the component. Override in subclasses."""
        pass
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame event. Returns True if event was consumed."""
        return False
    
    def update(self, dt: float) -> None:
        """Update component state. dt is delta time in seconds."""
        pass


class Label(Component):
    """Text label component."""
    
    def __init__(self, x: int, y: int, text: str, 
                 font_name: str = 'body',
                 color: Tuple[int, int, int] = Colors.TEXT_PRIMARY,
                 max_width: Optional[int] = None):
        super().__init__(x, y, 0, 0)
        self.text = text
        self.font_name = font_name
        self.color = color
        self.max_width = max_width
        self._update_size()
    
    def _update_size(self):
        font = FontManager.get(self.font_name)
        self.rect.width, self.rect.height = font.size(self.text)
    
    def set_text(self, text: str):
        self.text = text
        self._update_size()
    
    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        
        font = FontManager.get(self.font_name)
        
        if self.max_width and self.rect.width > self.max_width:
            # Truncate with ellipsis
            text = self.text
            while font.size(text + "...")[0] > self.max_width and len(text) > 0:
                text = text[:-1]
            text += "..." if text != self.text else ""
            rendered = font.render(text, True, self.color)
        else:
            rendered = font.render(self.text, True, self.color)
        
        surface.blit(rendered, (self.rect.x, self.rect.y))


class Button(Component):
    """Clickable button component."""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 text: str, on_click: Optional[Callable] = None,
                 style: str = 'primary'):
        super().__init__(x, y, width, height)
        self.text = text
        self.on_click = on_click
        self.style = style
        self.hovered = False
        self.pressed = False
    
    def _get_colors(self) -> Tuple[Tuple[int, int, int], ...]:
        """Get background and text colors based on style and state."""
        if self.style == 'primary':
            bg = Colors.ACCENT_PRIMARY
            text = Colors.TEXT_DARK
        elif self.style == 'secondary':
            bg = Colors.BG_LIGHT
            text = Colors.TEXT_PRIMARY
        elif self.style == 'danger':
            bg = Colors.ACCENT_ERROR
            text = Colors.TEXT_PRIMARY
        elif self.style == 'success':
            bg = Colors.ACCENT_SUCCESS
            text = Colors.TEXT_DARK
        else:
            bg = Colors.BG_MEDIUM
            text = Colors.TEXT_PRIMARY
        
        if not self.enabled:
            bg = tuple(c // 2 for c in bg)
            text = Colors.TEXT_MUTED
        elif self.pressed:
            bg = tuple(max(0, c - 30) for c in bg)
        elif self.hovered:
            bg = tuple(min(255, c + 20) for c in bg)
        
        return bg, text
    
    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        
        bg_color, text_color = self._get_colors()
        
        # Draw rounded rectangle background
        pygame.draw.rect(surface, bg_color, self.rect.to_pygame(), border_radius=8)
        
        # Draw border on hover
        if self.hovered and self.enabled:
            pygame.draw.rect(surface, Colors.BORDER_FOCUS, self.rect.to_pygame(), 
                           width=2, border_radius=8)
        
        # Draw text centered
        font = FontManager.get('button')
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.to_pygame().center)
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.contains(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.contains(event.pos):
                self.pressed = True
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                was_pressed = self.pressed
                self.pressed = False
                if was_pressed and self.rect.contains(event.pos) and self.on_click:
                    self.on_click()
                    return True
        
        return False


class InputField(Component):
    """Text input field component."""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 placeholder: str = "", on_change: Optional[Callable] = None,
                 on_submit: Optional[Callable] = None):
        super().__init__(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.on_change = on_change
        self.on_submit = on_submit
        self.focused = False
        self.cursor_pos = 0
        self.cursor_visible = True
        self.cursor_timer = 0
    
    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        
        # Background
        bg_color = Colors.BG_LIGHT if self.focused else Colors.BG_MEDIUM
        pygame.draw.rect(surface, bg_color, self.rect.to_pygame(), border_radius=6)
        
        # Border
        border_color = Colors.BORDER_FOCUS if self.focused else Colors.BORDER_DEFAULT
        pygame.draw.rect(surface, border_color, self.rect.to_pygame(), 
                        width=2, border_radius=6)
        
        # Text or placeholder
        font = FontManager.get('mono')
        if self.text:
            text_color = Colors.TEXT_PRIMARY
            display_text = self.text
        else:
            text_color = Colors.TEXT_MUTED
            display_text = self.placeholder
        
        text_surface = font.render(display_text, True, text_color)
        text_rect = text_surface.get_rect(midleft=(self.rect.x + 12, 
                                                    self.rect.y + self.rect.height // 2))
        
        # Clip text to input area
        clip_rect = pygame.Rect(self.rect.x + 8, self.rect.y, 
                               self.rect.width - 16, self.rect.height)
        surface.set_clip(clip_rect)
        surface.blit(text_surface, text_rect)
        surface.set_clip(None)
        
        # Cursor
        if self.focused and self.cursor_visible:
            cursor_x = self.rect.x + 12 + font.size(self.text[:self.cursor_pos])[0]
            cursor_y1 = self.rect.y + 8
            cursor_y2 = self.rect.y + self.rect.height - 8
            pygame.draw.line(surface, Colors.ACCENT_PRIMARY, 
                           (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                was_focused = self.focused
                self.focused = self.rect.contains(event.pos)
                if self.focused:
                    # Set cursor position based on click
                    font = FontManager.get('mono')
                    click_x = event.pos[0] - self.rect.x - 12
                    self.cursor_pos = len(self.text)
                    for i in range(len(self.text) + 1):
                        if font.size(self.text[:i])[0] >= click_x:
                            self.cursor_pos = i
                            break
                return self.focused or was_focused
        
        if not self.focused:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
                    if self.on_change:
                        self.on_change(self.text)
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
                    if self.on_change:
                        self.on_change(self.text)
            elif event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)
            elif event.key == pygame.K_RETURN:
                if self.on_submit:
                    self.on_submit(self.text)
            elif event.unicode and event.unicode.isprintable():
                self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                self.cursor_pos += 1
                if self.on_change:
                    self.on_change(self.text)
            
            return True
        
        return False
    
    def update(self, dt: float) -> None:
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible
    
    def set_text(self, text: str):
        """Set the input text programmatically."""
        self.text = text
        self.cursor_pos = len(text)
        if self.on_change:
            self.on_change(text)
    
    def clear(self):
        """Clear the input field."""
        self.text = ""
        self.cursor_pos = 0


class Dropdown(Component):
    """Dropdown selection component."""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 options: List[str], selected_index: int = 0,
                 on_change: Optional[Callable] = None):
        super().__init__(x, y, width, height)
        self.options = options
        self.selected_index = selected_index
        self.on_change = on_change
        self.expanded = False
        self.hovered_index = -1
    
    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        
        # Draw main button
        bg_color = Colors.BG_LIGHT if self.expanded else Colors.BG_MEDIUM
        pygame.draw.rect(surface, bg_color, self.rect.to_pygame(), border_radius=6)
        border_color = Colors.BORDER_FOCUS if self.expanded else Colors.BORDER_DEFAULT
        pygame.draw.rect(surface, border_color, self.rect.to_pygame(), 
                        width=2, border_radius=6)
        
        # Draw selected text
        font = FontManager.get('body')
        text = self.options[self.selected_index] if self.options else ""
        text_surface = font.render(text, True, Colors.TEXT_PRIMARY)
        text_rect = text_surface.get_rect(midleft=(self.rect.x + 12, 
                                                    self.rect.y + self.rect.height // 2))
        surface.blit(text_surface, text_rect)
        
        # Draw dropdown arrow
        arrow_x = self.rect.x + self.rect.width - 20
        arrow_y = self.rect.y + self.rect.height // 2
        if self.expanded:
            points = [(arrow_x - 5, arrow_y + 3), (arrow_x + 5, arrow_y + 3), (arrow_x, arrow_y - 3)]
        else:
            points = [(arrow_x - 5, arrow_y - 3), (arrow_x + 5, arrow_y - 3), (arrow_x, arrow_y + 3)]
        pygame.draw.polygon(surface, Colors.TEXT_SECONDARY, points)
        
        # Draw dropdown list if expanded
        if self.expanded:
            list_y = self.rect.y + self.rect.height + 4
            list_height = len(self.options) * 36 + 8
            list_rect = pygame.Rect(self.rect.x, list_y, self.rect.width, list_height)
            
            # Background
            pygame.draw.rect(surface, Colors.BG_PANEL, list_rect, border_radius=6)
            pygame.draw.rect(surface, Colors.BORDER_DEFAULT, list_rect, width=2, border_radius=6)
            
            # Options
            for i, option in enumerate(self.options):
                opt_y = list_y + 4 + i * 36
                opt_rect = pygame.Rect(self.rect.x + 4, opt_y, self.rect.width - 8, 32)
                
                # Highlight
                if i == self.hovered_index:
                    pygame.draw.rect(surface, Colors.ACCENT_PRIMARY, opt_rect, border_radius=4)
                    text_color = Colors.TEXT_DARK
                elif i == self.selected_index:
                    pygame.draw.rect(surface, Colors.BG_LIGHT, opt_rect, border_radius=4)
                    text_color = Colors.ACCENT_PRIMARY
                else:
                    text_color = Colors.TEXT_PRIMARY
                
                text_surface = font.render(option, True, text_color)
                text_rect = text_surface.get_rect(midleft=(opt_rect.x + 8, opt_rect.centery))
                surface.blit(text_surface, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            if self.expanded:
                list_y = self.rect.y + self.rect.height + 4
                for i in range(len(self.options)):
                    opt_y = list_y + 4 + i * 36
                    opt_rect = pygame.Rect(self.rect.x + 4, opt_y, self.rect.width - 8, 32)
                    if opt_rect.collidepoint(event.pos):
                        self.hovered_index = i
                        return True
                self.hovered_index = -1
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.contains(event.pos):
                    self.expanded = not self.expanded
                    return True
                elif self.expanded:
                    list_y = self.rect.y + self.rect.height + 4
                    for i in range(len(self.options)):
                        opt_y = list_y + 4 + i * 36
                        opt_rect = pygame.Rect(self.rect.x + 4, opt_y, self.rect.width - 8, 32)
                        if opt_rect.collidepoint(event.pos):
                            self.selected_index = i
                            self.expanded = False
                            if self.on_change:
                                self.on_change(i, self.options[i])
                            return True
                    self.expanded = False
                    return True
        
        return False
    
    def get_selected(self) -> str:
        """Get the currently selected option."""
        return self.options[self.selected_index] if self.options else ""


class ToggleButtonGroup(Component):
    """A group of toggle buttons where only one can be selected at a time."""
    
    def __init__(self, x: int, y: int, options: List[str], 
                 selected_index: int = 0,
                 on_change: Optional[Callable] = None,
                 button_width: int = 100, button_height: int = 40,
                 spacing: int = 8):
        total_width = len(options) * button_width + (len(options) - 1) * spacing
        super().__init__(x, y, total_width, button_height)
        self.options = options
        self.selected_index = selected_index
        self.on_change = on_change
        self.button_width = button_width
        self.button_height = button_height
        self.spacing = spacing
        self.hovered_index = -1
    
    def _get_button_rect(self, index: int) -> pygame.Rect:
        """Get the rectangle for a button at given index."""
        x = self.rect.x + index * (self.button_width + self.spacing)
        return pygame.Rect(x, self.rect.y, self.button_width, self.button_height)
    
    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        
        font = FontManager.get('button')
        
        for i, option in enumerate(self.options):
            btn_rect = self._get_button_rect(i)
            
            # Determine colors based on state
            if i == self.selected_index:
                bg_color = Colors.ACCENT_PRIMARY
                text_color = Colors.TEXT_DARK
                border_color = Colors.ACCENT_PRIMARY
            elif i == self.hovered_index:
                bg_color = Colors.BG_LIGHT
                text_color = Colors.ACCENT_PRIMARY
                border_color = Colors.ACCENT_PRIMARY
            else:
                bg_color = Colors.BG_MEDIUM
                text_color = Colors.TEXT_PRIMARY
                border_color = Colors.BORDER_DEFAULT
            
            # Draw button background
            pygame.draw.rect(surface, bg_color, btn_rect, border_radius=8)
            pygame.draw.rect(surface, border_color, btn_rect, width=2, border_radius=8)
            
            # Draw text centered
            text_surface = font.render(option, True, text_color)
            text_rect = text_surface.get_rect(center=btn_rect.center)
            surface.blit(text_surface, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            self.hovered_index = -1
            for i in range(len(self.options)):
                if self._get_button_rect(i).collidepoint(event.pos):
                    self.hovered_index = i
                    return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for i in range(len(self.options)):
                    if self._get_button_rect(i).collidepoint(event.pos):
                        if i != self.selected_index:
                            self.selected_index = i
                            if self.on_change:
                                self.on_change(i, self.options[i])
                        return True
        
        return False
    
    def get_selected(self) -> str:
        """Get the currently selected option."""
        return self.options[self.selected_index] if self.options else ""
    
    def set_selected(self, index: int):
        """Set the selected index."""
        if 0 <= index < len(self.options):
            self.selected_index = index


class Panel(Component):
    """Container panel with background and border."""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 title: str = "", padding: int = 16):
        super().__init__(x, y, width, height)
        self.title = title
        self.padding = padding
        self.children: List[Component] = []
    
    def add_child(self, child: Component) -> None:
        """Add a child component to the panel."""
        self.children.append(child)
    
    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        
        # Background
        pygame.draw.rect(surface, Colors.BG_PANEL, self.rect.to_pygame(), border_radius=12)
        pygame.draw.rect(surface, Colors.BORDER_DEFAULT, self.rect.to_pygame(), 
                        width=1, border_radius=12)
        
        # Title
        if self.title:
            font = FontManager.get('heading')
            title_surface = font.render(self.title, True, Colors.TEXT_PRIMARY)
            surface.blit(title_surface, (self.rect.x + self.padding, 
                                         self.rect.y + self.padding))
        
        # Draw children
        for child in self.children:
            child.draw(surface)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        for child in reversed(self.children):
            if child.handle_event(event):
                return True
        return False
    
    def update(self, dt: float) -> None:
        for child in self.children:
            child.update(dt)


class ValidationPanel(Panel):
    """Panel for displaying validation results."""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height, "Validation Result", 16)
        self.is_valid = None
        self.message = ""
        self.trace: List[str] = []
        self.scroll_offset = 0
    
    def set_result(self, is_valid: bool, message: str, trace: List[str]):
        """Set the validation result to display."""
        self.is_valid = is_valid
        self.message = message
        self.trace = trace
        self.scroll_offset = 0
    
    def clear(self):
        """Clear the validation result."""
        self.is_valid = None
        self.message = ""
        self.trace = []
    
    def _draw_checkmark(self, surface: pygame.Surface, x: int, y: int, size: int, color: Tuple[int, int, int]):
        """Draw a checkmark icon."""
        # Checkmark points
        points = [
            (x + size * 0.2, y + size * 0.5),
            (x + size * 0.4, y + size * 0.7),
            (x + size * 0.8, y + size * 0.3)
        ]
        pygame.draw.lines(surface, color, False, points, 4)
    
    def _draw_cross(self, surface: pygame.Surface, x: int, y: int, size: int, color: Tuple[int, int, int]):
        """Draw an X (cross) icon."""
        margin = size * 0.25
        pygame.draw.line(surface, color, 
                        (x + margin, y + margin), 
                        (x + size - margin, y + size - margin), 4)
        pygame.draw.line(surface, color, 
                        (x + size - margin, y + margin), 
                        (x + margin, y + size - margin), 4)
    
    def draw(self, surface: pygame.Surface) -> None:
        super().draw(surface)
        
        if not self.visible:
            return
        
        content_y = self.rect.y + 56
        
        if self.is_valid is not None:
            # Status indicator with icon
            status_color = Colors.ACCENT_SUCCESS if self.is_valid else Colors.ACCENT_ERROR
            
            # Draw icon circle background
            icon_size = 28
            icon_x = self.rect.x + self.padding
            icon_y = content_y
            
            # Draw filled circle
            center = (icon_x + icon_size // 2, icon_y + icon_size // 2)
            pygame.draw.circle(surface, status_color, center, icon_size // 2)
            
            # Draw icon (checkmark or cross)
            if self.is_valid:
                self._draw_checkmark(surface, icon_x, icon_y, icon_size, Colors.TEXT_DARK)
            else:
                self._draw_cross(surface, icon_x, icon_y, icon_size, Colors.TEXT_PRIMARY)
            
            # Draw status text
            status_text = "VALID" if self.is_valid else "INVALID"
            font = FontManager.get('heading')
            status_surface = font.render(status_text, True, status_color)
            surface.blit(status_surface, (icon_x + icon_size + 12, content_y))
            content_y += 40
            
            # Message
            font = FontManager.get('body')
            msg_surface = font.render(self.message, True, Colors.TEXT_SECONDARY)
            surface.blit(msg_surface, (self.rect.x + self.padding, content_y))
            content_y += 32
            
            # Trace (scrollable)
            if self.trace:
                trace_rect = pygame.Rect(self.rect.x + self.padding, content_y,
                                        self.rect.width - 2*self.padding,
                                        self.rect.height - (content_y - self.rect.y) - self.padding)
                
                pygame.draw.rect(surface, Colors.BG_DARK, trace_rect, border_radius=6)
                
                font = FontManager.get('mono_small')
                surface.set_clip(trace_rect.inflate(-8, -8))
                
                line_height = 20
                visible_lines = (trace_rect.height - 16) // line_height
                
                for i, line in enumerate(self.trace[self.scroll_offset:self.scroll_offset + visible_lines]):
                    y = content_y + 8 + i * line_height
                    line_surface = font.render(line[:80], True, Colors.TEXT_SECONDARY)
                    surface.blit(line_surface, (self.rect.x + self.padding + 8, y))
                
                surface.set_clip(None)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEWHEEL:
            if self.rect.contains(pygame.mouse.get_pos()):
                self.scroll_offset = max(0, min(len(self.trace) - 5, 
                                               self.scroll_offset - event.y))
                return True
        return super().handle_event(event)


class ConversionPanel(Panel):
    """Panel for displaying conversion results."""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height, "Conversion Results", 16)
        self.results: Dict[str, str] = {}
        self.scroll_offset = 0
    
    def set_results(self, infix: str = "", postfix: str = "", prefix: str = ""):
        """Set the conversion results."""
        self.results = {
            "Infix": infix,
            "Postfix": postfix,
            "Prefix": prefix
        }
    
    def clear(self):
        """Clear all results."""
        self.results = {}
    
    def draw(self, surface: pygame.Surface) -> None:
        super().draw(surface)
        
        if not self.visible or not self.results:
            return
        
        content_y = self.rect.y + 56
        font_label = FontManager.get('body')
        font_value = FontManager.get('mono')
        
        for notation, value in self.results.items():
            # Label
            label_surface = font_label.render(f"{notation}:", True, Colors.TEXT_SECONDARY)
            surface.blit(label_surface, (self.rect.x + self.padding, content_y))
            
            # Value box
            value_rect = pygame.Rect(self.rect.x + self.padding, content_y + 24,
                                    self.rect.width - 2*self.padding, 36)
            pygame.draw.rect(surface, Colors.BG_DARK, value_rect, border_radius=6)
            
            if value:
                value_surface = font_value.render(value[:50], True, Colors.ACCENT_PRIMARY)
                surface.blit(value_surface, (value_rect.x + 12, value_rect.y + 8))
            else:
                empty_surface = font_value.render("-", True, Colors.TEXT_MUTED)
                surface.blit(empty_surface, (value_rect.x + 12, value_rect.y + 8))
            
            content_y += 72


class StateVisualizer(Component):
    """Visualizes PDA states and transitions."""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y, width, height)
        self.states: List[Dict] = []
        self.transitions: List[Dict] = []
        self.current_state_name: Optional[str] = None
        self.animation_progress = 0.0
    
    def set_pda_data(self, data: Dict):
        """Set the PDA data for visualization."""
        self.states = data.get('states', [])
        self.transitions = data.get('transitions', [])
    
    def set_current_state(self, state_name: str):
        """Highlight the current state."""
        self.current_state_name = state_name
        self.animation_progress = 0.0
    
    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        
        # Background
        pygame.draw.rect(surface, Colors.BG_PANEL, self.rect.to_pygame(), border_radius=12)
        pygame.draw.rect(surface, Colors.BORDER_DEFAULT, self.rect.to_pygame(),
                        width=1, border_radius=12)
        
        # Title
        font = FontManager.get('heading')
        title = font.render("PDA State Diagram", True, Colors.TEXT_PRIMARY)
        surface.blit(title, (self.rect.x + 16, self.rect.y + 16))
        
        if not self.states:
            # Show placeholder
            font = FontManager.get('body')
            placeholder = font.render("Enter expression and validate to see states", 
                                     True, Colors.TEXT_MUTED)
            placeholder_rect = placeholder.get_rect(center=self.rect.to_pygame().center)
            surface.blit(placeholder, placeholder_rect)
            return
        
        # Calculate state positions
        num_states = len(self.states)
        if num_states == 0:
            return
        
        state_radius = 30
        center_x = self.rect.x + self.rect.width // 2
        center_y = self.rect.y + self.rect.height // 2 + 20
        
        # Position states in a line or circle depending on count
        state_positions = {}
        if num_states <= 5:
            # Linear layout
            spacing = min(120, (self.rect.width - 80) // max(1, num_states))
            start_x = center_x - (num_states - 1) * spacing // 2
            for i, state in enumerate(self.states):
                state_positions[state['name']] = (start_x + i * spacing, center_y)
        else:
            # Circular layout
            import math
            radius = min(self.rect.width, self.rect.height) // 3
            for i, state in enumerate(self.states):
                angle = 2 * math.pi * i / num_states - math.pi / 2
                x = center_x + int(radius * math.cos(angle))
                y = center_y + int(radius * math.sin(angle))
                state_positions[state['name']] = (x, y)
        
        # Draw transitions first (so they're behind states)
        for trans in self.transitions:
            from_pos = state_positions.get(trans['from'])
            to_pos = state_positions.get(trans['to'])
            if from_pos and to_pos:
                # Draw arrow
                pygame.draw.line(surface, Colors.TEXT_MUTED, from_pos, to_pos, 2)
        
        # Draw states
        font = FontManager.get('small')
        for state in self.states:
            pos = state_positions.get(state['name'])
            if not pos:
                continue
            
            # Determine color
            if state['name'] == self.current_state_name:
                color = Colors.STATE_CURRENT
                outline_color = Colors.ACCENT_PRIMARY
            elif state.get('is_accepting'):
                color = Colors.STATE_ACCEPT
                outline_color = Colors.STATE_ACCEPT
            elif state.get('type') == 'ERROR':
                color = Colors.STATE_ERROR
                outline_color = Colors.STATE_ERROR
            elif state.get('is_initial'):
                color = Colors.STATE_INITIAL
                outline_color = Colors.STATE_INITIAL
            else:
                color = Colors.STATE_NORMAL
                outline_color = Colors.TEXT_MUTED
            
            # Draw state circle
            pygame.draw.circle(surface, color, pos, state_radius)
            pygame.draw.circle(surface, outline_color, pos, state_radius, 3)
            
            # Double circle for accepting states
            if state.get('is_accepting'):
                pygame.draw.circle(surface, outline_color, pos, state_radius - 5, 2)
            
            # Arrow for initial state
            if state.get('is_initial'):
                arrow_start = (pos[0] - state_radius - 20, pos[1])
                arrow_end = (pos[0] - state_radius - 5, pos[1])
                pygame.draw.line(surface, outline_color, arrow_start, arrow_end, 2)
                pygame.draw.polygon(surface, outline_color, [
                    arrow_end,
                    (arrow_end[0] - 8, arrow_end[1] - 5),
                    (arrow_end[0] - 8, arrow_end[1] + 5)
                ])
            
            # State name
            name_short = state['name'].replace('q_', '')[:8]
            text_surface = font.render(name_short, True, Colors.TEXT_DARK)
            text_rect = text_surface.get_rect(center=pos)
            surface.blit(text_surface, text_rect)
    
    def update(self, dt: float) -> None:
        self.animation_progress = min(1.0, self.animation_progress + dt * 2)

