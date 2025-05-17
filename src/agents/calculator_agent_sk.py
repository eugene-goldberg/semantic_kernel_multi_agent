#!/usr/bin/env python3
"""
SK-based Calculator Agent for performing advanced mathematical operations.
This agent integrates with Semantic Kernel to provide advanced mathematical capabilities.
"""

from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from src.agents.plugins.calculator_plugin import CalculatorPlugin

class CalculatorAgent:
    """
    Calculator agent that provides advanced mathematical capabilities using Semantic Kernel.
    """
    
    def __init__(self, service=None, kernel=None):
        """
        Initialize calculator agent with calculator plugin
        
        Args:
            service: An optional pre-configured service
            kernel: An optional pre-configured kernel
        """
        if service is None:
            # Create a new service if none is provided
            service = AzureChatCompletion()
        
        # Create a kernel for this agent if not provided
        if kernel is None:
            kernel = Kernel()
        
        # Import the calculator plugin
        calculator_plugin = CalculatorPlugin()
        kernel.add_plugin(calculator_plugin, plugin_name="CalculatorPlugin")
        
        # Create the agent
        self.agent = ChatCompletionAgent(
            service=service,
            kernel=kernel,
            name="CalculatorAgent",
            instructions=(
                "You are a calculator specialist agent that performs advanced mathematical operations. "
                "You have access to powerful mathematical capabilities through your CalculatorPlugin skills. "
                "When asked about calculations, always use the appropriate function from CalculatorPlugin "
                "to get accurate results. "
                
                "For general calculations, use the Calculate function. "
                "For matrix operations, use the MatrixOperation function. "
                "For statistical analysis, use the Statistics function. "
                "For algebraic operations, use the Algebra function. "
                "For equation solving, use the SolveEquation function. "
                "For calculus operations, use the Calculus function. "
                
                "Provide your answers in a clear, concise manner, showing the steps of calculation "
                "when useful for understanding. "
                
                "If asked something not related to mathematics, politely explain "
                "that you specialize in calculations and mathematical operations only."
            ),
        )
    
    def get_agent(self):
        """Get the underlying ChatCompletionAgent"""
        return self.agent