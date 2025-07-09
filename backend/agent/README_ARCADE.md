# Arcade.dev Integration for PocketFlow Agent

This directory contains a comprehensive integration with the Arcade.dev platform, enabling AI agents to securely interact with various platforms including Gmail, Slack, X (Twitter), LinkedIn, and Discord through authenticated APIs.

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Set your Arcade API key
export ARCADE_API_KEY=your_arcade_api_key_here

# Install dependencies (if not already installed)
pip install -r requirements.txt
```

### 2. Basic Usage

```python
from agent.function_nodes.gmail_arcade import GmailSendEmailNode

# Create and run a Gmail node
email_node = GmailSendEmailNode()
shared = {
    "user_id": "user123",
    "recipient": "example@company.com",
    "subject": "Hello from AI Agent!",
    "body": "This email was sent automatically by our AI agent."
}

result = email_node.run(shared)
print(f"Email sent: {shared['gmail_send_result']}")
```

## 📁 Directory Structure

```
agent/
├── function_nodes/           # Platform-specific function nodes
│   ├── gmail_arcade.py      # Gmail operations (send, read, search, auth)
│   ├── slack_arcade.py      # Slack operations (messages, channels, files, auth)
│   ├── x_arcade.py          # X/Twitter operations (tweets, profiles, likes, auth)
│   ├── linkedin_arcade.py   # LinkedIn operations (posts, profile, messages, auth)
│   └── discord_arcade.py    # Discord operations (messages, channels, auth)
├── utils/
│   └── arcade_client.py     # Central Arcade API client utility
├── config/
│   └── function_nodes.json  # Node metadata and configuration
├── test/
│   └── test_arcade_nodes.py # Comprehensive unit tests
└── docs/
    └── arcade_integration.md # Detailed documentation
```

## 🎯 Supported Platforms

| Platform | Send | Read | Search | Manage | Auth |
|----------|------|------|--------|---------|------|
| **Gmail** | ✅ Send emails | ✅ Read inbox | ✅ Search emails | ✅ Manage labels | ✅ OAuth2 |
| **Slack** | ✅ Send messages | ✅ Read channels | ✅ Get messages | ✅ Upload files | ✅ OAuth2 |
| **X (Twitter)** | ✅ Post tweets | ✅ Read timeline | ✅ Get profiles | ✅ Like tweets | ✅ OAuth2 |
| **LinkedIn** | ✅ Post updates | ✅ Read profiles | ✅ Send messages | ✅ Get connections | ✅ OAuth2 |
| **Discord** | ✅ Send messages | ✅ Read channels | ✅ Get messages | ✅ Create channels | ✅ OAuth2 |

## 🔧 Available Function Nodes

### Gmail Nodes
- `GmailSendEmailNode`: Send emails with attachments, CC, BCC
- `GmailReadEmailsNode`: Read emails with filtering options
- `GmailSearchEmailsNode`: Advanced email search with Gmail operators
- `GmailAuthNode`: Handle Gmail OAuth authentication

### Slack Nodes
- `SlackSendMessageNode`: Send messages to channels, DMs, threads
- `SlackGetChannelsNode`: Retrieve workspace channels
- `SlackGetMessagesNode`: Get messages from channels
- `SlackUploadFileNode`: Upload files to Slack
- `SlackAuthNode`: Handle Slack workspace authentication

### X (Twitter) Nodes
- `XPostTweetNode`: Post tweets with media, replies, quotes
- `XGetTweetsNode`: Retrieve timeline, mentions, user tweets
- `XGetUserProfileNode`: Get user profile information
- `XLikeTweetNode`: Like/unlike tweets
- `XAuthNode`: Handle X API v2 authentication

### LinkedIn Nodes
- `LinkedInPostUpdateNode`: Post professional updates
- `LinkedInGetProfileNode`: Retrieve profile information
- `LinkedInSendMessageNode`: Send direct messages
- `LinkedInGetConnectionsNode`: Get connections list
- `LinkedInAuthNode`: Handle LinkedIn professional authentication

### Discord Nodes
- `DiscordSendMessageNode`: Send messages with embeds
- `DiscordGetChannelsNode`: Retrieve server channels
- `DiscordGetMessagesNode`: Get channel messages
- `DiscordCreateChannelNode`: Create new channels
- `DiscordAuthNode`: Handle Discord bot authentication

## 🔐 Authentication Flow

All platforms use OAuth2 through Arcade's secure authentication system:

1. **Check Authentication Status**
   ```python
   from agent.function_nodes.gmail_arcade import GmailAuthNode
   
   auth_node = GmailAuthNode()
   shared = {"user_id": "user123"}
   result = auth_node.run(shared)
   ```

2. **Handle Authentication URL** (if required)
   ```python
   if shared["gmail_auth_status"]["status"] == "requires_auth":
       print(f"Please visit: {shared['gmail_auth_status']['auth_url']}")
   ```

3. **Use Authenticated Nodes**
   ```python
   # Once authenticated, all platform nodes work seamlessly
   email_node = GmailSendEmailNode()
   result = email_node.run(shared)
   ```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all Arcade tests
python -m pytest agent/test/test_arcade_nodes.py -v

# Run tests for specific platform
python -m pytest agent/test/test_arcade_nodes.py::TestGmailArcadeNodes -v

# Run with coverage
python -m pytest agent/test/test_arcade_nodes.py --cov=agent.function_nodes --cov-report=html
```

## 📊 Node Configuration

All nodes are registered in `config/function_nodes.json` with metadata:

```json
{
  "gmail_send_email": {
    "description": "Send emails via Gmail using Arcade API",
    "category": "communication",
    "permission_level": "high",
    "inputs": ["user_id", "recipient", "subject", "body"],
    "outputs": ["gmail_send_result"],
    "estimated_cost": 0.01,
    "estimated_time": 5
  }
}
```

## 🛠 Usage Examples

### Multi-Platform Workflow

```python
from agent.function_nodes.gmail_arcade import GmailSendEmailNode
from agent.function_nodes.slack_arcade import SlackSendMessageNode
from agent.function_nodes.x_arcade import XPostTweetNode

def notify_team_about_deployment():
    shared = {"user_id": "deployment_bot"}
    
    # Send email notification
    email_node = GmailSendEmailNode()
    shared.update({
        "recipient": "team@company.com",
        "subject": "Deployment Completed",
        "body": "The latest deployment has been completed successfully."
    })
    email_node.run(shared)
    
    # Notify on Slack
    slack_node = SlackSendMessageNode()
    shared.update({
        "channel": "#deployments",
        "message": "🚀 Deployment completed successfully!"
    })
    slack_node.run(shared)
    
    # Tweet about it
    tweet_node = XPostTweetNode()
    shared.update({
        "text": "Just deployed our latest features! 🎉 #TechUpdate"
    })
    tweet_node.run(shared)

notify_team_about_deployment()
```

### Error Handling Best Practices

```python
import logging
from agent.utils.arcade_client import ArcadeClientError

logger = logging.getLogger(__name__)

def safe_email_send(email_data):
    try:
        node = GmailSendEmailNode()
        result = node.run(email_data)
        logger.info(f"Email sent successfully to {email_data['recipient']}")
        return {"success": True, "result": result}
        
    except ValueError as e:
        logger.error(f"Invalid email parameters: {e}")
        return {"success": False, "error": "Invalid parameters"}
        
    except ArcadeClientError as e:
        logger.error(f"Arcade API error: {e}")
        return {"success": False, "error": "API communication failed"}
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"success": False, "error": "Unknown error occurred"}
```

## 🔍 Debugging

Enable detailed logging for troubleshooting:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('agent.utils.arcade_client')
logger.setLevel(logging.DEBUG)

# Run your nodes with detailed logging
node = GmailSendEmailNode()
result = node.run(shared)
```

## 📖 Documentation

- **[Complete Integration Guide](docs/arcade_integration.md)**: Comprehensive documentation with examples, best practices, and API reference
- **[Function Node Tests](test/test_arcade_nodes.py)**: Unit tests demonstrating usage patterns
- **[Arcade Client Utility](utils/arcade_client.py)**: Core client implementation with inline documentation

## ⚡ Performance Considerations

- **Rate Limiting**: All nodes respect platform rate limits automatically
- **Retries**: Built-in retry logic for transient failures
- **Caching**: Authentication tokens are cached and auto-refreshed
- **Async Support**: Nodes can be used with PocketFlow's async capabilities

## 🚨 Important Notes

1. **API Keys**: Always set `ARCADE_API_KEY` environment variable
2. **User IDs**: Use consistent, unique user identifiers across sessions
3. **Permissions**: Each platform requires specific OAuth scopes
4. **Rate Limits**: Respect platform-specific rate limiting
5. **Error Handling**: Always implement proper error handling for production use

## 🤝 Contributing

When adding new platform support:

1. Create new function node file in `function_nodes/`
2. Add platform support to `arcade_client.py`
3. Update `function_nodes.json` with metadata
4. Add comprehensive unit tests
5. Update documentation

## 📞 Support

- **Arcade.dev Documentation**: https://docs.arcade.dev
- **PocketFlow Documentation**: Check main project README
- **Issues**: Report bugs and feature requests in the main repository

---

*This integration provides a production-ready solution for AI agents to interact with multiple platforms through secure, authenticated APIs. All components follow enterprise software development best practices with comprehensive testing, error handling, and documentation.*