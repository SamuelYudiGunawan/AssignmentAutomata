"""
Pushdown Automata (PDA) Module for Mathematical Expression Processing.

This module implements a generic Pushdown Automata that can be configured
to validate different types of mathematical expressions (infix, postfix, prefix).

A PDA is formally defined as a 7-tuple (Q, Σ, Γ, δ, q0, Z0, F) where:
- Q = finite set of states
- Σ = input alphabet
- Γ = stack alphabet
- δ = transition function
- q0 = initial state
- Z0 = initial stack symbol
- F = set of accepting states
"""

from typing import Dict, List, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field
from enum import Enum, auto


class StateType(Enum):
    """Enumeration of state types in the PDA."""
    INITIAL = auto()
    NORMAL = auto()
    ACCEPTING = auto()
    ERROR = auto()


@dataclass
class PDAState:
    """
    Represents a state in the Pushdown Automata.
    
    Attributes:
        name: Unique identifier for the state
        state_type: Type of state (initial, normal, accepting, error)
        description: Human-readable description of the state
    """
    name: str
    state_type: StateType = StateType.NORMAL
    description: str = ""
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if isinstance(other, PDAState):
            return self.name == other.name
        return False


@dataclass
class PDATransition:
    """
    Represents a transition in the PDA.
    
    A transition is triggered when:
    - Current state matches from_state
    - Input symbol matches input_symbol (or is epsilon/None)
    - Top of stack matches stack_top (or is epsilon/None)
    
    The transition results in:
    - Moving to to_state
    - Performing stack_action on the stack
    """
    from_state: PDAState
    to_state: PDAState
    input_symbol: Optional[str]  # None for epsilon transition
    stack_top: Optional[str]     # None for any stack top
    stack_action: str            # 'push:X', 'pop', 'none', or 'replace:X'
    description: str = ""
    
    def matches(self, current_state: PDAState, input_sym: Optional[str], 
                stack_top: Optional[str]) -> bool:
        """Check if this transition can be taken given current configuration."""
        if self.from_state != current_state:
            return False
        if self.input_symbol is not None and self.input_symbol != input_sym:
            return False
        if self.stack_top is not None and self.stack_top != stack_top:
            return False
        return True


class PDAStack:
    """
    Stack implementation for the Pushdown Automata.
    
    Provides standard stack operations with history tracking for visualization.
    """
    
    def __init__(self, initial_symbol: str = "Z0"):
        """Initialize stack with bottom marker."""
        self._stack: List[str] = [initial_symbol]
        self._history: List[Tuple[str, List[str]]] = []  # (action, stack_state)
        self._initial_symbol = initial_symbol
    
    def push(self, symbol: str) -> None:
        """Push a symbol onto the stack."""
        self._stack.append(symbol)
        self._history.append(("push:" + symbol, self._stack.copy()))
    
    def pop(self) -> Optional[str]:
        """Pop and return the top symbol, or None if only bottom marker remains."""
        if len(self._stack) > 1:
            symbol = self._stack.pop()
            self._history.append(("pop:" + symbol, self._stack.copy()))
            return symbol
        return None
    
    def peek(self) -> Optional[str]:
        """Return the top symbol without removing it."""
        return self._stack[-1] if self._stack else None
    
    def is_empty(self) -> bool:
        """Check if stack only contains the bottom marker."""
        return len(self._stack) <= 1
    
    def size(self) -> int:
        """Return number of elements (excluding bottom marker)."""
        return len(self._stack) - 1
    
    def clear(self) -> None:
        """Reset stack to initial state."""
        self._stack = [self._initial_symbol]
        self._history = []
    
    def get_contents(self) -> List[str]:
        """Return copy of current stack contents."""
        return self._stack.copy()
    
    def get_history(self) -> List[Tuple[str, List[str]]]:
        """Return history of stack operations."""
        return self._history.copy()
    
    def __str__(self) -> str:
        return f"Stack: {self._stack}"
    
    def __repr__(self) -> str:
        return f"PDAStack({self._stack})"


@dataclass
class PDAConfiguration:
    """
    Represents an instantaneous description (ID) of the PDA.
    
    An ID is a triple (q, w, γ) where:
    - q is the current state
    - w is the remaining input
    - γ is the current stack contents
    """
    state: PDAState
    remaining_input: str
    stack_contents: List[str]
    
    def __str__(self) -> str:
        stack_str = ''.join(reversed(self.stack_contents))
        return f"({self.state.name}, {self.remaining_input or 'ε'}, {stack_str})"


class PushdownAutomata:
    """
    Generic Pushdown Automata implementation.
    
    This class provides a flexible PDA that can be configured with custom
    states and transitions for different validation tasks.
    """
    
    def __init__(self, name: str = "PDA"):
        """Initialize an empty PDA."""
        self.name = name
        self.states: Dict[str, PDAState] = {}
        self.transitions: List[PDATransition] = []
        self.initial_state: Optional[PDAState] = None
        self.current_state: Optional[PDAState] = None
        self.stack = PDAStack()
        self.input_alphabet: set = set()
        self.stack_alphabet: set = {"Z0"}
        
        # For tracking execution
        self._execution_history: List[PDAConfiguration] = []
        self._transition_history: List[PDATransition] = []
    
    def add_state(self, name: str, state_type: StateType = StateType.NORMAL,
                  description: str = "") -> PDAState:
        """Add a state to the PDA."""
        state = PDAState(name, state_type, description)
        self.states[name] = state
        
        if state_type == StateType.INITIAL:
            self.initial_state = state
            self.current_state = state
        
        return state
    
    def add_transition(self, from_state: str, to_state: str,
                       input_symbol: Optional[str], stack_top: Optional[str],
                       stack_action: str, description: str = "") -> PDATransition:
        """
        Add a transition to the PDA.
        
        Args:
            from_state: Name of source state
            to_state: Name of destination state
            input_symbol: Input symbol to match (None for epsilon)
            stack_top: Stack top to match (None for any)
            stack_action: One of 'push:X', 'pop', 'none', 'replace:X'
            description: Human-readable description
        
        Returns:
            The created transition
        """
        from_s = self.states[from_state]
        to_s = self.states[to_state]
        
        transition = PDATransition(
            from_state=from_s,
            to_state=to_s,
            input_symbol=input_symbol,
            stack_top=stack_top,
            stack_action=stack_action,
            description=description
        )
        
        self.transitions.append(transition)
        
        if input_symbol:
            self.input_alphabet.add(input_symbol)
        
        return transition
    
    def reset(self) -> None:
        """Reset PDA to initial configuration."""
        self.current_state = self.initial_state
        self.stack.clear()
        self._execution_history = []
        self._transition_history = []
    
    def _execute_stack_action(self, action: str) -> bool:
        """Execute a stack action. Returns False if action fails."""
        if action == "none":
            return True
        elif action.startswith("push:"):
            symbol = action[5:]
            self.stack.push(symbol)
            self.stack_alphabet.add(symbol)
            return True
        elif action == "pop":
            result = self.stack.pop()
            return result is not None
        elif action.startswith("replace:"):
            symbol = action[8:]
            self.stack.pop()
            self.stack.push(symbol)
            self.stack_alphabet.add(symbol)
            return True
        return False
    
    def _find_transition(self, input_symbol: Optional[str]) -> Optional[PDATransition]:
        """Find a valid transition for the current configuration."""
        stack_top = self.stack.peek()
        
        for transition in self.transitions:
            if transition.matches(self.current_state, input_symbol, stack_top):
                return transition
        
        # Try epsilon transition if no match found
        if input_symbol is not None:
            for transition in self.transitions:
                if transition.matches(self.current_state, None, stack_top):
                    return transition
        
        return None
    
    def step(self, input_symbol: str) -> Tuple[bool, Optional[str]]:
        """
        Process a single input symbol.
        
        Args:
            input_symbol: The symbol to process
            
        Returns:
            Tuple of (success, error_message)
        """
        # Record current configuration
        config = PDAConfiguration(
            state=self.current_state,
            remaining_input=input_symbol,
            stack_contents=self.stack.get_contents()
        )
        self._execution_history.append(config)
        
        # Find valid transition
        transition = self._find_transition(input_symbol)
        
        if transition is None:
            # No valid transition - go to error state if exists
            if "q_error" in self.states:
                self.current_state = self.states["q_error"]
            return False, f"No valid transition for input '{input_symbol}' in state '{self.current_state.name}'"
        
        # Execute stack action
        if not self._execute_stack_action(transition.stack_action):
            if "q_error" in self.states:
                self.current_state = self.states["q_error"]
            return False, f"Stack action '{transition.stack_action}' failed"
        
        # Transition to new state
        self.current_state = transition.to_state
        self._transition_history.append(transition)
        
        return True, None
    
    def process(self, input_string: str) -> Tuple[bool, str, List[PDAConfiguration]]:
        """
        Process an entire input string.
        
        Args:
            input_string: The string to process
            
        Returns:
            Tuple of (accepted, message, execution_history)
        """
        self.reset()
        
        for symbol in input_string:
            success, error = self.step(symbol)
            if not success:
                return False, error, self._execution_history
        
        # Check final state
        if self.current_state.state_type == StateType.ACCEPTING:
            return True, "Input accepted", self._execution_history
        elif self.current_state.state_type == StateType.ERROR:
            return False, "Ended in error state", self._execution_history
        else:
            return False, f"Ended in non-accepting state '{self.current_state.name}'", self._execution_history
    
    def is_accepting(self) -> bool:
        """Check if current state is an accepting state."""
        return self.current_state and self.current_state.state_type == StateType.ACCEPTING
    
    def get_execution_history(self) -> List[PDAConfiguration]:
        """Return the execution history."""
        return self._execution_history.copy()
    
    def get_transition_history(self) -> List[PDATransition]:
        """Return the transition history."""
        return self._transition_history.copy()
    
    def get_current_configuration(self) -> PDAConfiguration:
        """Get current PDA configuration."""
        return PDAConfiguration(
            state=self.current_state,
            remaining_input="",
            stack_contents=self.stack.get_contents()
        )
    
    def get_diagram_data(self) -> Dict:
        """
        Generate data for creating automata diagram.
        
        Returns:
            Dictionary containing states and transitions for visualization
        """
        states_data = []
        for name, state in self.states.items():
            states_data.append({
                'name': name,
                'type': state.state_type.name,
                'description': state.description,
                'is_initial': state == self.initial_state,
                'is_accepting': state.state_type == StateType.ACCEPTING
            })
        
        transitions_data = []
        for t in self.transitions:
            transitions_data.append({
                'from': t.from_state.name,
                'to': t.to_state.name,
                'input': t.input_symbol or 'ε',
                'stack_top': t.stack_top or 'any',
                'action': t.stack_action,
                'label': f"{t.input_symbol or 'ε'}, {t.stack_top or 'any'} → {t.stack_action}"
            })
        
        return {
            'name': self.name,
            'states': states_data,
            'transitions': transitions_data,
            'input_alphabet': list(self.input_alphabet),
            'stack_alphabet': list(self.stack_alphabet)
        }
    
    def __str__(self) -> str:
        return f"PDA '{self.name}': {len(self.states)} states, {len(self.transitions)} transitions"

