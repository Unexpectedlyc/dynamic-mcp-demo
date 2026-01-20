# mcp_server.py
from fastmcp.tools import Tool
import yaml
import httpx
from typing import Any, Dict
from fastmcp import FastMCP
import inspect


# 初始化 FastMCP 应用
mcp = FastMCP("HTTP Tool Proxy 🌐")


def load_tools_config(config_path: str = "config.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def create_tool_function(tool_config: Dict[str, Any]):
    name = tool_config["name"]
    method = tool_config.get("method", "GET").upper()
    url_template = tool_config["url"]
    timeout = tool_config.get("timeout", 10)

    # 获取参数信息
    all_params = {}
    all_params.update(tool_config.get("path_params", {}))
    all_params.update(tool_config.get("query_params", {}))
    all_params.update(tool_config.get("body_params", {}))

    if not all_params:
        raise ValueError(f"Tool '{name}' must have at least one parameter")

    type_map = {"str": str, "int": int, "float": float, "bool": bool}

    # 创建带正确签名的函数
    def make_http_request(**kwargs):
        """Dynamically created HTTP request function"""
        # 构建 URL
        url = url_template
        for p in tool_config.get("path_params", {}):
            if p in kwargs:
                url = url.replace(f"{{{p}}}", str(kwargs[p]))

        query_params = {
            k: kwargs[k] for k in tool_config.get("query_params", {}) if k in kwargs
        }
        body_params = {
            k: kwargs[k] for k in tool_config.get("body_params", {}) if k in kwargs
        }

        with httpx.Client(timeout=timeout) as client:
            if method == "GET":
                resp = client.get(url, params=query_params)
            elif method == "POST":
                resp = client.post(url, params=query_params, json=body_params)
            elif method == "PUT":
                resp = client.put(url, params=query_params, json=body_params)
            elif method == "DELETE":
                resp = client.delete(url, params=query_params)
            else:
                raise ValueError(f"Unsupported method: {method}")
            resp.raise_for_status()
            return resp.text

    # 创建参数注解
    annotations = {"return": str}
    for param_name, param_type_str in all_params.items():
        annotations[param_name] = type_map[param_type_str]

    make_http_request.__name__ = name
    make_http_request.__doc__ = tool_config["description"]
    make_http_request.__annotations__ = annotations

    # 创建正确的签名
    sig_params = [
        inspect.Parameter(
            name=param_name,
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=type_map[param_type_str],
        )
        for param_name, param_type_str in all_params.items()
    ]
    make_http_request.__signature__ = inspect.Signature(sig_params)

    return make_http_request


def register_all_tools():
    config = load_tools_config()
    for tool_cfg in config.get("tools", []):
        func = create_tool_function(tool_cfg)
        # 使用 mcp.tool 装饰器注册（自动读取 __name__, __doc__, __annotations__）
        tool = Tool.from_function(func)
        mcp.add_tool(tool)
