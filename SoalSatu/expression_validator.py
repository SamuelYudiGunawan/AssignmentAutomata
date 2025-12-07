"""
Expression Validator Module using Pushdown Automata.

This module provides validators for mathematical expressions in different notations:
- Infix: (3+4)*2
- Postfix (Reverse Polish Notation): 3 4 + 2 *
- Prefix (Polish Notation): * + 3 4 2

Each validator uses a specialized PDA configuration for the specific notation.
"""

from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass
from enum import Enum, auto
from pushdown_automata import PushdownAutomata, StateType, PDAConfiguration


class NotationType(Enum):
    """Types of mathematical notation."""
    INFIX = auto()
    POSTFIX = auto()
    PREFIX = auto()


@dataclass
class ValidationResult:
    """
    Result of expression validation.
    
    Attributes:
        is_valid: Whether the expression is valid
        notation: The notation type that was validated
        message: Description of result or error
        execution_trace: Step-by-step execution history
        final_state: Name of the final state
    """
    is_valid: bool
    notation: NotationType
    message: str
    execution_trace: List[str]
    final_state: str


class ExpressionTokenizer:
    """
    Tokenizes mathematical expressions for PDA processing.
    
    Handles:
    - Single digits (0-9)
    - Multi-digit numbers
    - Operators (+, -, *, /)
    - Parentheses (for infix)
    - Whitespace separation (for postfix/prefix)
    """
    
    OPERATORS = {'+', '-', '*', '/'}
    DIGITS = set('0123456789')
    PARENTHESES = {'(', ')'}
    
    @staticmethod
    def tokenize_infix(expression: str) -> List[str]:
        """
        Tokenize an infix expression.
        
        Handles expressions like: (3+4)*2, 12+34, ((2+3)*4)
        """
        tokens = []
        current_number = ""
        
        for char in expression:
            if char in ExpressionTokenizer.DIGITS:
                current_number += char
            else:
                if current_number:
                    tokens.append(current_number)
                    current_number = ""
                
                if char in ExpressionTokenizer.OPERATORS:
                    tokens.append(char)
                elif char in ExpressionTokenizer.PARENTHESES:
                    tokens.append(char)
                elif char.isspace():
                    continue
                else:
                    # Invalid character
                    tokens.append(f"INVALID:{char}")
        
        if current_number:
            tokens.append(current_number)
        
        return tokens
    
    @staticmethod
    def tokenize_postfix(expression: str) -> List[str]:
        """
        Tokenize a postfix expression.
        
        Expects space-separated tokens: 3 4 + 2 *
        """
        tokens = []
        for token in expression.split():
            token = token.strip()
            if token:
                if token in ExpressionTokenizer.OPERATORS:
                    tokens.append(token)
                elif token.isdigit():
                    tokens.append(token)
                else:
                    tokens.append(f"INVALID:{token}")
        return tokens
    
    @staticmethod
    def tokenize_prefix(expression: str) -> List[str]:
        """
        Tokenize a prefix expression.
        
        Expects space-separated tokens: * + 3 4 2
        """
        # Same tokenization as postfix
        return ExpressionTokenizer.tokenize_postfix(expression)
    
    @staticmethod
    def classify_token(token: str) -> str:
        """
        Classify a token for PDA processing.
        
        Returns:
            'OPERAND' for numbers
            'OPERATOR' for +, -, *, /
            'LPAREN' for (
            'RPAREN' for )
            'INVALID' for unrecognized tokens
        """
        if token.startswith("INVALID:"):
            return "INVALID"
        if token in ExpressionTokenizer.OPERATORS:
            return "OPERATOR"
        if token == "(":
            return "LPAREN"
        if token == ")":
            return "RPAREN"
        if token.isdigit():
            return "OPERAND"
        return "INVALID"


class InfixValidator:
    """
    Validates infix mathematical expressions using PDA.
    
    PDA Design:
    - States: q_start, q_expect_operand, q_expect_operator, q_accept, q_error
    - Stack: Used for parentheses matching
    - Accept condition: End in q_expect_operator with empty parentheses stack
    """
    
    def __init__(self):
        """Initialize the infix validator PDA."""
        self.pda = PushdownAutomata("Infix Validator PDA")
        self._build_pda()
    
    def _build_pda(self) -> None:
        """Build the PDA states and transitions."""
        # Add states
        self.pda.add_state("q_start", StateType.INITIAL, 
                          "Initial state - expecting operand or '('")
        self.pda.add_state("q_expect_operand", StateType.NORMAL,
                          "Expecting an operand (number) or '('")
        self.pda.add_state("q_expect_operator", StateType.NORMAL,
                          "Expecting an operator or ')' or end")
        self.pda.add_state("q_accept", StateType.ACCEPTING,
                          "Expression accepted")
        self.pda.add_state("q_error", StateType.ERROR,
                          "Invalid expression")
        
        # Transitions from q_start
        self.pda.add_transition("q_start", "q_expect_operator", 
                               "OPERAND", None, "none",
                               "Read operand, expect operator next")
        self.pda.add_transition("q_start", "q_expect_operand",
                               "LPAREN", None, "push:(",
                               "Read '(', push to stack, expect operand")
        
        # Transitions from q_expect_operand  
        self.pda.add_transition("q_expect_operand", "q_expect_operator",
                               "OPERAND", None, "none",
                               "Read operand, expect operator next")
        self.pda.add_transition("q_expect_operand", "q_expect_operand",
                               "LPAREN", None, "push:(",
                               "Read '(', push to stack, still expect operand")
        
        # Transitions from q_expect_operator
        self.pda.add_transition("q_expect_operator", "q_expect_operand",
                               "OPERATOR", None, "none",
                               "Read operator, expect operand next")
        self.pda.add_transition("q_expect_operator", "q_expect_operator",
                               "RPAREN", "(", "pop",
                               "Read ')', pop matching '(' from stack")
    
    def validate(self, expression: str) -> ValidationResult:
        """
        Validate an infix expression.
        
        Args:
            expression: The infix expression to validate
            
        Returns:
            ValidationResult with validation details
        """
        self.pda.reset()
        tokens = ExpressionTokenizer.tokenize_infix(expression)
        execution_trace = []
        
        if not tokens:
            return ValidationResult(
                is_valid=False,
                notation=NotationType.INFIX,
                message="Empty expression",
                execution_trace=["No tokens to process"],
                final_state="q_error"
            )
        
        for token in tokens:
            token_type = ExpressionTokenizer.classify_token(token)
            
            if token_type == "INVALID":
                return ValidationResult(
                    is_valid=False,
                    notation=NotationType.INFIX,
                    message=f"Invalid token: {token}",
                    execution_trace=execution_trace,
                    final_state="q_error"
                )
            
            config_before = self.pda.get_current_configuration()
            success, error = self.pda.step(token_type)
            
            trace_entry = f"Token: '{token}' ({token_type}) | State: {config_before.state.name} → {self.pda.current_state.name} | Stack: {self.pda.stack.get_contents()}"
            execution_trace.append(trace_entry)
            
            if not success:
                return ValidationResult(
                    is_valid=False,
                    notation=NotationType.INFIX,
                    message=error,
                    execution_trace=execution_trace,
                    final_state=self.pda.current_state.name
                )
        
        # Check final conditions
        final_state = self.pda.current_state.name
        stack_empty = self.pda.stack.is_empty()
        
        if final_state == "q_expect_operator" and stack_empty:
            return ValidationResult(
                is_valid=True,
                notation=NotationType.INFIX,
                message="Valid infix expression",
                execution_trace=execution_trace,
                final_state=final_state
            )
        elif not stack_empty:
            return ValidationResult(
                is_valid=False,
                notation=NotationType.INFIX,
                message="Unmatched opening parenthesis",
                execution_trace=execution_trace,
                final_state=final_state
            )
        else:
            return ValidationResult(
                is_valid=False,
                notation=NotationType.INFIX,
                message=f"Expression incomplete - ended in state {final_state}",
                execution_trace=execution_trace,
                final_state=final_state
            )
    
    def get_pda(self) -> PushdownAutomata:
        """Return the underlying PDA for diagram generation."""
        return self.pda


class PostfixValidator:
    """
    Validates postfix (Reverse Polish Notation) expressions using PDA.
    
    PDA Design:
    - States: q_start, q_processing, q_accept, q_error
    - Stack: Tracks operand count (each operand pushes 'X', each operator pops 2 and pushes 1)
    - Accept condition: End with exactly one element on stack
    """
    
    def __init__(self):
        """Initialize the postfix validator PDA."""
        self.pda = PushdownAutomata("Postfix Validator PDA")
        self._build_pda()
    
    def _build_pda(self) -> None:
        """Build the PDA states and transitions."""
        # Add states
        self.pda.add_state("q_start", StateType.INITIAL,
                          "Initial state - expecting first token")
        self.pda.add_state("q_processing", StateType.NORMAL,
                          "Processing tokens")
        self.pda.add_state("q_accept", StateType.ACCEPTING,
                          "Expression accepted")
        self.pda.add_state("q_error", StateType.ERROR,
                          "Invalid expression")
        
        # Transitions for operands - push marker to stack
        self.pda.add_transition("q_start", "q_processing",
                               "OPERAND", None, "push:X",
                               "Read first operand, push marker")
        self.pda.add_transition("q_processing", "q_processing",
                               "OPERAND", None, "push:X",
                               "Read operand, push marker")
        
        # Transitions for operators - pop 2, push 1 (net effect: pop 1)
        # We'll handle this specially in validate() since PDA needs two pops
    
    def validate(self, expression: str) -> ValidationResult:
        """
        Validate a postfix expression.
        
        Uses a modified PDA approach where stack tracks operand count.
        
        Args:
            expression: The postfix expression to validate (space-separated)
            
        Returns:
            ValidationResult with validation details
        """
        self.pda.reset()
        tokens = ExpressionTokenizer.tokenize_postfix(expression)
        execution_trace = []
        
        if not tokens:
            return ValidationResult(
                is_valid=False,
                notation=NotationType.POSTFIX,
                message="Empty expression",
                execution_trace=["No tokens to process"],
                final_state="q_error"
            )
        
        # Track operand count using stack simulation
        operand_count = 0
        
        for i, token in enumerate(tokens):
            token_type = ExpressionTokenizer.classify_token(token)
            
            if token_type == "INVALID":
                return ValidationResult(
                    is_valid=False,
                    notation=NotationType.POSTFIX,
                    message=f"Invalid token: {token}",
                    execution_trace=execution_trace,
                    final_state="q_error"
                )
            
            if token_type == "LPAREN" or token_type == "RPAREN":
                return ValidationResult(
                    is_valid=False,
                    notation=NotationType.POSTFIX,
                    message="Parentheses not allowed in postfix notation",
                    execution_trace=execution_trace,
                    final_state="q_error"
                )
            
            state_before = "q_start" if i == 0 else "q_processing"
            
            if token_type == "OPERAND":
                operand_count += 1
                self.pda.stack.push("X")
                trace_entry = f"Token: '{token}' (OPERAND) | Operands: {operand_count} | Stack: {self.pda.stack.get_contents()}"
            else:  # OPERATOR
                if operand_count < 2:
                    return ValidationResult(
                        is_valid=False,
                        notation=NotationType.POSTFIX,
                        message=f"Not enough operands for operator '{token}'",
                        execution_trace=execution_trace,
                        final_state="q_error"
                    )
                operand_count -= 1  # Two operands become one result
                self.pda.stack.pop()
                trace_entry = f"Token: '{token}' (OPERATOR) | Operands: {operand_count} | Stack: {self.pda.stack.get_contents()}"
            
            execution_trace.append(trace_entry)
        
        # Check final condition: exactly one operand remaining
        if operand_count == 1:
            return ValidationResult(
                is_valid=True,
                notation=NotationType.POSTFIX,
                message="Valid postfix expression",
                execution_trace=execution_trace,
                final_state="q_accept"
            )
        elif operand_count > 1:
            return ValidationResult(
                is_valid=False,
                notation=NotationType.POSTFIX,
                message=f"Too many operands ({operand_count}) - missing operators",
                execution_trace=execution_trace,
                final_state="q_error"
            )
        else:
            return ValidationResult(
                is_valid=False,
                notation=NotationType.POSTFIX,
                message="No result - expression is incomplete",
                execution_trace=execution_trace,
                final_state="q_error"
            )
    
    def get_pda(self) -> PushdownAutomata:
        """Return the underlying PDA for diagram generation."""
        return self.pda


class PrefixValidator:
    """
    Validates prefix (Polish Notation) expressions using PDA.
    
    PDA Design:
    - Similar to postfix but processed right-to-left
    - States: q_start, q_processing, q_accept, q_error
    - Stack: Tracks expected operand count
    """
    
    def __init__(self):
        """Initialize the prefix validator PDA."""
        self.pda = PushdownAutomata("Prefix Validator PDA")
        self._build_pda()
    
    def _build_pda(self) -> None:
        """Build the PDA states and transitions."""
        # Add states
        self.pda.add_state("q_start", StateType.INITIAL,
                          "Initial state - process from right")
        self.pda.add_state("q_processing", StateType.NORMAL,
                          "Processing tokens right-to-left")
        self.pda.add_state("q_accept", StateType.ACCEPTING,
                          "Expression accepted")
        self.pda.add_state("q_error", StateType.ERROR,
                          "Invalid expression")
    
    def validate(self, expression: str) -> ValidationResult:
        """
        Validate a prefix expression.
        
        Processes tokens from right to left.
        
        Args:
            expression: The prefix expression to validate (space-separated)
            
        Returns:
            ValidationResult with validation details
        """
        self.pda.reset()
        tokens = ExpressionTokenizer.tokenize_prefix(expression)
        execution_trace = []
        
        if not tokens:
            return ValidationResult(
                is_valid=False,
                notation=NotationType.PREFIX,
                message="Empty expression",
                execution_trace=["No tokens to process"],
                final_state="q_error"
            )
        
        # Process right to left
        tokens = list(reversed(tokens))
        operand_count = 0
        
        for i, token in enumerate(tokens):
            token_type = ExpressionTokenizer.classify_token(token)
            
            if token_type == "INVALID":
                return ValidationResult(
                    is_valid=False,
                    notation=NotationType.PREFIX,
                    message=f"Invalid token: {token}",
                    execution_trace=execution_trace,
                    final_state="q_error"
                )
            
            if token_type == "LPAREN" or token_type == "RPAREN":
                return ValidationResult(
                    is_valid=False,
                    notation=NotationType.PREFIX,
                    message="Parentheses not allowed in prefix notation",
                    execution_trace=execution_trace,
                    final_state="q_error"
                )
            
            if token_type == "OPERAND":
                operand_count += 1
                self.pda.stack.push("X")
                trace_entry = f"Token: '{token}' (OPERAND) [R→L] | Operands: {operand_count} | Stack: {self.pda.stack.get_contents()}"
            else:  # OPERATOR
                if operand_count < 2:
                    return ValidationResult(
                        is_valid=False,
                        notation=NotationType.PREFIX,
                        message=f"Not enough operands for operator '{token}'",
                        execution_trace=execution_trace,
                        final_state="q_error"
                    )
                operand_count -= 1  # Two operands become one result
                self.pda.stack.pop()
                trace_entry = f"Token: '{token}' (OPERATOR) [R→L] | Operands: {operand_count} | Stack: {self.pda.stack.get_contents()}"
            
            execution_trace.append(trace_entry)
        
        # Check final condition: exactly one operand remaining
        if operand_count == 1:
            return ValidationResult(
                is_valid=True,
                notation=NotationType.PREFIX,
                message="Valid prefix expression",
                execution_trace=execution_trace,
                final_state="q_accept"
            )
        elif operand_count > 1:
            return ValidationResult(
                is_valid=False,
                notation=NotationType.PREFIX,
                message=f"Too many operands ({operand_count}) - missing operators",
                execution_trace=execution_trace,
                final_state="q_error"
            )
        else:
            return ValidationResult(
                is_valid=False,
                notation=NotationType.PREFIX,
                message="No result - expression is incomplete",
                execution_trace=execution_trace,
                final_state="q_error"
            )
    
    def get_pda(self) -> PushdownAutomata:
        """Return the underlying PDA for diagram generation."""
        return self.pda


class ExpressionValidator:
    """
    Unified expression validator that can validate all notation types.
    
    Automatically detects or accepts specified notation type and
    delegates to the appropriate specialized validator.
    """
    
    def __init__(self):
        """Initialize all validators."""
        self.infix_validator = InfixValidator()
        self.postfix_validator = PostfixValidator()
        self.prefix_validator = PrefixValidator()
    
    def validate(self, expression: str, notation: NotationType) -> ValidationResult:
        """
        Validate an expression in the specified notation.
        
        Args:
            expression: The expression to validate
            notation: The notation type (INFIX, POSTFIX, or PREFIX)
            
        Returns:
            ValidationResult with validation details
        """
        if notation == NotationType.INFIX:
            return self.infix_validator.validate(expression)
        elif notation == NotationType.POSTFIX:
            return self.postfix_validator.validate(expression)
        elif notation == NotationType.PREFIX:
            return self.prefix_validator.validate(expression)
        else:
            return ValidationResult(
                is_valid=False,
                notation=notation,
                message="Unknown notation type",
                execution_trace=[],
                final_state="q_error"
            )
    
    def validate_all(self, expression: str) -> Dict[NotationType, ValidationResult]:
        """
        Validate expression against all notation types.
        
        Useful for testing or when notation is unknown.
        
        Args:
            expression: The expression to validate
            
        Returns:
            Dictionary mapping notation type to validation result
        """
        return {
            NotationType.INFIX: self.validate(expression, NotationType.INFIX),
            NotationType.POSTFIX: self.validate(expression, NotationType.POSTFIX),
            NotationType.PREFIX: self.validate(expression, NotationType.PREFIX)
        }
    
    def get_pda(self, notation: NotationType) -> PushdownAutomata:
        """Get the PDA for a specific notation type."""
        if notation == NotationType.INFIX:
            return self.infix_validator.get_pda()
        elif notation == NotationType.POSTFIX:
            return self.postfix_validator.get_pda()
        elif notation == NotationType.PREFIX:
            return self.prefix_validator.get_pda()
        return None


# Convenience functions for direct validation
def validate_infix(expression: str) -> ValidationResult:
    """Validate an infix expression."""
    return InfixValidator().validate(expression)


def validate_postfix(expression: str) -> ValidationResult:
    """Validate a postfix expression."""
    return PostfixValidator().validate(expression)


def validate_prefix(expression: str) -> ValidationResult:
    """Validate a prefix expression."""
    return PrefixValidator().validate(expression)

