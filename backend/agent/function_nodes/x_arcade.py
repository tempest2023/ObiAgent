"""
X (Twitter) Arcade Function Node

This module provides X (formerly Twitter) functionality through the Arcade.dev platform,
enabling authenticated access to X operations like posting tweets, reading timeline,
and managing user interactions.
"""

from pocketflow import Node
from typing import Dict, Any, Optional, List
import logging
from agent.utils.arcade_client import call_arcade_tool, ArcadeClient, ArcadeClientError

logger = logging.getLogger(__name__)

class XPostTweetNode(Node):
    """
    Node to post tweets to X using Arcade API
    
    Posts tweets to X with support for text, media attachments,
    reply chains, and quote tweets.
    
    Example:
        >>> node = XPostTweetNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "text": "Hello world! 🌍 #FirstTweet",
        ...     "reply_to": None,  # Optional: tweet ID to reply to
        ...     "media_ids": []    # Optional: media attachment IDs
        ... }
        >>> node.run(shared)
    """
    
    def prep(self, shared: Dict[str, Any]):
        """
        Prepare tweet data for posting
        
        Args:
            shared: Contains tweet parameters
            
        Returns:
            Tuple of (user_id, tweet_params)
        """
        user_id = shared.get("user_id")
        if not user_id:
            logger.error("❌ XPostTweetNode: No user_id provided")
            raise ValueError("user_id is required for X operations")
        
        tweet_params = {
            "text": shared.get("text", shared.get("tweet_text", "")),
            "reply_to": shared.get("reply_to", shared.get("in_reply_to_status_id")),
            "quote_tweet_id": shared.get("quote_tweet_id"),
            "media_ids": shared.get("media_ids", []),
            "poll": shared.get("poll"),
            "geo": shared.get("geo"),
            "for_super_followers_only": shared.get("for_super_followers_only", False)
        }
        
        # Validate required fields
        if not tweet_params["text"] and not tweet_params["media_ids"]:
            logger.error("❌ XPostTweetNode: No text or media provided")
            raise ValueError("Either text or media_ids is required for posting tweet")
        
        # Check tweet length (X's limit is 280 characters for regular tweets)
        if tweet_params["text"] and len(tweet_params["text"]) > 280:
            logger.warning(f"⚠️ XPostTweetNode: Tweet text exceeds 280 characters ({len(tweet_params['text'])} chars)")
        
        logger.info(f"🐦 XPostTweetNode: prep - posting tweet")
        return user_id, tweet_params
    
    def exec(self, inputs):
        user_id, tweet_params = inputs
        try:
            logger.info(f"\ud83d\udc4c XPostTweetNode: Posting tweet via Arcade")
            result = call_arcade_tool(
                user_id=user_id,
                platform="x",
                action="post_tweet",
                parameters=tweet_params
            )
            from agent.utils.arcade_client import is_authorization_required
            if is_authorization_required(result):
                return {"authorization_required": True, **result}
            logger.info(f"\u2705 XPostTweetNode: Tweet posted successfully")
            return result
        except ArcadeClientError as e:
            from agent.utils.arcade_client import is_authorization_required_exception
            if is_authorization_required_exception(e):
                return {"authorization_required": True, "error": str(e), "url": getattr(e, "url", None)}
            logger.error(f"\u274c XPostTweetNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to post tweet via Arcade: {e}")
        except Exception as e:
            logger.error(f"\u274c XPostTweetNode: Unexpected error: {e}")
            raise RuntimeError(f"Tweet posting failed: {e}")
    def post(self, shared, prep_res, exec_res):
        from agent.utils.arcade_client import is_authorization_required
        if is_authorization_required(exec_res):
            shared["arcade_auth_url"] = exec_res.get("url")
            shared["arcade_auth_message"] = exec_res.get("message", exec_res.get("error", "Authorization required for X/Twitter."))
            return "wait_for_authorization"
        logger.info("\ud83d\udcbe XPostTweetNode: Storing tweet result")
        shared["x_post_result"] = exec_res
        shared["last_x_tweet"] = {
            "text": prep_res[1]["text"],
            "result": exec_res
        }
        return "default"

class XGetTweetsNode(Node):
    """
    Node to retrieve tweets from X using Arcade API
    
    Gets tweets from user timeline, mentions, or specific tweet threads.
    Supports filtering by date, user, and engagement metrics.
    
    Example:
        >>> node = XGetTweetsNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "timeline_type": "home",  # home, user, mentions
        ...     "count": 20,
        ...     "include_replies": False
        ... }
        >>> node.run(shared)
    """
    
    def prep(self, shared: Dict[str, Any]):
        """
        Prepare parameters for getting tweets
        
        Args:
            shared: Contains tweet query parameters
            
        Returns:
            Tuple of (user_id, tweet_params)
        """
        user_id = shared.get("user_id")
        if not user_id:
            logger.error("❌ XGetTweetsNode: No user_id provided")
            raise ValueError("user_id is required for X operations")
        
        tweet_params = {
            "timeline_type": shared.get("timeline_type", "home"),  # home, user, mentions
            "count": shared.get("count", 20),
            "since_id": shared.get("since_id"),
            "max_id": shared.get("max_id"),
            "include_replies": shared.get("include_replies", False),
            "include_retweets": shared.get("include_retweets", True),
            "screen_name": shared.get("screen_name"),  # For user timeline
            "exclude_replies": shared.get("exclude_replies", False)
        }
        
        logger.info(f"📬 XGetTweetsNode: prep - getting {tweet_params['timeline_type']} timeline")
        return user_id, tweet_params
    
    def exec(self, inputs):
        """
        Execute tweet retrieval via Arcade X API
        
        Args:
            inputs: Tuple of (user_id, tweet_params)
            
        Returns:
            List of tweets from X API via Arcade
        """
        user_id, tweet_params = inputs
        
        try:
            logger.info(f"📥 XGetTweetsNode: Getting tweets via Arcade")
            
            result = call_arcade_tool(
                user_id=user_id,
                platform="x",
                action="get_tweets",
                parameters=tweet_params
            )
            
            logger.info(f"✅ XGetTweetsNode: Retrieved tweets successfully")
            return result
            
        except ArcadeClientError as e:
            logger.error(f"❌ XGetTweetsNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to get tweets via Arcade: {e}")
        except Exception as e:
            logger.error(f"❌ XGetTweetsNode: Unexpected error: {e}")
            raise RuntimeError(f"Tweet retrieval failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """
        Store tweets result
        
        Args:
            shared: Shared data store
            prep_res: Result from prep method
            exec_res: Result from exec method
        """
        logger.info("💾 XGetTweetsNode: Storing tweets")
        shared["x_tweets"] = exec_res
        shared["last_tweet_check"] = {
            "timeline_type": prep_res[1]["timeline_type"],
            "count": len(exec_res) if isinstance(exec_res, list) else 1
        }
        return "default"

class XGetUserProfileNode(Node):
    """
    Node to retrieve user profile information from X using Arcade API
    
    Gets detailed user profile data including follower counts,
    bio, verification status, and recent activity.
    
    Example:
        >>> node = XGetUserProfileNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "target_username": "elonmusk",  # or target_user_id
        ...     "include_entities": True
        ... }
        >>> node.run(shared)
    """
    
    def prep(self, shared: Dict[str, Any]):
        """
        Prepare parameters for getting user profile
        
        Args:
            shared: Contains profile query parameters
            
        Returns:
            Tuple of (user_id, profile_params)
        """
        user_id = shared.get("user_id")
        if not user_id:
            logger.error("❌ XGetUserProfileNode: No user_id provided")
            raise ValueError("user_id is required for X operations")
        
        profile_params = {
            "target_username": shared.get("target_username", shared.get("screen_name")),
            "target_user_id": shared.get("target_user_id"),
            "include_entities": shared.get("include_entities", True)
        }
        
        # Validate that either username or user_id is provided
        if not profile_params["target_username"] and not profile_params["target_user_id"]:
            logger.error("❌ XGetUserProfileNode: No target user specified")
            raise ValueError("Either target_username or target_user_id is required")
        
        target = profile_params["target_username"] or profile_params["target_user_id"]
        logger.info(f"👤 XGetUserProfileNode: prep - getting profile for {target}")
        return user_id, profile_params
    
    def exec(self, inputs):
        """
        Execute user profile retrieval via Arcade X API
        
        Args:
            inputs: Tuple of (user_id, profile_params)
            
        Returns:
            User profile data from X API via Arcade
        """
        user_id, profile_params = inputs
        
        try:
            logger.info(f"📥 XGetUserProfileNode: Getting user profile via Arcade")
            
            result = call_arcade_tool(
                user_id=user_id,
                platform="x",
                action="get_user_profile",
                parameters=profile_params
            )
            
            logger.info(f"✅ XGetUserProfileNode: Retrieved user profile successfully")
            return result
            
        except ArcadeClientError as e:
            logger.error(f"❌ XGetUserProfileNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to get user profile via Arcade: {e}")
        except Exception as e:
            logger.error(f"❌ XGetUserProfileNode: Unexpected error: {e}")
            raise RuntimeError(f"User profile retrieval failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """
        Store user profile result
        
        Args:
            shared: Shared data store
            prep_res: Result from prep method
            exec_res: Result from exec method
        """
        logger.info("💾 XGetUserProfileNode: Storing user profile")
        shared["x_user_profile"] = exec_res
        shared["last_profile_check"] = {
            "target": prep_res[1].get("target_username") or prep_res[1].get("target_user_id"),
            "profile_data": exec_res
        }
        return "default"

class XLikeTweetNode(Node):
    """
    Node to like/unlike tweets on X using Arcade API
    
    Likes or unlikes tweets based on the action parameter.
    Supports bulk operations for multiple tweets.
    
    Example:
        >>> node = XLikeTweetNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "tweet_id": "1234567890123456789",
        ...     "action": "like"  # "like" or "unlike"
        ... }
        >>> node.run(shared)
    """
    
    def prep(self, shared: Dict[str, Any]):
        """
        Prepare parameters for liking/unliking tweets
        
        Args:
            shared: Contains like action parameters
            
        Returns:
            Tuple of (user_id, like_params)
        """
        user_id = shared.get("user_id")
        if not user_id:
            logger.error("❌ XLikeTweetNode: No user_id provided")
            raise ValueError("user_id is required for X operations")
        
        like_params = {
            "tweet_id": shared.get("tweet_id"),
            "tweet_ids": shared.get("tweet_ids", []),  # For bulk operations
            "action": shared.get("action", "like")  # "like" or "unlike"
        }
        
        # Validate required fields
        if not like_params["tweet_id"] and not like_params["tweet_ids"]:
            logger.error("❌ XLikeTweetNode: No tweet_id or tweet_ids provided")
            raise ValueError("Either tweet_id or tweet_ids is required for like action")
        
        # Validate action
        if like_params["action"] not in ["like", "unlike"]:
            logger.error(f"❌ XLikeTweetNode: Invalid action: {like_params['action']}")
            raise ValueError("action must be 'like' or 'unlike'")
        
        logger.info(f"❤️ XLikeTweetNode: prep - {like_params['action']} tweet(s)")
        return user_id, like_params
    
    def exec(self, inputs):
        """
        Execute tweet like/unlike via Arcade X API
        
        Args:
            inputs: Tuple of (user_id, like_params)
            
        Returns:
            Like action result from X API via Arcade
        """
        user_id, like_params = inputs
        
        try:
            logger.info(f"📤 XLikeTweetNode: {like_params['action']} tweet via Arcade")
            
            result = call_arcade_tool(
                user_id=user_id,
                platform="x",
                action="like_tweet",
                parameters=like_params
            )
            
            logger.info(f"✅ XLikeTweetNode: Tweet {like_params['action']} successful")
            return result
            
        except ArcadeClientError as e:
            logger.error(f"❌ XLikeTweetNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to {like_params['action']} tweet via Arcade: {e}")
        except Exception as e:
            logger.error(f"❌ XLikeTweetNode: Unexpected error: {e}")
            raise RuntimeError(f"Tweet {like_params['action']} failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """
        Store like action result
        
        Args:
            shared: Shared data store
            prep_res: Result from prep method
            exec_res: Result from exec method
        """
        logger.info("💾 XLikeTweetNode: Storing like action result")
        shared["x_like_result"] = exec_res
        shared["last_like_action"] = {
            "action": prep_res[1]["action"],
            "tweet_id": prep_res[1].get("tweet_id"),
            "result": exec_res
        }
        return "default"

class XAuthNode(Node):
    """
    Node to handle X authentication via Arcade
    
    Manages the OAuth flow for X access through Arcade platform.
    Handles authentication and scope management for X API v2.
    
    Example:
        >>> node = XAuthNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "scopes": ["tweet.write", "users.read", "like.write"]
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
            logger.error("❌ XAuthNode: No user_id provided")
            raise ValueError("user_id is required for X authentication")
        
        auth_params = {
            "scopes": shared.get("scopes", [
                "tweet.read",
                "tweet.write",
                "users.read",
                "like.read",
                "like.write",
                "follows.read",
                "offline.access"
            ])
        }
        
        logger.info(f"🔐 XAuthNode: prep - authenticating user {user_id}")
        return user_id, auth_params
    
    def exec(self, inputs):
        """
        Execute X authentication via Arcade
        
        Args:
            inputs: Tuple of (user_id, auth_params)
            
        Returns:
            Authentication result from Arcade
        """
        user_id, auth_params = inputs
        
        try:
            logger.info(f"🔑 XAuthNode: Starting X auth via Arcade")
            
            client = ArcadeClient()
            
            # Check if already authenticated
            if client.is_user_authenticated(user_id, "x"):
                logger.info(f"✅ XAuthNode: User already authenticated")
                return {"status": "already_authenticated", "user_id": user_id}
            
            # Start authentication flow
            auth_response = client.start_auth(
                user_id=user_id,
                platform="x",
                scopes=auth_params["scopes"]
            )
            
            # If authentication is required, wait for completion
            if auth_response.status == "requires_auth":
                logger.info(f"🔗 XAuthNode: Auth URL: {auth_response.url}")
                auth_response = client.wait_for_auth_completion(auth_response)
            
            logger.info(f"✅ XAuthNode: Authentication completed")
            return {
                "status": auth_response.status,
                "user_id": user_id,
                "auth_url": auth_response.url
            }
            
        except ArcadeClientError as e:
            logger.error(f"❌ XAuthNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to authenticate with X via Arcade: {e}")
        except Exception as e:
            logger.error(f"❌ XAuthNode: Unexpected error: {e}")
            raise RuntimeError(f"X authentication failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """
        Store authentication result
        
        Args:
            shared: Shared data store
            prep_res: Result from prep method
            exec_res: Result from exec method
        """
        logger.info("💾 XAuthNode: Storing auth result")
        shared["x_auth_status"] = exec_res
        shared["x_authenticated"] = exec_res.get("status") in ["completed", "already_authenticated"]
        return "default"