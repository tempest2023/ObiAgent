# Arcade.dev Integration Guide

This document provides comprehensive documentation for the Arcade.dev platform integration in the PocketFlow agent system. Arcade.dev is an AI tool-calling platform that enables secure, authenticated access to various platforms like Gmail, Slack, X (Twitter), LinkedIn, Discord, and more.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Platform Support](#platform-support)
4. [Usage Examples](#usage-examples)
5. [Authentication](#authentication)
6. [Error Handling](#error-handling)
7. [Best Practices](#best-practices)
8. [API Reference](#api-reference)

## Overview

The Arcade integration provides a unified interface for AI agents to interact with external platforms through authenticated APIs. Instead of managing OAuth flows and API integrations separately for each platform, Arcade handles:

- **OAuth Authentication**: Simplified authentication flows for all supported platforms
- **API Abstraction**: Consistent interface across different platform APIs
- **Security**: Secure token management and API access
- **Rate Limiting**: Built-in rate limiting and error handling

## Architecture

The integration follows a three-layer architecture:

```
┌─────────────────────────────────────────┐
│           Function Nodes                │
│  (Gmail, Slack, X, LinkedIn, Discord)   │
├─────────────────────────────────────────┤
│          Arcade Client Utility          │
│     (Common API calling logic)          │
├─────────────────────────────────────────┤
│           Arcade.dev Platform           │
│      (Authentication & API Proxy)       │
└─────────────────────────────────────────┘
```

### Key Components

1. **ArcadeClient**: Central utility class for making API calls
2. **Function Nodes**: Platform-specific nodes implementing PocketFlow patterns
3. **Error Handling**: Comprehensive error handling and logging
4. **Configuration**: JSON metadata for all function nodes

## Platform Support

### Gmail (Google)
- **Send Email**: Send emails with attachments, CC, BCC
- **Read Emails**: Retrieve emails with filtering options
- **Search Emails**: Advanced email search with Gmail operators
- **Authentication**: OAuth2 with Gmail scopes

### Slack
- **Send Messages**: Send messages to channels, DMs, threads
- **Get Channels**: Retrieve workspace channels
- **Get Messages**: Read channel message history
- **Upload Files**: Upload files to channels
- **Authentication**: OAuth2 with Slack workspace permissions

### X (Twitter)
- **Post Tweets**: Create tweets with media, replies, quotes
- **Get Tweets**: Retrieve timeline, mentions, user tweets
- **Get User Profile**: Access user profile information
- **Like Tweets**: Like/unlike tweets
- **Authentication**: OAuth2 with X API v2 permissions

### LinkedIn
- **Post Updates**: Share professional content
- **Get Profile**: Retrieve user profile data
- **Send Messages**: Direct messaging with connections
- **Get Connections**: Access connection lists
- **Authentication**: OAuth2 with LinkedIn professional permissions

### Discord
- **Send Messages**: Send messages with embeds to channels
- **Get Channels**: Retrieve server channel lists
- **Get Messages**: Read channel message history
- **Create Channels**: Create new text/voice channels
- **Authentication**: OAuth2 with Discord bot permissions

## Usage Examples

### Sending an Email via Gmail

```python
from agent.function_nodes.gmail_arcade import GmailSendEmailNode

# Create the node
email_node = GmailSendEmailNode()

# Prepare shared data
shared = {
    "user_id": "user123",
    "recipient": "colleague@company.com",
    "subject": "Project Update",
    "body": "Hi! Here's the latest update on our project...",
    "cc": ["manager@company.com"],
    "bcc": ["archive@company.com"],
    "attachments": ["/path/to/report.pdf"]
}

# Execute the node
result = email_node.run(shared)

# Check results
print(f"Email sent: {shared['gmail_send_result']}")
```

### Posting to Slack

```python
from agent.function_nodes.slack_arcade import SlackSendMessageNode

slack_node = SlackSendMessageNode()

shared = {
    "user_id": "user123",
    "channel": "#team-updates",
    "message": "🚀 Deployment completed successfully!",
    "thread_ts": None  # Optional: reply to existing thread
}

result = slack_node.run(shared)
print(f"Message sent: {shared['slack_send_result']}")
```

### Posting a Tweet

```python
from agent.function_nodes.x_arcade import XPostTweetNode

tweet_node = XPostTweetNode()

shared = {
    "user_id": "user123",
    "text": "Excited to share our new AI agent capabilities! 🤖 #AI #Innovation",
    "reply_to": None,  # Optional: tweet ID to reply to
    "media_ids": []    # Optional: media attachments
}

result = tweet_node.run(shared)
print(f"Tweet posted: {shared['x_post_result']}")
```

### LinkedIn Professional Update

```python
from agent.function_nodes.linkedin_arcade import LinkedInPostUpdateNode

linkedin_node = LinkedInPostUpdateNode()

shared = {
    "user_id": "user123",
    "text": "Thrilled to announce the launch of our AI-powered automation platform! 🚀",
    "visibility": "PUBLIC",  # PUBLIC, CONNECTIONS, LOGGED_IN
    "media_url": "https://company.com/product-image.jpg"
}

result = linkedin_node.run(shared)
print(f"LinkedIn post created: {shared['linkedin_post_result']}")
```

### Discord Community Engagement

```python
from agent.function_nodes.discord_arcade import DiscordSendMessageNode

discord_node = DiscordSendMessageNode()

shared = {
    "user_id": "user123",
    "channel_id": "1234567890123456789",
    "message": "Welcome to our community! 🎮",
    "embed": {
        "title": "Welcome!",
        "description": "Thanks for joining our Discord server",
        "color": 0x00ff00
    }
}

result = discord_node.run(shared)
print(f"Discord message sent: {shared['discord_send_result']}")
```

## Authentication

### Initial Setup

All platforms require initial authentication through Arcade's OAuth flow:

```python
from agent.function_nodes.gmail_arcade import GmailAuthNode

auth_node = GmailAuthNode()

shared = {
    "user_id": "user123",
    "scopes": [
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.readonly"
    ]
}

result = auth_node.run(shared)

if shared["gmail_auth_status"]["status"] == "requires_auth":
    print(f"Please visit: {shared['gmail_auth_status']['auth_url']}")
else:
    print("Authentication successful!")
```

### Authentication Flow

1. **Check Existing Auth**: Each node checks if user is already authenticated
2. **Start OAuth Flow**: If not authenticated, initiate OAuth with platform
3. **User Authorization**: User visits authorization URL and grants permissions
4. **Token Storage**: Arcade securely stores and manages access tokens
5. **Automatic Refresh**: Tokens are automatically refreshed as needed

### Platform-Specific Scopes

#### Gmail Scopes
- `gmail.send`: Send emails
- `gmail.readonly`: Read emails
- `gmail.modify`: Modify emails (mark as read, etc.)

#### Slack Scopes
- `chat:write`: Send messages
- `channels:read`: Read channel information
- `files:write`: Upload files
- `users:read`: Read user information

#### X Scopes
- `tweet.read`: Read tweets
- `tweet.write`: Post tweets
- `users.read`: Read user profiles
- `like.write`: Like/unlike tweets

#### LinkedIn Scopes
- `r_liteprofile`: Read basic profile
- `w_member_social`: Post updates
- `r_emailaddress`: Access email address

#### Discord Scopes
- `bot`: Basic bot permissions
- `messages.read`: Read messages
- `messages.write`: Send messages
- `channels.read`: View channels

## Error Handling

The integration includes comprehensive error handling:

### Error Types

```python
from agent.utils.arcade_client import ArcadeClientError, ArcadeAuthError, ArcadeAPIError

try:
    result = call_arcade_tool(user_id, platform, action, parameters)
except ArcadeAuthError as e:
    print(f"Authentication error: {e}")
    # Handle re-authentication
except ArcadeAPIError as e:
    print(f"API error: {e}")
    # Handle API-specific errors
except ArcadeClientError as e:
    print(f"General Arcade error: {e}")
    # Handle general errors
```

### Common Error Scenarios

1. **Authentication Expired**: Token needs refresh
2. **Rate Limiting**: Too many requests
3. **Invalid Parameters**: Malformed request data
4. **Platform Errors**: Specific platform API errors
5. **Network Issues**: Connectivity problems

### Retry Logic

Nodes include built-in retry logic for transient errors:

```python
# Example with retry configuration
node = GmailSendEmailNode(max_retries=3, wait=5)
```

## Best Practices

### 1. User ID Management

Always use consistent, unique user IDs across your application:

```python
# Good: Use persistent user identifiers
user_id = f"user_{database_user_id}"

# Avoid: Using temporary or session-based IDs
user_id = f"session_{session_id}"
```

### 2. Error Handling

Implement proper error handling for all operations:

```python
def send_email_safely(shared_data):
    try:
        node = GmailSendEmailNode()
        return node.run(shared_data)
    except ValueError as e:
        logger.error(f"Invalid parameters: {e}")
        return {"error": "Invalid email parameters"}
    except RuntimeError as e:
        logger.error(f"Email sending failed: {e}")
        return {"error": "Failed to send email"}
```

### 3. Rate Limiting

Respect platform rate limits:

```python
import time

def send_multiple_emails(email_list):
    for email_data in email_list:
        send_email(email_data)
        time.sleep(1)  # Avoid rate limiting
```

### 4. Data Validation

Validate input data before making API calls:

```python
def validate_email_data(shared):
    required_fields = ["user_id", "recipient", "subject", "body"]
    for field in required_fields:
        if not shared.get(field):
            raise ValueError(f"Missing required field: {field}")
    
    # Validate email format
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, shared["recipient"]):
        raise ValueError("Invalid email format")
```

### 5. Logging

Use structured logging for debugging:

```python
import logging

logger = logging.getLogger(__name__)

def execute_with_logging(node, shared):
    logger.info(f"Executing {node.__class__.__name__} for user {shared.get('user_id')}")
    try:
        result = node.run(shared)
        logger.info(f"Success: {node.__class__.__name__} completed")
        return result
    except Exception as e:
        logger.error(f"Error in {node.__class__.__name__}: {e}")
        raise
```

## API Reference

### ArcadeClient

Main client class for interacting with Arcade platform.

#### Methods

##### `__init__(api_key: Optional[str] = None)`
Initialize the Arcade client.

**Parameters:**
- `api_key`: Arcade API key (optional, uses ARCADE_API_KEY env var if not provided)

##### `start_auth(user_id: str, platform: str, scopes: Optional[List[str]] = None) -> ArcadeAuthResponse`
Start OAuth authorization process.

**Parameters:**
- `user_id`: Unique user identifier
- `platform`: Platform name (gmail, slack, x, linkedin, discord)
- `scopes`: List of OAuth scopes to request

**Returns:**
- `ArcadeAuthResponse`: Authentication response with status and URL

##### `make_tool_call(tool_call: ArcadeToolCall) -> str`
Execute a tool call through Arcade platform.

**Parameters:**
- `tool_call`: ArcadeToolCall object with tool name, parameters, and user ID

**Returns:**
- `str`: Response from the tool call

##### `is_user_authenticated(user_id: str, platform: str) -> bool`
Check if user is authenticated for a platform.

**Parameters:**
- `user_id`: User identifier
- `platform`: Platform name

**Returns:**
- `bool`: True if authenticated, False otherwise

### Convenience Functions

##### `call_arcade_tool(user_id: str, platform: str, action: str, parameters: Dict[str, Any]) -> str`
Simplified function for making tool calls.

**Parameters:**
- `user_id`: User identifier
- `platform`: Platform name
- `action`: Action to perform
- `parameters`: Action parameters

**Returns:**
- `str`: Result from the tool call

### Data Classes

#### ArcadeAuthResponse
```python
@dataclass
class ArcadeAuthResponse:
    status: str
    url: Optional[str] = None
    token: Optional[str] = None
    user_id: Optional[str] = None
```

#### ArcadeToolCall
```python
@dataclass
class ArcadeToolCall:
    tool_name: str
    parameters: Dict[str, Any]
    user_id: str
```

### Exception Classes

#### ArcadeClientError
Base exception for all Arcade client errors.

#### ArcadeAuthError
Authentication-related errors.

#### ArcadeAPIError
API call-related errors.

## Node Configuration

All Arcade nodes are registered in `function_nodes.json` with metadata:

```json
{
  "gmail_send_email": {
    "name": "gmail_send_email",
    "description": "Send emails via Gmail using Arcade API",
    "category": "communication",
    "permission_level": "high",
    "inputs": ["user_id", "recipient", "subject", "body"],
    "outputs": ["gmail_send_result"],
    "estimated_cost": 0.01,
    "estimated_time": 5,
    "module_path": "agent.function_nodes.gmail_arcade",
    "class_name": "GmailSendEmailNode"
  }
}
```

## Testing

The integration includes comprehensive unit tests:

```bash
# Run all Arcade node tests
python -m pytest backend/agent/test/test_arcade_nodes.py

# Run specific platform tests
python -m pytest backend/agent/test/test_arcade_nodes.py::TestGmailArcadeNodes

# Run with coverage
python -m pytest backend/agent/test/test_arcade_nodes.py --cov=agent.function_nodes
```

## Environment Variables

Required environment variables:

```bash
# Arcade API key (required)
ARCADE_API_KEY=your_arcade_api_key_here

# Optional: Custom Arcade API base URL
ARCADE_API_BASE_URL=https://api.arcade-ai.com
```

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Check API key is correctly set
   - Verify user has completed OAuth flow
   - Check platform-specific scope requirements

2. **Rate Limiting**
   - Implement exponential backoff
   - Reduce request frequency
   - Use batch operations where possible

3. **Parameter Errors**
   - Validate all required parameters
   - Check parameter types and formats
   - Review platform-specific requirements

4. **Network Issues**
   - Implement retry logic
   - Check firewall/proxy settings
   - Verify internet connectivity

### Debug Logging

Enable debug logging for detailed troubleshooting:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('agent.utils.arcade_client')
logger.setLevel(logging.DEBUG)
```

### Support

For additional support:
- Review Arcade.dev documentation: https://docs.arcade.dev
- Check GitHub issues and discussions
- Contact platform support for API-specific issues

---

*This documentation covers the comprehensive Arcade.dev integration for the PocketFlow agent system. For the latest updates and features, refer to the official Arcade.dev documentation and release notes.*