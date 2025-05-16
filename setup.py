#!/usr/bin/env python3
import os
import sys

def check_python_version():
    """Check if Python version is compatible"""
    required_version = (3, 8)
    current_version = sys.version_info
    
    if current_version < required_version:
        print(f"Error: Python {required_version[0]}.{required_version[1]} or higher is required")
        print(f"Current version: {current_version[0]}.{current_version[1]}")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists and create from example if not"""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("Creating .env file from .env.example...")
            with open(".env.example", "r") as example_file:
                example_content = example_file.read()
                
            with open(".env", "w") as env_file:
                env_file.write(example_content)
                
            print("Please fill in your API keys and configuration in the .env file")
        else:
            print("Error: .env.example file not found")
            return False
    
    return True

def main():
    """Main setup function"""
    print("Setting up Semantic Kernel Multi-Agent Application...")
    
    # Check Python version
    if not check_python_version():
        return
    
    # Check .env file
    if not check_env_file():
        return
    
    # Install dependencies
    print("\nInstalling dependencies...")
    os.system(f"{sys.executable} -m pip install -r requirements.txt")
    
    print("\nSetup complete! You can now try the following commands:")
    print("\n# Run local chat:")
    print("python src/scripts/local_chat.py")
    
    print("\n# Deploy agents to Azure AI Agent Service:")
    print("python src/scripts/deploy_agents.py")
    
    print("\n# Start the API server:")
    print("python src/scripts/run_api_server.py")
    
    print("\n# Use the HTTP client:")
    print("python src/scripts/http_client.py chat --agent chat")
    
    print("\nFor more information, please refer to the README.md file.")

if __name__ == "__main__":
    main()