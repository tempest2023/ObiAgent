# Workflow Demo - Google Arcade Node Examples

This directory contains simple demo workflows that showcase various Google Arcade Node capabilities using PocketFlow framework.

## Overview

These demos demonstrate how to use Google Arcade nodes to interact with different platforms through authenticated APIs:
- Gmail (send emails, read inbox, search emails)
- Slack (send messages, get channels, upload files)
- X/Twitter (post tweets, get user profiles, like tweets)
- LinkedIn (post updates, get profiles, send messages)
- Discord (send messages, get channels, create channels)

## Prerequisites

1. **Environment Setup**:
   ```bash
   export ARCADE_API_KEY=your_arcade_api_key_here
   ```

2. **Dependencies**: All required packages are already listed in `requirements.txt`

## Demo Workflows

### 1. Simple Email Workflow (`simple_email_demo.py`)
- **Purpose**: Demonstrate basic Gmail operations
- **Features**: Send email, read inbox, search emails
- **Use Case**: Automated email notifications

### 2. Social Media Workflow (`social_media_demo.py`)
- **Purpose**: Multi-platform social media posting
- **Features**: Post to Twitter, LinkedIn, and share via email
- **Use Case**: Content distribution across platforms

### 3. Team Communication Workflow (`team_communication_demo.py`)
- **Purpose**: Coordinate team communications
- **Features**: Send Slack messages, Gmail notifications, Discord updates
- **Use Case**: Project status updates and notifications

### 4. Customer Support Workflow (`customer_support_demo.py`)
- **Purpose**: Handle customer inquiries across channels
- **Features**: Monitor emails, respond via appropriate channels
- **Use Case**: Multi-channel customer service

### 5. Content Research Workflow (`content_research_demo.py`)
- **Purpose**: Research and content gathering
- **Features**: Search emails, gather social media insights
- **Use Case**: Market research and content preparation

## Running the Demos

### Basic Usage
```bash
cd backend/workflow_demo
python simple_email_demo.py
```

### Interactive Mode
```bash
cd backend
python server.py
# Then navigate to the web interface and select a demo workflow
```

### Demo Mode (No Authentication Required)
```bash
cd backend/workflow_demo
python simple_email_demo.py --demo
```

## Authentication Flow

1. **First Run**: Each demo will check authentication status
2. **If Required**: You'll get an authorization URL to complete OAuth
3. **Subsequent Runs**: Uses cached credentials automatically

## Demo Structure

Each demo follows the PocketFlow agentic coding pattern:

```python
# 1. Flow Design - High-level workflow structure
# 2. Utilities - Platform-specific function nodes
# 3. Node Design - Individual task handlers
# 4. Implementation - Complete workflow execution
```

## Customization

To create your own workflow:

1. **Copy a demo**: Start with the closest example
2. **Modify nodes**: Adjust parameters and logic
3. **Update flow**: Change the node connections
4. **Test**: Run with `--demo` flag first

## Error Handling

- All demos include comprehensive error handling
- Authorization errors are handled gracefully
- Rate limiting is respected automatically
- Retry logic is built-in for transient failures

## Best Practices

1. **Start Simple**: Begin with single-platform workflows
2. **Test Incrementally**: Use demo mode for testing
3. **Handle Auth**: Always check authentication status
4. **Respect Limits**: Be mindful of API rate limits
5. **Log Everything**: Use proper logging for debugging

## Support

- Check the main [README_ARCADE.md](../agent/README_ARCADE.md) for detailed API documentation
- Review individual function node implementations in [function_nodes/](../agent/function_nodes/)
- Test individual nodes using the test suite in [test/](../agent/test/)

## Contributing

When adding new demo workflows:

1. Follow the existing naming convention
2. Include comprehensive documentation
3. Add error handling and logging
4. Test both demo and live modes
5. Update this README with your new demo