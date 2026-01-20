import yaml
from typing import Dict, Any
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamable_http_client
from contextlib import AsyncExitStack


def load_config(config_path: str = "config.yaml") -> Dict[Any, Any]:
    """
    读取配置文件

    Args:
        config_path (str): 配置文件路径，默认为 "config.yaml"

    Returns:
        Dict[Any, Any]: 配置文件内容的字典表示

    Raises:
        FileNotFoundError: 当配置文件不存在时
        yaml.YAMLError: 当配置文件格式错误时
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件 {config_path} 不存在")

    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
            return config
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"配置文件解析错误: {e}")


async def connect_to_stdio_server(server_script_path: str, exit_stack):
    """Connect to an MCP server

    Args:
        server_script_path: Path to the server script (.py or .js)
    """
    is_python = server_script_path.endswith(".py")
    is_js = server_script_path.endswith(".js")
    if not (is_python or is_js):
        raise ValueError("Server script must be a .py or .js file")

    command = "python" if is_python else "node"
    server_params = StdioServerParameters(
        command=command, args=[server_script_path], env=None
    )

    stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
    stdio, write = stdio_transport
    session = await exit_stack.enter_async_context(ClientSession(stdio, write))

    return session


async def connect_to_sse_server(url: str, exit_stack):
    sse_transport = await exit_stack.enter_async_context(sse_client(url))
    sse, write = sse_transport
    session = await exit_stack.enter_async_context(ClientSession(sse, write))

    return session


async def connect_to_streamablehttp_server(url: str, exit_stack):
    streamablehttp_transport = await exit_stack.enter_async_context(
        streamable_http_client(url)
    )
    streamablehttp, write = streamablehttp_transport
    session = await exit_stack.enter_async_context(ClientSession(streamablehttp, write))

    return session


async def connect_to_server():
    exit_stack = AsyncExitStack()
    """Connect to an MCP server"""
    config = load_config()
    transport = config["server"]["transport"]
    host = config["server"]["ip"] or "localhost"
    port = config["server"]["port"] or 8000
    if transport == "stdio":
        server_script_path = "Backend/mcp_server.py"
        session = await connect_to_stdio_server(server_script_path, exit_stack)
    elif transport == "sse":
        url = f"http://{host}:{port}/sse"
        session = await connect_to_sse_server(url, exit_stack)
    elif transport == "http":
        url = f"http://{host}:{port}/mcp"
        session = await connect_to_streamablehttp_server(url, exit_stack)
    else:
        raise ValueError("Invalid mcp_type")

    await session.initialize()
    # List available tools
    response = await session.list_tools()
    tools = response.tools
    print("\nConnected to server with tools:", [tool.name for tool in tools])
    return tools


async def execute_mcp_tool(tool, params=None):
    """
    执行指定的MCP工具
    :param tool: MCP工具对象
    :param params: 工具执行参数字典
    :return: 执行结果
    """
    if params is None:
        params = {}

    # 重新建立连接以执行工具
    # 注意：在生产环境中，您可能想要复用现有的连接
    exit_stack = AsyncExitStack()
    config = load_config()
    transport = config["server"]["transport"]
    host = config["server"]["ip"] or "localhost"
    port = config["server"]["port"] or 8000

    if transport == "stdio":
        server_script_path = "Backend/mcp_server.py"
        session = await connect_to_stdio_server(server_script_path, exit_stack)
    elif transport == "sse":
        url = f"http://{host}:{port}/sse"
        session = await connect_to_sse_server(url, exit_stack)
    elif transport == "http":
        url = f"http://{host}:{port}/mcp"
        session = await connect_to_streamablehttp_server(url, exit_stack)
    else:
        raise ValueError(f"不支持的传输协议: {transport}")

    try:
        await session.initialize()
        # 执行MCP工具并返回结果
        result = await session.call_tool(tool.name, params)
        return result
    except Exception as e:
        error_message = f"执行工具 {tool.name} 失败: {str(e)}"
        print(error_message)
        raise Exception(error_message)
    finally:
        # 清理资源
        await exit_stack.aclose()


# 使用示例
if __name__ == "__main__":
    try:
        config = load_config()
        print("服务器配置:")
        print(f"  IP: {config['server']['ip']}")
        print(f"  端口: {config['server']['port']}")
        print(f"  传输协议: {config['server']['transport']}")

        print("\n工具配置:")
        for tool in config["tools"]:
            print(f"  工具名称: {tool['name']}")
            print(f"  描述: {tool['description']}")
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"错误: {e}")
