# ParseFinalDecision Tool Node

This folder contains the implementation for the **parse_final_decision** tool node of the risk_manager agent.

## Files

- **`processor.py`** - Contains the main processing logic for this tool node
- **`__init__.py`** - Makes this directory a Python package

## Purpose

The parse_final_decision tool node is responsible for:
- Executing tool-based operations
- Processing data using available tools
- Providing tool-specific functionality

## Available Tools

This node has access to the following tools:
- parse_final_decision

## Usage

```python
from src.nodes.tools.parse_final_decision.processor import ParseFinalDecisionToolNode

# Initialize the tool node
node = ParseFinalDecisionToolNode(config)

# Run the tool node
result = await node.run(input_data)

# Get available tools
tools = node.get_available_tools()
```

## Configuration

This tool node uses the following configuration:
- **Type**: Tool Node
- **Available Tools**: Node-specific tools
- **Storage**: none/in-memory/none

## Customization

To customize this tool node:

1. **Modify Processor**: Edit `processor.py` to change the tool processing behavior
2. **Add Tools**: Update the tools configuration for this specific node
3. **Tool Integration**: Implement specific tool integrations in the logic

## Note

Tool nodes do not have prompts - they focus on tool execution and data processing.
