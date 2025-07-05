"""
Arcade API Client Utility

This module provides a centralized client for interacting with the Arcade.dev platform,
which offers authenticated integrations for various platforms like Gmail, Slack, X, LinkedIn, etc.

The client handles authentication, API calls, and common error handling for Arcade tools.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import httpx
import asyncio
from openai import OpenAI

logger = logging.getLogger(__name__)

@dataclass
class ArcadeAuthResponse:
    """Response from Arcade authentication flow"""
    status: str
    url: Optional[str] = None
    token: Optional[str] = None
    user_id: Optional[str] = None

@dataclass
class ArcadeToolCall:
    """Represents a tool call to Arcade platform"""
    tool_name: str
    parameters: Dict[str, Any]
    user_id: str

class ArcadeClientError(Exception):
    """Base exception for Arcade client errors"""
    pass

class ArcadeAuthError(ArcadeClientError):
    """Authentication related errors"""
    pass

class ArcadeAPIError(ArcadeClientError):
    """API call related errors"""
    pass

class ArcadeClient:
    """
    Client for interacting with Arcade.dev platform
    
    Provides methods for:
    - User authentication via OAuth
    - Making tool calls to various platforms
    - Managing user sessions
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Arcade client
        
        Args:
            api_key: Arcade API key. If not provided, will try to get from ARCADE_API_KEY env var
        """
        self.api_key = api_key or os.environ.get("ARCADE_API_KEY")
        if not self.api_key:
            raise ArcadeClientError("ARCADE_API_KEY environment variable or api_key parameter is required")
        
        self.base_url = "https://api.arcade-ai.com"
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
        
        # Platform-specific tool mappings
        self.platform_tools = {
            "gmail": {
                "send_email": "Google.SendEmail",
                "read_emails": "Google.ReadEmails", 
                "search_emails": "Google.SearchEmails",
                "get_email": "Google.GetEmail"
            },
            "outlook": {
                "send_email": "Microsoft.SendEmail",
                "read_emails": "Microsoft.ReadEmails",
                "search_emails": "Microsoft.SearchEmails"
            },
            "slack": {
                "send_message": "Slack.SendMessage",
                "get_channels": "Slack.GetChannels",
                "get_messages": "Slack.GetMessages",
                "upload_file": "Slack.UploadFile"
            },
            "x": {
                "post_tweet": "X.PostTweet",
                "get_tweets": "X.GetTweets",
                "get_user_profile": "X.GetUserProfile",
                "like_tweet": "X.LikeTweet"
            },
            "linkedin": {
                "post_update": "LinkedIn.PostUpdate",
                "get_profile": "LinkedIn.GetProfile", 
                "send_message": "LinkedIn.SendMessage",
                "get_connections": "LinkedIn.GetConnections"
            },
            "discord": {
                "send_message": "Discord.SendMessage",
                "get_channels": "Discord.GetChannels",
                "get_messages": "Discord.GetMessages",
                "create_channel": "Discord.CreateChannel"
            }
        }
        
        logger.info("🎮 ArcadeClient initialized successfully")

    def start_auth(self, user_id: str, platform: str, scopes: Optional[List[str]] = None) -> ArcadeAuthResponse:
        """
        Start OAuth authorization process for a platform
        
        Args:
            user_id: Unique identifier for the user
            platform: Platform name (e.g., 'google', 'slack', 'x')
            scopes: List of OAuth scopes to request
            
        Returns:
            ArcadeAuthResponse with auth status and URL if needed
        """
        try:
            logger.info(f"🔐 Starting auth for user {user_id} on platform {platform}")
            
            # For now, simulate the auth response based on Arcade's pattern
            # In real implementation, this would call Arcade's auth API
            auth_response = ArcadeAuthResponse(
                status="requires_auth",
                url=f"{self.base_url}/auth/{platform}?user_id={user_id}",
                user_id=user_id
            )
            
            logger.info(f"✅ Auth started for {platform}. Status: {auth_response.status}")
            return auth_response
            
        except Exception as e:
            logger.error(f"❌ Failed to start auth for {platform}: {e}")
            raise ArcadeAuthError(f"Authentication failed for {platform}: {e}")

    def wait_for_auth_completion(self, auth_response: ArcadeAuthResponse, timeout: int = 300) -> ArcadeAuthResponse:
        """
        Wait for OAuth completion (polling-based)
        
        Args:
            auth_response: Initial auth response
            timeout: Maximum time to wait in seconds
            
        Returns:
            Updated ArcadeAuthResponse with token if successful
        """
        logger.info(f"⏳ Waiting for auth completion for user {auth_response.user_id}")
        
        # For demo purposes, simulate successful auth
        # In real implementation, this would poll Arcade's auth status endpoint
        import time
        time.sleep(2)  # Simulate waiting
        
        auth_response.status = "completed"
        auth_response.token = f"arcade_token_{auth_response.user_id}"
        
        logger.info("✅ Authentication completed successfully")
        return auth_response

    def make_tool_call(self, tool_call: ArcadeToolCall) -> str:
        """
        Make a tool call through Arcade platform
        
        Args:
            tool_call: ArcadeToolCall with tool name, parameters, and user ID
            
        Returns:
            Response from the tool call
        """
        try:
            logger.info(f"🔧 Making tool call: {tool_call.tool_name} for user {tool_call.user_id}")
            
            # Create the prompt based on the tool call
            prompt = self._create_tool_prompt(tool_call)
            
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4o-mini",
                user=tool_call.user_id,
                tools=[tool_call.tool_name],
                tool_choice="auto",
            )
            
            result = response.choices[0].message.content
            logger.info(f"✅ Tool call completed successfully")
            logger.debug(f"📄 Tool call result: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Tool call failed: {e}")
            raise ArcadeAPIError(f"Tool call failed: {e}")

    def _create_tool_prompt(self, tool_call: ArcadeToolCall) -> str:
        """
        Create a natural language prompt for the tool call
        
        Args:
            tool_call: ArcadeToolCall to convert to prompt
            
        Returns:
            Natural language prompt string
        """
        platform = self._extract_platform_from_tool(tool_call.tool_name)
        action = self._extract_action_from_tool(tool_call.tool_name)
        
        # Build prompt based on platform and action
        if platform == "google" and action == "sendemail":
            return f"Send an email to {tool_call.parameters.get('recipient')} with subject '{tool_call.parameters.get('subject')}' and body '{tool_call.parameters.get('body')}'"
        
        elif platform == "slack" and action == "sendmessage":
            return f"Send a Slack message to {tool_call.parameters.get('channel')} saying: {tool_call.parameters.get('message')}"
        
        elif platform == "x" and action == "posttweet":
            return f"Post a tweet with the text: {tool_call.parameters.get('text')}"
        
        elif platform == "linkedin" and action == "postupdate":
            return f"Post a LinkedIn update with the text: {tool_call.parameters.get('text')}"
        
        elif platform == "discord" and action == "sendmessage":
            return f"Send a Discord message to {tool_call.parameters.get('channel')} saying: {tool_call.parameters.get('message')}"
        
        # Default generic prompt
        return f"Use {tool_call.tool_name} with parameters: {tool_call.parameters}"

    def _extract_platform_from_tool(self, tool_name: str) -> str:
        """Extract platform name from tool name (e.g., 'Google.SendEmail' -> 'google')"""
        return tool_name.split('.')[0].lower()

    def _extract_action_from_tool(self, tool_name: str) -> str:
        """Extract action from tool name (e.g., 'Google.SendEmail' -> 'sendemail')"""
        return tool_name.split('.')[1].lower()

    def get_available_tools(self, platform: str) -> Dict[str, str]:
        """
        Get available tools for a platform
        
        Args:
            platform: Platform name
            
        Returns:
            Dictionary mapping action names to tool names
        """
        return self.platform_tools.get(platform.lower(), {})

    def is_user_authenticated(self, user_id: str, platform: str) -> bool:
        """
        Check if user is authenticated for a platform
        
        Args:
            user_id: User identifier
            platform: Platform name
            
        Returns:
            True if authenticated, False otherwise
        """
        # For demo purposes, assume users are authenticated
        # In real implementation, this would check with Arcade's auth status
        logger.info(f"🔍 Checking auth status for user {user_id} on {platform}")
        return True

def call_arcade_tool(user_id: str, platform: str, action: str, parameters: Dict[str, Any]) -> str:
    """
    Convenience function for making Arcade tool calls
    
    Args:
        user_id: User identifier
        platform: Platform name (gmail, slack, x, linkedin, discord)
        action: Action to perform (send_email, post_tweet, etc.)
        parameters: Action parameters
        
    Returns:
        Result from the tool call
    """
    client = ArcadeClient()
    
    # Get the tool name for this platform/action
    available_tools = client.get_available_tools(platform)
    tool_name = available_tools.get(action)
    
    if not tool_name:
        raise ValueError(f"Action '{action}' not available for platform '{platform}'. Available actions: {list(available_tools.keys())}")
    
    # Create and execute tool call
    tool_call = ArcadeToolCall(
        tool_name=tool_name,
        parameters=parameters,
        user_id=user_id
    )
    
    return client.make_tool_call(tool_call)

# Example usage functions for testing
if __name__ == "__main__":
    # Example: Send an email via Gmail
    try:
        result = call_arcade_tool(
            user_id="test_user",
            platform="gmail",
            action="send_email",
            parameters={
                "recipient": "test@example.com",
                "subject": "Test Email",
                "body": "This is a test email sent via Arcade"
            }
        )
        print(f"Email sent: {result}")
    except Exception as e:
        print(f"Error: {e}")