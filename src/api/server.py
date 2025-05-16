import asyncio
import json
import os
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.utils.azure_agent_factory import AzureAgentFactory

app = FastAPI(title="Multi-Agent API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active threads
active_threads: Dict[str, dict] = {}

class MessageRequest(BaseModel):
    """Request model for sending a message"""
    message: str
    agent_type: str = "chat"  # Default to chat agent
    thread_id: Optional[str] = None  # Optional thread ID for continuing a conversation

class MessageResponse(BaseModel):
    """Response model for a message"""
    thread_id: str
    agent_id: str
    response: str

@app.get("/")
async def root():
    """Root endpoint with Azure AI Foundry Hub and Project info"""
    # Check if deployment info exists
    deployment_info = {}
    if os.path.exists("deployment_info.json"):
        try:
            with open("deployment_info.json", "r") as f:
                deployment_info = json.load(f)
        except Exception:
            pass
            
    return {
        "message": "Multi-Agent API is running",
        "azure_ai_foundry": {
            "hub": deployment_info.get("hub_name", "Not configured"),
            "project": deployment_info.get("project_name", "Not configured"),
            "deployment_time": deployment_info.get("deployment_time", "Unknown")
        }
    }

@app.get("/agents")
async def get_agents():
    """Get information about deployed agents"""
    try:
        # Check if deployment info exists
        if not os.path.exists("deployment_info.json"):
            raise HTTPException(status_code=404, detail="No deployment info found")
            
        # Load deployment info
        with open("deployment_info.json", "r") as f:
            deployment_info = json.load(f)
        
        # Create client
        client = await AzureAgentFactory.create_client()
        
        # Get agent details
        agents = []
        for agent_key, agent_id in deployment_info.items():
            # Skip non-agent keys in the deployment info
            if not agent_key.endswith("_agent_id"):
                continue
                
            try:
                agent = await client.agents.get_agent(agent_id)
                agents.append({
                    "name": agent.name,
                    "id": agent.id,
                    "type": agent_key.replace("_agent_id", ""),
                    "model": agent.model,
                    "created_at": str(agent.created_at)
                })
            except Exception as e:
                # Skip agents that can't be retrieved
                print(f"Error retrieving agent {agent_id}: {str(e)}")
        
        # Add foundry information
        result = {
            "azure_ai_foundry": {
                "hub": deployment_info.get("hub_name", "Not configured"),
                "project": deployment_info.get("project_name", "Not configured")
            },
            "agents": agents
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agents: {str(e)}")

@app.post("/message", response_model=MessageResponse)
async def send_message(request: MessageRequest, background_tasks: BackgroundTasks):
    """Send a message to an agent"""
    try:
        # Load deployment info
        if not os.path.exists("deployment_info.json"):
            raise HTTPException(status_code=404, detail="No deployment info found")
            
        with open("deployment_info.json", "r") as f:
            deployment_info = json.load(f)
        
        # Determine agent ID based on type
        agent_key = f"{request.agent_type}_agent_id"
        if agent_key not in deployment_info:
            raise HTTPException(status_code=404, detail=f"No agent found with type: {request.agent_type}")
            
        agent_id = deployment_info[agent_key]
        
        # Create client
        client = await AzureAgentFactory.create_client()
        
        # Get or create thread
        thread_id = request.thread_id
        if thread_id and thread_id in active_threads:
            # Use existing thread
            thread_id = thread_id
        else:
            # Create a new thread
            thread = await AzureAgentFactory.create_thread(client)
            thread_id = thread.id
            
            # Store thread info
            active_threads[thread_id] = {
                "agent_id": agent_id,
                "last_activity": asyncio.get_event_loop().time()
            }
            
            # Clean up thread after 30 minutes of inactivity
            background_tasks.add_task(cleanup_thread, thread_id, 1800)
        
        # Add message to thread
        await AzureAgentFactory.add_message_to_thread(
            thread_id=thread_id,
            content=request.message,
            client=client
        )
        
        # Run the agent
        await AzureAgentFactory.run_agent(
            thread_id=thread_id,
            agent_id=agent_id,
            client=client
        )
        
        # Get the messages
        messages = await AzureAgentFactory.get_messages(
            thread_id=thread_id,
            client=client
        )
        
        # Get the latest assistant message
        response = None
        for message in reversed(messages):
            if message.role == "assistant":
                response = message.content
                break
        
        if not response:
            raise HTTPException(status_code=500, detail="No response received from agent")
            
        # Update last activity
        active_threads[thread_id]["last_activity"] = asyncio.get_event_loop().time()
            
        return MessageResponse(
            thread_id=thread_id,
            agent_id=agent_id,
            response=response
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")

async def cleanup_thread(thread_id: str, timeout: int):
    """
    Clean up a thread after timeout seconds of inactivity
    
    Args:
        thread_id: The thread ID
        timeout: Timeout in seconds
    """
    # Wait for timeout
    await asyncio.sleep(timeout)
    
    # Check if thread still exists and is inactive
    if thread_id in active_threads:
        current_time = asyncio.get_event_loop().time()
        last_activity = active_threads[thread_id]["last_activity"]
        
        if current_time - last_activity >= timeout:
            # Clean up the thread
            try:
                client = await AzureAgentFactory.create_client()
                await AzureAgentFactory.delete_thread(thread_id=thread_id, client=client)
                print(f"Thread {thread_id} deleted due to inactivity")
            except Exception as e:
                print(f"Error deleting thread {thread_id}: {str(e)}")
            finally:
                # Remove from active threads
                active_threads.pop(thread_id, None)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)