# Workflow Demo Summary

本目录所有演示均基于 PocketFlow + Google Arcade function_nodes 真实 API 调用，无任何 mock/demo 节点。

## 运行须知

- **必须设置 ARCADE_API_KEY**，否则 demo 会自动跳过。
- **所有 demo 只用 function_nodes 真实节点**，如依赖缺失会输出 "Lack xxx nodes to run"。
- **不再支持 demo mode**，所有流程均为真实 API 交互。

## Demo 列表与节点依赖

### 1. Simple Email Demo (`simple_email_demo.py`)
- **功能**：Gmail 认证、发邮件、读邮件、查邮件
- **节点**：GmailAuthNode, GmailSendEmailNode, GmailReadEmailsNode, GmailSearchEmailsNode

### 2. Social Media Demo (`social_media_demo.py`)
- **功能**：发推文、发 LinkedIn、邮件通知
- **节点**：XPostTweetNode, LinkedInPostUpdateNode, GmailSendEmailNode

### 3. Team Communication Demo (`team_communication_demo.py`)
- **功能**：Slack 通知、Gmail 通知、Discord 通知
- **节点**：SlackSendMessageNode, GmailSendEmailNode, DiscordSendMessageNode

### 4. Customer Support Demo (`customer_support_demo.py`)
- **功能**：读取客户邮件、自动回复、Slack 通知
- **节点**：GmailReadEmailsNode, GmailSendEmailNode, SlackSendMessageNode

### 5. Content Research Demo (`content_research_demo.py`)
- **功能**：Web 搜索、结果总结
- **节点**：WebSearchNode, ResultSummarizerNode

## 运行方式

```bash
cd backend/workflow_demo
python run_demos.py
```

- 每个 demo 会自动检查 ARCADE_API_KEY，缺失则跳过。
- 若缺少 function_node，控制台会输出 "Lack xxx nodes to run"。

## 设计原则

- 所有流程均为真实 API 调用，便于生产环境集成和测试。
- 推荐直接复用 function_nodes 真实节点进行自定义开发。

---
*本目录所有演示均为 PocketFlow + Google Arcade function_nodes 真实 API 调用范例*