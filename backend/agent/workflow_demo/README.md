# Workflow Demo - Google Arcade Node Examples

本目录包含基于 PocketFlow 框架的 Google Arcade function_nodes 真实 API 调用演示。

## 重要说明

- **所有 demo 均为真实 API 调用**，不再包含任何 mock/demo/fake 节点。
- **运行前必须设置 ARCADE_API_KEY**，否则 demo 会自动跳过。
- **每个 demo 只用 function_nodes 真实节点**，如依赖缺失会输出 "Lack xxx nodes to run"。
- **不再支持 demo mode**，所有流程均为真实 API 交互。

## 依赖环境

1. **环境变量**：
   ```bash
   export ARCADE_API_KEY=your_arcade_api_key_here
   ```
2. **依赖包**：见项目 requirements.txt

## Demo Workflows

### 1. Simple Email Workflow (`simple_email_demo.py`)
- **功能**：Gmail 认证、发邮件、读邮件、查邮件
- **节点**：GmailAuthNode, GmailSendEmailNode, GmailReadEmailsNode, GmailSearchEmailsNode

### 2. Social Media Workflow (`social_media_demo.py`)
- **功能**：发推文、发 LinkedIn、邮件通知
- **节点**：XPostTweetNode, LinkedInPostUpdateNode, GmailSendEmailNode

### 3. Team Communication Workflow (`team_communication_demo.py`)
- **功能**：Slack 通知、Gmail 通知、Discord 通知
- **节点**：SlackSendMessageNode, GmailSendEmailNode, DiscordSendMessageNode

### 4. Customer Support Workflow (`customer_support_demo.py`)
- **功能**：读取客户邮件、自动回复、Slack 通知
- **节点**：GmailReadEmailsNode, GmailSendEmailNode, SlackSendMessageNode

### 5. Content Research Workflow (`content_research_demo.py`)
- **功能**：Web 搜索、结果总结
- **节点**：WebSearchNode, ResultSummarizerNode

## 运行方式

```bash
cd backend/workflow_demo
python run_demos.py
```

- 每个 demo 会自动检查 ARCADE_API_KEY，缺失则跳过。
- 若缺少 function_node，控制台会输出 "Lack xxx nodes to run"。

## 扩展与支持

- 参考 [function_nodes/](../agent/function_nodes/) 了解所有可用节点。
- 如需自定义流程，建议直接复用 function_nodes 真实节点。
- 详细 API 文档见主项目 README。