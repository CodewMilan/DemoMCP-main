# FastMCP Name Server

A simple FastMCP server that takes a name as input and provides various name-related operations.

## Features

- **get_name**: Takes a name and returns a greeting message
- **print_name**: Takes a name and prints it to console
- **format_name**: Formats a name in different ways (uppercase, lowercase, title, reverse)

## Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone or download this project
2. Navigate to the project directory:
   ```bash
   cd fastmcp-name-project
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Server

To start the FastMCP server:

```bash
python server.py
```

The server will start and be ready to accept MCP connections.

## Usage

The server provides three main tools:

### 1. get_name
- **Input**: `name` (string)
- **Output**: A greeting message with the provided name
- **Example**: Input "Alice" → Output "Hello, Alice! Nice to meet you."

### 2. print_name
- **Input**: `name` (string)
- **Output**: Prints the name to console and returns confirmation
- **Example**: Input "Bob" → Prints "Name received: Bob" and returns "Successfully printed: Bob"

### 3. format_name
- **Input**: 
  - `name` (string) - The name to format
  - `format_type` (string, optional) - Format type: "uppercase", "lowercase", "title", "reverse"
- **Output**: The formatted name
- **Examples**:
  - Input "john", "uppercase" → Output "JOHN"
  - Input "MARY", "lowercase" → Output "mary"
  - Input "alice smith", "title" → Output "Alice Smith"
  - Input "hello", "reverse" → Output "olleh"

## Project Structure

```
fastmcp-name-project/
├── server.py          # Main FastMCP server implementation
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Development

To modify the server:

1. Edit `server.py` to add new tools or modify existing ones
2. Each tool is defined using the `@mcp.tool()` decorator
3. Tools can accept parameters with type hints
4. Tools should be async functions that return strings

## Example Tool Definition

```python
@mcp.tool()
async def my_tool(input_param: str) -> str:
    """
    Description of what the tool does.
    
    Args:
        input_param: Description of the parameter
        
    Returns:
        Description of the return value
    """
    return f"Processed: {input_param}"
```

## Troubleshooting

- Make sure Python 3.8+ is installed
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that the server starts without errors
- Verify MCP client can connect to the server
