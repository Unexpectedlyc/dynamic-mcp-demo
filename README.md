# dynamic-mcp-demo 🚀

通过配置文件实现 MCP 工具的动态加载 ⚙️

## 项目简介 📖

这是一个演示如何通过配置文件动态加载 MCP 工具的项目。该项目展示了如何使用配置驱动的方法来灵活加载和管理 MCP（Model Context Protocol）工具，从而提升系统的可扩展性和可维护性。

## 主要特性 ✨

- 🔄 **动态加载**: 通过配置文件实现 MCP 工具的动态加载
- ⚙️ **配置驱动**: 使用 YAML 配置文件管理工具定义
- 🛠️ **灵活性**: 支持多种 HTTP 方法 (GET, POST, PUT, DELETE)
- 📦 **模块化设计**: 工具注册与业务逻辑完全分离
- 🌐 **HTTP 代理**: 支持路径参数、查询参数和请求体参数
- 📝 **类型安全**: 支持参数类型验证 (str, int, float, bool)

## 支持的传输协议 📡

- `stdio`: 标准输入输出传输
- `sse`: Server-Sent Events 传输
- `http`: HTTP 流式传输

## 快速开始 🚀

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置工具

修改config.yaml文件来定义您的工具：

```yaml
server:
  ip: localhost
  port: 8080
  transport: sse

tools:
  - name: get_weather
    description: 获取指定城市的天气信息
    method: GET
    url: https://api.example.com/weather
    query_params:
      city: str
    timeout: 10
```

### 3. 启动后端服务

```bash
python Backend/mcp_server.py
```

### 4. 运行前端应用

```bash
python Frontend/app.py
```

## 配置说明 📝

### 服务器配置

| 字段        | 类型    | 描述                                  |
| ----------- | ------- | ------------------------------------- |
| `ip`        | string  | 服务器 IP 地址（SSE/HTTP 传输时必需） |
| `port`      | integer | 服务器端口（SSE/HTTP 传输时必需）     |
| `transport` | string  | 传输协议：`stdio`, `sse`, `http`      |

### 工具配置

| 字段           | 类型    | 描述                                      |
| -------------- | ------- | ----------------------------------------- |
| `name`         | string  | 工具名称（必须唯一）                      |
| `description`  | string  | 工具描述信息                              |
| `method`       | string  | HTTP 方法：`GET`, `POST`, `PUT`, `DELETE` |
| `url`          | string  | 目标 API 的 URL 模板                      |
| `path_params`  | object  | URL 路径参数及其类型                      |
| `query_params` | object  | 查询字符串参数及其类型                    |
| `body_params`  | object  | 请求体参数及其类型                        |
| `timeout`      | integer | 请求超时时间（秒）                        |

## 工具类型示例 💡

### GET 请求示例

```yaml
- name: get_weather
  description: 获取指定城市的天气信息
  method: GET
  url: https://api.example.com/weather
  query_params:
    city: str
  timeout: 10
```

### POST 请求示例

```yaml
- name: create_user
  description: 创建新用户
  method: POST
  url: https://api.example.com/users
  body_params:
    name: str
    email: str
    age: int
  timeout: 15
```

### 带路径参数的请求示例

```yaml
- name: get_stock_price
  description: 获取股票价格
  method: GET
  url: https://api.example.com/stocks/{symbol}
  path_params:
    symbol: str
  timeout: 5
```

## 项目结构 🏗️

```
dynamic-mcp-demo/
├── Backend/
│   ├── mcp_server.py     # MCP 服务器主入口
│   └── register_tool.py  # 工具注册和创建逻辑
├── Frontend/
│   └── app.py           # 前端连接示例
├── config.yaml          # 工具配置文件
├── utils.py             # 通用工具函数
├── requirements.txt     # 依赖包列表
└── README.md            # 项目说明文档
```

## 贡献指南 🤝

欢迎提交 Issue 和 Pull Request 来帮助改进这个演示项目！

## 许可证 📄

MIT License

---

_该项目演示了如何使用 FastMCP 框架创建动态可配置的工具代理服务_
