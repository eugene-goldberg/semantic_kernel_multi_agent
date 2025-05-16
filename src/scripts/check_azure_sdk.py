#!/usr/bin/env python3
"""
Check available modules and classes in the Azure AI Projects SDK
"""

try:
    print("Checking azure.ai.projects package...")
    import azure.ai.projects
    print(f"Package version: {azure.ai.projects.__version__}")
    
    print("\nAvailable modules in azure.ai.projects:")
    for module in dir(azure.ai.projects):
        if not module.startswith('_'):
            print(f"  - {module}")
    
    print("\nChecking models module...")
    import azure.ai.projects.models
    print("\nAvailable classes in azure.ai.projects.models:")
    for cls in dir(azure.ai.projects.models):
        if not cls.startswith('_'):
            print(f"  - {cls}")
    
    print("\nChecking if AIProjectClient exists...")
    if hasattr(azure.ai.projects, 'AIProjectClient'):
        print("  ✓ AIProjectClient exists")
        client_class = azure.ai.projects.AIProjectClient
        print("\nMethods available in AIProjectClient:")
        for method in dir(client_class):
            if not method.startswith('_'):
                print(f"  - {method}")
    else:
        print("  ✗ AIProjectClient does not exist")
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure azure-ai-projects is installed with: pip install azure-ai-projects")
    
except Exception as e:
    print(f"Unexpected error: {e}")