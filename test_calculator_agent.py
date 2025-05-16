#!/usr/bin/env python3
"""
Test script for the Calculator Agent.
This tests the calculator agent's ability to handle different types of mathematical operations.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.agents.calculator_agent import CalculatorAgent

def test_calculator_agent():
    """Test the calculator agent with various mathematical operations"""
    print("Testing Calculator Agent...")
    calculator = CalculatorAgent()
    
    # Test cases for different types of operations
    test_cases = [
        {
            "name": "Simple Arithmetic",
            "query": "Calculate 2 + 2 * 3",
            "expected_type": "arithmetic"
        },
        {
            "name": "Matrix Determinant",
            "query": "Calculate the determinant of matrix [[1, 2], [3, 4]]",
            "expected_type": "matrix"
        },
        {
            "name": "Statistical Analysis",
            "query": "Calculate the mean, median and standard deviation of 10, 20, 30, 40, 50",
            "expected_type": "statistics"
        },
        {
            "name": "Algebraic Expression",
            "query": "Simplify the expression x^2 + 2*x + 1",
            "expected_type": "algebra"
        },
        {
            "name": "Calculus - Derivative",
            "query": "Find the derivative of x^3 with respect to x",
            "expected_type": "calculus"
        },
        {
            "name": "Equation Solving",
            "query": "Solve the equation x^2 - 5*x + 6 = 0",
            "expected_type": "equation"
        }
    ]
    
    # Run tests
    for test in test_cases:
        print(f"\n--- Testing {test['name']} ---")
        print(f"Query: {test['query']}")
        
        # Check if the operation type is correctly identified
        operation_type = calculator._determine_operation_type(test['query'])
        print(f"Identified operation type: {operation_type}")
        
        # Process the query
        result = calculator.process_request(test['query'])
        print(f"Result: {result}")
        
        # Verify the operation type
        if operation_type == test['expected_type']:
            print(f"✓ Operation type correctly identified as {operation_type}")
        else:
            print(f"✗ Expected {test['expected_type']} but got {operation_type}")

def main():
    """Main entry point"""
    try:
        test_calculator_agent()
        print("\nCalculator Agent tests completed")
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()