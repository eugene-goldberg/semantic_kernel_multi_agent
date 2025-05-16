from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings

from src.config.settings import (
    get_project_connection_string, 
    AZURE_OPENAI_DEPLOYMENT_NAME,
    AZURE_AI_HUB_NAME,
    AZURE_AI_PROJECT_NAME
)

class AzureAgentFactory:
    """Factory class for creating and deploying agents to Azure AI Agent Service"""
    
    @staticmethod
    async def create_client():
        """
        Create an Azure AI Project client that connects to a specific Project within a Hub
        
        Returns:
            AIProjectClient: Configured client for Azure AI Foundry
        """
        try:
            # First try using connection string
            connection_string = get_project_connection_string()
            credential = DefaultAzureCredential()
            
            return AIProjectClient.from_connection_string(
                connection_string=connection_string,
                credential=credential
            )
            
        except ValueError as e:
            # If connection string is incomplete, try using hub and project name directly
            if not (AZURE_AI_HUB_NAME and AZURE_AI_PROJECT_NAME):
                raise ValueError("Failed to create AI Project client. "
                                "Please provide either a complete connection string or "
                                "Hub name and Project name.") from e
                                
            # Log information about connecting
            print(f"Connecting to Hub '{AZURE_AI_HUB_NAME}', Project '{AZURE_AI_PROJECT_NAME}'")
            
            # Create client using connection string approach
            print(f"Creating client for hub '{AZURE_AI_HUB_NAME}' and project '{AZURE_AI_PROJECT_NAME}'")
            
            # Construct connection string manually
            from src.config.settings import AZURE_AI_PROJECT_HOST, AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP
            connection_string = f"{AZURE_AI_PROJECT_HOST};{AZURE_SUBSCRIPTION_ID};{AZURE_RESOURCE_GROUP};{AZURE_AI_HUB_NAME}/{AZURE_AI_PROJECT_NAME}"
            
            return AIProjectClient.from_connection_string(
                connection_string=connection_string,
                credential=credential
            )
    
    @staticmethod
    async def deploy_chat_agent(client=None):
        """
        Create and deploy a chat agent to Azure AI Agent Service
        
        Args:
            client: Optional pre-created client
            
        Returns:
            AzureAIAgent: The deployed agent
        """
        if client is None:
            client = await AzureAgentFactory.create_client()
        
        agent_definition = await client.agents.create_agent(
            model=AZURE_OPENAI_DEPLOYMENT_NAME,
            name="ChatAgent",
            instructions=(
                "You are a helpful assistant that provides friendly, concise, and accurate information. "
                "You should be conversational but prioritize accuracy and brevity over verbosity. "
                "If you don't know something, admit it clearly rather than making guesses. "
                "If the question is about weather information, inform the user that you'll need to "
                "ask a specialist weather agent to get accurate weather data."
            )
        )
        
        return AzureAIAgent(
            client=client,
            definition=agent_definition
        )
    
    @staticmethod
    async def deploy_weather_agent(client=None):
        """
        Create and deploy a weather agent to Azure AI Agent Service
        
        Args:
            client: Optional pre-created client
            
        Returns:
            AzureAIAgent: The deployed agent
        """
        if client is None:
            client = await AzureAgentFactory.create_client()
        
        # Define OpenAPI spec for weather API
        weather_api_tools = {
            "type": "openapi",
            "config": {
                "openapi_schema": {
                    "openapi": "3.0.0",
                    "info": {
                        "title": "Weather API",
                        "version": "1.0.0"
                    },
                    "servers": [
                        {
                            "url": "https://api.openweathermap.org/data/2.5",
                        }
                    ],
                    "paths": {
                        "/weather": {
                            "get": {
                                "summary": "Get current weather data",
                                "description": "Access current weather data for any location on Earth",
                                "operationId": "getCurrentWeather",
                                "parameters": [
                                    {
                                        "name": "q",
                                        "in": "query",
                                        "description": "City name",
                                        "required": True,
                                        "schema": {
                                            "type": "string"
                                        }
                                    },
                                    {
                                        "name": "appid",
                                        "in": "query",
                                        "description": "API key",
                                        "required": True,
                                        "schema": {
                                            "type": "string"
                                        }
                                    },
                                    {
                                        "name": "units",
                                        "in": "query",
                                        "description": "Units of measurement",
                                        "required": False,
                                        "schema": {
                                            "type": "string",
                                            "enum": ["standard", "metric", "imperial"],
                                            "default": "metric"
                                        }
                                    }
                                ],
                                "responses": {
                                    "200": {
                                        "description": "Successful response",
                                        "content": {
                                            "application/json": {
                                                "schema": {
                                                    "type": "object"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "/forecast": {
                            "get": {
                                "summary": "Get forecast data",
                                "description": "Get a forecast for a specific location",
                                "operationId": "getForecast",
                                "parameters": [
                                    {
                                        "name": "q",
                                        "in": "query",
                                        "description": "City name",
                                        "required": True,
                                        "schema": {
                                            "type": "string"
                                        }
                                    },
                                    {
                                        "name": "appid",
                                        "in": "query",
                                        "description": "API key",
                                        "required": True,
                                        "schema": {
                                            "type": "string"
                                        }
                                    },
                                    {
                                        "name": "units",
                                        "in": "query",
                                        "description": "Units of measurement",
                                        "required": False,
                                        "schema": {
                                            "type": "string",
                                            "enum": ["standard", "metric", "imperial"],
                                            "default": "metric"
                                        }
                                    },
                                    {
                                        "name": "cnt",
                                        "in": "query",
                                        "description": "Number of days",
                                        "required": False,
                                        "schema": {
                                            "type": "integer",
                                            "default": 5
                                        }
                                    }
                                ],
                                "responses": {
                                    "200": {
                                        "description": "Successful response",
                                        "content": {
                                            "application/json": {
                                                "schema": {
                                                    "type": "object"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        agent_definition = await client.agents.create_agent(
            model=AZURE_OPENAI_DEPLOYMENT_NAME,
            name="WeatherAgent",
            instructions=(
                "You are a weather specialist agent that provides accurate and helpful weather information. "
                "You have access to real-time weather data through the Weather API. "
                "When asked about weather, always use the appropriate function to get accurate data. "
                "For current weather, use the getCurrentWeather function. "
                "For forecasts, use the getForecast function. "
                "Provide your answers in a friendly, concise manner, focusing on the most relevant information "
                "for the user's query. If you're asked something not related to weather, politely explain "
                "that you specialize in weather information only."
            ),
            tools=[weather_api_tools]
        )
        
        return AzureAIAgent(
            client=client,
            definition=agent_definition
        )
    
    @staticmethod
    async def create_thread(client=None):
        """
        Create a new conversation thread
        
        Args:
            client: Optional pre-created client
            
        Returns:
            Thread: The created thread
        """
        if client is None:
            client = await AzureAgentFactory.create_client()
        
        return await client.agents.create_thread()
    
    @staticmethod
    async def add_message_to_thread(thread_id, content, client=None):
        """
        Add a message to a thread
        
        Args:
            thread_id: The thread ID
            content: The message content
            client: Optional pre-created client
            
        Returns:
            Message: The created message
        """
        if client is None:
            client = await AzureAgentFactory.create_client()
        
        return await client.agents.create_message(
            thread_id=thread_id,
            role="user",
            content=content
        )
    
    @staticmethod
    async def run_agent(thread_id, agent_id, client=None):
        """
        Run an agent on a thread
        
        Args:
            thread_id: The thread ID
            agent_id: The agent ID
            client: Optional pre-created client
            
        Returns:
            Run: The created run
        """
        if client is None:
            client = await AzureAgentFactory.create_client()
        
        run = await client.agents.create_run(
            thread_id=thread_id,
            agent_id=agent_id
        )
        
        # Wait for the run to complete
        while run.status not in ["completed", "failed", "cancelled"]:
            run = await client.agents.get_run(
                thread_id=thread_id,
                run_id=run.id
            )
        
        return run
    
    @staticmethod
    async def get_messages(thread_id, client=None):
        """
        Get messages from a thread
        
        Args:
            thread_id: The thread ID
            client: Optional pre-created client
            
        Returns:
            List[Message]: The messages
        """
        if client is None:
            client = await AzureAgentFactory.create_client()
        
        return await client.agents.list_messages(thread_id=thread_id)
    
    @staticmethod
    async def delete_agent(agent_id, client=None):
        """
        Delete an agent
        
        Args:
            agent_id: The agent ID
            client: Optional pre-created client
        """
        if client is None:
            client = await AzureAgentFactory.create_client()
        
        await client.agents.delete_agent(agent_id=agent_id)
    
    @staticmethod
    async def delete_thread(thread_id, client=None):
        """
        Delete a thread
        
        Args:
            thread_id: The thread ID
            client: Optional pre-created client
        """
        if client is None:
            client = await AzureAgentFactory.create_client()
        
        await client.agents.delete_thread(thread_id=thread_id)