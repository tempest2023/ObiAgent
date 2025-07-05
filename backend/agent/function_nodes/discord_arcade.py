"""
Discord Arcade Function Node

This module provides Discord functionality through the Arcade.dev platform,
enabling authenticated access to Discord operations like sending messages,
managing servers, and interacting with communities.
"""

from pocketflow import Node
from typing import Dict, Any, Optional, List
import logging
from agent.utils.arcade_client import call_arcade_tool, ArcadeClient, ArcadeClientError

logger = logging.getLogger(__name__)

class DiscordSendMessageNode(Node):
    """
    Node to send messages to Discord channels using Arcade API
    
    Sends messages to Discord text channels with support for embeds,
    reactions, and rich formatting.
    
    Example:
        >>> node = DiscordSendMessageNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "channel_id": "1234567890123456789",
        ...     "message": "Hello Discord! 🎮",
        ...     "embed": {"title": "Bot Update", "description": "New features available!"}
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
            logger.error("❌ DiscordSendMessageNode: No user_id provided")
            raise ValueError("user_id is required for Discord operations")
        
        message_params = {
            "channel_id": shared.get("channel_id", shared.get("channel")),
            "message": shared.get("message", shared.get("content", "")),
            "embed": shared.get("embed"),
            "embeds": shared.get("embeds", []),
            "components": shared.get("components", []),
            "files": shared.get("files", []),
            "tts": shared.get("tts", False),
            "allowed_mentions": shared.get("allowed_mentions"),
            "message_reference": shared.get("message_reference")  # For replies
        }
        
        # Validate required fields
        if not message_params["channel_id"]:
            logger.error("❌ DiscordSendMessageNode: No channel_id provided")
            raise ValueError("channel_id is required for sending Discord message")
        
        if not message_params["message"] and not message_params["embed"] and not message_params["embeds"] and not message_params["files"]:
            logger.error("❌ DiscordSendMessageNode: No content provided")
            raise ValueError("Either message, embed, embeds, or files is required")
        
        logger.info(f"🎮 DiscordSendMessageNode: prep - sending to channel {message_params['channel_id']}")
        return user_id, message_params
    
    def exec(self, inputs):
        """
        Execute message sending via Arcade Discord API
        
        Args:
            inputs: Tuple of (user_id, message_params)
            
        Returns:
            Response from Discord API via Arcade
        """
        user_id, message_params = inputs
        
        try:
            logger.info(f"📤 DiscordSendMessageNode: Sending message via Arcade")
            
            result = call_arcade_tool(
                user_id=user_id,
                platform="discord",
                action="send_message",
                parameters=message_params
            )
            
            logger.info(f"✅ DiscordSendMessageNode: Message sent successfully")
            return result
            
        except ArcadeClientError as e:
            logger.error(f"❌ DiscordSendMessageNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to send Discord message via Arcade: {e}")
        except Exception as e:
            logger.error(f"❌ DiscordSendMessageNode: Unexpected error: {e}")
            raise RuntimeError(f"Discord message sending failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """
        Store message sending result
        
        Args:
            shared: Shared data store
            prep_res: Result from prep method
            exec_res: Result from exec method
        """
        logger.info("💾 DiscordSendMessageNode: Storing message result")
        shared["discord_send_result"] = exec_res
        shared["last_discord_message"] = {
            "channel_id": prep_res[1]["channel_id"],
            "message": prep_res[1]["message"],
            "result": exec_res
        }
        return "default"

class DiscordGetChannelsNode(Node):
    """
    Node to retrieve Discord channels using Arcade API
    
    Gets list of channels from a Discord server with optional
    filtering by channel type and permissions.
    
    Example:
        >>> node = DiscordGetChannelsNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "guild_id": "1234567890123456789",
        ...     "channel_types": ["text", "voice"]
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
            logger.error("❌ DiscordGetChannelsNode: No user_id provided")
            raise ValueError("user_id is required for Discord operations")
        
        channel_params = {
            "guild_id": shared.get("guild_id", shared.get("server_id")),
            "channel_types": shared.get("channel_types", ["text", "voice", "category"]),
            "include_private": shared.get("include_private", False),
            "include_threads": shared.get("include_threads", False)
        }
        
        # guild_id is optional for DM channels
        logger.info(f"📋 DiscordGetChannelsNode: prep - getting channels")
        return user_id, channel_params
    
    def exec(self, inputs):
        """
        Execute channel retrieval via Arcade Discord API
        
        Args:
            inputs: Tuple of (user_id, channel_params)
            
        Returns:
            List of channels from Discord API via Arcade
        """
        user_id, channel_params = inputs
        
        try:
            logger.info(f"📥 DiscordGetChannelsNode: Getting channels via Arcade")
            
            result = call_arcade_tool(
                user_id=user_id,
                platform="discord",
                action="get_channels",
                parameters=channel_params
            )
            
            logger.info(f"✅ DiscordGetChannelsNode: Retrieved channels successfully")
            return result
            
        except ArcadeClientError as e:
            logger.error(f"❌ DiscordGetChannelsNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to get Discord channels via Arcade: {e}")
        except Exception as e:
            logger.error(f"❌ DiscordGetChannelsNode: Unexpected error: {e}")
            raise RuntimeError(f"Discord channel retrieval failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """
        Store channels result
        
        Args:
            shared: Shared data store
            prep_res: Result from prep method
            exec_res: Result from exec method
        """
        logger.info("💾 DiscordGetChannelsNode: Storing channels")
        shared["discord_channels"] = exec_res
        shared["discord_channel_count"] = len(exec_res) if isinstance(exec_res, list) else 1
        return "default"

class DiscordGetMessagesNode(Node):
    """
    Node to retrieve messages from Discord channels using Arcade API
    
    Gets messages from a specific channel with optional filtering
    by date range, author, or message type.
    
    Example:
        >>> node = DiscordGetMessagesNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "channel_id": "1234567890123456789",
        ...     "limit": 50,
        ...     "before": "1234567890123456789"
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
            logger.error("❌ DiscordGetMessagesNode: No user_id provided")
            raise ValueError("user_id is required for Discord operations")
        
        message_params = {
            "channel_id": shared.get("channel_id", shared.get("channel")),
            "limit": shared.get("limit", 50),
            "before": shared.get("before"),
            "after": shared.get("after"),
            "around": shared.get("around"),
            "include_pinned": shared.get("include_pinned", False)
        }
        
        if not message_params["channel_id"]:
            logger.error("❌ DiscordGetMessagesNode: No channel_id provided")
            raise ValueError("channel_id is required for getting Discord messages")
        
        logger.info(f"📬 DiscordGetMessagesNode: prep - getting messages from {message_params['channel_id']}")
        return user_id, message_params
    
    def exec(self, inputs):
        """
        Execute message retrieval via Arcade Discord API
        
        Args:
            inputs: Tuple of (user_id, message_params)
            
        Returns:
            List of messages from Discord API via Arcade
        """
        user_id, message_params = inputs
        
        try:
            logger.info(f"📥 DiscordGetMessagesNode: Getting messages via Arcade")
            
            result = call_arcade_tool(
                user_id=user_id,
                platform="discord",
                action="get_messages",
                parameters=message_params
            )
            
            logger.info(f"✅ DiscordGetMessagesNode: Retrieved messages successfully")
            return result
            
        except ArcadeClientError as e:
            logger.error(f"❌ DiscordGetMessagesNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to get Discord messages via Arcade: {e}")
        except Exception as e:
            logger.error(f"❌ DiscordGetMessagesNode: Unexpected error: {e}")
            raise RuntimeError(f"Discord message retrieval failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """
        Store messages result
        
        Args:
            shared: Shared data store
            prep_res: Result from prep method
            exec_res: Result from exec method
        """
        logger.info("💾 DiscordGetMessagesNode: Storing messages")
        shared["discord_messages"] = exec_res
        shared["last_discord_message_check"] = {
            "channel_id": prep_res[1]["channel_id"],
            "count": len(exec_res) if isinstance(exec_res, list) else 1
        }
        return "default"

class DiscordCreateChannelNode(Node):
    """
    Node to create Discord channels using Arcade API
    
    Creates new text or voice channels in a Discord server
    with customizable permissions and settings.
    
    Example:
        >>> node = DiscordCreateChannelNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "guild_id": "1234567890123456789",
        ...     "name": "new-channel",
        ...     "type": "text",  # text, voice, category
        ...     "topic": "Channel for project discussions"
        ... }
        >>> node.run(shared)
    """
    
    def prep(self, shared: Dict[str, Any]):
        """
        Prepare parameters for creating channel
        
        Args:
            shared: Contains channel creation parameters
            
        Returns:
            Tuple of (user_id, create_params)
        """
        user_id = shared.get("user_id")
        if not user_id:
            logger.error("❌ DiscordCreateChannelNode: No user_id provided")
            raise ValueError("user_id is required for Discord operations")
        
        create_params = {
            "guild_id": shared.get("guild_id", shared.get("server_id")),
            "name": shared.get("name"),
            "type": shared.get("type", "text"),  # text, voice, category
            "topic": shared.get("topic"),
            "position": shared.get("position"),
            "permission_overwrites": shared.get("permission_overwrites", []),
            "parent_id": shared.get("parent_id"),  # For channels under a category
            "nsfw": shared.get("nsfw", False),
            "rate_limit_per_user": shared.get("rate_limit_per_user", 0)
        }
        
        # Validate required fields
        if not create_params["guild_id"]:
            logger.error("❌ DiscordCreateChannelNode: No guild_id provided")
            raise ValueError("guild_id is required for creating Discord channel")
        
        if not create_params["name"]:
            logger.error("❌ DiscordCreateChannelNode: No channel name provided")
            raise ValueError("name is required for creating Discord channel")
        
        # Validate channel type
        valid_types = ["text", "voice", "category", "news", "store"]
        if create_params["type"] not in valid_types:
            logger.warning(f"⚠️ DiscordCreateChannelNode: Invalid type '{create_params['type']}', using 'text'")
            create_params["type"] = "text"
        
        logger.info(f"🎮 DiscordCreateChannelNode: prep - creating channel '{create_params['name']}'")
        return user_id, create_params
    
    def exec(self, inputs):
        """
        Execute channel creation via Arcade Discord API
        
        Args:
            inputs: Tuple of (user_id, create_params)
            
        Returns:
            Created channel data from Discord API via Arcade
        """
        user_id, create_params = inputs
        
        try:
            logger.info(f"📤 DiscordCreateChannelNode: Creating channel via Arcade")
            
            result = call_arcade_tool(
                user_id=user_id,
                platform="discord",
                action="create_channel",
                parameters=create_params
            )
            
            logger.info(f"✅ DiscordCreateChannelNode: Channel created successfully")
            return result
            
        except ArcadeClientError as e:
            logger.error(f"❌ DiscordCreateChannelNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to create Discord channel via Arcade: {e}")
        except Exception as e:
            logger.error(f"❌ DiscordCreateChannelNode: Unexpected error: {e}")
            raise RuntimeError(f"Discord channel creation failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """
        Store channel creation result
        
        Args:
            shared: Shared data store
            prep_res: Result from prep method
            exec_res: Result from exec method
        """
        logger.info("💾 DiscordCreateChannelNode: Storing channel creation result")
        shared["discord_create_channel_result"] = exec_res
        shared["last_created_channel"] = {
            "name": prep_res[1]["name"],
            "type": prep_res[1]["type"],
            "guild_id": prep_res[1]["guild_id"],
            "result": exec_res
        }
        return "default"

class DiscordAuthNode(Node):
    """
    Node to handle Discord authentication via Arcade
    
    Manages the OAuth flow for Discord access through Arcade platform.
    Handles bot permissions and scope management for Discord API.
    
    Example:
        >>> node = DiscordAuthNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "scopes": ["bot", "messages.read", "messages.write"]
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
            logger.error("❌ DiscordAuthNode: No user_id provided")
            raise ValueError("user_id is required for Discord authentication")
        
        auth_params = {
            "scopes": shared.get("scopes", [
                "bot",
                "messages.read",
                "messages.write",
                "guilds",
                "channels.read",
                "channels.write"
            ])
        }
        
        logger.info(f"🔐 DiscordAuthNode: prep - authenticating user {user_id}")
        return user_id, auth_params
    
    def exec(self, inputs):
        """
        Execute Discord authentication via Arcade
        
        Args:
            inputs: Tuple of (user_id, auth_params)
            
        Returns:
            Authentication result from Arcade
        """
        user_id, auth_params = inputs
        
        try:
            logger.info(f"🔑 DiscordAuthNode: Starting Discord auth via Arcade")
            
            client = ArcadeClient()
            
            # Check if already authenticated
            if client.is_user_authenticated(user_id, "discord"):
                logger.info(f"✅ DiscordAuthNode: User already authenticated")
                return {"status": "already_authenticated", "user_id": user_id}
            
            # Start authentication flow
            auth_response = client.start_auth(
                user_id=user_id,
                platform="discord",
                scopes=auth_params["scopes"]
            )
            
            # If authentication is required, wait for completion
            if auth_response.status == "requires_auth":
                logger.info(f"🔗 DiscordAuthNode: Auth URL: {auth_response.url}")
                auth_response = client.wait_for_auth_completion(auth_response)
            
            logger.info(f"✅ DiscordAuthNode: Authentication completed")
            return {
                "status": auth_response.status,
                "user_id": user_id,
                "auth_url": auth_response.url
            }
            
        except ArcadeClientError as e:
            logger.error(f"❌ DiscordAuthNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to authenticate with Discord via Arcade: {e}")
        except Exception as e:
            logger.error(f"❌ DiscordAuthNode: Unexpected error: {e}")
            raise RuntimeError(f"Discord authentication failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """
        Store authentication result
        
        Args:
            shared: Shared data store
            prep_res: Result from prep method
            exec_res: Result from exec method
        """
        logger.info("💾 DiscordAuthNode: Storing auth result")
        shared["discord_auth_status"] = exec_res
        shared["discord_authenticated"] = exec_res.get("status") in ["completed", "already_authenticated"]
        return "default"