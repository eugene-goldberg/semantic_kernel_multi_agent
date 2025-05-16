#!/usr/bin/env python3
"""
Calculator Agent for performing advanced mathematical operations.
This agent utilizes specialized math libraries for calculations that
would not be available to other agents.
"""

import os
import numpy as np
import scipy as sp
import sympy as sym
import pandas as pd
from typing import Dict, Any, Optional, List, Union
import json
import re

class CalculatorAgent:
    """
    Agent specialized in mathematical calculations using advanced libraries.
    """
    
    def __init__(self):
        """Initialize the calculator agent with specialized math capabilities."""
        self.operation_map = {
            "matrix": self.matrix_operations,
            "statistics": self.statistical_analysis,
            "algebra": self.algebraic_operations,
            "calculus": self.calculus_operations,
            "equation": self.solve_equation
        }

    def process_request(self, query: str) -> str:
        """
        Process a calculation request and return the result.
        
        Args:
            query: The user's calculation request
            
        Returns:
            A string containing the calculation result
        """
        # Extract operation type and parameters from query
        operation_type = self._determine_operation_type(query)
        parameters = self._extract_parameters(query, operation_type)
        
        # Call the appropriate operation handler
        if operation_type in self.operation_map:
            try:
                result = self.operation_map[operation_type](parameters)
                return self._format_result(result, operation_type)
            except Exception as e:
                return f"Error performing {operation_type} calculation: {str(e)}"
        else:
            # For simple arithmetic expressions, use direct evaluation
            try:
                # Clean the expression to ensure it's safe to evaluate
                cleaned_expr = self._clean_arithmetic_expression(query)
                if cleaned_expr:
                    # Use sympy to safely evaluate the expression
                    result = float(sym.sympify(cleaned_expr, evaluate=True))
                    return f"Result: {result}"
                return "I couldn't parse a valid calculation from your request."
            except Exception as e:
                return f"Error evaluating expression: {str(e)}"

    def _determine_operation_type(self, query: str) -> str:
        """Determine the type of mathematical operation from the query."""
        query = query.lower()
        
        if any(term in query for term in ["matrix", "determinant", "eigenvalue", "inverse"]):
            return "matrix"
        elif any(term in query for term in ["mean", "median", "variance", "standard deviation", "correlation"]):
            return "statistics"
        elif any(term in query for term in ["factor", "expand", "simplify", "polynomial"]):
            return "algebra"
        elif any(term in query for term in ["integrate", "derivative", "differentiate", "limit"]):
            return "calculus"
        elif any(term in query for term in ["solve", "equation", "find x", "find y"]):
            return "equation"
        else:
            return "arithmetic"

    def _extract_parameters(self, query: str, operation_type: str) -> Dict[str, Any]:
        """Extract relevant parameters from the query based on operation type."""
        params = {}
        
        if operation_type == "matrix":
            # Extract matrix dimensions and values
            matrix_match = re.search(r'matrix\s+of\s+(?:size\s+)?(\d+)(?:\s*[xX]\s*|\s+by\s+)(\d+)', query)
            if matrix_match:
                params["rows"] = int(matrix_match.group(1))
                params["cols"] = int(matrix_match.group(2))
            
            # Look for matrix values in form [[a,b],[c,d]]
            values_match = re.search(r'\[\s*\[(.*?)\](?:\s*,\s*\[(.*?)\])*\s*\]', query)
            if values_match:
                # Parse the matrix values
                matrix_str = values_match.group(0)
                try:
                    params["values"] = json.loads(matrix_str.replace("'", '"'))
                except:
                    # If direct parsing fails, do a more lenient pass
                    cleaned = re.sub(r'\s+', '', matrix_str)
                    params["values"] = eval(cleaned)  # Only use eval for matrix values from structured input
            
            # Extract operation (determinant, inverse, etc.)
            if "determinant" in query:
                params["operation"] = "determinant"
            elif "inverse" in query:
                params["operation"] = "inverse"
            elif "eigenvalue" in query:
                params["operation"] = "eigenvalues"
            else:
                params["operation"] = "info"
                
        elif operation_type == "statistics":
            # Extract data points
            numbers = re.findall(r'[-+]?\d*\.\d+|\d+', query)
            if numbers:
                params["data"] = [float(num) for num in numbers]
            
            # Extract statistical operation
            if "mean" in query:
                params["operation"] = "mean"
            elif "median" in query:
                params["operation"] = "median"
            elif "variance" in query:
                params["operation"] = "variance"
            elif "standard deviation" in query:
                params["operation"] = "std"
            elif "correlation" in query:
                params["operation"] = "correlation"
            else:
                params["operation"] = "summary"
                
        elif operation_type == "equation":
            # Extract equation to solve
            eq_match = re.search(r'(?:solve|equation)\s+(.*?)(?:$|for\s+)', query, re.IGNORECASE)
            if eq_match:
                params["equation"] = eq_match.group(1).strip()
            
            # Extract variable to solve for
            var_match = re.search(r'for\s+([a-zA-Z])', query, re.IGNORECASE)
            if var_match:
                params["variable"] = var_match.group(1)
            else:
                params["variable"] = "x"  # Default variable
                
        elif operation_type == "calculus":
            # Extract expression for calculus operations
            expr_match = re.search(r'(?:of|expression)\s+(.*?)(?:$|with\s+respect)', query, re.IGNORECASE)
            if expr_match:
                params["expression"] = expr_match.group(1).strip()
            
            # Extract variable for differentiation/integration
            var_match = re.search(r'(?:with\s+respect\s+to|regarding|for)\s+([a-zA-Z])', query, re.IGNORECASE)
            if var_match:
                params["variable"] = var_match.group(1)
            else:
                params["variable"] = "x"  # Default variable
            
            # Extract calculation type
            if "derivative" in query or "differentiate" in query:
                params["operation"] = "derivative"
            elif "integrate" in query:
                params["operation"] = "integrate"
            elif "limit" in query:
                params["operation"] = "limit"
                # Extract the approaching value
                approach_match = re.search(r'approach(?:es|ing)?\s+([-+]?\d*\.\d+|\d+|infinity)', query, re.IGNORECASE)
                if approach_match:
                    value = approach_match.group(1).lower()
                    params["approach"] = float('inf') if value == "infinity" else float(value)
                
        elif operation_type == "algebra":
            # Extract expression for algebraic operations
            expr_match = re.search(r'(?:expression|polynomial)\s+(.*?)(?:$|\s+)', query, re.IGNORECASE)
            if expr_match:
                params["expression"] = expr_match.group(1).strip()
            
            # Extract operation type
            if "factor" in query:
                params["operation"] = "factor"
            elif "expand" in query:
                params["operation"] = "expand"
            elif "simplify" in query:
                params["operation"] = "simplify"
            else:
                params["operation"] = "simplify"  # Default operation
                
        return params

    def _clean_arithmetic_expression(self, query: str) -> str:
        """Clean and extract a safe arithmetic expression from a query."""
        # Remove all text except numbers, basic operators, and parentheses
        operators = r'[\+\-\*\/\^\(\)\.\d\s]'
        expr = ''.join(re.findall(operators, query))
        
        # Further clean the expression
        expr = expr.replace('^', '**')  # Convert caret to Python power operator
        expr = re.sub(r'\s+', '', expr)  # Remove whitespace
        
        # Basic validation to ensure expression is reasonable
        if not expr or not re.search(r'\d', expr):
            return ""
            
        # Verify balanced parentheses
        if expr.count('(') != expr.count(')'):
            return ""
            
        return expr

    def _format_result(self, result: Any, operation_type: str) -> str:
        """Format the calculation result based on the operation type."""
        if operation_type == "matrix":
            if isinstance(result, np.ndarray):
                return f"Result:\n{np.array2string(result, precision=4, suppress_small=True)}"
            else:
                return f"Result: {result}"
                
        elif operation_type == "statistics":
            if isinstance(result, dict):
                return "\n".join([f"{k.capitalize()}: {v}" for k, v in result.items()])
            else:
                return f"Result: {result}"
                
        elif operation_type in ["equation", "algebra", "calculus"]:
            return f"Result: {result}"
            
        return f"Result: {result}"

    def matrix_operations(self, params: Dict[str, Any]) -> Any:
        """
        Perform matrix operations using NumPy.
        
        Args:
            params: Dictionary containing matrix operation parameters
            
        Returns:
            The result of the matrix operation
        """
        operation = params.get("operation", "info")
        
        # Create matrix from values if provided
        if "values" in params:
            matrix = np.array(params["values"], dtype=float)
        elif "rows" in params and "cols" in params:
            # Generate random matrix if only dimensions provided
            matrix = np.random.rand(params["rows"], params["cols"])
        else:
            return "Insufficient matrix information provided"
        
        # Perform requested operation
        if operation == "determinant":
            if matrix.shape[0] != matrix.shape[1]:
                return "Cannot calculate determinant of non-square matrix"
            return np.linalg.det(matrix)
            
        elif operation == "inverse":
            if matrix.shape[0] != matrix.shape[1]:
                return "Cannot calculate inverse of non-square matrix"
            try:
                return np.linalg.inv(matrix)
            except np.linalg.LinAlgError:
                return "Matrix is singular, cannot compute inverse"
                
        elif operation == "eigenvalues":
            if matrix.shape[0] != matrix.shape[1]:
                return "Cannot calculate eigenvalues of non-square matrix"
            return np.linalg.eigvals(matrix)
            
        else:  # info
            info = {
                "shape": matrix.shape,
                "rank": np.linalg.matrix_rank(matrix),
                "frobenius_norm": np.linalg.norm(matrix, 'fro')
            }
            return f"Matrix information:\nShape: {info['shape']}\nRank: {info['rank']}\nFrobenius Norm: {info['frobenius_norm']:.4f}"

    def statistical_analysis(self, params: Dict[str, Any]) -> Any:
        """
        Perform statistical analysis using NumPy and SciPy.
        
        Args:
            params: Dictionary containing statistical analysis parameters
            
        Returns:
            The result of the statistical analysis
        """
        operation = params.get("operation", "summary")
        
        if "data" not in params or not params["data"]:
            return "No data provided for statistical analysis"
            
        data = np.array(params["data"])
        
        if operation == "mean":
            return np.mean(data)
            
        elif operation == "median":
            return np.median(data)
            
        elif operation == "variance":
            return np.var(data)
            
        elif operation == "std":
            return np.std(data)
            
        elif operation == "correlation":
            if len(data) < 2:
                return "Need at least two datasets for correlation"
            # Split data in half for correlation
            mid = len(data) // 2
            return np.corrcoef(data[:mid], data[mid:])[0, 1]
            
        else:  # summary
            quartiles = np.percentile(data, [25, 50, 75])
            return {
                "mean": np.mean(data),
                "median": np.median(data),
                "std": np.std(data),
                "min": np.min(data),
                "max": np.max(data),
                "q1": quartiles[0],
                "q3": quartiles[2]
            }

    def algebraic_operations(self, params: Dict[str, Any]) -> Any:
        """
        Perform algebraic operations using SymPy.
        
        Args:
            params: Dictionary containing algebraic operation parameters
            
        Returns:
            The result of the algebraic operation
        """
        operation = params.get("operation", "simplify")
        
        if "expression" not in params:
            return "No expression provided for algebraic operation"
            
        expr_str = params["expression"]
        
        # Define common symbols
        x, y, z = sym.symbols('x y z')
        
        # Parse the expression
        try:
            expr = sym.sympify(expr_str)
        except Exception as e:
            return f"Error parsing expression: {str(e)}"
        
        if operation == "factor":
            return sym.factor(expr)
            
        elif operation == "expand":
            return sym.expand(expr)
            
        elif operation == "simplify":
            return sym.simplify(expr)
            
        return sym.simplify(expr)  # Default to simplify

    def calculus_operations(self, params: Dict[str, Any]) -> Any:
        """
        Perform calculus operations using SymPy.
        
        Args:
            params: Dictionary containing calculus operation parameters
            
        Returns:
            The result of the calculus operation
        """
        operation = params.get("operation", "derivative")
        
        if "expression" not in params:
            return "No expression provided for calculus operation"
            
        expr_str = params["expression"]
        variable = params.get("variable", "x")
        
        # Define symbols for common variables
        x, y, z = sym.symbols('x y z')
        t = sym.symbols('t')
        
        # Get the variable symbol
        var_symbol = locals()[variable] if variable in locals() else sym.symbols(variable)
        
        # Parse the expression
        try:
            expr = sym.sympify(expr_str)
        except Exception as e:
            return f"Error parsing expression: {str(e)}"
        
        if operation == "derivative":
            return sym.diff(expr, var_symbol)
            
        elif operation == "integrate":
            return sym.integrate(expr, var_symbol)
            
        elif operation == "limit":
            approach = params.get("approach", 0)
            return sym.limit(expr, var_symbol, approach)
            
        return "Unknown calculus operation"

    def solve_equation(self, params: Dict[str, Any]) -> Any:
        """
        Solve equations using SymPy.
        
        Args:
            params: Dictionary containing equation parameters
            
        Returns:
            The solution to the equation
        """
        if "equation" not in params:
            return "No equation provided to solve"
            
        eq_str = params["equation"]
        variable = params.get("variable", "x")
        
        # Define symbols for common variables
        x, y, z = sym.symbols('x y z')
        
        # Get the variable symbol
        var_symbol = locals()[variable] if variable in locals() else sym.symbols(variable)
        
        # Parse the equation
        try:
            # Check if equation contains an equals sign
            if "=" in eq_str:
                left_str, right_str = eq_str.split("=", 1)
                left = sym.sympify(left_str)
                right = sym.sympify(right_str)
                equation = sym.Eq(left, right)
            else:
                # If no equals sign, assume expression = 0
                equation = sym.Eq(sym.sympify(eq_str), 0)
                
            # Solve the equation
            solution = sym.solve(equation, var_symbol)
            
            if not solution:
                return f"No solution found for the equation {equation}"
            elif len(solution) == 1:
                return f"{variable} = {solution[0]}"
            else:
                return f"{variable} = {solution}"
                
        except Exception as e:
            return f"Error solving equation: {str(e)}"