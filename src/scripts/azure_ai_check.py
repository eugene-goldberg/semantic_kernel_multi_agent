#!/usr/bin/env python3
"""
Direct check for Azure AI resources using Azure CLI.
"""

import os
import sys
import subprocess
import json
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_cmd(cmd):
    """Run a shell command and return the output as JSON."""
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            shell=True
        )
        if not result.stdout.strip():
            return None
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {cmd}")
        logger.error(f"Error: {e.stderr}")
        return None
    except json.JSONDecodeError:
        # Return raw output if not JSON
        return result.stdout.strip()

def main():
    """Check Azure AI resources."""
    # Load environment variables
    load_dotenv()
    load_dotenv('.env.ai_foundry')
    
    # Get configuration from environment
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    resource_group = os.getenv("AZURE_RESOURCE_GROUP")
    
    # Check Azure login status
    login_info = run_cmd("az account show")
    if not login_info:
        logger.error("Not logged in to Azure. Run 'az login' first.")
        return
    
    print(f"Logged in as: {login_info.get('user', {}).get('name')}")
    print(f"Using subscription: {login_info.get('name')} ({login_info.get('id')})")
    
    # Check resource group
    rg_info = run_cmd(f"az group show --name {resource_group}")
    if not rg_info:
        logger.error(f"Resource group {resource_group} not found.")
        return
    
    print(f"\nResource Group: {rg_info.get('name')} ({rg_info.get('location')})")
    
    # List all resources in the group
    resources = run_cmd(f"az resource list --resource-group {resource_group}")
    if not resources:
        logger.error(f"No resources found in resource group {resource_group}.")
        return
    
    print(f"\nFound {len(resources)} resources in the resource group:")
    for resource in resources:
        print(f"- {resource.get('name')} ({resource.get('type')})")
    
    # Check specifically for AI resources
    ai_resources = [r for r in resources if "Microsoft.MachineLearningServices" in r.get("type", "")]
    
    print(f"\nFound {len(ai_resources)} Azure AI resources:")
    for resource in ai_resources:
        print(f"- {resource.get('name')} ({resource.get('type')})")
        
        # If it's a workspace, get more details
        if resource.get("type") == "Microsoft.MachineLearningServices/workspaces":
            workspace_name = resource.get("name")
            print(f"\nWorkspace Details for {workspace_name}:")
            
            # Try to get workspace details
            workspace_details = run_cmd(f"az ml workspace show --name {workspace_name} --resource-group {resource_group}")
            if workspace_details:
                print(json.dumps(workspace_details, indent=2))
            else:
                print("  Unable to retrieve workspace details. ML extension may not be installed.")
                print("  Try: az extension add -n ml")
    
    # Check deployment info file
    print("\nLocal Deployment Info:")
    try:
        with open("ai_foundry_deployment_info.json", "r") as f:
            deployment_info = json.load(f)
            print(json.dumps(deployment_info, indent=2))
    except Exception as e:
        print(f"Error reading deployment info: {str(e)}")

if __name__ == "__main__":
    main()