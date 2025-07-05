"""
LinkedIn Arcade Function Node

This module provides LinkedIn functionality through the Arcade.dev platform,
enabling authenticated access to LinkedIn operations like posting updates,
managing connections, and professional networking.
"""

from pocketflow import Node
from typing import Dict, Any, Optional, List
import logging
from agent.utils.arcade_client import call_arcade_tool, ArcadeClient, ArcadeClientError

logger = logging.getLogger(__name__)

class LinkedInPostUpdateNode(Node):
    """
    Node to post updates to LinkedIn using Arcade API
    
    Posts content to LinkedIn feed with support for text, media,
    articles, and professional updates.
    
    Example:
        >>> node = LinkedInPostUpdateNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "text": "Excited to share my latest project! 🚀",
        ...     "visibility": "PUBLIC",  # PUBLIC, CONNECTIONS, LOGGED_IN
        ...     "media_url": "https://example.com/image.jpg"
        ... }
        >>> node.run(shared)
    """
    
    def prep(self, shared: Dict[str, Any]):
        """
        Prepare update data for posting
        
        Args:
            shared: Contains update parameters
            
        Returns:
            Tuple of (user_id, update_params)
        """
        user_id = shared.get("user_id")
        if not user_id:
            logger.error("❌ LinkedInPostUpdateNode: No user_id provided")
            raise ValueError("user_id is required for LinkedIn operations")
        
        update_params = {
            "text": shared.get("text", shared.get("content", "")),
            "visibility": shared.get("visibility", "PUBLIC"),  # PUBLIC, CONNECTIONS, LOGGED_IN
            "media_url": shared.get("media_url"),
            "media_urls": shared.get("media_urls", []),
            "article_url": shared.get("article_url"),
            "title": shared.get("title"),
            "description": shared.get("description"),
            "hashtags": shared.get("hashtags", [])
        }
        
        # Validate required fields
        if not update_params["text"] and not update_params["media_url"] and not update_params["article_url"]:
            logger.error("❌ LinkedInPostUpdateNode: No content provided")
            raise ValueError("Either text, media_url, or article_url is required for LinkedIn post")
        
        # Validate visibility
        valid_visibility = ["PUBLIC", "CONNECTIONS", "LOGGED_IN"]
        if update_params["visibility"] not in valid_visibility:
            logger.warning(f"⚠️ LinkedInPostUpdateNode: Invalid visibility '{update_params['visibility']}', using PUBLIC")
            update_params["visibility"] = "PUBLIC"
        
        logger.info(f"💼 LinkedInPostUpdateNode: prep - posting update")
        return user_id, update_params
    
    def exec(self, inputs):
        """
        Execute update posting via Arcade LinkedIn API
        
        Args:
            inputs: Tuple of (user_id, update_params)
            
        Returns:
            Response from LinkedIn API via Arcade
        """
        user_id, update_params = inputs
        
        try:
            logger.info(f"📤 LinkedInPostUpdateNode: Posting update via Arcade")
            
            result = call_arcade_tool(
                user_id=user_id,
                platform="linkedin",
                action="post_update",
                parameters=update_params
            )
            
            logger.info(f"✅ LinkedInPostUpdateNode: Update posted successfully")
            return result
            
        except ArcadeClientError as e:
            logger.error(f"❌ LinkedInPostUpdateNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to post LinkedIn update via Arcade: {e}")
        except Exception as e:
            logger.error(f"❌ LinkedInPostUpdateNode: Unexpected error: {e}")
            raise RuntimeError(f"LinkedIn update posting failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """
        Store update posting result
        
        Args:
            shared: Shared data store
            prep_res: Result from prep method
            exec_res: Result from exec method
        """
        logger.info("💾 LinkedInPostUpdateNode: Storing update result")
        shared["linkedin_post_result"] = exec_res
        shared["last_linkedin_post"] = {
            "text": prep_res[1]["text"],
            "visibility": prep_res[1]["visibility"],
            "result": exec_res
        }
        return "default"

class LinkedInGetProfileNode(Node):
    """
    Node to retrieve LinkedIn profile information using Arcade API
    
    Gets detailed profile data including professional experience,
    connections, and contact information.
    
    Example:
        >>> node = LinkedInGetProfileNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "profile_id": None,  # None for own profile, ID for others
        ...     "fields": ["id", "firstName", "lastName", "headline"]
        ... }
        >>> node.run(shared)
    """
    
    def prep(self, shared: Dict[str, Any]):
        """
        Prepare parameters for getting profile
        
        Args:
            shared: Contains profile query parameters
            
        Returns:
            Tuple of (user_id, profile_params)
        """
        user_id = shared.get("user_id")
        if not user_id:
            logger.error("❌ LinkedInGetProfileNode: No user_id provided")
            raise ValueError("user_id is required for LinkedIn operations")
        
        profile_params = {
            "profile_id": shared.get("profile_id"),  # None for own profile
            "fields": shared.get("fields", [
                "id", "firstName", "lastName", "headline", 
                "summary", "industryName", "locationName",
                "numConnections", "pictureUrl"
            ])
        }
        
        target = profile_params["profile_id"] or "own profile"
        logger.info(f"👤 LinkedInGetProfileNode: prep - getting profile for {target}")
        return user_id, profile_params
    
    def exec(self, inputs):
        """
        Execute profile retrieval via Arcade LinkedIn API
        
        Args:
            inputs: Tuple of (user_id, profile_params)
            
        Returns:
            Profile data from LinkedIn API via Arcade
        """
        user_id, profile_params = inputs
        
        try:
            logger.info(f"📥 LinkedInGetProfileNode: Getting profile via Arcade")
            
            result = call_arcade_tool(
                user_id=user_id,
                platform="linkedin",
                action="get_profile",
                parameters=profile_params
            )
            
            logger.info(f"✅ LinkedInGetProfileNode: Retrieved profile successfully")
            return result
            
        except ArcadeClientError as e:
            logger.error(f"❌ LinkedInGetProfileNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to get LinkedIn profile via Arcade: {e}")
        except Exception as e:
            logger.error(f"❌ LinkedInGetProfileNode: Unexpected error: {e}")
            raise RuntimeError(f"LinkedIn profile retrieval failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """
        Store profile result
        
        Args:
            shared: Shared data store
            prep_res: Result from prep method
            exec_res: Result from exec method
        """
        logger.info("💾 LinkedInGetProfileNode: Storing profile")
        shared["linkedin_profile"] = exec_res
        shared["last_profile_check"] = {
            "profile_id": prep_res[1].get("profile_id"),
            "profile_data": exec_res
        }
        return "default"

class LinkedInSendMessageNode(Node):
    """
    Node to send messages on LinkedIn using Arcade API
    
    Sends direct messages to LinkedIn connections with support
    for text content and professional networking.
    
    Example:
        >>> node = LinkedInSendMessageNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "recipient_id": "connection123",
        ...     "message": "Hi! I'd love to connect about your recent post.",
        ...     "subject": "Great post on AI!"
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
            logger.error("❌ LinkedInSendMessageNode: No user_id provided")
            raise ValueError("user_id is required for LinkedIn operations")
        
        message_params = {
            "recipient_id": shared.get("recipient_id"),
            "recipient_ids": shared.get("recipient_ids", []),  # For group messages
            "message": shared.get("message", shared.get("text", "")),
            "subject": shared.get("subject")
        }
        
        # Validate required fields
        if not message_params["recipient_id"] and not message_params["recipient_ids"]:
            logger.error("❌ LinkedInSendMessageNode: No recipient provided")
            raise ValueError("Either recipient_id or recipient_ids is required")
        
        if not message_params["message"]:
            logger.error("❌ LinkedInSendMessageNode: No message provided")
            raise ValueError("message is required for sending LinkedIn message")
        
        logger.info(f"💬 LinkedInSendMessageNode: prep - sending message")
        return user_id, message_params
    
    def exec(self, inputs):
        """
        Execute message sending via Arcade LinkedIn API
        
        Args:
            inputs: Tuple of (user_id, message_params)
            
        Returns:
            Response from LinkedIn API via Arcade
        """
        user_id, message_params = inputs
        
        try:
            logger.info(f"📤 LinkedInSendMessageNode: Sending message via Arcade")
            
            result = call_arcade_tool(
                user_id=user_id,
                platform="linkedin",
                action="send_message",
                parameters=message_params
            )
            
            logger.info(f"✅ LinkedInSendMessageNode: Message sent successfully")
            return result
            
        except ArcadeClientError as e:
            logger.error(f"❌ LinkedInSendMessageNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to send LinkedIn message via Arcade: {e}")
        except Exception as e:
            logger.error(f"❌ LinkedInSendMessageNode: Unexpected error: {e}")
            raise RuntimeError(f"LinkedIn message sending failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """
        Store message sending result
        
        Args:
            shared: Shared data store
            prep_res: Result from prep method
            exec_res: Result from exec method
        """
        logger.info("💾 LinkedInSendMessageNode: Storing message result")
        shared["linkedin_message_result"] = exec_res
        shared["last_linkedin_message"] = {
            "recipient_id": prep_res[1].get("recipient_id"),
            "message": prep_res[1]["message"],
            "result": exec_res
        }
        return "default"

class LinkedInGetConnectionsNode(Node):
    """
    Node to retrieve LinkedIn connections using Arcade API
    
    Gets list of user's connections with optional filtering
    by industry, location, or connection level.
    
    Example:
        >>> node = LinkedInGetConnectionsNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "start": 0,
        ...     "count": 50,
        ...     "fields": ["id", "firstName", "lastName", "headline"]
        ... }
        >>> node.run(shared)
    """
    
    def prep(self, shared: Dict[str, Any]):
        """
        Prepare parameters for getting connections
        
        Args:
            shared: Contains connection query parameters
            
        Returns:
            Tuple of (user_id, connection_params)
        """
        user_id = shared.get("user_id")
        if not user_id:
            logger.error("❌ LinkedInGetConnectionsNode: No user_id provided")
            raise ValueError("user_id is required for LinkedIn operations")
        
        connection_params = {
            "start": shared.get("start", 0),
            "count": shared.get("count", 50),
            "fields": shared.get("fields", [
                "id", "firstName", "lastName", "headline", "industryName"
            ]),
            "modified_since": shared.get("modified_since")
        }
        
        logger.info(f"🤝 LinkedInGetConnectionsNode: prep - getting connections")
        return user_id, connection_params
    
    def exec(self, inputs):
        """
        Execute connections retrieval via Arcade LinkedIn API
        
        Args:
            inputs: Tuple of (user_id, connection_params)
            
        Returns:
            List of connections from LinkedIn API via Arcade
        """
        user_id, connection_params = inputs
        
        try:
            logger.info(f"📥 LinkedInGetConnectionsNode: Getting connections via Arcade")
            
            result = call_arcade_tool(
                user_id=user_id,
                platform="linkedin",
                action="get_connections",
                parameters=connection_params
            )
            
            logger.info(f"✅ LinkedInGetConnectionsNode: Retrieved connections successfully")
            return result
            
        except ArcadeClientError as e:
            logger.error(f"❌ LinkedInGetConnectionsNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to get LinkedIn connections via Arcade: {e}")
        except Exception as e:
            logger.error(f"❌ LinkedInGetConnectionsNode: Unexpected error: {e}")
            raise RuntimeError(f"LinkedIn connections retrieval failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """
        Store connections result
        
        Args:
            shared: Shared data store
            prep_res: Result from prep method
            exec_res: Result from exec method
        """
        logger.info("💾 LinkedInGetConnectionsNode: Storing connections")
        shared["linkedin_connections"] = exec_res
        shared["linkedin_connection_count"] = len(exec_res) if isinstance(exec_res, list) else 1
        return "default"

class LinkedInAuthNode(Node):
    """
    Node to handle LinkedIn authentication via Arcade
    
    Manages the OAuth flow for LinkedIn access through Arcade platform.
    Handles professional networking permissions and scope management.
    
    Example:
        >>> node = LinkedInAuthNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "scopes": ["r_liteprofile", "w_member_social"]
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
            logger.error("❌ LinkedInAuthNode: No user_id provided")
            raise ValueError("user_id is required for LinkedIn authentication")
        
        auth_params = {
            "scopes": shared.get("scopes", [
                "r_liteprofile",
                "r_emailaddress",
                "w_member_social",
                "r_member_social",
                "rw_company_admin"
            ])
        }
        
        logger.info(f"🔐 LinkedInAuthNode: prep - authenticating user {user_id}")
        return user_id, auth_params
    
    def exec(self, inputs):
        """
        Execute LinkedIn authentication via Arcade
        
        Args:
            inputs: Tuple of (user_id, auth_params)
            
        Returns:
            Authentication result from Arcade
        """
        user_id, auth_params = inputs
        
        try:
            logger.info(f"🔑 LinkedInAuthNode: Starting LinkedIn auth via Arcade")
            
            client = ArcadeClient()
            
            # Check if already authenticated
            if client.is_user_authenticated(user_id, "linkedin"):
                logger.info(f"✅ LinkedInAuthNode: User already authenticated")
                return {"status": "already_authenticated", "user_id": user_id}
            
            # Start authentication flow
            auth_response = client.start_auth(
                user_id=user_id,
                platform="linkedin",
                scopes=auth_params["scopes"]
            )
            
            # If authentication is required, wait for completion
            if auth_response.status == "requires_auth":
                logger.info(f"🔗 LinkedInAuthNode: Auth URL: {auth_response.url}")
                auth_response = client.wait_for_auth_completion(auth_response)
            
            logger.info(f"✅ LinkedInAuthNode: Authentication completed")
            return {
                "status": auth_response.status,
                "user_id": user_id,
                "auth_url": auth_response.url
            }
            
        except ArcadeClientError as e:
            logger.error(f"❌ LinkedInAuthNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to authenticate with LinkedIn via Arcade: {e}")
        except Exception as e:
            logger.error(f"❌ LinkedInAuthNode: Unexpected error: {e}")
            raise RuntimeError(f"LinkedIn authentication failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """
        Store authentication result
        
        Args:
            shared: Shared data store
            prep_res: Result from prep method
            exec_res: Result from exec method
        """
        logger.info("💾 LinkedInAuthNode: Storing auth result")
        shared["linkedin_auth_status"] = exec_res
        shared["linkedin_authenticated"] = exec_res.get("status") in ["completed", "already_authenticated"]
        return "default"