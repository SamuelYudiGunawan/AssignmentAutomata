"""
State Machine module for Fighting Game Combo Detection.

This module implements a Trie-based state machine that can efficiently
detect multiple combo sequences simultaneously.
"""

from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, field


@dataclass
class StateNode:
    """
    Represents a single state (node) in the state machine Trie.
    
    Attributes:
        transitions: Dictionary mapping input symbols to next states
        combo_name: Name of the combo if this is an accept state
        is_accept: Boolean indicating if this is an accept state
        state_id: Unique identifier for this state (for diagram reference)
    """
    state_id: int = 0
    transitions: Dict[str, 'StateNode'] = field(default_factory=dict)
    combo_name: Optional[str] = None
    is_accept: bool = False
    
    def add_transition(self, input_symbol: str, next_state: 'StateNode') -> None:
        """
        Add a transition from this state to another state.
        
        Args:
            input_symbol: The input that triggers this transition
            next_state: The destination state
        """
        self.transitions[input_symbol] = next_state
    
    def get_next_state(self, input_symbol: str) -> Optional['StateNode']:
        """
        Get the next state for a given input symbol.
        
        Args:
            input_symbol: The input symbol to process
            
        Returns:
            The next state if transition exists, None otherwise
        """
        return self.transitions.get(input_symbol)
    
    def has_transition(self, input_symbol: str) -> bool:
        """Check if a transition exists for the given input."""
        return input_symbol in self.transitions


class ComboStateMachine:
    """
    A Trie-based state machine for detecting fighting game combos.
    
    This class builds a prefix tree (Trie) from a list of combo sequences,
    allowing efficient detection of multiple overlapping combo patterns.
    
    Attributes:
        root: The initial state (root of the Trie)
        current_state: The current state during input processing
        combo_list: List of all registered combos for reference
    """
    
    def __init__(self):
        """Initialize the state machine with an empty root state."""
        self._state_counter = 0
        self.root = self._create_state()
        self.current_state = self.root
        self.combo_list: List[Tuple[List[str], str]] = []
        self.input_history: List[str] = []
    
    def _create_state(self) -> StateNode:
        """Create a new state with a unique ID."""
        state = StateNode(state_id=self._state_counter)
        self._state_counter += 1
        return state
    
    def build_from_combos(self, combos: List[Tuple[List[str], str]]) -> None:
        """
        Build the Trie structure from a list of combos.
        
        Args:
            combos: List of tuples containing (input_sequence, combo_name)
                   where input_sequence is a list of input symbols
        """
        self.combo_list = combos
        
        for sequence, combo_name in combos:
            current = self.root
            
            for input_symbol in sequence:
                if not current.has_transition(input_symbol):
                    new_state = self._create_state()
                    current.add_transition(input_symbol, new_state)
                current = current.get_next_state(input_symbol)
            
            # Mark the final state as accept state
            current.is_accept = True
            current.combo_name = combo_name
    
    def process_input(self, input_symbol: str) -> Optional[str]:
        """
        Process a single input and transition to the next state.
        
        Args:
            input_symbol: The input symbol to process
            
        Returns:
            The combo name if an accept state is reached, None otherwise
        """
        next_state = self.current_state.get_next_state(input_symbol)
        
        if next_state is None:
            # No valid transition, check if we can start a new combo from root
            next_state = self.root.get_next_state(input_symbol)
            if next_state is None:
                # No valid combo starts with this input, reset
                self.reset()
                return None
            else:
                # Start a new combo sequence
                self.input_history = [input_symbol]
                self.current_state = next_state
        else:
            # Valid transition from current state
            self.input_history.append(input_symbol)
            self.current_state = next_state
        
        # Check if we've reached an accept state
        if self.current_state.is_accept:
            combo_name = self.current_state.combo_name
            self.reset()
            return combo_name
        
        return None
    
    def reset(self) -> None:
        """Reset the state machine to the initial state."""
        self.current_state = self.root
        self.input_history = []
    
    def get_current_state_id(self) -> int:
        """Get the ID of the current state."""
        return self.current_state.state_id
    
    def get_possible_transitions(self) -> List[str]:
        """Get list of possible inputs from current state."""
        return list(self.current_state.transitions.keys())
    
    def get_progress_percentage(self) -> float:
        """
        Estimate progress towards completing a combo.
        
        Returns:
            A float between 0 and 1 indicating progress
        """
        if not self.input_history:
            return 0.0
        
        # Find the longest matching combo
        max_length = 0
        for sequence, _ in self.combo_list:
            if len(sequence) > max_length:
                # Check if current history is a prefix of this combo
                is_prefix = True
                for i, symbol in enumerate(self.input_history):
                    if i >= len(sequence) or sequence[i] != symbol:
                        is_prefix = False
                        break
                if is_prefix:
                    max_length = len(sequence)
        
        if max_length == 0:
            return 0.0
        
        return len(self.input_history) / max_length
    
    def get_state_diagram_data(self) -> Dict:
        """
        Generate data structure for creating automata diagram.
        
        Returns:
            Dictionary containing states and transitions for diagram generation
        """
        states = []
        transitions = []
        visited = set()
        
        def traverse(node: StateNode, path: str = ""):
            if node.state_id in visited:
                return
            visited.add(node.state_id)
            
            state_info = {
                'id': node.state_id,
                'is_accept': node.is_accept,
                'combo_name': node.combo_name,
                'path': path
            }
            states.append(state_info)
            
            for input_symbol, next_node in node.transitions.items():
                transitions.append({
                    'from': node.state_id,
                    'to': next_node.state_id,
                    'input': input_symbol
                })
                traverse(next_node, path + input_symbol)
        
        traverse(self.root)
        
        return {
            'states': states,
            'transitions': transitions,
            'initial_state': 0,
            'total_states': self._state_counter
        }

