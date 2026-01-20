import streamlit as st
from utils.utils import connect_to_server, execute_mcp_tool
import asyncio
import json


async def run_app():
    st.title("MCP 工具信息展示")

    if st.button("连接到 MCP 服务器"):
        with st.spinner("正在连接到 MCP 服务器..."):
            try:
                result = await connect_to_server()

                if result:
                    st.success("成功连接到 MCP 服务器！")
                    st.session_state.mcp_tools = result
                else:
                    st.error("未能从 MCP 服务器获取数据")

            except Exception as e:
                st.error(f"连接失败: {str(e)}")

    # 显示可用的MCP工具并提供执行功能
    if hasattr(st.session_state, "mcp_tools"):
        st.subheader("可用的 MCP 工具:")

        tools = st.session_state.mcp_tools
        if isinstance(tools, list):
            for idx, tool in enumerate(tools):
                with st.expander(f"工具 {idx + 1}: {tool.name}"):
                    st.json(tool)

                    # 创建带参数输入的表单
                    with st.form(key=f"form_{idx}"):
                        st.write(f"**执行参数:**")

                        # 动态生成参数输入字段
                        params = {}
                        if tool.inputSchema:
                            schema = tool.inputSchema
                            if isinstance(schema, str):
                                try:
                                    schema = json.loads(schema)
                                except:
                                    st.warning("无法解析输入模式")
                                    continue

                            if "properties" in schema:
                                for param_name, param_info in schema[
                                    "properties"
                                ].items():
                                    param_type = param_info.get("type", "string")

                                    # 获取参数的标题或使用参数名作为标签
                                    label = param_info.get("title", param_name)
                                    description = param_info.get("description", "")

                                    # 根据参数类型生成不同类型的输入组件
                                    if param_type == "string":
                                        default_value = param_info.get("default", "")
                                        params[param_name] = st.text_input(
                                            f"{label}",
                                            value=default_value,
                                            help=description,
                                        )
                                    elif param_type == "integer":
                                        default_value = param_info.get("default", 0)
                                        min_value = param_info.get("minimum", None)
                                        max_value = param_info.get("maximum", None)
                                        params[param_name] = st.number_input(
                                            f"{label}",
                                            value=int(default_value),
                                            min_value=min_value,
                                            max_value=max_value,
                                            step=1,
                                            help=description,
                                        )
                                    elif param_type == "number":
                                        default_value = param_info.get("default", 0.0)
                                        min_value = param_info.get("minimum", None)
                                        max_value = param_info.get("maximum", None)
                                        params[param_name] = st.number_input(
                                            f"{label}",
                                            value=float(default_value),
                                            min_value=min_value,
                                            max_value=max_value,
                                            help=description,
                                        )
                                    elif param_type == "boolean":
                                        default_value = param_info.get("default", False)
                                        params[param_name] = st.checkbox(
                                            f"{label}",
                                            value=bool(default_value),
                                            help=description,
                                        )
                                    elif param_type == "array":
                                        # 对于数组类型，提供文本输入，用户可以用逗号分隔
                                        default_value = ", ".join(
                                            param_info.get("default", [])
                                        )
                                        array_input = st.text_input(
                                            f"{label} (用逗号分隔)",
                                            value=default_value,
                                            help=description,
                                        )
                                        # 将逗号分隔的字符串转换为数组
                                        params[param_name] = [
                                            item.strip()
                                            for item in array_input.split(",")
                                            if item.strip()
                                        ]
                                    else:
                                        # 默认为文本输入
                                        default_value = param_info.get("default", "")
                                        params[param_name] = st.text_input(
                                            f"{label}",
                                            value=str(default_value),
                                            help=description,
                                        )

                        # 提交按钮
                        submitted = st.form_submit_button(f"执行工具: {tool.name}")

                        if submitted:
                            await execute_tool_with_params_handler(tool, idx, params)
        elif isinstance(tools, dict):
            st.json(tools)


async def execute_tool_with_params_handler(tool, index, params):
    """处理带参数的工具执行函数"""
    with st.spinner(f"正在执行工具 {tool.name}..."):
        try:
            # 执行MCP工具，传递参数
            execution_result = await execute_mcp_tool(tool, params)

            st.success(f"工具 {tool.name} 执行成功！")

            # 显示执行结果
            with st.expander("查看执行结果", expanded=True):
                st.json(execution_result)

        except Exception as e:
            st.error(f"执行工具失败: {str(e)}")
            st.exception(e)  # 显示完整的错误堆栈


async def execute_tool_handler(tool, index):
    """处理不带参数的工具执行函数"""
    with st.spinner(f"正在执行工具 {tool.name}..."):
        try:
            # 执行MCP工具，无参数
            execution_result = await execute_mcp_tool(tool)

            st.success(f"工具 {tool.name} 执行成功！")

            # 显示执行结果
            with st.expander("查看执行结果", expanded=True):
                st.json(execution_result)

        except Exception as e:
            st.error(f"执行工具失败: {str(e)}")


if __name__ == "__main__":
    asyncio.run(run_app())
