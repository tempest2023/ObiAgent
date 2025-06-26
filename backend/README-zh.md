# PocketFlow 通用智能体系统

一个构建于 PocketFlow 之上的智能代理系统，能够动态设计并执行工作流来解决用户的复杂问题。该系统具备学习能力，可以从成功的工作流中积累经验，并提供智能的用户交互和敏感操作权限管理功能。

## 📋 目录

- [🎯 系统概览](#-系统概览)
- [🏗️ 系统架构](#️-系统架构)
- [🚀 快速开始](#-快速开始)
- [📡 API 接口](#-api-接口)
- [🔧 使用示例](#-使用示例)
- [🧠 学习与优化机制](#-学习与优化机制)
- [🔒 安全与权限控制](#-安全与权限控制)
- [📊 统计与监控](#-统计与监控)
- [🛠️ 开发说明](#️-开发说明)
- [日志系统](#日志系统)
- [配置说明](#配置说明)
- [扩展指南](#扩展指南)
- [故障排查](#故障排查)
- [🤝 贡献须知](#-贡献须知)
- [📝 许可协议](#-许可协议)
- [🔗 相关文档](#-相关文档)

## 🎯 系统概览

通用智能体系统旨在通过以下方式解决复杂和模糊的问题：

1. **分析** 用户问题并设计合适的工作流
2. **动态执行** 工作流，调用可用节点
3. **学习** 成功的工作流模式并重用
4. **处理** 用户交互和敏感权限申请
5. **优化** 工作流流程，基于执行结果与用户反馈

## 🏗️ 系统架构

### 核心组件

#### 1. **节点注册器** ([`utils/node_registry.py`](agent/utils/node_registry.py))

* **作用**：记录所有智能体可用的节点
* **功能**：

  * 节点元数据（描述、输入、输出、权限等级）
  * 分类（搜索、分析、预订、支付等）
  * 权限等级（无、基础、敏感、关键）
  * 示例用法模式

#### 2. **工作流存储器** ([`utils/workflow_store.py`](agent/utils/workflow_store.py))

* **作用**：持久化保存成功的工作流以供重用
* **功能**：

  * 工作流模式的持久化存储
  * 基于相似度的工作流检索
  * 成功率跟踪与学习机制
  * 提供工作流优化建议

#### 3. **权限管理器** ([`utils/permission_manager.py`](agent/utils/permission_manager.py))

* **作用**：处理敏感操作所需的用户权限
* **功能**：

  * 创建并跟踪权限申请请求
  * 权限请求超时处理
  * 支持多种权限类型（支付、预订等）
  * 用户响应处理机制

#### 4. **智能体节点** ([`nodes.py`](agent/nodes.py))

##### WorkflowDesignerNode（工作流设计节点）

* 使用 LLM 分析用户问题
* 根据可用节点设计工作流
* 借鉴类似历史工作流
* 生成结构化工作流定义

##### WorkflowExecutorNode（工作流执行节点）

* 动态执行设计好的工作流
* 节点名映射为实际实现函数
* 处理进度反馈与异常管理
* 将成功工作流保存入存储器

##### UserInteractionNode（用户交互节点）

* 处理用户问题与回应
* 发送权限申请
* 收集用户输入

##### WorkflowOptimizerNode（工作流优化节点）

* 分析工作流结果中的问题
* 提出改进建议
* 集成用户反馈

### 工作流设计图示

系统采用高级流程设计以处理复杂场景：

```mermaid
graph TD
    A[用户问题] --> B[WorkflowDesignerNode]
    B --> C[WorkflowExecutorNode]
    C --> D{需要用户输入？}
    D -->|是| E[UserInteractionNode]
    D -->|否| F[WorkflowOptimizerNode]
    E --> G{收到回应？}
    G -->|否| E
    G -->|是| C
    F --> H{需要优化？}
    H -->|是| B
    H -->|否| I[成功]
```

## 🚀 快速开始

### 前置条件

1. **Python 3.8+**
2. **OpenAI API Key**（用于调用 LLM）
3. **Google Gemini API Key**（可选备用 LLM）
4. **Firecrawl API Key**（用于网页抓取）
您可以获取您的 API 密钥在 https://www.firecrawl.dev/ 。
您可以在 `.env` 文件中设置您的 API 密钥。然后运行 `python3 setup_env.py` 生成 `.env_activate.sh` 和 `.env_deactivate.sh` 文件。使用 `.env_activate.sh` 激活环境变量，而不会覆盖现有的环境变量。使用 `.env_deactivate.sh` 停用环境变量并恢复原始环境变量。

### 安装步骤

1. **克隆项目并进入目录：**

   ```bash
   cd backend
   ```

2. **安装依赖：**

   ```bash
   pip install -r requirements.txt
   ```

3. **设置环境变量：**

   ```bash
   export OPENAI_API_KEY="你的-openai-api-key"
   export GEMINI_API_KEY="你的-gemini-api-key"  # 可选
   ```

4. **运行服务：**

   ```bash
   python server.py
   ```

服务器将运行在 `http://localhost:8000`

### API 文档

运行后访问 `http://localhost:8000/docs` 查看交互式 API 文档。

## 📡 API 接口

### WebSocket 接口

#### `/api/v1/ws` - 通用智能体 WebSocket

处理实时交互：

**消息类型：**

* `chat`: 用户提问
* `user_response`: 用户对智能体提问的回应
* `permission_response`: 用户对权限请求的回应
* `feedback`: 用户反馈用于优化

**使用示例：**

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws');

ws.send(JSON.stringify({
    type: 'chat',
    content: '帮我订一张洛杉矶飞往上海的高性价比机票，最好是下午出发的。'
}));

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data.type, data.content);
};
```

### REST API 接口

#### 节点注册

* `GET /api/v1/nodes` - 获取所有节点
* `GET /api/v1/nodes/{node_name}` - 获取指定节点
* `GET /api/v1/nodes/category/{category}` - 按类别获取节点

#### 工作流存储

* `GET /api/v1/workflows` - 获取所有工作流
* `GET /api/v1/workflows/{workflow_id}` - 获取指定工作流
* `GET /api/v1/workflows/similar?question={question}` - 查询相似工作流
* `DELETE /api/v1/workflows/{workflow_id}` - 删除工作流
* `GET /api/v1/workflows/stats` - 获取工作流统计信息

#### 权限管理

* `GET /api/v1/permissions` - 获取待处理权限请求
* `GET /api/v1/permissions/{request_id}` - 获取指定权限请求
* `POST /api/v1/permissions/{request_id}/respond` - 响应权限请求
* `GET /api/v1/permissions/stats` - 获取权限统计

## 🔧 使用示例

### 订票场景示例

请求示例：

> “帮我订一张从洛杉矶飞往上海的高性价比机票，最好下午出发。”

**执行流程：**

1. **WorkflowDesignerNode** 设计出如下工作流：

   ```yaml
   workflow:
     name: 订票工作流
     nodes:
       - name: flight_search
         description: 搜索航班选项
       - name: cost_analysis
         description: 成本分析与筛选性价比
       - name: result_summarizer
         description: 总结推荐结果
   ```

2. **WorkflowExecutorNode** 执行：

   * 模拟搜索航班
   * 分析费用与偏好
   * 输出推荐

3. **UserInteractionNode** 若需信息或权限则通知用户

4. **WorkflowOptimizerNode** 根据结果优化流程

5. **Workflow Store** 保存该工作流供下次使用

### 添加新节点

在 [`utils/node_registry.py`](agent/utils/node_registry.py) 注册：

```python
node_registry.register_node(NodeMetadata(
    name="custom_node",
    description="该节点的功能描述",
    category=NodeCategory.ANALYSIS,
    permission_level=PermissionLevel.NONE,
    inputs=["input1", "input2"],
    outputs=["output1"],
    examples=[{"input1": "示例", "output1": "结果"}]
))
```

然后在 [`nodes.py`](agent/nodes.py) 的 `WorkflowExecutorNode._execute_node()` 中实现逻辑。

## 🧠 学习与优化机制

### 工作流学习

* 成功的工作流会自动保存
* 相似问题可复用历史流程
* 系统记录成功率并用于排序

### 优化机制

* 失败工作流会触发分析与优化建议
* 用户反馈用于改进流程
* 系统可基于问题重构工作流

### 权限处理

* 敏感操作需显式权限
* 权限请求支持超时机制
* 不同操作有不同权限等级

## 🔒 安全与权限控制

### 权限等级

* **NONE**：无需权限
* **BASIC**：用户确认即可
* **SENSITIVE**：需要详细确认
* **CRITICAL**：需明确详细批准

### 敏感操作包括：

* 支付处理
* 预订确认
* 数据访问
* 系统变更操作

## 📊 统计与监控

系统提供完整的统计信息：

* **工作流存储**：成功率、使用次数、节点类别
* **权限管理**：允许/拒绝率、响应时间
* **节点注册器**：各类节点概览

## 🛠️ 开发说明

### 项目结构

```
backend/
├── agent/
│   ├── nodes.py              # 智能体节点实现
│   ├── flow.py               # 工作流逻辑
│   ├── utils/
│   │   ├── node_registry.py  # 节点注册器
│   │   ├── workflow_store.py # 工作流存储
│   │   ├── permission_manager.py # 权限管理
│   │   └── stream_llm.py     # LLM 工具
│   └── README.md
├── server.py                 # FastAPI 服务入口
├── requirements.txt          # 项目依赖
└── README.md                 # 项目说明文档
```

### 扩展指南

1. **添加新节点**：注册节点并在执行器中实现
2. **新增工作流**：在 [`flow.py`](agent/flow.py) 中编写逻辑
3. **扩展工具包**：新增 utils 模块
4. **新增 API**：在 FastAPI 中添加新接口

## 🧪 测试

### 单元测试

系统包含全面的功能节点单元测试：

```bash
# 运行所有功能节点测试
pytest agent/test/test_function_nodes.py

# 运行详细输出
pytest agent/test/test_function_nodes.py -v

# 运行特定测试
pytest agent/test/test_function_nodes.py::test_flight_search
```

### 测试覆盖范围

测试套件覆盖所有功能节点：
- `FirecrawlScrapeNode` - 网页抓取功能
- `FlightBookingNode` - 机票预订模拟
- `PreferenceMatcherNode` - 用户偏好匹配
- `DataFormatterNode` - 数据格式化工具
- `PermissionRequestNode` - 权限处理
- `UserQueryNode` - 用户交互管理
- `ResultSummarizerNode` - 结果汇总
- `CostAnalysisNode` - 成本分析逻辑
- `FlightSearchNode` - 航班搜索模拟
- `AnalyzeResultsNode` - 搜索结果分析
- `WebSearchNode` - 网络搜索功能

### 测试特性

- **模拟依赖**：外部 API 和 LLM 调用被模拟以确保测试可靠性
- **全面覆盖**：每个节点的 `prep`、`exec` 和 `post` 方法都被测试
- **错误处理**：测试包含错误场景和边界情况
- **共享存储验证**：测试验证共享存储中的数据存储正确性

### 测试方式

```bash
# 测试服务是否正常
curl http://localhost:8000/health

# 测试节点接口
curl http://localhost:8000/api/v1/nodes

# 测试工作流存储
curl http://localhost:8000/api/v1/workflows
```

## 日志系统

系统包含一个全面的日志系统，用于跟踪执行流程和调试问题。

### 日志级别

* **DEBUG**：开发时的详细日志（包括函数名和行号）
* **INFO**：生产环境推荐使用的标准日志
* **WARNING**：仅记录警告和错误
* **ERROR**：仅记录错误信息
* **QUIET**：仅记录关键错误（适用于性能要求高的场景）

### 使用方式

```bash
# 通过环境变量设置日志等级
export LOG_LEVEL=DEBUG
python server.py

# 或在代码中设置
from logging_config import setup_logging
setup_logging('DEBUG')

# 测试不同日志等级
python test_logging.py
```

### 日志功能特点

* **表情符号日志**：便于快速识别不同操作类型
* **结构化日志信息**：清晰一致的日志格式
* **节点级别日志**：每个节点独立记录日志
* **流程跟踪**：支持完整工作流的执行过程追踪
* **错误处理日志**：详细记录错误上下文
* **性能监控**：跟踪执行时间和资源使用情况

### 示例日志输出

```log
2024-01-15 10:30:15 - agent.nodes - INFO - 🔄 WorkflowDesignerNode: 开始 prep_async
2024-01-15 10:30:15 - agent.nodes - INFO - 📝 WorkflowDesignerNode: 正在处理问题：帮我订一张从洛杉矶出发的机票...
2024-01-15 10:30:15 - agent.nodes - INFO - 🔧 WorkflowDesignerNode: 找到 11 个可用节点
2024-01-15 10:30:15 - agent.nodes - INFO - 🤖 WorkflowDesignerNode: 调用 LLM 设计工作流
2024-01-15 10:30:18 - agent.nodes - INFO - ✅ WorkflowDesignerNode: 成功解析 YAML 响应
2024-01-15 10:30:18 - agent.nodes - INFO - 🎯 WorkflowDesignerNode: 成功设计出名为 'Flight Booking Workflow' 的 6 步工作流
```

## 配置说明

### 环境变量

* `OPENAI_API_KEY`：你的 OpenAI API 密钥
* `LOG_LEVEL`：日志级别（DEBUG, INFO, WARNING, ERROR, QUIET）
* `LOG_FILE`：可选，日志输出文件路径

### 日志配置方式

日志系统支持多种配置方式：

1. **使用环境变量**：

   ```bash
   export LOG_LEVEL=DEBUG
   export LOG_FILE=logs/agent.log
   ```

2. **在代码中配置**：

   ```python
   from logging_config import setup_logging

   # 设置不同日志等级
   setup_logging('DEBUG')      # 详细日志
   setup_logging('INFO')       # 标准日志
   setup_logging('QUIET')      # 最小化日志
   ```

3. **文件输出日志**：

   ```python
   setup_logging('INFO', 'logs/agent.log')
   ```

## 扩展指南

### 添加新节点

1. 在 [`agent/nodes.py`](agent/nodes.py) 中创建新的节点类
2. 实现必要的异步方法（`prep_async`, `exec_async`, `post_async`）
3. 添加日志语句以便调试
4. 在 [`agent/utils/node_registry.py`](agent/utils/node_registry.py) 中注册新节点

### 添加新工作流

1. 设计工作流结构
2. 实现所需节点逻辑
3. 更新工作流存储以支持保存/读取
4. 使用 demo 或 Web 接口进行测试

### 自定义日志格式

1. 修改 [`logging_config.py`](logging_config.py) 实现自定义格式
2. 为特定模块添加新的 logger
3. 为不同环境配置不同日志等级

## 故障排查

### 常见问题

1. **导入错误**：请确认所有依赖已正确安装
2. **API 密钥问题**：确认 OpenAI API 密钥已设置
3. **WebSocket 连接失败**：检查服务器是否在正确端口运行
4. **日志不输出**：确认 `LOG_LEVEL` 环境变量设置是否正确

### 调试模式

若需详细调试信息，可启用 DEBUG 日志：

```bash
LOG_LEVEL=DEBUG python server.py
```

该模式将输出以下详细信息：

* 节点执行流程
* LLM 调用及返回值
* WebSocket 通信信息
* 错误细节和堆栈信息

## 🤝 贡献须知

1. 遵循 PocketFlow 的设计模式
2. 补充完整文档
3. 包含异常处理与日志记录
4. 结合多种用户场景进行测试
5. 更新节点注册器支持新功能

## 📝 许可协议

本项目遵循与 PocketFlow 相同的开源许可协议。

## 🔗 相关文档

- [主项目 README](../README.md) - ObiAgent 项目整体概览
- [智能体文档](agent/README.md) - 详细的智能体实现文档
- [依赖清单](requirements.txt) - Python 依赖包
- [服务器实现](server.py) - FastAPI 服务器代码

---

**注意**：本系统为演示版本，外部服务如订票、支付等为模拟实现。若用于生产环境，请接入真实 API 服务。
