"""
Game Controller module for Fighting Game Combo Detector.

This module handles keyboard input, timing validation, and 
manages the interaction between user input and the state machine.
"""

import time
from typing import Optional, Callable, List
from state_machine import ComboStateMachine
from combo_definitions import get_all_combos


class GameController:
    """
    Controller class that manages input processing and timing.

    This class is responsible for:
    - Processing keyboard input
    - Enforcing the 1-second timeout between inputs
    - Tracking space key hold duration for charged combos
    - Communicating with the state machine
    - Managing freeze state after combo execution

    Attributes:
        state_machine: The combo detection state machine
        last_input_time: Timestamp of the last valid input
        space_press_time: Timestamp when space was pressed (for charged combo)
        is_space_held: Whether space is currently being held
        timeout: Maximum allowed time between inputs (in seconds)
        charge_min: Minimum hold time for charged combo (in seconds)
        charge_max: Maximum hold time for charged combo (in seconds)
    """

    TIMEOUT = 1.0  # 1 second timeout between inputs
    NORMAL_COMBO_MAX = 1.9  # < 1.9 seconds = normal combo
    CHARGE_MIN = 2.0  # Minimum hold time for super combo
    CHARGE_MAX = 3.0  # Maximum hold time for super combo (> 3s = cancel)
    FREEZE_DURATION = 1.0  # 1 seconds freeze after combo

    def __init__(self):
        """Initialize the game controller."""
        self.state_machine = ComboStateMachine()
        self.state_machine.build_from_combos(get_all_combos())

        self.last_input_time: float = 0.0
        self.space_press_time: float = 0.0
        self.is_space_held: bool = False
        self.pending_combo: Optional[str] = None

        # Freeze state management
        self.is_frozen: bool = False
        self.freeze_start_time: float = 0.0
        self.frozen_state_id: int = 0
        self.frozen_history: List[str] = []

        # Callbacks for GUI updates
        self.on_combo_detected: Optional[Callable[[str, bool], None]] = None
        self.on_input_received: Optional[Callable[[str], None]] = None
        self.on_timeout: Optional[Callable[[], None]] = None
        self.on_state_change: Optional[Callable[[int, List[str]], None]] = None
        self.on_charge_update: Optional[Callable[[float], None]] = None
        self.on_freeze_end: Optional[Callable[[], None]] = None
        self.on_combo_cancelled: Optional[Callable[[], None]] = None

        # Input history for display (stores direction names, not symbols)
        self.display_history: List[str] = []

    def set_combo_callback(self, callback: Callable[[str, bool], None]) -> None:
        """Set callback for when a combo is detected."""
        self.on_combo_detected = callback

    def set_input_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for when input is received."""
        self.on_input_received = callback

    def set_timeout_callback(self, callback: Callable[[], None]) -> None:
        """Set callback for when timeout occurs."""
        self.on_timeout = callback

    def set_state_change_callback(self, callback: Callable[[int, List[str]], None]) -> None:
        """Set callback for when state changes."""
        self.on_state_change = callback

    def set_charge_callback(self, callback: Callable[[float], None]) -> None:
        """Set callback for charge progress updates."""
        self.on_charge_update = callback

    def set_freeze_end_callback(self, callback: Callable[[], None]) -> None:
        """Set callback for when freeze ends."""
        self.on_freeze_end = callback

    def set_combo_cancelled_callback(self, callback: Callable[[], None]) -> None:
        """Set callback for when combo is cancelled (held too long)."""
        self.on_combo_cancelled = callback

    def is_space_available(self) -> bool:
        """
        Check if SPACE is a valid input at the current state.
        SPACE can only be pressed when it's a valid transition.
        """
        if self.is_frozen:
            return False
        return self.state_machine.current_state.has_transition('SPACE')

    def check_timeout(self) -> bool:
        """
        Check if the timeout has been exceeded.
        Timer is frozen while space is held.

        Returns:
            True if timeout exceeded and reset occurred, False otherwise
        """
        if self.is_frozen:
            return False

        # Don't check timeout while space is held (timer frozen)
        if self.is_space_held:
            return False

        if self.last_input_time == 0:
            return False

        current_time = time.time()
        if current_time - self.last_input_time > self.TIMEOUT:
            self._reset_with_callback()
            return True
        return False

    def _check_freeze_timeout(self) -> None:
        """Check if freeze duration has ended."""
        if not self.is_frozen:
            return

        current_time = time.time()
        if current_time - self.freeze_start_time >= self.FREEZE_DURATION:
            self._end_freeze()

    def _check_space_overhold(self) -> bool:
        """
        Check if space has been held too long (> 3 seconds).
        If so, cancel the combo.

        Returns:
            True if combo was cancelled, False otherwise
        """
        if not self.is_space_held:
            return False

        current_time = time.time()
        hold_duration = current_time - self.space_press_time

        if hold_duration > self.CHARGE_MAX:
            # Cancel combo - held too long
            self.is_space_held = False
            self._reset_with_callback()
            if self.on_combo_cancelled:
                self.on_combo_cancelled()
            return True
        return False

    def _start_freeze(self) -> None:
        """Start the freeze state after combo execution."""
        self.is_frozen = True
        self.freeze_start_time = time.time()
        self.frozen_state_id = self.state_machine.get_current_state_id()
        self.frozen_history = self.display_history.copy()

    def _end_freeze(self) -> None:
        """End the freeze state and reset."""
        self.is_frozen = False
        self.state_machine.reset()
        self.display_history = []
        self.last_input_time = 0.0

        if self.on_freeze_end:
            self.on_freeze_end()

        self._notify_state_change()

    def _reset_with_callback(self) -> None:
        """Reset state machine and trigger timeout callback."""
        if self.is_frozen:
            return

        self.state_machine.reset()
        self.display_history = []
        self.last_input_time = 0.0

        if self.on_timeout:
            self.on_timeout()

        self._notify_state_change()

    def _notify_state_change(self) -> None:
        """Notify listeners about state change."""
        if self.on_state_change:
            state_id = self.state_machine.get_current_state_id()
            possible = self.state_machine.get_possible_transitions()
            self.on_state_change(state_id, possible)

    def process_key_down(self, key: str) -> Optional[str]:
        """
        Process a key press event.

        Args:
            key: The key that was pressed ('UP', 'DOWN', 'LEFT', 'RIGHT', 'SPACE')

        Returns:
            The combo name if detected (for non-space keys), None otherwise
        """
        # Block all input during freeze
        if self.is_frozen:
            return None

        current_time = time.time()

        # Handle space key specially for charged combo
        if key == 'SPACE':
            # Only allow space if it's a valid transition
            if not self.is_space_available():
                return None
            self.space_press_time = current_time
            self.is_space_held = True
            return None

        # Check timeout for non-space keys
        if self.last_input_time > 0 and current_time - self.last_input_time > self.TIMEOUT:
            self._reset_with_callback()

        # Update last input time
        self.last_input_time = current_time

        # Add to display history (store direction name, not symbol)
        self.display_history.append(key)

        # Notify input received
        if self.on_input_received:
            self.on_input_received(key)

        # Process through state machine
        result = self.state_machine.process_input(key)

        # Notify state change
        self._notify_state_change()

        if result:
            # Combo detected (shouldn't happen without SPACE, but handle it)
            self._start_freeze()
            if self.on_combo_detected:
                self.on_combo_detected(result, False)

        return result

    def process_key_up(self, key: str) -> Optional[str]:
        """
        Process a key release event.

        Args:
            key: The key that was released

        Returns:
            The combo name if space was released and combo detected, None otherwise
        """
        # Block all input during freeze
        if self.is_frozen:
            self.is_space_held = False
            return None

        if key != 'SPACE' or not self.is_space_held:
            return None

        current_time = time.time()
        hold_duration = current_time - self.space_press_time
        self.is_space_held = False

        # Check if held too long (> 3 seconds) - cancel combo
        if hold_duration > self.CHARGE_MAX:
            self._reset_with_callback()
            if self.on_combo_cancelled:
                self.on_combo_cancelled()
            return None

        # Update last input time
        self.last_input_time = current_time

        # Add space to display history
        self.display_history.append('SPACE')

        # Notify input received
        if self.on_input_received:
            self.on_input_received('SPACE')

        # Process through state machine
        result = self.state_machine.process_input('SPACE')

        # Notify state change
        self._notify_state_change()

        if result:
            # Determine combo type based on hold duration:
            # < 1 second = normal combo
            # 2-3 seconds = super combo
            # Note: 1-2 seconds is a "dead zone" - still normal combo
            is_charged = self.CHARGE_MIN <= hold_duration <= self.CHARGE_MAX

            combo_name = result
            if is_charged:
                combo_name = f"SUPER {result}"

            # Start freeze state
            self._start_freeze()

            if self.on_combo_detected:
                self.on_combo_detected(combo_name, is_charged)

            return combo_name

        return None

    def get_charge_progress(self) -> float:
        """
        Get the current charge progress for UI display.

        Progress zones:
        - 0.0 to 0.33: Normal zone (< 1 second)
        - 0.33 to 0.66: Dead zone (1-2 seconds) 
        - 0.66 to 1.0: Super zone (2-3 seconds)
        - > 1.0: Overcharge/cancel zone (> 3 seconds)

        Returns:
            Float indicating charge progress
        """
        if not self.is_space_held or self.is_frozen:
            return 0.0

        current_time = time.time()
        hold_duration = current_time - self.space_press_time

        # Map hold duration to progress (0 to 3 seconds -> 0 to 1.0)
        return min(1.0, hold_duration / self.CHARGE_MAX)

    def get_charge_zone(self) -> str:
        """
        Get the current charge zone name.

        Returns:
            'none', 'normal', 'charging', 'super', or 'cancel'
        """
        if not self.is_space_held or self.is_frozen:
            return 'none'

        current_time = time.time()
        hold_duration = current_time - self.space_press_time

        if hold_duration < self.NORMAL_COMBO_MAX:
            return 'normal'
        elif hold_duration < self.CHARGE_MIN:
            return 'charging'
        elif hold_duration <= self.CHARGE_MAX:
            return 'super'
        else:
            return 'cancel'

    def is_in_charge_zone(self) -> bool:
        """Check if currently in the super combo zone (2-3 seconds)."""
        return self.get_charge_zone() == 'super'

    def get_time_until_timeout(self) -> float:
        """
        Get time remaining until timeout.
        Returns full timeout if space is held (timer frozen).

        Returns:
            Seconds remaining, or TIMEOUT if no input has been made
        """
        if self.is_frozen or self.last_input_time == 0:
            return self.TIMEOUT

        # Timer is frozen while space is held
        if self.is_space_held:
            return self.TIMEOUT

        elapsed = time.time() - self.last_input_time
        remaining = self.TIMEOUT - elapsed
        return max(0.0, remaining)

    def get_freeze_time_remaining(self) -> float:
        """Get time remaining in freeze state."""
        if not self.is_frozen:
            return 0.0

        elapsed = time.time() - self.freeze_start_time
        remaining = self.FREEZE_DURATION - elapsed
        return max(0.0, remaining)

    def get_current_progress(self) -> float:
        """Get progress towards completing a combo."""
        if self.is_frozen:
            return 1.0  # Show 100% during freeze
        return self.state_machine.get_progress_percentage()

    def get_display_history(self) -> List[str]:
        """Get the current input history for display."""
        if self.is_frozen:
            return self.frozen_history.copy()
        return self.display_history.copy()

    def reset(self) -> None:
        """Manually reset the controller state."""
        if self.is_frozen:
            self._end_freeze()
        else:
            self._reset_with_callback()
        self.is_space_held = False
        self.space_press_time = 0.0
        self.pending_combo = None

    def update(self) -> None:
        """
        Update method to be called each frame.
        Handles timeout checking, freeze state, space overhold, and charge progress updates.
        """
        # Check freeze timeout first
        self._check_freeze_timeout()

        # Check if space has been held too long
        self._check_space_overhold()

        # Check for input timeout (only if not frozen and space not held)
        if not self.is_frozen:
            self.check_timeout()

        # Update charge progress if space is held
        if self.is_space_held and self.on_charge_update:
            self.on_charge_update(self.get_charge_progress())
