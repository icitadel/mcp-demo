from server import mcp

# Import tools so they get registered via decorators
import tools.csv_tools
import tools.parquet_tools

# Entry point to run the MCP server
if __name__ == "__main__":
    # No print statements - MCP requires pure JSON communication
    mcp.run()