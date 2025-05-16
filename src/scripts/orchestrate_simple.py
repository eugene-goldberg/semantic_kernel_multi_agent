#!/usr/bin/env python3
"""
Simplified orchestration system using direct API calls to Azure OpenAI.
This avoids complex Semantic Kernel plugin registration.
"""

import os
import sys
import asyncio
import json
import requests
from dotenv import load_dotenv

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.services.weather_service import WeatherService

class SimpleOrchestrator:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get Azure OpenAI configuration
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.api_version = "2024-05-01-preview"
        
        if not all([self.endpoint, self.api_key, self.deployment]):
            raise ValueError("Azure OpenAI configuration not found in .env file")
        
        # Create weather service
        self.weather_service = WeatherService()
        
        # System message for the assistant
        self.system_message = """
        You are a helpful assistant that provides friendly, concise, and accurate information.
        When the user asks about weather, you should use the GetWeather function to get accurate weather information.
        Always extract the location from the user's question when dealing with weather queries.
        
        For example:
        - If they ask 'What's the weather like in Seattle?', call GetWeather with location='Seattle, WA'
        - If they ask 'Will it rain tomorrow in Chicago?', call GetWeather with location='Chicago, IL' and type='forecast'
        
        DO NOT make up weather information. ALWAYS use the GetWeather function for weather queries.
        For other questions, answer directly from your knowledge.
        """
        
        # Tool definitions
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "GetWeather",
                    "description": "Get weather information for a location (current or forecast)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g. Seattle, WA"
                            },
                            "type": {
                                "type": "string",
                                "enum": ["current", "forecast"],
                                "description": "The type of weather information to retrieve"
                            }
                        },
                        "required": ["location"]
                    }
                }
            }
        ]
    
    async def get_weather(self, location, weather_type="current"):
        """Get weather information directly from the weather service"""
        try:
            if weather_type.lower() == "forecast":
                result = self.weather_service.get_forecast(city=location, days=3)
                
                # Format the forecast data into a readable string
                forecast_str = f"Weather forecast for {location}:\n"
                
                for day in result.get("forecast", [])[:3]:  # First 3 days
                    name = day.get("name", "Unknown")
                    temp = day.get("temperature", "N/A")
                    condition = day.get("description", "Unknown")
                    forecast_str += f"- {name}: {temp}°F, {condition}\n"
                
                return forecast_str
            else:
                # Default to current weather
                result = self.weather_service.get_current_weather(city=location)
                
                # Format the current weather data into a readable string
                temp = result.get("temperature", "N/A")
                condition = result.get("description", "Unknown")
                wind = result.get("wind_speed", "N/A")
                wind_dir = result.get("wind_direction", "")
                
                return (f"Current weather in {location}: {temp}°F, {condition}, "
                        f"Wind: {wind} mph {wind_dir}")
                
        except Exception as e:
            return (f"Error retrieving weather information: {str(e)}\n"
                   f"Note: This weather service only works for US locations.")
    
    async def chat_completion_request(self, messages, tools=None, tool_choice=None):
        """Send a chat completion request to Azure OpenAI"""
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        url = f"{self.endpoint}openai/deployments/{self.deployment}/chat/completions?api-version={self.api_version}"
        
        payload = {
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 800
        }
        
        if tools:
            payload["tools"] = tools
            
        if tool_choice:
            payload["tool_choice"] = tool_choice
            
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error calling Azure OpenAI: {str(e)}")
            if hasattr(response, 'text'):
                print(f"Response: {response.text}")
            raise
    
    async def chat_with_function_calling(self, input_text, chat_history=None):
        """Chat with the model using function calling to trigger weather functions"""
        if chat_history is None:
            chat_history = []
        
        # Prepare the messages
        messages = [
            {"role": "system", "content": self.system_message}
        ]
        
        # Add chat history
        for msg in chat_history:
            messages.append(msg)
        
        # Add the current user message
        messages.append({"role": "user", "content": input_text})
        
        # Make the initial request
        response = await self.chat_completion_request(
            messages=messages,
            tools=self.tools,
            tool_choice="auto"
        )
        
        # Get the response content
        response_message = response["choices"][0]["message"]
        content = response_message.get("content")
        function_calls = []
        
        # Check if the model wants to call a function
        if "tool_calls" in response_message:
            # Process each tool call
            for tool_call in response_message["tool_calls"]:
                if tool_call["function"]["name"] == "GetWeather":
                    # Parse the arguments
                    args = json.loads(tool_call["function"]["arguments"])
                    location = args.get("location")
                    weather_type = args.get("type", "current")
                    
                    print(f"\nCalling weather service for: {location} ({weather_type})")
                    
                    # Call the function
                    weather_result = await self.get_weather(
                        location=location,
                        weather_type=weather_type
                    )
                    
                    function_calls.append({
                        "name": "GetWeather",
                        "arguments": args,
                        "result": weather_result
                    })
                    
                    # Create a new message to continue the conversation
                    followup_messages = messages.copy()
                    followup_messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": tool_call["id"],
                                "type": "function",
                                "function": {
                                    "name": "GetWeather",
                                    "arguments": tool_call["function"]["arguments"]
                                }
                            }
                        ]
                    })
                    followup_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": weather_result
                    })
                    
                    # Get the final response that includes the function result
                    final_response = await self.chat_completion_request(
                        messages=followup_messages
                    )
                    
                    # Update the content with the final response
                    content = final_response["choices"][0]["message"]["content"]
                    
                    break
        
        return content, function_calls

    async def run_chat(self):
        """Run the orchestration chat"""
        print("Setting up orchestration...")
        
        print("\nWelcome to the Multi-Agent Chat!")
        print("You can ask general questions or about the weather.")
        print("Type 'exit' to quit.")
        
        # Chat loop
        chat_history = []
        
        while True:
            try:
                user_input = input("\nYou: ")
                
                # Check for exit command
                if user_input.lower() == "exit":
                    print("Exiting chat...")
                    break
                    
                # Empty input should just prompt again
                if not user_input.strip():
                    continue
                    
                # Process the user input with function calling
                response, function_calls = await self.chat_with_function_calling(
                    user_input,
                    chat_history
                )
                
                # Add messages to chat history
                chat_history.append({"role": "user", "content": user_input})
                chat_history.append({"role": "assistant", "content": response})
                
                # If there were function calls, show debug info
                if function_calls:
                    print("\n[Function calls processed]")
                
                # Print the response
                print(f"Agent: {response}")
                
            except Exception as e:
                print(f"Error: {str(e)}")
                import traceback
                traceback.print_exc()

async def main():
    """Main entry point"""
    try:
        orchestrator = SimpleOrchestrator()
        await orchestrator.run_chat()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())