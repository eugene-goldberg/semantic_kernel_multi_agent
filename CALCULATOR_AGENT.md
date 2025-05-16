# Calculator Agent Documentation

## Overview

The Calculator Agent is a specialized agent that performs advanced mathematical operations using powerful Python libraries like NumPy, SciPy, SymPy, and Pandas. It extends the multi-agent system by providing mathematical capabilities that would not be available to the other agents.

## Features

The Calculator Agent can handle various types of mathematical operations:

1. **Matrix Operations**
   - Determinants
   - Inverse matrices
   - Eigenvalues
   - Matrix information (shape, rank, norm)

2. **Statistical Analysis**
   - Mean, median, variance
   - Standard deviation
   - Correlation
   - Summary statistics (min, max, quartiles)

3. **Algebraic Operations**
   - Simplify expressions
   - Factor polynomials
   - Expand expressions

4. **Calculus Operations**
   - Derivatives
   - Integrals
   - Limits

5. **Equation Solving**
   - Linear equations
   - Quadratic equations
   - Systems of equations

6. **General Arithmetic**
   - Basic operations (addition, subtraction, multiplication, division)
   - Complex expressions

## Implementation

The Calculator Agent consists of three main components:

1. **Calculator Agent Class** (`src/agents/calculator_agent.py`)
   - Implements the core mathematical functionality
   - Uses specialized libraries for advanced operations
   - Parses user queries to identify the required operation

2. **Calculator Plugin** (`src/agents/plugins/calculator_plugin.py`)
   - Provides a Semantic Kernel interface to the Calculator Agent
   - Exposes functions that can be called via function calling
   - Enables integration with the orchestration system

3. **Deployment Script** (`src/scripts/deploy_calculator_agent.py`)
   - Deploys the Calculator Agent to Azure OpenAI as an Assistant
   - Configures the agent with function calling capabilities
   - Saves the deployment information for orchestration

## Orchestration Integration

The Calculator Agent is integrated with the orchestration system:

1. The Orchestrator Agent is updated to recognize mathematical queries
2. Mathematical requests are routed to the Calculator Agent
3. Results are returned to the user through the Orchestrator

## Usage Examples

### Matrix Operations

```
Calculate the determinant of matrix [[1, 2], [3, 4]]
```

### Statistical Analysis

```
What is the mean and standard deviation of 10, 20, 30, 40, 50?
```

### Algebraic Operations

```
Simplify the expression x^2 + 2*x + 1
```

### Calculus Operations

```
Find the derivative of x^3 with respect to x
```

### Equation Solving

```
Solve the equation x^2 - 5*x + 6 = 0
```

## Deployment

To deploy the Calculator Agent independently:

```bash
python3 src/scripts/deploy_calculator_agent.py
```

To update the orchestration system to include the Calculator Agent:

```bash
python3 src/scripts/deploy_orchestration_openai.py
```

## Testing

To test the Calculator Agent locally:

```bash
python3 test_calculator_agent.py
```

## Technical Details

### Dependencies

The Calculator Agent requires the following Python libraries:

- NumPy: For matrix operations and numerical computations
- SciPy: For advanced scientific computations
- SymPy: For symbolic mathematics
- Pandas: For data analysis
- Matplotlib: For visualization (if needed)

### Implementation Pattern

The agent follows a pattern of:
1. Parsing the query to identify the operation type
2. Extracting relevant parameters
3. Performing the calculation using specialized libraries
4. Formatting the result for display

## Future Enhancements

Potential future enhancements for the Calculator Agent include:

1. Support for more advanced statistical methods
2. Visualization capabilities for data and functions
3. Support for differential equations
4. Machine learning integrations for data analysis
5. Natural language parsing improvements for mathematical expressions