#!/usr/bin/env python3
"""
Orchestration system using Semantic Kernel to delegate from chat agent to weather agent.
"""

import os
import sys
import asyncio
import json
from dotenv import load_dotenv
import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureTextCompletion
from semantic_kernel.planners import FunctionCallingStepwisePlanner

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.agents.plugins.weather_plugin import WeatherPlugin
from src.agents.plugins.calculator_plugin import CalculatorPlugin
from src.services.weather_service import WeatherService

def setup_kernel_with_openai():
    """Set up a kernel with Azure OpenAI"""
    # Load environment variables
    load_dotenv()
    
    # Get Azure OpenAI configuration
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    if not all([endpoint, api_key, deployment]):
        raise ValueError("Azure OpenAI configuration not found in .env file")
    
    # Create a kernel
    kernel = sk.Kernel()
    
    # Add Azure OpenAI chat service
    kernel.add_service(
        AzureChatCompletion(
            service_id="chat", 
            deployment_name=deployment,
            endpoint=endpoint,
            api_key=api_key,
            api_version="2024-02-15-preview"
        )
    )
    
    return kernel

async def setup_chat_agent(kernel):
    """Set up the chat agent with function calling capabilities"""
    # Create a planner that can use function calling
    planner = FunctionCallingStepwisePlanner(
        service_id="chat"
    )
    
    # Set the kernel for the planner
    planner._kernel = kernel
    
    # Create the system message
    system_message = """
    You are a helpful assistant that provides friendly, concise, and accurate information.
    
    When the user asks about weather, you should call the GetWeather function to get accurate weather information.
    Always extract the location from the user's question when dealing with weather queries.
    For example:
    - If they ask 'What's the weather like in Seattle?', call GetWeather with location='Seattle, WA'
    - If they ask 'Will it rain tomorrow in Chicago?', call GetWeather with location='Chicago, IL' and type='forecast'
    DO NOT make up weather information. ALWAYS use the GetWeather function for weather queries.
    
    When the user asks about calculations or mathematical operations, use the appropriate function from the CalculatorPlugin:
    - For basic calculations, use the Calculate function
    - For matrix operations, use the MatrixOperation function
    - For statistical analysis, use the Statistics function
    - For equation solving, use the SolveEquation function
    - For calculus operations, use the Calculus function
    - For algebraic operations, use the Algebra function
    
    For other questions, answer directly from your knowledge.
    """
    
    return planner, system_message

async def setup_plugins(kernel):
    """Set up all plugins"""
    # Create and set up weather plugin
    weather_service = WeatherService()
    weather_plugin = WeatherPlugin(weather_service)
    kernel.add_plugin(weather_plugin, plugin_name="WeatherPlugin")
    
    # Create and set up calculator plugin
    calculator_plugin = CalculatorPlugin()
    kernel.add_plugin(calculator_plugin, plugin_name="CalculatorPlugin")
    
    return weather_plugin, calculator_plugin

async def orchestration_chat():
    """Run the orchestration chat"""
    print("Setting up Semantic Kernel orchestration...")
    
    # Set up the kernel
    kernel = setup_kernel_with_openai()
    
    # Set up plugins
    await setup_plugins(kernel)
    
    # Set up the chat agent with function calling
    planner, system_message = await setup_chat_agent(kernel)
    
    print("\nWelcome to the SK Multi-Agent Chat!")
    print("You can ask general questions, weather information, or mathematical calculations.")
    print("Examples:")
    print("  - 'What's the weather like in Seattle?'")
    print("  - 'Calculate the square root of 64'")
    print("  - 'Who wrote Pride and Prejudice?'")
    print("Type 'exit' to quit.")
    
    # Chat loop
    chat_history = []
    
    while True:
        try:
            user_input = input("\nYou: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting chat...")
            break
        
        if user_input.lower() == "exit":
            print("Exiting chat...")
            break
        
        # Add user message to chat history
        chat_history.append({"role": "user", "content": user_input})
        
        # Execute the planner to potentially call functions
        try:
            print("Thinking...", end="\r")
            # Execute with function calling planner
            result = await planner.invoke(
                kernel=kernel,
                question=user_input
            )
            
            # Add assistant message to chat history
            chat_history.append({"role": "assistant", "content": str(result)})
            
            # Print the response (clear the "Thinking..." first)
            print("          ", end="\r")
            print(f"Agent: {result}")
            
            # Optionally clear history if it gets too long to save tokens
            if len(chat_history) > 10:
                # Keep the first (system) message and last 4 exchanges
                chat_history = [chat_history[0]] + chat_history[-8:]
            
        except Exception as e:
            print(f"Error: {str(e)}")
            print("Let me try again with a simpler approach...")
            
            # Fallback to regular completion
            print("Thinking (fallback)...", end="\r")
            chat_service = kernel.get_service("chat")
            response = await chat_service.complete_chat_async(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_input}
                ]
            )
            response_text = response[0].content if response else "Sorry, I couldn't generate a response."
            print("                      ", end="\r")
            print(f"Agent: {response_text}")
            
            # Add to chat history
            chat_history.append({"role": "assistant", "content": response_text})
            
            # Optionally clear history if it gets too long to save tokens
            if len(chat_history) > 10:
                # Keep the first (system) message and last 4 exchanges
                chat_history = [chat_history[0]] + chat_history[-8:]

async def main():
    """Main entry point"""
    try:
        await orchestration_chat()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())