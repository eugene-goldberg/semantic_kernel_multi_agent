#!/usr/bin/env python3
"""
Calculator Plugin for Semantic Kernel.
Provides a plugin interface to the CalculatorAgent for advanced math operations.
"""

import os
import sys
from typing import Optional
import json

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)

from semantic_kernel.functions import kernel_function
from src.agents.calculator_agent import CalculatorAgent

class CalculatorPlugin:
    """
    Plugin that provides advanced mathematical calculation capabilities
    using the CalculatorAgent.
    """
    
    def __init__(self):
        """Initialize the calculator plugin with the calculator agent."""
        self.calculator = CalculatorAgent()
    
    @kernel_function(
        description="Perform a mathematical calculation",
        name="Calculate"
    )
    def calculate(self, expression: str) -> str:
        """
        Perform a mathematical calculation or operation.
        
        Args:
            expression: The mathematical expression or operation to evaluate
            
        Returns:
            The result of the calculation as a formatted string
        """
        return self.calculator.process_request(expression)
    
    @kernel_function(
        description="Perform matrix operations (determinant, inverse, eigenvalues, etc.)",
        name="MatrixOperation"
    )
    def matrix_operation(self, operation: str, matrix: str) -> str:
        """
        Perform operations on matrices.
        
        Args:
            operation: The operation to perform (determinant, inverse, eigenvalues, info)
            matrix: The matrix as a string in format [[a,b],[c,d]]
            
        Returns:
            The result of the matrix operation
        """
        try:
            # Parse the matrix input
            matrix_data = json.loads(matrix.replace("'", '"'))
            
            # Create parameters for the calculator
            params = {
                "operation": operation.lower(),
                "values": matrix_data
            }
            
            # Call the calculator's matrix operations function
            result = self.calculator.matrix_operations(params)
            return str(result)
        except Exception as e:
            return f"Error performing matrix operation: {str(e)}"
    
    @kernel_function(
        description="Perform statistical analysis on a dataset",
        name="Statistics"
    )
    def statistics(self, operation: str, data: str) -> str:
        """
        Perform statistical analysis on a dataset.
        
        Args:
            operation: The statistical operation (mean, median, variance, std, correlation, summary)
            data: The dataset as a comma-separated list of numbers
            
        Returns:
            The result of the statistical analysis
        """
        try:
            # Parse the data input
            numbers = [float(x.strip()) for x in data.split(",")]
            
            # Create parameters for the calculator
            params = {
                "operation": operation.lower(),
                "data": numbers
            }
            
            # Call the calculator's statistical analysis function
            result = self.calculator.statistical_analysis(params)
            return str(result)
        except Exception as e:
            return f"Error performing statistical analysis: {str(e)}"
    
    @kernel_function(
        description="Solve mathematical equations",
        name="SolveEquation"
    )
    def solve_equation(self, equation: str, variable: Optional[str] = "x") -> str:
        """
        Solve mathematical equations.
        
        Args:
            equation: The equation to solve (e.g. "x^2 + 2*x - 3 = 0")
            variable: The variable to solve for (default: x)
            
        Returns:
            The solution to the equation
        """
        try:
            # Create parameters for the calculator
            params = {
                "equation": equation,
                "variable": variable
            }
            
            # Call the calculator's equation solver function
            result = self.calculator.solve_equation(params)
            return str(result)
        except Exception as e:
            return f"Error solving equation: {str(e)}"
    
    @kernel_function(
        description="Perform calculus operations (derivatives, integrals, limits)",
        name="Calculus"
    )
    def calculus(self, operation: str, expression: str, variable: Optional[str] = "x") -> str:
        """
        Perform calculus operations.
        
        Args:
            operation: The calculus operation (derivative, integrate, limit)
            expression: The mathematical expression to operate on
            variable: The variable to operate with respect to (default: x)
            
        Returns:
            The result of the calculus operation
        """
        try:
            # Create parameters for the calculator
            params = {
                "operation": operation.lower(),
                "expression": expression,
                "variable": variable
            }
            
            # Call the calculator's calculus operations function
            result = self.calculator.calculus_operations(params)
            return str(result)
        except Exception as e:
            return f"Error performing calculus operation: {str(e)}"
    
    @kernel_function(
        description="Perform algebraic operations (factor, expand, simplify)",
        name="Algebra"
    )
    def algebra(self, operation: str, expression: str) -> str:
        """
        Perform algebraic operations.
        
        Args:
            operation: The algebraic operation (factor, expand, simplify)
            expression: The expression to operate on
            
        Returns:
            The result of the algebraic operation
        """
        try:
            # Create parameters for the calculator
            params = {
                "operation": operation.lower(),
                "expression": expression
            }
            
            # Call the calculator's algebraic operations function
            result = self.calculator.algebraic_operations(params)
            return str(result)
        except Exception as e:
            return f"Error performing algebraic operation: {str(e)}"