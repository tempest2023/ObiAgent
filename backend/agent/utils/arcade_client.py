"""
Arcade.dev API Client

This module provides a client for interacting with the Arcade.dev platform,
enabling authenticated access to various platforms like Gmail, Slack, X, LinkedIn, Discord.
"""

import os
import json
from typing import Dict, Any, Optional, List
import logging
import httpx

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
    Client for interacting with the Arcade.dev API
    
    Provides methods for authentication, tool calling, and platform-specific operations.
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.arcade.dev"):
        """
        Initialize the Arcade client
        
        Args:
            api_key: Arcade API key (defaults to ARCADE_API_KEY environment variable)
            base_url: Base URL for the Arcade API
        """
        self.api_key = api_key or os.getenv("ARCADE_API_KEY")
        if not self.api_key:
            raise ArcadeAuthError("Arcade API key is required. Set ARCADE_API_KEY environment variable or pass api_key parameter.")
        
        self.base_url = base_url.rstrip('/')
        self.session_headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'PocketFlow-Agent/1.0'
        }
        
        # Platform-specific tool mappings
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
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make an HTTP request to the Arcade API using httpx
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            logger.debug(f"Making {method} request to {url}")
            if method.upper() == "GET":
                response = httpx.get(url, headers=self.session_headers, timeout=30)
            else:
                response = httpx.request(method.upper(), url, headers=self.session_headers, json=data, timeout=30)
            response.raise_for_status()
            if response.text:
                return response.json()
            return {}
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error in Arcade API request: {e.response.status_code} - {e.response.text}")
            raise ArcadeAPIError(f"HTTP {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"URL error in Arcade API request: {e}")
            raise ArcadeAPIError(f"Network error: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in Arcade API response: {e}")
            raise ArcadeAPIError(f"Invalid JSON response: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in Arcade API request: {e}")
            raise ArcadeAPIError(f"Unexpected error: {e}")
    
    def call_tool(self, tool_name: str, user_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a specific Arcade tool
        
        Args:
            tool_name: Name of the tool to call
            user_id: User ID for authentication context
            parameters: Tool-specific parameters
            
        Returns:
            Tool execution result
            
        Raises:
            ArcadeAPIError: If the tool call fails
        """
        payload = {
            'tool_name': tool_name,
            'user_id': user_id,
            'parameters': parameters
        }
        
        logger.info(f"Calling Arcade tool: {tool_name} for user {user_id}")
        logger.debug(f"Tool parameters: {parameters}")
        
        try:
            response = self._make_request('POST', '/v1/tools/execute', payload)
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
        Authenticate a user with a specific platform
        
        Args:
            user_id: User ID
            platform: Platform to authenticate with
            scopes: Required scopes/permissions
            
        Returns:
            Authentication result
        """
        tool_name = self.get_platform_tool_name(platform, 'auth')
        parameters = {
            'scopes': scopes
        }
        
        return self.call_tool(tool_name, user_id, parameters)
    
    def get_oauth_url(self, user_id: str, platform: str, scopes: List[str], redirect_uri: str) -> str:
        """
        Get OAuth authorization URL for a platform
        
        Args:
            user_id: User ID
            platform: Platform name
            scopes: Required scopes
            redirect_uri: OAuth redirect URI
            
        Returns:
            OAuth authorization URL
        """
        payload = {
            'user_id': user_id,
            'platform': platform,
            'scopes': scopes,
            'redirect_uri': redirect_uri
        }
        
        response = self._make_request('POST', '/v1/oauth/authorize', payload)
        return response.get('authorization_url', '')
    
    def handle_oauth_callback(self, user_id: str, platform: str, code: str, state: str) -> Dict[str, Any]:
        """
        Handle OAuth callback and exchange code for tokens
        
        Args:
            user_id: User ID
            platform: Platform name
            code: OAuth authorization code
            state: OAuth state parameter
            
        Returns:
            Token exchange result
        """
        payload = {
            'user_id': user_id,
            'platform': platform,
            'code': code,
            'state': state
        }
        
        return self._make_request('POST', '/v1/oauth/callback', payload)


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