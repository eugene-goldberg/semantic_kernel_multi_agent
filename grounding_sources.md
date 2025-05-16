# Grounding "Claude Code": Semantic Kernel, Azure AI Agent Service & Foundry

This document compiles key documentation and examples for building and deploying multi-agent applications using the Microsoft Semantic Kernel SDK, Azure AI Agent Service, and Azure AI Foundry.

## I. Microsoft Semantic Kernel SDK (Core & Multi-Agent Focus)

Semantic Kernel is an open-source SDK that lets you easily build AI agents that can call your existing code. It integrates Large Language Models (LLMs) with conventional programming languages like C# and Python.

### A. Core Concepts & Getting Started

* **Official Semantic Kernel Documentation (Microsoft Learn):** The primary source for all SK documentation.
    * **URL:** [https://learn.microsoft.com/en-us/semantic-kernel/](https://learn.microsoft.com/en-us/semantic-kernel/)
    * **Key Areas for Claude Code:**
        * Introduction to Semantic Kernel
        * Kernel, Plugins (Skills/Functions), Planners, Memory
        * Connectors (for AI services, memory, etc.)
        * Supported Languages (Python, C#)

* **Semantic Kernel GitHub Repository (microsoft/semantic-kernel):** Contains the SDK source code, samples, and discussions.
    * **URL:** [https://github.com/microsoft/semantic-kernel](https://github.com/microsoft/semantic-kernel)
    * **Key Areas for Claude Code:**
        * `samples/` directory for both Python and C#.
        * Documentation within the repo (often in `/docs` or as READMEs in sample folders).
        * Discussions and Issues for community insights and troubleshooting.

* **Semantic Kernel for Beginners (microsoft/ai-agents-for-beginners - Lesson 2):** This lesson explores agentic frameworks and covers core Semantic Kernel components.
    * **URL:** [https://microsoft.github.io/ai-agents-for-beginners/02-explore-agentic-frameworks/](https://microsoft.github.io/ai-agents-for-beginners/02-explore-agentic-frameworks/)
    * **Key Areas for Claude Code:** Understanding AI Connectors, Plugins (semantic and native functions).

### B. Multi-Agent Systems with Semantic Kernel

* **Semantic Kernel Agent Framework Documentation (Microsoft Learn):**
    * **Semantic Kernel Agent Architecture:** Explains the foundational concepts of agents in SK, how they collaborate, and align with core SK features.
        * **URL:** [https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-architecture](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-architecture)
    * **Semantic Kernel Agent Framework Overview:** Defines what an AI agent is in the SK context, the problems agents solve, and how to install the necessary packages (e.g., `Microsoft.SemanticKernel.Agents.Core`).
        * **URL:** [https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/)
    * **Exploring the Semantic Kernel ChatCompletionAgent:** Details on using a specific agent type that can be a building block in multi-agent systems.
        * **URL:** [https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/chat-completion-agent](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/chat-completion-agent)

* **Microsoft Learn Training Module: Orchestrate a multi-agent solution using Semantic Kernel:** A structured learning path.
    * **URL:** [https://learn.microsoft.com/en-us/training/modules/orchestrate-semantic-kernel-multi-agent-solution/](https://learn.microsoft.com/en-us/training/modules/orchestrate-semantic-kernel-multi-agent-solution/)
    * **Key Learnings for Claude Code:** Building AI agents with SK, developing multi-agent solutions, creating custom agent selection and termination strategies.

* **Semantic Kernel Developer Blog Posts (Official):**
    * **Introducing enterprise multi-agent support in Semantic Kernel:** Discusses first-class agent abstractions, `AgentChat`, and orchestration patterns (group chat vs. task-based).
        * **URL:** [https://devblogs.microsoft.com/semantic-kernel/introducing-agents-in-semantic-kernel/](https://devblogs.microsoft.com/semantic-kernel/introducing-agents-in-semantic-kernel/)
    * **Guest Blog: Building Multi-Agent Systems with Multi-Models in Semantic Kernel – Part 1:** Provides conceptual understanding and examples of multi-agent collaboration.
        * **URL:** [https://devblogs.microsoft.com/semantic-kernel/guest-blog-building-multi-agent-systems-with-multi-models-in-semantic-kernel-part-1/](https://devblogs.microsoft.com/semantic-kernel/guest-blog-building-multi-agent-systems-with-multi-models-in-semantic-kernel-part-1/) (Also see Arafat Tehsin's blog for similar content: [https://arafattehsin.com/building-multi-agent-systems-with-multi-models-in-semantic-kernel-part-1/](https://arafattehsin.com/building-multi-agent-systems-with-multi-models-in-semantic-kernel-part-1/))

* **GitHub Examples for Multi-Agent Systems with SK:**
    * **Azure-Samples/ai-multi-agent-presentation-builder:** Demonstrates a swarm agent architecture using an orchestrator and expert agents with SK.
        * **URL:** [https://github.com/Azure-Samples/ai-multi-agent-presentation-builder](https://github.com/Azure-Samples/ai-multi-agent-presentation-builder)
    * **Azure-Samples/semantic-kernel-workshop:** A hands-on workshop that includes modules on agent creation, orchestration, multi-agent communication patterns, and agent selection.
        * **URL:** [https://github.com/Azure-Samples/semantic-kernel-workshop](https://github.com/Azure-Samples/semantic-kernel-workshop)
        * **Focus on:** Notebooks related to "Basic Agents" and "Advanced Agent Patterns."
    * **Azure-Samples/aspire-semantic-kernel-creative-writer:** A multi-agent solution for creative writing using .NET Aspire and Semantic Kernel.
        * **URL:** [https://github.com/Azure-Samples/aspire-semantic-kernel-creative-writer](https://github.com/Azure-Samples/aspire-semantic-kernel-creative-writer)

* **Community Articles on Multi-Agent SK:**
    * **The Developer's Cantina: Using Semantic Kernel to create multi-agent scenarios:**
        * **URL:** [https://www.developerscantina.com/p/semantic-kernel-multiagents/](https://www.developerscantina.com/p/semantic-kernel-multiagents/)
    * **Saptak Sen: Intelligent Agents with Semantic Kernel: A Comprehensive Guide:**
        * **URL:** [https://saptak.in/writing/2025/03/22/building-intelligent-agents-with-semantic-kernel](https://saptak.in/writing/2025/03/22/building-intelligent-agents-with-semantic-kernel)
    * **Akira AI: Multi-Agent Orchestration Redefined with Microsoft Semantic Kernel:**
        * **URL:** [https://www.akira.ai/blog/multi-agent-with-microsoft-semantic-kernel](https://www.akira.ai/blog/multi-agent-with-microsoft-semantic-kernel)
    * **Digital Bricks: Orchestrating Multi‑Agent AI With Semantic Kernel:**
        * **URL:** [https://www.digitalbricks.ai/blog-posts/orchestrating-multi-agent-ai-with-semantic-kernel](https://www.digitalbricks.ai/blog-posts/orchestrating-multi-agent-ai-with-semantic-kernel)

## II. Azure AI Agent Service

The Azure AI Agent Service is a fully managed service designed to help developers build, deploy, and scale AI agents within Azure AI Foundry.

* **Official Documentation (Microsoft Learn):**
    * **What is Azure AI Agent Service?:** Overview, capabilities (automatic tool calling, out-of-the-box tools, data integrations, security).
        * **URL:** [https://learn.microsoft.com/en-us/azure/ai-services/agents/overview](https://learn.microsoft.com/en-us/azure/ai-services/agents/overview)
    * **Quickstart - Create a new Azure AI Agent Service project:** Step-by-step guide to setting up a project and deploying a model.
        * **URL:** [https://learn.microsoft.com/en-us/azure/ai-services/agents/quickstart](https://learn.microsoft.com/en-us/azure/ai-services/agents/quickstart)
    * **Azure AI Agent Service concepts (within Azure AI Foundry docs):** Covers agents, threads, messages, tools, runs, personas, instructions.
        * **URL:** (Often found under Azure AI Foundry documentation, e.g., linked from [https://learn.microsoft.com/en-us/azure/ai-foundry/](https://learn.microsoft.com/en-us/azure/ai-foundry/) under "Concepts")

* **Developer's Guide to Azure AI Agents (The New Stack):** Provides a good overview of core components and how they map to agent anatomy.
    * **URL:** [https://thenewstack.io/a-developers-guide-to-azure-ai-agents/](https://thenewstack.io/a-developers-guide-to-azure-ai-agents/)

* **GitHub Examples & Workshops:**
    * **Azure-Samples/get-started-with-ai-agents:** A sample showing how to deploy an app using Azure AI Agent Service, typically involving Azure Container Apps.
        * **URL:** [https://github.com/Azure-Samples/get-started-with-ai-agents](https://github.com/Azure-Samples/get-started-with-ai-agents)
    * **Azure-Samples/azure-ai-agent-service-enterprise-demo:** Demonstrates building a streaming enterprise agent using Azure AI Agent Service, integrating local documents, Bing, and custom tools.
        * **URL:** [https://github.com/Azure-Samples/azure-ai-agent-service-enterprise-demo](https://github.com/Azure-Samples/azure-ai-agent-service-enterprise-demo)
    * **microsoft/aitour-build-your-first-agent-with-azure-ai-agent-service:** A hands-on workshop for creating agents with Azure AI Agent Service, covering function calling, data visualization, and Bing integration.
        * **URL:** [https://github.com/microsoft/aitour-build-your-first-agent-with-azure-ai-agent-service](https://github.com/microsoft/aitour-build-your-first-agent-with-azure-ai-agent-service)
    * **microsoft/ai-agents-for-beginners (Lesson on Azure AI Agent Service):** Provides context on Azure AI Agent Service, its core concepts, and how it integrates with frameworks.
        * **URL:** [https://microsoft.github.io/ai-agents-for-beginners/02-explore-agentic-frameworks/](https://microsoft.github.io/ai-agents-for-beginners/02-explore-agentic-frameworks/) (Check for specific sections on Azure AI Agent Service)

* **Deployment Guides:**
    * **Deploy Your First Azure AI Agent Service on Azure App Service (Microsoft Community Hub):** A step-by-step guide for deployment.
        * **URL:** [https://techcommunity.microsoft.com/blog/azure-ai-services-blog/deploy-your-first-azure-ai-agent-service-on-azure-app-service/4396173](https://techcommunity.microsoft.com/blog/azure-ai-services-blog/deploy-your-first-azure-ai-agent-service-on-azure-app-service/4396173)

## III. Azure AI Foundry SDK & Platform

Azure AI Foundry is the unified platform where Azure AI Agent Service resides. The SDK helps in interacting with these services programmatically.

* **Official Documentation (Microsoft Learn):**
    * **Azure AI Foundry Overview:** Main page for the platform, explaining its role in designing, customizing, and managing AI applications and agents.
        * **URL:** [https://learn.microsoft.com/en-us/azure/ai-foundry/](https://learn.microsoft.com/en-us/azure/ai-foundry/) (or [https://azure.microsoft.com/en-us/products/ai-foundry](https://azure.microsoft.com/en-us/products/ai-foundry))
    * **Get started with the Azure AI Foundry SDKs:** How-to guide for using the SDK.
        * **URL:** (Usually found within the Azure AI Foundry documentation on Microsoft Learn, e.g., under How-To Guides)
    * **Azure AI Foundry Pricing:** Understanding cost implications.
        * **URL:** [https://azure.microsoft.com/en-us/pricing/details/ai-foundry/](https://azure.microsoft.com/en-us/pricing/details/ai-foundry/)

* **GitHub Examples & Workshops:**
    * **Azure/ai-foundry-workshop:** A hands-on workshop guiding through building intelligent apps and AI agents on Azure AI Foundry. Covers fundamentals, model deployment, agent development, evaluation, and deploying an E2E sample.
        * **URL:** [https://github.com/Azure/ai-foundry-workshop](https://github.com/Azure/ai-foundry-workshop)
    * **Azure-Samples/get-started-with-ai-chat:** Basic sample for deploying chat web apps with Azure AI Foundry and SDKs.
        * **URL:** [https://github.com/Azure-Samples/get-started-with-ai-chat](https://github.com/Azure-Samples/get-started-with-ai-chat)

## IV. Integration & Directly Related Concepts

* **Semantic Kernel and Azure AI Agent Service Integration:**
    * **Exploring the Semantic Kernel Azure AI Agent (Microsoft Learn):** Details on `AzureAIAgent`, a specialized agent in SK for seamless integration with Azure AI Agent Service, automating tool calling, and managing conversation history.
        * **URL:** [https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/azure-ai-agent](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/azure-ai-agent)
    * **Using Azure AI Agents with Semantic Kernel in .NET and Python (Semantic Kernel Dev Blog):** Blog post showcasing how to use Azure AI Agents with SK in both .NET and Python.
        * **URL:** [https://devblogs.microsoft.com/semantic-kernel/using-azure-ai-agents-with-semantic-kernel-in-net-and-python/](https://devblogs.microsoft.com/semantic-kernel/using-azure-ai-agents-with-semantic-kernel-in-net-and-python/)

* **Building Multi-Agent Applications on Azure AI Foundry (Webinar/Info):**
    * **URL:** [https://info.microsoft.com/ww-landing-build-multi-agent-applications-with-azure-ai-foundry.html](https://info.microsoft.com/ww-landing-build-multi-agent-applications-with-azure-ai-foundry.html)
    * **Focus:** How Azure AI Agent Service, combined with frameworks like Semantic Kernel and AutoGen, transforms multi-agent development and deployment.

* **General Articles on Azure AI Agent Service & Foundry (News/Blogs):**
    * **Azure AI Agent Service Now in Public Preview (InfoQ):** Provides context on the service, its capabilities, and its place within Azure AI Foundry.
        * **URL:** [https://www.infoq.com/news/2025/02/azure-ai-agent-service-preview/](https://www.infoq.com/news/2025/02/azure-ai-agent-service-preview/)
    * **New capabilities in Azure AI Foundry to build advanced agentic applications (Azure Blog):** Discusses the evolution of Azure AI Foundry, the role of Semantic Kernel's agent framework for multi-agent systems, and the Azure AI Agent Service.
        * **URL:** [https://azure.microsoft.com/en-us/blog/new-capabilities-in-azure-ai-foundry-to-build-advanced-agentic-applications/](https://azure.microsoft.com/en-us/blog/new-capabilities-in-azure-ai-foundry-to-build-advanced-agentic-applications/)

**Tips for "Claude Code":**

* Start with the foundational Semantic Kernel concepts before diving deep into multi-agent specifics.
* Understand how plugins (tools) are defined and used in SK, as this is key for agent capabilities.
* Explore the `Agent` and `AgentGroupChat` (or similar orchestration mechanisms) in Semantic Kernel for managing interactions between agents.
* Review the `AzureAIAgent` in Semantic Kernel for direct integration patterns with the Azure AI Agent Service.
* The GitHub sample repositories (especially those under `Azure-Samples` and `microsoft`) are invaluable for practical code examples. Pay attention to how projects are structured, dependencies managed, and services configured.
* Note the distinction between building the agent logic with Semantic Kernel and then *deploying/hosting* that agent using Azure AI Agent Service.

This compilation should provide a strong foundation for "Claude Code" to understand and generate code for your multi-agent application on the Microsoft AI stack.