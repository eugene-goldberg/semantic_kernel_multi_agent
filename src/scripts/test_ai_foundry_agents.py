#!/usr/bin/env python3
"""
Script to test all deployed agents in Azure AI Foundry.
"""

import os
import sys
import json
import time
import logging
import requests
from azure.identity import AzureCliCredential

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Azure AI Foundry settings
SUBSCRIPTION_ID = "514bd6d3-2c02-45c6-a86f-29cf262a379a"
RESOURCE_GROUP = "semantic-kernel-multi-agent-rg"
WORKSPACE_NAME = "sk-multi-agent-project"
REGION = "eastus"
API_VERSION = "2024-12-01-preview"

# Base URL for the Azure AI Foundry API
BASE_URL = f"https://{REGION}.api.azureml.ms/agents/v1.0/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP}/providers/Microsoft.MachineLearningServices/workspaces/{WORKSPACE_NAME}"

# Test messages for each agent type
TEST_MESSAGES = {
    "chat": [
        "What is the capital of France?",
        "Tell me a joke about programming."
    ],
    "weather": [
        "What's the weather like in Seattle?",
        "Is it raining in New York City?"
    ],
    "calculator": [
        "What is 15 + 27?",
        "Calculate the square root of 144."
    ],
    "orchestrator": [
        "Tell me about the weather in Miami.",
        "What is 125 divided by 5?"
    ]
}

# Functions for various weather operations
WEATHER_FUNCTIONS = {
    "get_current_weather": {
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The unit of temperature to use"
                }
            },
            "required": ["location"]
        }
    }
}

# Functions for calculator operations
CALCULATOR_FUNCTIONS = {
    "calculate": {
        "description": "Perform a calculation with the given expression",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate"
                }
            },
            "required": ["expression"]
        }
    }
}

def load_deployment_info():
    """Load deployment information from JSON file."""
    try:
        with open(os.path.join(project_root, 'ai_foundry_deployment_info.json'), 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading deployment info: {str(e)}")
        return None

def get_token():
    """Get Azure AD token."""
    credential = AzureCliCredential()
    token = credential.get_token("https://management.azure.com/.default").token
    return token

def create_thread(headers):
    """Create a new conversation thread."""
    url = f"{BASE_URL}/threads?api-version={API_VERSION}"
    response = requests.post(url, headers=headers, json={})
    
    if response.status_code in [200, 201]:
        return response.json().get("id")
    else:
        logger.error(f"Failed to create thread: {response.status_code}")
        logger.error(response.text)
        return None

def send_message(agent_id, thread_id, message, headers):
    """Send a message to the agent's thread."""
    url = f"{BASE_URL}/threads/{thread_id}/messages?api-version={API_VERSION}"
    payload = {
        "role": "user",
        "content": message
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code in [200, 201]:
        return response.json().get("id")
    else:
        logger.error(f"Failed to send message: {response.status_code}")
        logger.error(response.text)
        return None

def start_run(agent_id, thread_id, headers):
    """Start a run to process the messages in the thread."""
    url = f"{BASE_URL}/threads/{thread_id}/runs?api-version={API_VERSION}"
    payload = {
        "assistant_id": agent_id
    }
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code in [200, 201]:
        return response.json().get("id")
    else:
        logger.error(f"Failed to start run: {response.status_code}")
        logger.error(response.text)
        return None

def get_run_status(agent_id, thread_id, run_id, headers):
    """Get the status of a run."""
    url = f"{BASE_URL}/threads/{thread_id}/runs/{run_id}?api-version={API_VERSION}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("status")
    else:
        logger.error(f"Failed to get run status: {response.status_code}")
        logger.error(response.text)
        return None

def submit_tool_outputs(agent_id, thread_id, run_id, tool_outputs, headers):
    """Submit tool outputs for a run."""
    url = f"{BASE_URL}/threads/{thread_id}/runs/{run_id}/submit-tool-outputs?api-version={API_VERSION}"
    payload = {"tool_outputs": tool_outputs}
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code in [200, 201]:
        return True
    else:
        logger.error(f"Failed to submit tool outputs: {response.status_code}")
        logger.error(response.text)
        return False

def get_messages(agent_id, thread_id, headers):
    """Get all messages in a thread."""
    url = f"{BASE_URL}/threads/{thread_id}/messages?api-version={API_VERSION}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        logger.error(f"Failed to get messages: {response.status_code}")
        logger.error(response.text)
        return []

def handle_tool_call(tool_call):
    """Handle a tool call from the agent."""
    tool_call_id = tool_call.get("id")
    function_name = tool_call.get("function", {}).get("name")
    function_args = json.loads(tool_call.get("function", {}).get("arguments", "{}"))
    
    if function_name == "get_current_weather":
        location = function_args.get("location", "Seattle")
        unit = function_args.get("unit", "celsius")
        
        # Mock weather data
        weather_data = {
            "location": location,
            "temperature": 22 if unit == "celsius" else 72,
            "unit": unit,
            "forecast": ["sunny", "partly cloudy"],
            "humidity": 65
        }
        
        return {
            "tool_call_id": tool_call_id,
            "output": json.dumps(weather_data)
        }
    
    elif function_name == "calculate":
        expression = function_args.get("expression", "")
        
        try:
            # Safe eval for simple calculations
            result = eval(expression, {"__builtins__": {}}, {"sqrt": lambda x: x**0.5})
            return {
                "tool_call_id": tool_call_id,
                "output": str(result)
            }
        except Exception as e:
            return {
                "tool_call_id": tool_call_id,
                "output": f"Error calculating: {str(e)}"
            }
    
    return {
        "tool_call_id": tool_call_id,
        "output": "Unsupported function"
    }

def process_run(agent_id, thread_id, run_id, headers):
    """Process a run until it completes."""
    status = "queued"
    max_attempts = 30
    attempts = 0
    
    while status in ["queued", "in_progress", "requires_action"] and attempts < max_attempts:
        status = get_run_status(agent_id, thread_id, run_id, headers)
        logger.info(f"Run status: {status}")
        
        if status == "requires_action":
            # Get the run details to find required actions
            url = f"{BASE_URL}/assistants/{agent_id}/threads/{thread_id}/runs/{run_id}?api-version={API_VERSION}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                run_data = response.json()
                required_action = run_data.get("required_action", {})
                tool_calls = required_action.get("submit_tool_outputs", {}).get("tool_calls", [])
                
                if tool_calls:
                    # Process each tool call
                    tool_outputs = []
                    for tool_call in tool_calls:
                        tool_output = handle_tool_call(tool_call)
                        tool_outputs.append(tool_output)
                    
                    # Submit tool outputs
                    submitted = submit_tool_outputs(agent_id, thread_id, run_id, tool_outputs, headers)
                    if submitted:
                        logger.info("Tool outputs submitted successfully")
                    else:
                        logger.error("Failed to submit tool outputs")
        
        attempts += 1
        time.sleep(1)
    
    return status

def test_agent(agent_type, agent_id, test_messages, headers):
    """Test an agent with a series of messages."""
    print(f"\n=== TESTING {agent_type.upper()} AGENT ===")
    logger.info(f"Testing {agent_type} agent with ID: {agent_id}")
    
    # Create a new thread
    thread_id = create_thread(headers)
    if not thread_id:
        logger.error(f"Could not create thread for {agent_type} agent")
        return False
    
    logger.info(f"Created thread with ID: {thread_id}")
    
    for msg_index, message in enumerate(test_messages):
        print(f"Q: {message}")
        
        # Send message
        message_id = send_message(agent_id, thread_id, message, headers)
        if not message_id:
            logger.error(f"Could not send message to {agent_type} agent")
            continue
        
        # Start run
        run_id = start_run(agent_id, thread_id, headers)
        if not run_id:
            logger.error(f"Could not start run for {agent_type} agent")
            continue
        
        # Process run
        status = process_run(agent_id, thread_id, run_id, headers)
        
        if status == "completed":
            # Get the latest messages
            messages = get_messages(agent_id, thread_id, headers)
            # Find the most recent assistant message
            assistant_messages = [m for m in messages if m.get("role") == "assistant"]
            if assistant_messages:
                latest_message = assistant_messages[0]
                content = latest_message.get("content", [])
                
                # Log content structure
                logger.info(f"Message content type: {type(content)}")
                logger.info(f"Message content: {json.dumps(content, indent=2)}")
                
                # Extract text from content
                text_content = ""
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            text_obj = item.get("text", {})
                            if isinstance(text_obj, dict) and "value" in text_obj:
                                text_content += text_obj["value"]
                            elif isinstance(text_obj, str):
                                text_content += text_obj
                        elif isinstance(item, str):
                            text_content += item
                elif isinstance(content, str):
                    text_content = content
                
                print(f"A: {text_content}\n")
            else:
                print("A: No response received\n")
        else:
            print(f"A: Run did not complete. Final status: {status}\n")
    
    return True

def main():
    """Main function to test all agents."""
    # Load deployment info
    deployment_info = load_deployment_info()
    if not deployment_info or deployment_info.get("deployment_status") != "success":
        logger.error("No successful deployment info found")
        return
    
    # Get agent IDs
    agent_ids = {
        "chat": deployment_info.get("chat_agent_id"),
        "weather": deployment_info.get("weather_agent_id"),
        "calculator": deployment_info.get("calculator_agent_id"),
        "orchestrator": deployment_info.get("orchestrator_agent_id")
    }
    
    # Get Azure AD token
    token = get_token()
    
    # Set headers for API requests
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("Starting tests for Azure AI Foundry agents...\n")
    
    # Test each agent
    for agent_type, agent_id in agent_ids.items():
        if agent_id:
            test_agent(agent_type, agent_id, TEST_MESSAGES[agent_type], headers)
    
    print("\nAll tests completed.")

if __name__ == "__main__":
    main()