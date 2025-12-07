"""
Expression Converter Module for Mathematical Notations.

This module provides conversion between different mathematical notations:
- Infix: (3+4)*2
- Postfix (Reverse Polish Notation): 3 4 + 2 *
- Prefix (Polish Notation): * + 3 4 2

Conversion Algorithms:
- Infix → Postfix: Shunting-yard algorithm
- Infix → Prefix: Reverse, swap parentheses, Shunting-yard, reverse result
- Postfix → Infix: Stack-based evaluation with expression building
- Prefix → Infix: Right-to-left stack evaluation
- Postfix ↔ Prefix: Via Infix as intermediate
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass
from expression_validator import (
    NotationType, ExpressionTokenizer, ValidationResult,
    validate_infix, validate_postfix, validate_prefix
)


@dataclass
class ConversionResult:
    """
    Result of expression conversion.
    
    Attributes:
        success: Whether conversion was successful
        source_notation: The input notation type
        target_notation: The output notation type
        source_expression: Original expression
        result_expression: Converted expression (empty if failed)
        steps: Step-by-step conversion process
        error_message: Error description if failed
    """
    success: bool
    source_notation: NotationType
    target_notation: NotationType
    source_expression: str
    result_expression: str
    steps: List[str]
    error_message: str = ""


class ExpressionConverter:
    """
    Converts mathematical expressions between infix, postfix, and prefix notations.
    
    All conversions validate input before processing and provide
    step-by-step traces of the conversion process.
    """
    
    # Operator precedence (higher number = higher precedence)
    PRECEDENCE = {
        '+': 1,
        '-': 1,
        '*': 2,
        '/': 2
    }
    
    # Operator associativity (True = left-to-right)
    LEFT_ASSOCIATIVE = {
        '+': True,
        '-': True,
        '*': True,
        '/': True
    }
    
    def __init__(self):
        """Initialize the converter."""
        pass
    
    def _get_precedence(self, operator: str) -> int:
        """Get precedence of an operator."""
        return self.PRECEDENCE.get(operator, 0)
    
    def _is_left_associative(self, operator: str) -> bool:
        """Check if operator is left associative."""
        return self.LEFT_ASSOCIATIVE.get(operator, True)
    
    def _is_operator(self, token: str) -> bool:
        """Check if token is an operator."""
        return token in self.PRECEDENCE
    
    def _is_operand(self, token: str) -> bool:
        """Check if token is an operand (number)."""
        return token.isdigit()
    
    # ==================== INFIX TO POSTFIX ====================
    
    def infix_to_postfix(self, expression: str) -> ConversionResult:
        """
        Convert infix expression to postfix using Shunting-yard algorithm.
        
        Algorithm:
        1. Read tokens left to right
        2. If operand, add to output
        3. If operator, pop operators with >= precedence to output, then push
        4. If '(', push to stack
        5. If ')', pop to output until '(' found
        6. Pop remaining operators to output
        
        Args:
            expression: Infix expression (e.g., "(3+4)*2")
            
        Returns:
            ConversionResult with postfix expression
        """
        # Validate input
        validation = validate_infix(expression)
        if not validation.is_valid:
            return ConversionResult(
                success=False,
                source_notation=NotationType.INFIX,
                target_notation=NotationType.POSTFIX,
                source_expression=expression,
                result_expression="",
                steps=["Validation failed: " + validation.message],
                error_message=validation.message
            )
        
        tokens = ExpressionTokenizer.tokenize_infix(expression)
        output = []
        operator_stack = []
        steps = [f"Input tokens: {tokens}"]
        
        for token in tokens:
            if self._is_operand(token):
                output.append(token)
                steps.append(f"Operand '{token}' → Output: {output}, Stack: {operator_stack}")
            
            elif self._is_operator(token):
                while (operator_stack and 
                       operator_stack[-1] != '(' and
                       self._is_operator(operator_stack[-1]) and
                       (self._get_precedence(operator_stack[-1]) > self._get_precedence(token) or
                        (self._get_precedence(operator_stack[-1]) == self._get_precedence(token) and
                         self._is_left_associative(token)))):
                    output.append(operator_stack.pop())
                operator_stack.append(token)
                steps.append(f"Operator '{token}' → Output: {output}, Stack: {operator_stack}")
            
            elif token == '(':
                operator_stack.append(token)
                steps.append(f"'(' → Output: {output}, Stack: {operator_stack}")
            
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                if operator_stack:
                    operator_stack.pop()  # Remove '('
                steps.append(f"')' → Output: {output}, Stack: {operator_stack}")
        
        # Pop remaining operators
        while operator_stack:
            output.append(operator_stack.pop())
        
        result = ' '.join(output)
        steps.append(f"Final result: {result}")
        
        return ConversionResult(
            success=True,
            source_notation=NotationType.INFIX,
            target_notation=NotationType.POSTFIX,
            source_expression=expression,
            result_expression=result,
            steps=steps
        )
    
    # ==================== INFIX TO PREFIX ====================
    
    def infix_to_prefix(self, expression: str) -> ConversionResult:
        """
        Convert infix expression to prefix.
        
        Algorithm:
        1. Reverse the infix expression
        2. Swap '(' with ')' and vice versa
        3. Apply Shunting-yard algorithm (modified for right associativity)
        4. Reverse the result
        
        Args:
            expression: Infix expression (e.g., "(3+4)*2")
            
        Returns:
            ConversionResult with prefix expression
        """
        # Validate input
        validation = validate_infix(expression)
        if not validation.is_valid:
            return ConversionResult(
                success=False,
                source_notation=NotationType.INFIX,
                target_notation=NotationType.PREFIX,
                source_expression=expression,
                result_expression="",
                steps=["Validation failed: " + validation.message],
                error_message=validation.message
            )
        
        tokens = ExpressionTokenizer.tokenize_infix(expression)
        steps = [f"Input tokens: {tokens}"]
        
        # Step 1: Reverse tokens
        reversed_tokens = list(reversed(tokens))
        steps.append(f"Reversed: {reversed_tokens}")
        
        # Step 2: Swap parentheses
        swapped_tokens = []
        for token in reversed_tokens:
            if token == '(':
                swapped_tokens.append(')')
            elif token == ')':
                swapped_tokens.append('(')
            else:
                swapped_tokens.append(token)
        steps.append(f"Swapped parentheses: {swapped_tokens}")
        
        # Step 3: Modified Shunting-yard (right associative)
        output = []
        operator_stack = []
        
        for token in swapped_tokens:
            if self._is_operand(token):
                output.append(token)
            
            elif self._is_operator(token):
                # For prefix, we use > instead of >= for same precedence
                while (operator_stack and 
                       operator_stack[-1] != '(' and
                       self._is_operator(operator_stack[-1]) and
                       self._get_precedence(operator_stack[-1]) > self._get_precedence(token)):
                    output.append(operator_stack.pop())
                operator_stack.append(token)
            
            elif token == '(':
                operator_stack.append(token)
            
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                if operator_stack:
                    operator_stack.pop()  # Remove '('
        
        # Pop remaining operators
        while operator_stack:
            output.append(operator_stack.pop())
        
        steps.append(f"After Shunting-yard: {output}")
        
        # Step 4: Reverse result
        result_tokens = list(reversed(output))
        result = ' '.join(result_tokens)
        steps.append(f"Final result (reversed): {result}")
        
        return ConversionResult(
            success=True,
            source_notation=NotationType.INFIX,
            target_notation=NotationType.PREFIX,
            source_expression=expression,
            result_expression=result,
            steps=steps
        )
    
    # ==================== POSTFIX TO INFIX ====================
    
    def postfix_to_infix(self, expression: str) -> ConversionResult:
        """
        Convert postfix expression to infix.
        
        Algorithm:
        1. Read tokens left to right
        2. If operand, push to stack
        3. If operator, pop two operands, create infix expression, push result
        
        Args:
            expression: Postfix expression (e.g., "3 4 + 2 *")
            
        Returns:
            ConversionResult with infix expression
        """
        # Validate input
        validation = validate_postfix(expression)
        if not validation.is_valid:
            return ConversionResult(
                success=False,
                source_notation=NotationType.POSTFIX,
                target_notation=NotationType.INFIX,
                source_expression=expression,
                result_expression="",
                steps=["Validation failed: " + validation.message],
                error_message=validation.message
            )
        
        tokens = ExpressionTokenizer.tokenize_postfix(expression)
        stack = []
        steps = [f"Input tokens: {tokens}"]
        
        for token in tokens:
            if self._is_operand(token):
                stack.append(token)
                steps.append(f"Push operand '{token}' → Stack: {stack}")
            
            elif self._is_operator(token):
                if len(stack) < 2:
                    return ConversionResult(
                        success=False,
                        source_notation=NotationType.POSTFIX,
                        target_notation=NotationType.INFIX,
                        source_expression=expression,
                        result_expression="",
                        steps=steps,
                        error_message="Not enough operands for operator"
                    )
                
                operand2 = stack.pop()
                operand1 = stack.pop()
                
                # Add parentheses for clarity
                result_expr = f"({operand1}{token}{operand2})"
                stack.append(result_expr)
                steps.append(f"Apply '{token}' to {operand1}, {operand2} → '{result_expr}' → Stack: {stack}")
        
        if len(stack) != 1:
            return ConversionResult(
                success=False,
                source_notation=NotationType.POSTFIX,
                target_notation=NotationType.INFIX,
                source_expression=expression,
                result_expression="",
                steps=steps,
                error_message="Invalid expression - stack should have exactly one element"
            )
        
        result = stack[0]
        steps.append(f"Final result: {result}")
        
        return ConversionResult(
            success=True,
            source_notation=NotationType.POSTFIX,
            target_notation=NotationType.INFIX,
            source_expression=expression,
            result_expression=result,
            steps=steps
        )
    
    # ==================== PREFIX TO INFIX ====================
    
    def prefix_to_infix(self, expression: str) -> ConversionResult:
        """
        Convert prefix expression to infix.
        
        Algorithm:
        1. Read tokens right to left
        2. If operand, push to stack
        3. If operator, pop two operands, create infix expression, push result
        
        Args:
            expression: Prefix expression (e.g., "* + 3 4 2")
            
        Returns:
            ConversionResult with infix expression
        """
        # Validate input
        validation = validate_prefix(expression)
        if not validation.is_valid:
            return ConversionResult(
                success=False,
                source_notation=NotationType.PREFIX,
                target_notation=NotationType.INFIX,
                source_expression=expression,
                result_expression="",
                steps=["Validation failed: " + validation.message],
                error_message=validation.message
            )
        
        tokens = ExpressionTokenizer.tokenize_prefix(expression)
        # Process right to left
        tokens = list(reversed(tokens))
        stack = []
        steps = [f"Input tokens (reversed): {tokens}"]
        
        for token in tokens:
            if self._is_operand(token):
                stack.append(token)
                steps.append(f"Push operand '{token}' → Stack: {stack}")
            
            elif self._is_operator(token):
                if len(stack) < 2:
                    return ConversionResult(
                        success=False,
                        source_notation=NotationType.PREFIX,
                        target_notation=NotationType.INFIX,
                        source_expression=expression,
                        result_expression="",
                        steps=steps,
                        error_message="Not enough operands for operator"
                    )
                
                # Note: For prefix, order is reversed compared to postfix
                operand1 = stack.pop()
                operand2 = stack.pop()
                
                result_expr = f"({operand1}{token}{operand2})"
                stack.append(result_expr)
                steps.append(f"Apply '{token}' to {operand1}, {operand2} → '{result_expr}' → Stack: {stack}")
        
        if len(stack) != 1:
            return ConversionResult(
                success=False,
                source_notation=NotationType.PREFIX,
                target_notation=NotationType.INFIX,
                source_expression=expression,
                result_expression="",
                steps=steps,
                error_message="Invalid expression - stack should have exactly one element"
            )
        
        result = stack[0]
        steps.append(f"Final result: {result}")
        
        return ConversionResult(
            success=True,
            source_notation=NotationType.PREFIX,
            target_notation=NotationType.INFIX,
            source_expression=expression,
            result_expression=result,
            steps=steps
        )
    
    # ==================== POSTFIX TO PREFIX ====================
    
    def postfix_to_prefix(self, expression: str) -> ConversionResult:
        """
        Convert postfix expression to prefix via infix.
        
        Args:
            expression: Postfix expression (e.g., "3 4 + 2 *")
            
        Returns:
            ConversionResult with prefix expression
        """
        # First convert to infix
        infix_result = self.postfix_to_infix(expression)
        if not infix_result.success:
            return ConversionResult(
                success=False,
                source_notation=NotationType.POSTFIX,
                target_notation=NotationType.PREFIX,
                source_expression=expression,
                result_expression="",
                steps=infix_result.steps,
                error_message=infix_result.error_message
            )
        
        # Then convert infix to prefix
        prefix_result = self.infix_to_prefix(infix_result.result_expression)
        
        # Combine steps
        combined_steps = infix_result.steps.copy()
        combined_steps.append("--- Converting Infix to Prefix ---")
        combined_steps.extend(prefix_result.steps)
        
        return ConversionResult(
            success=prefix_result.success,
            source_notation=NotationType.POSTFIX,
            target_notation=NotationType.PREFIX,
            source_expression=expression,
            result_expression=prefix_result.result_expression,
            steps=combined_steps,
            error_message=prefix_result.error_message
        )
    
    # ==================== PREFIX TO POSTFIX ====================
    
    def prefix_to_postfix(self, expression: str) -> ConversionResult:
        """
        Convert prefix expression to postfix via infix.
        
        Args:
            expression: Prefix expression (e.g., "* + 3 4 2")
            
        Returns:
            ConversionResult with postfix expression
        """
        # First convert to infix
        infix_result = self.prefix_to_infix(expression)
        if not infix_result.success:
            return ConversionResult(
                success=False,
                source_notation=NotationType.PREFIX,
                target_notation=NotationType.POSTFIX,
                source_expression=expression,
                result_expression="",
                steps=infix_result.steps,
                error_message=infix_result.error_message
            )
        
        # Then convert infix to postfix
        postfix_result = self.infix_to_postfix(infix_result.result_expression)
        
        # Combine steps
        combined_steps = infix_result.steps.copy()
        combined_steps.append("--- Converting Infix to Postfix ---")
        combined_steps.extend(postfix_result.steps)
        
        return ConversionResult(
            success=postfix_result.success,
            source_notation=NotationType.PREFIX,
            target_notation=NotationType.POSTFIX,
            source_expression=expression,
            result_expression=postfix_result.result_expression,
            steps=combined_steps,
            error_message=postfix_result.error_message
        )
    
    # ==================== UNIFIED CONVERSION ====================
    
    def convert(self, expression: str, 
                source: NotationType, 
                target: NotationType) -> ConversionResult:
        """
        Convert expression from source notation to target notation.
        
        Args:
            expression: The expression to convert
            source: Source notation type
            target: Target notation type
            
        Returns:
            ConversionResult with converted expression
        """
        if source == target:
            return ConversionResult(
                success=True,
                source_notation=source,
                target_notation=target,
                source_expression=expression,
                result_expression=expression,
                steps=["No conversion needed - same notation"]
            )
        
        # Infix conversions
        if source == NotationType.INFIX:
            if target == NotationType.POSTFIX:
                return self.infix_to_postfix(expression)
            elif target == NotationType.PREFIX:
                return self.infix_to_prefix(expression)
        
        # Postfix conversions
        elif source == NotationType.POSTFIX:
            if target == NotationType.INFIX:
                return self.postfix_to_infix(expression)
            elif target == NotationType.PREFIX:
                return self.postfix_to_prefix(expression)
        
        # Prefix conversions
        elif source == NotationType.PREFIX:
            if target == NotationType.INFIX:
                return self.prefix_to_infix(expression)
            elif target == NotationType.POSTFIX:
                return self.prefix_to_postfix(expression)
        
        return ConversionResult(
            success=False,
            source_notation=source,
            target_notation=target,
            source_expression=expression,
            result_expression="",
            steps=[],
            error_message="Invalid conversion requested"
        )
    
    def convert_to_all(self, expression: str, 
                       source: NotationType) -> dict:
        """
        Convert expression to all other notations.
        
        Args:
            expression: The expression to convert
            source: Source notation type
            
        Returns:
            Dictionary mapping target notation to ConversionResult
        """
        results = {}
        for target in NotationType:
            results[target] = self.convert(expression, source, target)
        return results


# Convenience functions
def infix_to_postfix(expression: str) -> str:
    """Convert infix to postfix. Returns empty string on failure."""
    result = ExpressionConverter().infix_to_postfix(expression)
    return result.result_expression if result.success else ""


def infix_to_prefix(expression: str) -> str:
    """Convert infix to prefix. Returns empty string on failure."""
    result = ExpressionConverter().infix_to_prefix(expression)
    return result.result_expression if result.success else ""


def postfix_to_infix(expression: str) -> str:
    """Convert postfix to infix. Returns empty string on failure."""
    result = ExpressionConverter().postfix_to_infix(expression)
    return result.result_expression if result.success else ""


def postfix_to_prefix(expression: str) -> str:
    """Convert postfix to prefix. Returns empty string on failure."""
    result = ExpressionConverter().postfix_to_prefix(expression)
    return result.result_expression if result.success else ""


def prefix_to_infix(expression: str) -> str:
    """Convert prefix to infix. Returns empty string on failure."""
    result = ExpressionConverter().prefix_to_infix(expression)
    return result.result_expression if result.success else ""


def prefix_to_postfix(expression: str) -> str:
    """Convert prefix to postfix. Returns empty string on failure."""
    result = ExpressionConverter().prefix_to_postfix(expression)
    return result.result_expression if result.success else ""

