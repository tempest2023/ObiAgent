"""
Gmail Arcade Function Node

This module provides Gmail functionality through the Arcade.dev platform,
enabling authenticated access to Gmail operations like sending emails,
reading messages, and searching the inbox.
"""

from pocketflow import Node
from typing import Dict, Any, Optional
import logging
from agent.utils.arcade_client import call_arcade_tool, ArcadeClient, ArcadeClientError

logger = logging.getLogger(__name__)

class GmailSendEmailNode(Node):
    """
    Node to send emails via Gmail using Arcade API
    
    Sends emails through authenticated Gmail access via Arcade platform.
    Supports features like CC, BCC, attachments, and custom formatting.
    
    Example:
        >>> node = GmailSendEmailNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "recipient": "example@gmail.com",
        ...     "subject": "Meeting Update", 
        ...     "body": "The meeting has been rescheduled",
        ...     "cc": ["manager@company.com"],
        ...     "bcc": ["hr@company.com"]
        ... }
        >>> node.run(shared)
    """
    
    def prep(self, shared: Dict[str, Any]):
        """
        Prepare email data for sending
        
        Args:
            shared: Contains email parameters
            
        Returns:
            Tuple of (user_id, email_params)
        """
        user_id = shared.get("user_id")
        if not user_id:
            logger.error("❌ GmailSendEmailNode: No user_id provided")
            raise ValueError("user_id is required for Gmail operations")
        
        # Extract email parameters
        email_params = {
            "recipient": shared.get("recipient"),
            "subject": shared.get("subject", ""),
            "body": shared.get("body", ""),
            "cc": shared.get("cc", []),
            "bcc": shared.get("bcc", []),
            "reply_to": shared.get("reply_to"),
            "attachments": shared.get("attachments", [])
        }
        
        # Validate required fields
        if not email_params["recipient"]:
            logger.error("❌ GmailSendEmailNode: No recipient provided")
            raise ValueError("recipient is required for sending email")
        
        logger.info(f"📧 GmailSendEmailNode: prep - sending to {email_params['recipient']}")
        return user_id, email_params
    
    def exec(self, inputs):
        """
        Execute email sending via Arcade Gmail API
        
        Args:
            inputs: Tuple of (user_id, email_params)
            
        Returns:
            Response from Gmail API via Arcade
        """
        user_id, email_params = inputs
        
        try:
            logger.info(f"📤 GmailSendEmailNode: Sending email via Arcade")
            
            # Use Arcade client to send email
            result = call_arcade_tool(
                user_id=user_id,
                platform="gmail",
                action="send_email",
                parameters=email_params
            )
            
            logger.info(f"✅ GmailSendEmailNode: Email sent successfully")
            return result
            
        except ArcadeClientError as e:
            logger.error(f"❌ GmailSendEmailNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to send email via Arcade: {e}")
        except Exception as e:
            logger.error(f"❌ GmailSendEmailNode: Unexpected error: {e}")
            raise RuntimeError(f"Email sending failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """
        Store email sending result
        
        Args:
            shared: Shared data store
            prep_res: Result from prep method
            exec_res: Result from exec method
        """
        logger.info("💾 GmailSendEmailNode: Storing email result")
        shared["gmail_send_result"] = exec_res
        shared["last_email_sent"] = {
            "recipient": prep_res[1]["recipient"],
            "subject": prep_res[1]["subject"],
            "timestamp": exec_res
        }
        return "default"

class GmailReadEmailsNode(Node):
    """
    Node to read emails from Gmail using Arcade API
    
    Retrieves emails from the user's Gmail inbox with filtering options.
    Supports pagination, date filtering, and label-based filtering.
    
    Example:
        >>> node = GmailReadEmailsNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "max_results": 10,
        ...     "unread_only": True,
        ...     "label": "INBOX"
        ... }
        >>> node.run(shared)
    """
    
    def prep(self, shared: Dict[str, Any]):
        """
        Prepare parameters for reading emails
        
        Args:
            shared: Contains read parameters
            
        Returns:
            Tuple of (user_id, read_params)
        """
        user_id = shared.get("user_id")
        if not user_id:
            logger.error("❌ GmailReadEmailsNode: No user_id provided")
            raise ValueError("user_id is required for Gmail operations")
        
        read_params = {
            "max_results": shared.get("max_results", 10),
            "unread_only": shared.get("unread_only", False),
            "label": shared.get("label", "INBOX"),
            "from_email": shared.get("from_email"),
            "after_date": shared.get("after_date"),
            "before_date": shared.get("before_date")
        }
        
        logger.info(f"📬 GmailReadEmailsNode: prep - reading {read_params['max_results']} emails")
        return user_id, read_params
    
    def exec(self, inputs):
        """
        Execute email reading via Arcade Gmail API
        
        Args:
            inputs: Tuple of (user_id, read_params)
            
        Returns:
            List of emails from Gmail API via Arcade
        """
        user_id, read_params = inputs
        
        try:
            logger.info(f"📥 GmailReadEmailsNode: Reading emails via Arcade")
            
            # Use Arcade client to read emails
            result = call_arcade_tool(
                user_id=user_id,
                platform="gmail",
                action="read_emails",
                parameters=read_params
            )
            
            logger.info(f"✅ GmailReadEmailsNode: Retrieved emails successfully")
            return result
            
        except ArcadeClientError as e:
            logger.error(f"❌ GmailReadEmailsNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to read emails via Arcade: {e}")
        except Exception as e:
            logger.error(f"❌ GmailReadEmailsNode: Unexpected error: {e}")
            raise RuntimeError(f"Email reading failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """
        Store email reading result
        
        Args:
            shared: Shared data store
            prep_res: Result from prep method
            exec_res: Result from exec method
        """
        logger.info(f"💾 GmailReadEmailsNode: Storing {len(exec_res)} emails")
        shared["gmail_emails"] = exec_res
        shared["last_email_check"] = {
            "count": len(exec_res) if isinstance(exec_res, list) else 1,
            "params": prep_res[1]
        }
        return "default"

class GmailSearchEmailsNode(Node):
    """
    Node to search emails in Gmail using Arcade API
    
    Performs advanced search in Gmail with various criteria including
    sender, subject, body text, date ranges, and Gmail search operators.
    
    Example:
        >>> node = GmailSearchEmailsNode()
        >>> shared = {
        ...     "user_id": "user123",
        ...     "search_query": "from:boss@company.com subject:urgent",
        ...     "max_results": 20
        ... }
        >>> node.run(shared)
    """
    
    def prep(self, shared: Dict[str, Any]):
        """
        Prepare search parameters
        
        Args:
            shared: Contains search parameters
            
        Returns:
            Tuple of (user_id, search_params)
        """
        user_id = shared.get("user_id")
        if not user_id:
            logger.error("❌ GmailSearchEmailsNode: No user_id provided")
            raise ValueError("user_id is required for Gmail operations")
        
        search_params = {
            "query": shared.get("search_query", shared.get("query", "")),
            "max_results": shared.get("max_results", 10),
            "include_spam_trash": shared.get("include_spam_trash", False)
        }
        
        if not search_params["query"]:
            logger.error("❌ GmailSearchEmailsNode: No search query provided")
            raise ValueError("search_query is required for email search")
        
        logger.info(f"🔍 GmailSearchEmailsNode: prep - searching for '{search_params['query']}'")
        return user_id, search_params
    
    def exec(self, inputs):
        """
        Execute email search via Arcade Gmail API
        
        Args:
            inputs: Tuple of (user_id, search_params)
            
        Returns:
            Search results from Gmail API via Arcade
        """
        user_id, search_params = inputs
        
        try:
            logger.info(f"🔎 GmailSearchEmailsNode: Searching emails via Arcade")
            
            # Use Arcade client to search emails
            result = call_arcade_tool(
                user_id=user_id,
                platform="gmail",
                action="search_emails",
                parameters=search_params
            )
            
            logger.info(f"✅ GmailSearchEmailsNode: Search completed successfully")
            return result
            
        except ArcadeClientError as e:
            logger.error(f"❌ GmailSearchEmailsNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to search emails via Arcade: {e}")
        except Exception as e:
            logger.error(f"❌ GmailSearchEmailsNode: Unexpected error: {e}")
            raise RuntimeError(f"Email search failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """
        Store search results
        
        Args:
            shared: Shared data store
            prep_res: Result from prep method
            exec_res: Result from exec method
        """
        logger.info("💾 GmailSearchEmailsNode: Storing search results")
        shared["gmail_search_results"] = exec_res
        shared["last_search"] = {
            "query": prep_res[1]["query"],
            "results_count": len(exec_res) if isinstance(exec_res, list) else 1
        }
        return "default"

class GmailAuthNode(Node):
    """
    Node to handle Gmail authentication via Arcade
    
    Manages the OAuth flow for Gmail access through Arcade platform.
    Handles initial authentication and token refresh.
    
    Example:
        >>> node = GmailAuthNode()
        >>> shared = {"user_id": "user123"}
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
            logger.error("❌ GmailAuthNode: No user_id provided")
            raise ValueError("user_id is required for Gmail authentication")
        
        auth_params = {
            "scopes": shared.get("scopes", [
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.modify"
            ])
        }
        
        logger.info(f"🔐 GmailAuthNode: prep - authenticating user {user_id}")
        return user_id, auth_params
    
    def exec(self, inputs):
        """
        Execute Gmail authentication via Arcade
        
        Args:
            inputs: Tuple of (user_id, auth_params)
            
        Returns:
            Authentication result from Arcade
        """
        user_id, auth_params = inputs
        
        try:
            logger.info(f"🔑 GmailAuthNode: Starting Gmail auth via Arcade")
            
            client = ArcadeClient()
            
            # Check if already authenticated
            if client.is_user_authenticated(user_id, "google"):
                logger.info(f"✅ GmailAuthNode: User already authenticated")
                return {"status": "already_authenticated", "user_id": user_id}
            
            # Start authentication flow
            auth_response = client.start_auth(
                user_id=user_id,
                platform="google",
                scopes=auth_params["scopes"]
            )
            
            # If authentication is required, wait for completion
            if auth_response.status == "requires_auth":
                logger.info(f"🔗 GmailAuthNode: Auth URL: {auth_response.url}")
                # In real implementation, you'd return the URL to the user
                # For demo, we'll simulate completion
                auth_response = client.wait_for_auth_completion(auth_response)
            
            logger.info(f"✅ GmailAuthNode: Authentication completed")
            return {
                "status": auth_response.status,
                "user_id": user_id,
                "auth_url": auth_response.url
            }
            
        except ArcadeClientError as e:
            logger.error(f"❌ GmailAuthNode: Arcade client error: {e}")
            raise RuntimeError(f"Failed to authenticate with Gmail via Arcade: {e}")
        except Exception as e:
            logger.error(f"❌ GmailAuthNode: Unexpected error: {e}")
            raise RuntimeError(f"Gmail authentication failed: {e}")
    
    def post(self, shared, prep_res, exec_res):
        """
        Store authentication result
        
        Args:
            shared: Shared data store
            prep_res: Result from prep method
            exec_res: Result from exec method
        """
        logger.info("💾 GmailAuthNode: Storing auth result")
        shared["gmail_auth_status"] = exec_res
        shared["gmail_authenticated"] = exec_res.get("status") in ["completed", "already_authenticated"]
        return "default"