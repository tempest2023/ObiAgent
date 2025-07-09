"""
Slack Arcade Function Node

This module provides Slack functionality through the Arcade.dev platform,
enabling authenticated access to Slack operations like sending messages,
managing channels, and file uploads.
"""

from pocketflow import Node
from typing import Dict, Any, Optional, List
import logging
from agent.utils.arcade_client import call_arcade_tool, ArcadeClient, ArcadeClientError

logger = logging.getLogger(__name__)

class SlackSendMessageNode(Node):
    """
    Node to send messages to Slack channels using Arcade API
    
    Sends messages to Slack channels, DMs, or group messages through
    authenticated Slack access via Arcade platform.
    
    Example:
        >>> node = SlackSendMessageNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "channel": "#general",
        ...     "message": "Hello team! 👋",
        ...     "thread_ts": None  # Optional: reply to thread
        ... }
        >>> node.run(shared)
    """
    
    def prep(self, shared: Dict[str, Any]):
        """
        Prepare message data for sending
        
        Args:
            shared: Contains message parameters
            
        Returns:
            Tuple of (user_id, message_params)
        """
        user_id = shared.get("user_id")
        if not user_id:
            logger.error("❌ SlackSendMessageNode: No user_id provided")
            raise ValueError("user_id is required for Slack operations")
        
        message_params = {
            "channel": shared.get("channel"),
            "message": shared.get("message", shared.get("text", "")),
            "thread_ts": shared.get("thread_ts"),
            "attachments": shared.get("attachments", []),
            "blocks": shared.get("blocks", []),
            "as_user": shared.get("as_user", True),
            "icon_emoji": shared.get("icon_emoji"),
            "username": shared.get("username")
        }
        
        # Validate required fields
        if not message_params["channel"]:
            logger.error("❌ SlackSendMessageNode: No channel provided")
            raise ValueError("channel is required for sending Slack message")
        
        if not message_params["message"]:
            logger.error("❌ SlackSendMessageNode: No message provided")
            raise ValueError("message is required for sending Slack message")
        
        logger.info(f"💬 SlackSendMessageNode: prep - sending to {message_params['channel']}")
        return user_id, message_params
    
    def exec(self, inputs):
        user_id, message_params = inputs
        try:
            logger.info(f"\ud83d\udce4 SlackSendMessageNode: Sending message via Arcade")
            result = call_arcade_tool(
                user_id=user_id,
                platform="slack",
                action="send_message",
                parameters=message_params
            )
            from agent.utils.arcade_client import is_authorization_required
            if is_authorization_required(result):
                return {"authorization_required": True, **result}
            logger.info(f"\u2705 SlackSendMessageNode: Message sent successfully")
            return result
        except ArcadeClientError as e:
            from agent.utils.arcade_client import is_authorization_required_exception
            if is_authorization_required_exception(e):
                return {"authorization_required": True, "error": str(e), "url": getattr(e, "url", None)}
            logger.error(f"\u274c SlackSendMessageNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to send Slack message via Arcade: {e}")
        except Exception as e:
            logger.error(f"\u274c SlackSendMessageNode: Unexpected error: {e}")
            raise RuntimeError(f"Slack message sending failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        from agent.utils.arcade_client import is_authorization_required
        if is_authorization_required(exec_res):
            shared["arcade_auth_url"] = exec_res.get("url")
            shared["arcade_auth_message"] = exec_res.get("message", exec_res.get("error", "Authorization required for Slack."))
            return "wait_for_authorization"
        logger.info("\ud83d\udcbe SlackSendMessageNode: Storing message result")
        shared["slack_send_result"] = exec_res
        shared["last_slack_message"] = {
            "channel": prep_res[1]["channel"],
            "message": prep_res[1]["message"],
            "result": exec_res
        }
        return "default"

class SlackGetChannelsNode(Node):
    """
    Node to retrieve Slack channels using Arcade API
    
    Gets list of channels that the user has access to, including
    public channels, private channels, and DMs.
    
    Example:
        >>> node = SlackGetChannelsNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "types": ["public_channel", "private_channel"],
        ...     "exclude_archived": True
        ... }
        >>> node.run(shared)
    """
    
    def prep(self, shared: Dict[str, Any]):
        """
        Prepare parameters for getting channels
        
        Args:
            shared: Contains channel query parameters
            
        Returns:
            Tuple of (user_id, channel_params)
        """
        user_id = shared.get("user_id")
        if not user_id:
            logger.error("❌ SlackGetChannelsNode: No user_id provided")
            raise ValueError("user_id is required for Slack operations")
        
        channel_params = {
            "types": shared.get("types", ["public_channel", "private_channel"]),
            "exclude_archived": shared.get("exclude_archived", True),
            "limit": shared.get("limit", 100),
            "exclude_members": shared.get("exclude_members", False)
        }
        
        logger.info(f"📋 SlackGetChannelsNode: prep - getting channels")
        return user_id, channel_params
    
    def exec(self, inputs):
        """
        Execute channel retrieval via Arcade Slack API
        
        Args:
            inputs: Tuple of (user_id, channel_params)
            
        Returns:
            List of channels from Slack API via Arcade
        """
        user_id, channel_params = inputs
        
        try:
            logger.info(f"📥 SlackGetChannelsNode: Getting channels via Arcade")
            
            result = call_arcade_tool(
                user_id=user_id,
                platform="slack",
                action="get_channels",
                parameters=channel_params
            )
            
            logger.info(f"✅ SlackGetChannelsNode: Retrieved channels successfully")
            return result
            
        except ArcadeClientError as e:
            logger.error(f"❌ SlackGetChannelsNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to get Slack channels via Arcade: {e}")
        except Exception as e:
            logger.error(f"❌ SlackGetChannelsNode: Unexpected error: {e}")
            raise RuntimeError(f"Slack channel retrieval failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """
        Store channel list result
        
        Args:
            shared: Shared data store
            prep_res: Result from prep method
            exec_res: Result from exec method
        """
        logger.info("💾 SlackGetChannelsNode: Storing channels")
        shared["slack_channels"] = exec_res
        shared["slack_channel_count"] = len(exec_res) if isinstance(exec_res, list) else 1
        return "default"

class SlackGetMessagesNode(Node):
    """
    Node to retrieve messages from Slack channels using Arcade API
    
    Gets messages from a specific channel with optional filtering
    by date range, user, or message type.
    
    Example:
        >>> node = SlackGetMessagesNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "channel": "#general",
        ...     "count": 50,
        ...     "latest": "1234567890.123456"
        ... }
        >>> node.run(shared)
    """
    
    def prep(self, shared: Dict[str, Any]):
        """
        Prepare parameters for getting messages
        
        Args:
            shared: Contains message query parameters
            
        Returns:
            Tuple of (user_id, message_params)
        """
        user_id = shared.get("user_id")
        if not user_id:
            logger.error("❌ SlackGetMessagesNode: No user_id provided")
            raise ValueError("user_id is required for Slack operations")
        
        message_params = {
            "channel": shared.get("channel"),
            "count": shared.get("count", 50),
            "latest": shared.get("latest"),
            "oldest": shared.get("oldest"),
            "inclusive": shared.get("inclusive", False),
            "unreads": shared.get("unreads", False)
        }
        
        if not message_params["channel"]:
            logger.error("❌ SlackGetMessagesNode: No channel provided")
            raise ValueError("channel is required for getting Slack messages")
        
        logger.info(f"📬 SlackGetMessagesNode: prep - getting messages from {message_params['channel']}")
        return user_id, message_params
    
    def exec(self, inputs):
        """
        Execute message retrieval via Arcade Slack API
        
        Args:
            inputs: Tuple of (user_id, message_params)
            
        Returns:
            List of messages from Slack API via Arcade
        """
        user_id, message_params = inputs
        
        try:
            logger.info(f"📥 SlackGetMessagesNode: Getting messages via Arcade")
            
            result = call_arcade_tool(
                user_id=user_id,
                platform="slack",
                action="get_messages",
                parameters=message_params
            )
            
            logger.info(f"✅ SlackGetMessagesNode: Retrieved messages successfully")
            return result
            
        except ArcadeClientError as e:
            logger.error(f"❌ SlackGetMessagesNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to get Slack messages via Arcade: {e}")
        except Exception as e:
            logger.error(f"❌ SlackGetMessagesNode: Unexpected error: {e}")
            raise RuntimeError(f"Slack message retrieval failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """
        Store messages result
        
        Args:
            shared: Shared data store
            prep_res: Result from prep method
            exec_res: Result from exec method
        """
        logger.info("💾 SlackGetMessagesNode: Storing messages")
        shared["slack_messages"] = exec_res
        shared["last_message_check"] = {
            "channel": prep_res[1]["channel"],
            "count": len(exec_res) if isinstance(exec_res, list) else 1
        }
        return "default"

class SlackUploadFileNode(Node):
    """
    Node to upload files to Slack using Arcade API
    
    Uploads files to Slack channels with optional comments and
    sharing settings.
    
    Example:
        >>> node = SlackUploadFileNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "file_path": "/path/to/file.pdf",
        ...     "channels": ["#general"],
        ...     "title": "Project Report",
        ...     "initial_comment": "Here's the latest report"
        ... }
        >>> node.run(shared)
    """
    
    def prep(self, shared: Dict[str, Any]):
        """
        Prepare parameters for file upload
        
        Args:
            shared: Contains file upload parameters
            
        Returns:
            Tuple of (user_id, upload_params)
        """
        user_id = shared.get("user_id")
        if not user_id:
            logger.error("❌ SlackUploadFileNode: No user_id provided")
            raise ValueError("user_id is required for Slack operations")
        
        upload_params = {
            "file_path": shared.get("file_path"),
            "file_content": shared.get("file_content"),
            "filename": shared.get("filename"),
            "title": shared.get("title"),
            "channels": shared.get("channels", []),
            "initial_comment": shared.get("initial_comment"),
            "filetype": shared.get("filetype"),
            "thread_ts": shared.get("thread_ts")
        }
        
        # Validate required fields
        if not upload_params["file_path"] and not upload_params["file_content"]:
            logger.error("❌ SlackUploadFileNode: No file_path or file_content provided")
            raise ValueError("Either file_path or file_content is required for file upload")
        
        logger.info(f"📎 SlackUploadFileNode: prep - uploading file")
        return user_id, upload_params
    
    def exec(self, inputs):
        """
        Execute file upload via Arcade Slack API
        
        Args:
            inputs: Tuple of (user_id, upload_params)
            
        Returns:
            Upload result from Slack API via Arcade
        """
        user_id, upload_params = inputs
        
        try:
            logger.info(f"📤 SlackUploadFileNode: Uploading file via Arcade")
            
            result = call_arcade_tool(
                user_id=user_id,
                platform="slack",
                action="upload_file",
                parameters=upload_params
            )
            
            logger.info(f"✅ SlackUploadFileNode: File uploaded successfully")
            return result
            
        except ArcadeClientError as e:
            logger.error(f"❌ SlackUploadFileNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to upload file to Slack via Arcade: {e}")
        except Exception as e:
            logger.error(f"❌ SlackUploadFileNode: Unexpected error: {e}")
            raise RuntimeError(f"Slack file upload failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """
        Store upload result
        
        Args:
            shared: Shared data store
            prep_res: Result from prep method
            exec_res: Result from exec method
        """
        logger.info("💾 SlackUploadFileNode: Storing upload result")
        shared["slack_upload_result"] = exec_res
        shared["last_file_upload"] = {
            "filename": prep_res[1].get("filename"),
            "channels": prep_res[1].get("channels"),
            "result": exec_res
        }
        return "default"

class SlackAuthNode(Node):
    """
    Node to handle Slack authentication via Arcade
    
    Manages the OAuth flow for Slack access through Arcade platform.
    Handles workspace authentication and scope management.
    
    Example:
        >>> node = SlackAuthNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "scopes": ["chat:write", "channels:read"]
        ... }
        >>> node.run(shared)
    """
    
    def prep(self, shared: Dict[str, Any]):
        """
        Prepare authentication parameters
        
        Args:
            shared: Contains user_id and optional scopes
            
        Returns:
            Tuple of (user_id, auth_params)
        """
        user_id = shared.get("user_id")
        if not user_id:
            logger.error("❌ SlackAuthNode: No user_id provided")
            raise ValueError("user_id is required for Slack authentication")
        
        auth_params = {
            "scopes": shared.get("scopes", [
                "chat:write",
                "channels:read",
                "groups:read",
                "im:read",
                "files:write",
                "users:read"
            ])
        }
        
        logger.info(f"🔐 SlackAuthNode: prep - authenticating user {user_id}")
        return user_id, auth_params
    
    def exec(self, inputs):
        """
        Execute Slack authentication via Arcade
        
        Args:
            inputs: Tuple of (user_id, auth_params)
            
        Returns:
            Authentication result from Arcade
        """
        user_id, auth_params = inputs
        
        try:
            logger.info(f"🔑 SlackAuthNode: Starting Slack auth via Arcade")
            
            client = ArcadeClient()
            
            # Check if already authenticated
            if client.is_user_authenticated(user_id, "slack"):
                logger.info(f"✅ SlackAuthNode: User already authenticated")
                return {"status": "already_authenticated", "user_id": user_id}
            
            # Start authentication flow
            auth_response = client.start_auth(
                user_id=user_id,
                platform="slack",
                scopes=auth_params["scopes"]
            )
            
            # If authentication is required, wait for completion
            if auth_response.status == "requires_auth":
                logger.info(f"🔗 SlackAuthNode: Auth URL: {auth_response.url}")
                auth_response = client.wait_for_auth_completion(auth_response)
            
            logger.info(f"✅ SlackAuthNode: Authentication completed")
            return {
                "status": auth_response.status,
                "user_id": user_id,
                "auth_url": auth_response.url
            }
            
        except ArcadeClientError as e:
            logger.error(f"❌ SlackAuthNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to authenticate with Slack via Arcade: {e}")
        except Exception as e:
            logger.error(f"❌ SlackAuthNode: Unexpected error: {e}")
            raise RuntimeError(f"Slack authentication failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """
        Store authentication result
        
        Args:
            shared: Shared data store
            prep_res: Result from prep method
            exec_res: Result from exec method
        """
        logger.info("💾 SlackAuthNode: Storing auth result")
        shared["slack_auth_status"] = exec_res
        shared["slack_authenticated"] = exec_res.get("status") in ["completed", "already_authenticated"]
        return "default"