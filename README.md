# Building a Basic MCP Server with Python
This tutorial is based on the [Model Context Protocol (MCP)](https://docs.anthropic.com/mcp/), and the code is adapted from a [Medium.com article](https://medium.com/data-engineering-with-dremio/building-a-basic-mcp-server-with-python-4c34c41031ed).  There is an Interactive Artifact (for Windows) one-shot by [Claude](https://claude.ai/public/artifacts/cce2ed12-cf73-4e7f-bdab-55b13700936c)

## Overview

The Model Context Protocol (MCP) enables AI assistants like Claude to securely interact with external data and custom tools. This tutorial walks through creating a basic MCP server that reads CSV and Parquet files.

## Prerequisites

- Python 3.8+
- Basic understanding of Python
- `uv` (modern Python project manager)

## Project Setup

### 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart your terminal and verify:
```bash
uv --version
```

### 2. Create Project Structure

```bash
uv init mix_server
cd mix_server
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
uv add "mcp[cli]" pandas pyarrow
```

### 4. Create Folder Structure

```bash
mkdir data tools utils
touch server.py main.py
```

Your structure should look like:
```
mix_server/
├── data/           # Sample data files
├── tools/          # MCP tool definitions  
├── utils/          # Reusable utilities
├── server.py       # MCP server instance
└── main.py         # Entry point
```

## Create Sample Data

### CSV File
Create `data/sample.csv`:
```csv
id,name,email,signup_date
1,Alice Johnson,alice@example.com,2023-01-15
2,Bob Smith,bob@example.com,2023-02-22
3,Carol Lee,carol@example.com,2023-03-10
4,David Wu,david@example.com,2023-04-18
5,Eva Brown,eva@example.com,2023-05-30
```

### Generate Parquet File
Create `generate_parquet.py`:
```python
import pandas as pd

df = pd.read_csv("data/sample.csv")
df.to_parquet("data/sample.parquet", index=False)
```

Run it:
```bash
uv run generate_parquet.py
```

## Build Utility Functions

Create `utils/file_reader.py`:
```python
import pandas as pd
from pathlib import Path

# Base directory where our data lives
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def read_csv_summary(filename: str) -> str:
    """Read a CSV file and return a simple summary."""
    file_path = DATA_DIR / filename
    df = pd.read_csv(file_path)
    return f"CSV file '{filename}' has {len(df)} rows and {len(df.columns)} columns."

def read_parquet_summary(filename: str) -> str:
    """Read a Parquet file and return a simple summary.""" 
    file_path = DATA_DIR / filename
    df = pd.read_parquet(file_path)
    return f"Parquet file '{filename}' has {len(df)} rows and {len(df.columns)} columns."
```

## Create MCP Server

### Define Server Instance
Create `server.py`:
```python
from mcp.server.fastmcp import FastMCP

# Shared MCP server instance
mcp = FastMCP("mix_server")
```

### CSV Tool
Create `tools/csv_tools.py`:
```python
from server import mcp
from utils.file_reader import read_csv_summary

@mcp.tool()
def summarize_csv_file(filename: str) -> str:
    """
    Summarize a CSV file by reporting its number of rows and columns.
    Args:
        filename: Name of the CSV file in the /data directory (e.g., 'sample.csv')
    Returns:
        A string describing the file's dimensions.
    """
    return read_csv_summary(filename)
```

### Parquet Tool  
Create `tools/parquet_tools.py`:
```python
from server import mcp
from utils.file_reader import read_parquet_summary

@mcp.tool()
def summarize_parquet_file(filename: str) -> str:
    """
    Summarize a Parquet file by reporting its number of rows and columns.
    Args:
        filename: Name of the Parquet file in the /data directory (e.g., 'sample.parquet')
    Returns:
        A string describing the file's dimensions.
    """
    return read_parquet_summary(filename)
```

### Entry Point
Create `main.py`:
```python
from server import mcp

# Import tools so they get registered via decorators
import tools.csv_tools
import tools.parquet_tools

# Entry point to run the server
if __name__ == "__main__":
    mcp.run()
```

## Connect to Claude for Desktop

### 1. Run the Server
```bash
uv run main.py
```

### 2. Install Claude for Desktop
Download from: https://www.anthropic.com/claude

### 3. Configure Claude
Create/edit the config file:

**macOS/Linux:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

Add this configuration (replace with your actual path):
```json
{
  "mcpServers": {
    "mix_server": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/mix_server",
        "run",
        "main.py"
      ]
    }
  }
}
```

### 4. Restart Claude for Desktop
You should see a hammer icon indicating available tools:
- `summarize_csv_file`
- `summarize_parquet_file`

## Test Your Server

Try asking Claude:
- "Summarize the CSV file named sample.csv"
- "How many rows are in sample.parquet?"

Claude will automatically call your tools and return the results!

## Troubleshooting

- Ensure `uv run main.py` is running without errors
- Verify file paths in config JSON are correct
- Check that data files exist in `/data` directory
- Look for error messages in Claude UI

## Next Steps

Extend your MCP server by:
- Adding more advanced data analysis tools
- Supporting additional file formats
- Creating tools that filter or transform data
- Adding async operations for API calls
- Building custom prompts with `@mcp.prompt()`
- Exposing static data with `@mcp.resource()`

## Key Concepts

- **MCP Tools**: Python functions decorated with `@mcp.tool()` that AI can call
- **FastMCP**: Simplified framework for building MCP servers
- **Tool Registration**: Automatic via decorators when modules are imported
- **Natural Language Interface**: Claude translates user requests to tool calls

You now have a working foundation for building AI-powered tools that can interact with local data through natural language!
