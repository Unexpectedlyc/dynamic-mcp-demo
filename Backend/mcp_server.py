from utils.utils import load_config
from Backend.register_tool import mcp, register_all_tools


def run_server():
    config = load_config()
    register_all_tools()
    transport = config["server"]["transport"]
    host = config["server"]["ip"] or "localhost"
    port = config["server"]["port"] or 8080
    if transport == "stdio":
        mcp.run()
    elif transport == "sse" or transport == "http":
        mcp.run(
            transport=transport,
            host=host,
            port=port,
        )
    else:
        raise ValueError(f"Invalid transport: {transport}")


if __name__ == "__main__":
    run_server()
