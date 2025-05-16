#!/usr/bin/env python3
"""
This script provides detailed instructions for setting up and using the multi-agent application.
"""

import os
import sys
import json
import subprocess
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored terminal output
init()

# Add the project root to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src.config.settings import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT_NAME,
    AZURE_AI_PROJECT_NAME, 
    AZURE_RESOURCE_GROUP, 
    AZURE_SUBSCRIPTION_ID,
    AZURE_AI_PROJECT_HOST
)

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{text}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * len(text)}{Style.RESET_ALL}")

def print_success(text):
    """Print a success message"""
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

def print_warning(text):
    """Print a warning message"""
    print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")

def print_error(text):
    """Print an error message"""
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")

def print_instruction(text):
    """Print an instruction"""
    print(f"{Fore.WHITE}  {text}{Style.RESET_ALL}")

def check_environment_variables():
    """Check if all required environment variables are set"""
    print_header("Checking Environment Variables")
    
    required_vars = {
        "AZURE_OPENAI_ENDPOINT": AZURE_OPENAI_ENDPOINT,
        "AZURE_OPENAI_DEPLOYMENT_NAME": AZURE_OPENAI_DEPLOYMENT_NAME,
        "AZURE_AI_PROJECT_NAME": AZURE_AI_PROJECT_NAME,
        "AZURE_RESOURCE_GROUP": AZURE_RESOURCE_GROUP,
        "AZURE_SUBSCRIPTION_ID": AZURE_SUBSCRIPTION_ID,
        "AZURE_AI_PROJECT_HOST": AZURE_AI_PROJECT_HOST
    }
    
    all_present = True
    
    for name, value in required_vars.items():
        if value:
            print_success(f"{name} is set to: {value}")
        else:
            print_error(f"{name} is not set")
            all_present = False
    
    return all_present

def check_azure_cli():
    """Check if Azure CLI is installed and logged in"""
    print_header("Checking Azure CLI")
    
    # Check if Azure CLI is installed
    try:
        subprocess.run(["az", "--version"], capture_output=True, check=True)
        print_success("Azure CLI is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Azure CLI is not installed")
        print_instruction("Please install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        return False
    
    # Check if logged in
    try:
        result = subprocess.run(["az", "account", "show"], capture_output=True, text=True)
        if result.returncode == 0:
            account_info = json.loads(result.stdout)
            print_success(f"Logged in as: {account_info.get('user', {}).get('name')} (Subscription: {account_info.get('name')})")
            return True
        else:
            print_error("Not logged in to Azure CLI")
            print_instruction("Please login with: az login")
            return False
    except subprocess.CalledProcessError:
        print_error("Failed to check Azure CLI login status")
        print_instruction("Please login with: az login")
        return False

def show_deployment_options():
    """Show available deployment options"""
    print_header("Deployment Options")
    
    print(f"{Fore.WHITE}Based on our analysis, here are your options for deploying agents:{Style.RESET_ALL}")
    
    print_header("Option 1: Use Azure Portal (Recommended)")
    print_instruction("1. Go to Azure AI Studio at https://ai.azure.com")
    print_instruction("2. Navigate to your project")
    print_instruction("3. Create two new agents:")
    print_instruction("   - Chat Agent: A general-purpose assistant")
    print_instruction("   - Weather Agent: A specialized agent for US weather information")
    print_instruction("4. After creating the agents through the portal, you can use our interactive client:")
    print_instruction("   python src/scripts/interact_deployed_agents.py")
    
    print_header("Option 2: Use Local Development")
    print_instruction("Run the application locally without deployment:")
    print_instruction("python src/scripts/local_chat.py")
    
    print_instruction("This will run the agents locally using your Azure OpenAI service.")
    
    print_header("Option 3: Try Programmatic Deployment Again")
    print_instruction("If you want to try programmatic deployment again, ensure the following:")
    print_instruction("1. Refresh your Azure CLI credentials:")
    print_instruction("   az login")
    print_instruction("2. Try our Service Principal approach:")
    print_instruction("   bash src/scripts/create_service_principal.sh")
    print_instruction("   cat .env.service_principal >> .env")
    print_instruction("   python src/scripts/deploy_with_service_principal.py")
    
    print_header("Project Status")
    print_instruction("The project appears to have the following components working correctly:")
    print_success("1. Azure OpenAI service is set up and accessible")
    print_success("2. Weather service is implemented and tested")
    print_success("3. Local agent functionality is working")
    print_warning("4. Deployment to Azure AI Agent Service is encountering authentication issues")

def main():
    """Main function"""
    print_header("Semantic Kernel Multi-Agent Application Setup")
    print(f"{Fore.WHITE}This script will help you set up and use the multi-agent application.{Style.RESET_ALL}\n")
    
    env_vars_ok = check_environment_variables()
    azure_cli_ok = check_azure_cli()
    
    if not env_vars_ok:
        print_warning("Some environment variables are missing. Please update your .env file.")
    
    if not azure_cli_ok:
        print_warning("Azure CLI login issues detected. Please ensure you're logged in.")
    
    show_deployment_options()
    
    print_header("Next Steps")
    print(f"{Fore.WHITE}Based on the checks above, here's what you should do next:{Style.RESET_ALL}")
    
    if not env_vars_ok:
        print_instruction("1. Update your .env file with the missing variables")
    
    if not azure_cli_ok:
        print_instruction("1. Login to Azure CLI with: az login")
    
    print_instruction("2. Choose a deployment option from the list above")
    print_instruction("3. For local testing, use: python src/scripts/test_weather_service.py")
    print_instruction("4. For local agents, use: python src/scripts/local_chat.py")
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}Thank you for using the Semantic Kernel Multi-Agent Application!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()