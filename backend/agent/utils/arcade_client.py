"""
Arcade.dev API Client

This module provides a client for interacting with the Arcade.dev platform,
enabling authenticated access to various platforms like Gmail, Slack, X, LinkedIn, Discord.
"""

import os
import json
from typing import Dict, Any, Optional, List
import logging
from arcadepy import Arcade

logger = logging.getLogger(__name__)

class ArcadeClientError(Exception):
    """Base exception for Arcade client errors"""
    pass

class ArcadeAuthError(ArcadeClientError):
    """Authentication-related errors"""
    pass

class ArcadeAPIError(ArcadeClientError):
    """API-related errors"""
    pass

class ArcadeClient:
    """
    Client for interacting with the Arcade.dev API using the official Arcade SDK (arcadepy)
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ARCADE_API_KEY")
        if not self.api_key:
            raise ArcadeAuthError("Arcade API key is required. Set ARCADE_API_KEY environment variable or pass api_key parameter.")
        self.client = Arcade(api_key=self.api_key)
        # Platform-specific tool mappings (for legacy compatibility)
        self.platform_tools = {
            'gmail': {
                'send_email': 'gmail_send_email',
                'read_emails': 'gmail_read_emails', 
                'search_emails': 'gmail_search_emails',
                'auth': 'gmail_auth'
            },
            'slack': {
                'send_message': 'slack_send_message',
                'get_channels': 'slack_get_channels',
                'get_messages': 'slack_get_messages',
                'upload_file': 'slack_upload_file',
                'auth': 'slack_auth'
            },
            'x': {
                'post_tweet': 'x_post_tweet',
                'get_tweets': 'x_get_tweets',
                'get_user_profile': 'x_get_user_profile',
                'like_tweet': 'x_like_tweet',
                'auth': 'x_auth'
            },
            'linkedin': {
                'post_update': 'linkedin_post_update',
                'get_profile': 'linkedin_get_profile',
                'send_message': 'linkedin_send_message',
                'get_connections': 'linkedin_get_connections',
                'auth': 'linkedin_auth'
            },
            'discord': {
                'send_message': 'discord_send_message',
                'get_channels': 'discord_get_channels',
                'get_messages': 'discord_get_messages',
                'create_channel': 'discord_create_channel',
                'auth': 'discord_auth'
            }
        }
    
    # All HTTP logic is now handled by the Arcade SDK
    
    def call_tool(self, tool_name: str, user_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a specific Arcade tool using the official SDK
        """
        logger.info(f"Calling Arcade tool: {tool_name} for user {user_id}")
        logger.debug(f"Tool parameters: {parameters}")
        try:
            # Use the Arcade SDK's tool execution method
            response = self.client.tools.execute(
                tool_name=tool_name,
                user_id=user_id,
                parameters=parameters
            )
            logger.info(f"Tool {tool_name} executed successfully")
            return response
        except Exception as e:
            logger.error(f"Failed to call tool {tool_name}: {e}")
            raise
    
    def get_platform_tool_name(self, platform: str, action: str) -> str:
        """
        Get the full tool name for a platform action
        
        Args:
            platform: Platform name (gmail, slack, x, linkedin, discord)
            action: Action name (send_message, read_emails, etc.)
            
        Returns:
            Full tool name for Arcade API
            
        Raises:
            ValueError: If platform or action is not supported
        """
        if platform not in self.platform_tools:
            raise ValueError(f"Unsupported platform: {platform}")
        
        if action not in self.platform_tools[platform]:
            raise ValueError(f"Unsupported action '{action}' for platform '{platform}'")
        
        return self.platform_tools[platform][action]
    
    def authenticate_user(self, user_id: str, platform: str, scopes: List[str]) -> Dict[str, Any]:
        """
        Authenticate a user with a specific platform using the Arcade SDK
        """
        tool_name = self.get_platform_tool_name(platform, 'auth')
        parameters = {'scopes': scopes}
        return self.call_tool(tool_name, user_id, parameters)

    def get_oauth_url(self, user_id: str, platform: str, scopes: List[str], redirect_uri: str) -> str:
        """
        Get OAuth authorization URL for a platform using the Arcade SDK
        """
        # The Arcade SDK may provide a direct method for this; if not, use a tool call
        tool_name = self.get_platform_tool_name(platform, 'auth')
        parameters = {'scopes': scopes, 'redirect_uri': redirect_uri}
        response = self.call_tool(tool_name, user_id, parameters)
        return response.get('authorization_url', '')

    def handle_oauth_callback(self, user_id: str, platform: str, code: str, state: str) -> Dict[str, Any]:
        """
        Handle OAuth callback and exchange code for tokens using the Arcade SDK
        """
        # The Arcade SDK may provide a direct method for this; if not, use a tool call
        tool_name = self.get_platform_tool_name(platform, 'auth')
        parameters = {'code': code, 'state': state}
        return self.call_tool(tool_name, user_id, parameters)


def call_arcade_tool(user_id: str, platform: str, action: str, parameters: Dict[str, Any], 
                    api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to call an Arcade tool using platform and action
    
    Args:
        user_id: User ID for authentication context
        platform: Platform name (gmail, slack, x, linkedin, discord)
        action: Action name (send_email, post_tweet, etc.)
        parameters: Tool-specific parameters
        api_key: Optional API key (defaults to environment variable)
        
    Returns:
        Tool execution result
        
    Raises:
        ArcadeClientError: If the tool call fails
    """
    client = ArcadeClient(api_key=api_key)
    
    # Get the tool name from platform and action
    tool_name = client.get_platform_tool_name(platform, action)
    
    return client.call_tool(tool_name, user_id, parameters)


def get_arcade_client(api_key: Optional[str] = None) -> ArcadeClient:
    """
    Get an Arcade client instance
    
    Args:
        api_key: Optional API key (defaults to environment variable)
        
    Returns:
        Configured ArcadeClient instance
    """
    return ArcadeClient(api_key=api_key)


def is_authorization_required(result: dict) -> bool:
    """
    Detect if the Arcade API result indicates authorization is required.
    """
    if not isinstance(result, dict):
        return False
    # Arcade convention: look for 'authorization_required' or specific error codes/messages
    if result.get("authorization_required"):
        return True
    if "auth_url" in result or "authorization_url" in result:
        return True
    if result.get("error") and ("auth" in result["error"].lower() or "authorize" in result["error"].lower()):
        return True
    return False

def is_authorization_required_exception(exc: Exception) -> bool:
    """
    Detect if an exception is due to authorization required (ArcadeAuthError or similar).
    """
    if hasattr(exc, "__class__") and exc.__class__.__name__ == "ArcadeAuthError":
        return True
    msg = str(exc).lower()
    if "auth" in msg or "authorize" in msg or "token" in msg:
        return True
    return False

# Example usage and testing
if __name__ == "__main__":
    # Example usage
    try:
        client = ArcadeClient()
        
        # Example: Send a Gmail email
        result = client.call_tool(
            tool_name='gmail_send_email',
            user_id='test_user',
            parameters={
                'recipient': 'test@example.com',
                'subject': 'Test Email',
                'body': 'This is a test email from Arcade API'
            }
        )
        print("Gmail send result:", result)
        
    except ArcadeClientError as e:
        print(f"Arcade client error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")