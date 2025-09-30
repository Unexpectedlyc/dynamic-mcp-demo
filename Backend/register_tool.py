# mcp_server.py
from fastmcp.tools import Tool
import yaml
import httpx
from typing import Any, Dict, get_type_hints
from fastmcp import FastMCP
from pydantic import BaseModel, create_model
import inspect
import types
from typing import get_type_hints

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

    # 合并所有参数
    all_params = {}
    all_params.update(tool_config.get("path_params", {}))
    all_params.update(tool_config.get("query_params", {}))
    all_params.update(tool_config.get("body_params", {}))

    if not all_params:
        raise ValueError(f"Tool '{name}' must have at least one parameter")

    # 类型映射
    type_map = {"str": str, "int": int, "float": float, "bool": bool}

    # 构建参数名和类型
    param_names = list(all_params.keys())
    param_types = [type_map[all_params[n]] for n in param_names]

    # 构建函数体逻辑（闭包捕获配置）
    def make_handler(tool_cfg, url_tmpl, meth, to):
        def handler(*args):
            # args 顺序与 param_names 一致
            kwargs = dict(zip(param_names, args))

            # 构建 URL
            url = url_tmpl
            for p in tool_cfg.get("path_params", {}):
                url = url.replace(f"{{{p}}}", str(kwargs[p]))

            query_params = {
                k: kwargs[k] for k in tool_cfg.get("query_params", {}) if k in kwargs
            }
            body_params = {
                k: kwargs[k] for k in tool_cfg.get("body_params", {}) if k in kwargs
            }

            with httpx.Client(timeout=to) as client:
                if meth == "GET":
                    resp = client.get(url, params=query_params)
                elif meth == "POST":
                    resp = client.post(url, params=query_params, json=body_params)
                elif meth == "PUT":
                    resp = client.put(url, params=query_params, json=body_params)
                elif meth == "DELETE":
                    resp = client.delete(url, params=query_params)
                else:
                    raise ValueError(f"Unsupported method: {meth}")
                resp.raise_for_status()
                return resp.text

        return handler

    # 创建函数对象，带固定参数签名
    handler_func = make_handler(tool_config, url_template, method, timeout)

    # 手动设置函数名和文档
    handler_func.__name__ = name
    handler_func.__doc__ = tool_config["description"]

    # 构建新的函数签名（无 *args/**kwargs）
    sig_params = [
        inspect.Parameter(
            name=p_name, kind=inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=p_type
        )
        for p_name, p_type in zip(param_names, param_types)
    ]
    new_sig = inspect.Signature(sig_params, return_annotation=str)
    handler_func.__signature__ = new_sig

    # 设置类型注解（用于 FastMCP 推断）
    handler_func.__annotations__ = dict(zip(param_names, param_types))
    handler_func.__annotations__["return"] = str

    return handler_func


def register_all_tools():
    config = load_tools_config()
    for tool_cfg in config.get("tools", []):
        func = create_tool_function(tool_cfg)
        # 使用 mcp.tool 装饰器注册（自动读取 __name__, __doc__, __annotations__）
        tool = Tool.from_function(func)
        mcp.add_tool(tool)
