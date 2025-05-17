#!/usr/bin/env python3
"""
Interactive client for agents deployed to Azure AI Foundry.
This script provides a unified interface for interacting with deployed agents.
"""

import os
import sys
import json
import time
import asyncio
import logging
import aiohttp
import subprocess
from dotenv import load_dotenv

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AiFoundryClient:
    """Client for interacting with agents deployed to Azure AI Foundry."""
    
    def __init__(self):
        """Initialize the client."""
        # Load environment variables
        load_dotenv()
        load_dotenv('.env.ai_foundry')
        
        # Azure Resources
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        self.workspace_name = os.getenv("AZURE_WORKSPACE_NAME")
        self.region = os.getenv("AZURE_REGION", "westus")
        
        # API Configuration
        self.api_version = os.getenv("AI_FOUNDRY_API_VERSION", "2024-12-01-preview")
        
        # Load agent information
        self.agents = self._load_agent_info()
        self.current_agent = "orchestrator"  # Default agent
        
        # Initialize conversation thread
        self.thread_id = None
        
        logger.info(f"Initialized AI Foundry client for workspace: {self.workspace_name}")
    
    def get_base_url(self) -> str:
        """Get the base URL for the Azure AI Foundry API"""
        return f"https://{self.region}.api.azureml.ms/agents/v1.0/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{self.workspace_name}"
    
    async def _get_access_token(self) -> str:
        """
        Get an Azure AD access token using the Azure CLI.
        
        Returns:
            str: The access token
        """
        try:
            result = subprocess.run(
                ["az", "account", "get-access-token", "--query", "accessToken", "-o", "tsv"],
                capture_output=True,
                text=True,
                check=True
            )
            token = result.stdout.strip()
            return token
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get access token: {e.stderr}")
            raise
    
    def _load_agent_info(self):
        """Load agent information from deployment file."""
        try:
            # Try to load from AI Foundry deployment info
            if os.path.exists("ai_foundry_deployment_info.json"):
                with open("ai_foundry_deployment_info.json", "r") as f:
                    deployment_info = json.load(f)
            # Fall back to regular deployment info
            elif os.path.exists("orchestration_deployment_info.json"):
                with open("orchestration_deployment_info.json", "r") as f:
                    deployment_info = json.load(f)
            else:
                logger.warning("No deployment info found. Using placeholder agent IDs.")
                return {
                    "chat": {"id": "chat_agent_placeholder"},
                    "weather": {"id": "weather_agent_placeholder"},
                    "calculator": {"id": "calculator_agent_placeholder"},
                    "orchestrator": {"id": "orchestrator_agent_placeholder"}
                }
            
            # Extract agent IDs
            agents = {
                "chat": {"id": deployment_info.get("chat_agent_id")},
                "weather": {"id": deployment_info.get("weather_agent_id")},
                "calculator": {"id": deployment_info.get("calculator_agent_id")},
                "orchestrator": {"id": deployment_info.get("orchestrator_agent_id")}
            }
            
            logger.info("Loaded agent IDs:")
            for agent_type, agent_info in agents.items():
                if agent_info["id"]:
                    logger.info(f"- {agent_type.capitalize()}: {agent_info['id']}")
                else:
                    logger.warning(f"- {agent_type.capitalize()}: Not found")
            
            return agents
        except Exception as e:
            logger.error(f"Error loading agent information: {str(e)}")
            raise
    
    async def create_thread(self):
        """Create a new conversation thread."""
        try:
            # Get access token
            token = await self._get_access_token()
            
            # Set up HTTP headers
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Generate API URL
            base_url = self.get_base_url()
            url = f"{base_url}/threads?api-version={self.api_version}"
            
            # Send the request to create the thread
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        logger.error(f"Error creating thread: {error_text}")
                        raise Exception(f"Failed to create thread: {response.status} - {error_text}")
                    
                    thread_data = await response.json()
                    self.thread_id = thread_data.get("id")
                    
                    if not self.thread_id:
                        logger.error(f"No thread ID returned: {thread_data}")
                        raise Exception("No thread ID returned from the API")
                    
                    logger.info(f"Created thread with ID: {self.thread_id}")
                    return f"Created new conversation thread: {self.thread_id}"
        except Exception as e:
            logger.error(f"Error creating thread: {str(e)}")
            return f"Error creating thread: {str(e)}"
    
    async def send_message(self, message):
        """
        Send a message to the current agent.
        
        Args:
            message: User message text
            
        Returns:
            Agent response text
        """
        # Get current agent ID
        agent_id = self.agents[self.current_agent]["id"]
        if not agent_id or agent_id.endswith("_placeholder"):
            return f"Error: No valid {self.current_agent} agent found"
        
        try:
            # Get access token
            token = await self._get_access_token()
            
            # Set up HTTP headers
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Generate base API URL
            base_url = self.get_base_url()
            
            # Create or get thread if needed
            if not self.thread_id:
                logger.info("No active thread. Creating one...")
                thread_url = f"{base_url}/threads?api-version={self.api_version}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(thread_url, headers=headers) as response:
                        if response.status >= 400:
                            error_text = await response.text()
                            logger.error(f"Error creating thread: {error_text}")
                            raise Exception(f"Failed to create thread: {response.status} - {error_text}")
                        
                        thread_data = await response.json()
                        self.thread_id = thread_data.get("id")
                        logger.info(f"Created new thread: {self.thread_id}")
            
            # Add message to thread
            message_url = f"{base_url}/threads/{self.thread_id}/messages?api-version={self.api_version}"
            message_payload = {
                "role": "user",
                "content": message
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(message_url, headers=headers, json=message_payload) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        logger.error(f"Error adding message: {error_text}")
                        raise Exception(f"Failed to add message: {response.status} - {error_text}")
                    
                    logger.info(f"Added message to thread: {self.thread_id}")
            
            # Run the agent on the thread
            run_url = f"{base_url}/threads/{self.thread_id}/runs?api-version={self.api_version}"
            run_payload = {
                "assistant_id": agent_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(run_url, headers=headers, json=run_payload) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        logger.error(f"Error starting run: {error_text}")
                        raise Exception(f"Failed to start run: {response.status} - {error_text}")
                    
                    run_data = await response.json()
                    run_id = run_data.get("id")
                    
                    if not run_id:
                        logger.error(f"No run ID returned: {run_data}")
                        raise Exception("No run ID returned from the API")
                    
                    logger.info(f"Started run with ID: {run_id}")
            
            # Wait for the run to complete
            run_status_url = f"{base_url}/threads/{self.thread_id}/runs/{run_id}?api-version={self.api_version}"
            status = "queued"
            
            print("Agent processing...", end="", flush=True)
            while status not in ["completed", "failed", "cancelled"]:
                async with aiohttp.ClientSession() as session:
                    async with session.get(run_status_url, headers=headers) as response:
                        if response.status >= 400:
                            error_text = await response.text()
                            logger.error(f"Error checking run status: {error_text}")
                            raise Exception(f"Failed to check run status: {response.status} - {error_text}")
                        
                        run_status_data = await response.json()
                        status = run_status_data.get("status")
                        logger.info(f"Run status: {status}")
                        
                        # Handle tool calls if needed
                        if status == "requires_action" and run_status_data.get("required_action", {}).get("type") == "submit_tool_outputs":
                            # Extract tool calls
                            tool_calls = run_status_data.get("required_action", {}).get("submit_tool_outputs", {}).get("tool_calls", [])
                            logger.info(f"Processing {len(tool_calls)} tool calls")
                            
                            # Process each tool call
                            tool_outputs = []
                            for tool_call in tool_calls:
                                tool_call_id = tool_call.get("id")
                                function_name = tool_call.get("function", {}).get("name")
                                function_args = json.loads(tool_call.get("function", {}).get("arguments", "{}"))
                                
                                logger.info(f"Processing tool call: {function_name} with args: {function_args}")
                                
                                if function_name == "GetWeather":
                                    location = function_args.get("location", "Seattle, WA")
                                    weather_type = function_args.get("type", "current")
                                    # Simulate weather response
                                    output = f"Weather data for {location} ({weather_type}): Temperature: 72°F, Condition: Sunny"
                                    
                                elif function_name == "Calculate":
                                    expression = function_args.get("expression", "")
                                    try:
                                        # Enhanced calculation handling
                                        # Replace sqrt with math operation
                                        if "sqrt" in expression:
                                            # Replace sqrt(x) with x**0.5
                                            import re
                                            match = re.search(r'sqrt\((\d+)\)', expression)
                                            if match:
                                                num = int(match.group(1))
                                                result = num**0.5
                                                output = f"The square root of {num} is {result}"
                                            else:
                                                # Basic evaluation as fallback
                                                result = eval(expression, {"__builtins__": {}}, {"sqrt": lambda x: x**0.5})
                                                output = f"Result of {expression} = {result}"
                                        # Handle power operations
                                        elif "^" in expression:
                                            # Replace x^y with x**y
                                            exp_parts = expression.split("^")
                                            if len(exp_parts) == 2:
                                                base = float(exp_parts[0].strip())
                                                power = float(exp_parts[1].strip())
                                                result = base**power
                                                output = f"{base} raised to the power of {power} is {result}"
                                            else:
                                                # Safe evaluation
                                                expression = expression.replace("^", "**")
                                                result = eval(expression, {"__builtins__": {}})
                                                output = f"Result of {expression} = {result}"
                                        # Handle special symbols like √
                                        elif "√" in expression:
                                            # Replace √x with x**0.5
                                            num = float(expression.replace("√", "").strip())
                                            result = num**0.5
                                            output = f"The square root of {num} is {result}"
                                        else:
                                            # Basic evaluation for simple expressions
                                            # Use safe eval with limited builtins
                                            import math
                                            safe_dict = {
                                                "abs": abs, "float": float, "int": int,
                                                "max": max, "min": min, "round": round,
                                                "sum": sum, "pow": pow,
                                                # Add math functions
                                                "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos,
                                                "tan": math.tan, "pi": math.pi, "e": math.e
                                            }
                                            result = eval(expression, {"__builtins__": {}}, safe_dict)
                                            output = f"Result of {expression} = {result}"
                                    except Exception as calc_error:
                                        # For pure numbers, just return them
                                        if expression.strip().isdigit():
                                            output = expression.strip()
                                        else:
                                            output = f"Error calculating {expression}: {str(calc_error)}"
                                elif function_name == "RouteToAgent":
                                    agent_type = function_args.get("agent_type", "chat")
                                    query = function_args.get("query", "")
                                    
                                    # Handle different agent types
                                    if agent_type == "chat":
                                        # Simulate a response from the chat agent
                                        output = f"Routed to ChatAgent: {query}"
                                        
                                        # For general knowledge questions, provide responses directly
                                        if "president" in query.lower():
                                            output = "The first president of the United States was George Washington, who served from 1789 to 1797."
                                        elif "capital" in query.lower():
                                            output = "The capital of France is Paris."
                                        else:
                                            output = f"As a general assistant, I can help with that. {query}"
                                    elif agent_type == "weather":
                                        output = f"Routed to WeatherAgent: The weather is sunny and 72°F"
                                    elif agent_type == "calculator":
                                        output = f"Routed to CalculatorAgent: Let me calculate that for you."
                                    else:
                                        output = f"Unknown agent type: {agent_type}"
                                else:
                                    output = f"Unsupported function: {function_name}"
                                
                                # Add to tool outputs
                                tool_outputs.append({
                                    "tool_call_id": tool_call_id,
                                    "output": output
                                })
                            
                            # Submit tool outputs
                            submit_url = f"{base_url}/threads/{self.thread_id}/runs/{run_id}/submit_tool_outputs?api-version={self.api_version}"
                            submit_payload = {
                                "tool_outputs": tool_outputs
                            }
                            
                            async with aiohttp.ClientSession() as session:
                                async with session.post(submit_url, headers=headers, json=submit_payload) as response:
                                    if response.status >= 400:
                                        error_text = await response.text()
                                        logger.error(f"Error submitting tool outputs: {error_text}")
                                        raise Exception(f"Failed to submit tool outputs: {response.status} - {error_text}")
                                    
                                    logger.info(f"Successfully submitted {len(tool_outputs)} tool outputs")
                        
                        # Print a waiting animation
                        print(".", end="", flush=True)
                        
                        # Wait a bit before checking again
                        await asyncio.sleep(1)
            
            # Clear the loading animation
            print("\r" + " " * 50 + "\r", end="", flush=True)
            
            # Check if run failed
            if status == "failed":
                failure_reason = "Unknown error" if "failure" not in run_status_data else run_status_data["failure"]["reason"]
                return f"Error: Agent run failed - {failure_reason}"
            
            # Get messages from the thread
            messages_url = f"{base_url}/threads/{self.thread_id}/messages?api-version={self.api_version}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(messages_url, headers=headers) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        logger.error(f"Error getting messages: {error_text}")
                        raise Exception(f"Failed to get messages: {response.status} - {error_text}")
                    
                    messages_data = await response.json()
                    
                    # Extract the last assistant message
                    assistant_messages = [msg for msg in messages_data.get("data", []) if msg.get("role") == "assistant"]
                    if not assistant_messages:
                        return "Error: No response from agent"
                    
                    # Get the latest message
                    latest_message = assistant_messages[0]  # First is most recent
                    logger.debug(f"Latest message content structure: {latest_message}")
                    response_text = ""
                    
                    # Process content parts
                    for content_part in latest_message.get("content", []):
                        if content_part.get("type") == "text":
                            text_value = content_part.get("text", "")
                            if isinstance(text_value, dict) and "value" in text_value:
                                response_text += text_value["value"]
                            elif isinstance(text_value, str):
                                response_text += text_value
                            else:
                                response_text += str(text_value)
                    
                    return response_text
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"Error communicating with agent: {str(e)}"
    
    def switch_agent(self, agent_type):
        """
        Switch to a different agent.
        
        Args:
            agent_type: Type of agent to switch to
            
        Returns:
            Message indicating the switch
        """
        if agent_type not in self.agents:
            return f"Unknown agent type: {agent_type}"
        
        if not self.agents[agent_type]["id"] or self.agents[agent_type]["id"].endswith("_placeholder"):
            return f"Error: {agent_type.capitalize()} agent not found in deployment info"
        
        # Switch agent
        self.current_agent = agent_type
        
        # Thread will be cleared on next message
        self.thread_id = None
        
        return f"Switched to {agent_type.capitalize()} Agent"

async def interactive_chat():
    """Run an interactive chat session with deployed agents."""
    try:
        client = AiFoundryClient()
        
        print("\n=== AI Foundry Agent Interactive Chat ===")
        print(f"Currently using: {client.current_agent.capitalize()} Agent")
        print("Commands:")
        print("  'exit' - Exit the chat")
        print("  'switch chat/weather/calculator/orchestrator' - Switch to a different agent")
        print("  'clear' - Clear conversation thread")
        
        while True:
            try:
                user_input = input("\nYou: ")
            except (KeyboardInterrupt, EOFError):
                print("\nExiting chat...")
                break
            
            # Process commands
            if user_input.lower() == "exit":
                print("Exiting chat...")
                break
            elif user_input.lower() == "clear":
                result = await client.create_thread()
                print(f"System: {result}")
                continue
            elif user_input.lower().startswith("switch "):
                agent_type = user_input.lower().split(" ", 1)[1].strip()
                result = client.switch_agent(agent_type)
                print(f"System: {result}")
                continue
            elif not user_input.strip():
                continue
            
            # Process regular message
            response = await client.send_message(user_input)
            print(f"{client.current_agent.capitalize()} Agent: {response}")
            
    except Exception as e:
        logger.error(f"Error in interactive chat: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Main entry point."""
    try:
        await interactive_chat()
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())