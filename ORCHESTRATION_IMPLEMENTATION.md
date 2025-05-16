# Multi-Agent Orchestration Implementation Details

This document provides the technical implementation details of the multi-agent orchestration system built with Semantic Kernel 1.30.0.

## Architecture

The multi-agent orchestration system follows these architectural principles:

1. **Main Orchestrator**: A chat agent that handles general inquiries and orchestrates specialized tasks
2. **Domain-Specific Plugins**: Specialized components (like the weather plugin) that perform specific tasks
3. **Function Calling**: The mechanism for delegating tasks from the orchestrator to plugins

## Implementation Components

### 1. Semantic Kernel Setup

```python
def setup_kernel_with_openai():
    # Load environment variables
    load_dotenv()
    
    # Get Azure OpenAI configuration
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    # Create a kernel
    kernel = sk.Kernel()
    
    # Add Azure OpenAI chat service with function calling enabled
    kernel.add_service(
        AzureChatCompletion(
            service_id="chat", 
            deployment_name=deployment,
            endpoint=endpoint,
            api_key=api_key,
            api_version="2024-05-01-preview"
        )
    )
    
    return kernel
```

### 2. Plugin Registration

Plugin registration in Semantic Kernel 1.30.0 requires creating a KernelPlugin:

```python
async def setup_weather_plugin(kernel):
    # Create a weather service instance
    weather_service = WeatherService()
    
    # Create the weather plugin instance
    weather_plugin_obj = WeatherPlugin(weather_service)
    
    # Create a KernelPlugin using from_object
    from semantic_kernel.functions import KernelPlugin
    weather_plugin = KernelPlugin.from_object("WeatherPlugin", weather_plugin_obj, 
                                              description="Provides weather information for US cities")
    
    # Add the plugin to the kernel
    kernel.plugins["WeatherPlugin"] = weather_plugin
    
    return weather_plugin
```

### 3. Function Calling Implementation

The system prompt instructs the model to use function calling for weather queries:

```python
system_message = """
You are a helpful assistant that provides friendly, concise, and accurate information.
When the user asks about weather, you should use the GetWeather function to get accurate weather information.
Always extract the location from the user's question when dealing with weather queries.

For example:
- If they ask 'What's the weather like in Seattle?', call GetWeather with location='Seattle, WA'
- If they ask 'Will it rain tomorrow in Chicago?', call GetWeather with location='Chicago, IL' and type='forecast'

DO NOT make up weather information. ALWAYS use the GetWeather function for weather queries.
For other questions, answer directly from your knowledge.
"""
```

Function definitions are provided to the model:

```python
tools = [
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
```

### 4. Function Execution Flow

When the model decides to call a function:

1. The arguments are extracted from the model's response
2. The appropriate function from the plugin is called
3. The result is passed back to the model to formulate a final response

```python
# Check if the model wants to call a function
if hasattr(response, "tool_calls") and response.tool_calls:
    # Process each tool call
    for tool_call in response.tool_calls:
        if tool_call.function.name == "GetWeather":
            # Parse the arguments
            args = json.loads(tool_call.function.arguments)
            location = args.get("location")
            weather_type = args.get("type", "current")
            
            # Get the actual weather plugin function
            weather_plugin = kernel.plugins["WeatherPlugin"]
            weather_function = weather_plugin["GetWeather"]
            
            # Call the function
            weather_result = await weather_function.invoke(
                location=location,
                type=weather_type
            )
            
            # Create a new message to continue the conversation
            followup_messages = messages.copy()
            followup_messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": "GetWeather",
                            "arguments": tool_call.function.arguments
                        }
                    }
                ]
            })
            followup_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(weather_result)
            })
            
            # Get the final response that includes the function result
            final_response = await kernel.invoke("chat", 
                messages=followup_messages
            )
            
            content = final_response.value
```

## Plugin Implementation

The weather plugin is implemented with these key functions:

1. **GetCurrentWeather**: For current weather
2. **GetWeatherForecast**: For weather forecasts
3. **GetWeather**: A unified function that handles both current and forecast queries

Each function is decorated with `@kernel_function` to make it available to Semantic Kernel:

```python
@kernel_function(
    description="Get weather information for a location (current or forecast)",
    name="GetWeather"
)
def get_weather(self, location: str, type: Optional[str] = "current") -> str:
    """
    General function to get weather information, either current or forecast.
    This is the main function that will be called by the chat agent.
    
    Args:
        location (str): The city and state, e.g. Seattle, WA
        type (str): Either "current" or "forecast"
        
    Returns:
        str: Weather information as a formatted string
    """
    # Implementation details...
```

## Orchestration Workflow

The full orchestration workflow follows these steps:

1. User input is received
2. The chat agent processes the input with the system prompt guiding function calling
3. If weather information is needed, the weather plugin is called
4. The chat agent incorporates the weather information into its response
5. The response is presented to the user
6. Chat history is updated for context in future interactions

## Key Differences from Previous Versions

This implementation differs from earlier attempts in that it:

1. Uses Semantic Kernel 1.30.0's plugin registration system with `KernelPlugin`
2. Properly implements the tool calling interface compatible with Azure OpenAI
3. Handles function calling in a way that maintains conversation context

## Technical Considerations

- **API Versions**: Requires Azure OpenAI API version 2024-05-01-preview or newer
- **Function Call Format**: Follows the OpenAI function calling format
- **Error Handling**: Includes robust error handling for failed function calls and API errors

## Future Enhancements

Possible future enhancements include:

1. Dynamic plugin discovery and registration
2. More sophisticated orchestration patterns with multiple specialized agents
3. Memory integration to retain context across sessions
4. Authentication and authorization for sensitive operations