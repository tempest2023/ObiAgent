"""
Unit tests for Arcade function nodes

This module contains comprehensive tests for all Arcade platform integration nodes,
including Gmail, Slack, X, LinkedIn, and Discord functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import all Arcade nodes
from agent.function_nodes.gmail_arcade import (
    GmailSendEmailNode, GmailReadEmailsNode, GmailSearchEmailsNode, GmailAuthNode
)
from agent.function_nodes.slack_arcade import (
    SlackSendMessageNode, SlackGetChannelsNode, SlackGetMessagesNode, 
    SlackUploadFileNode, SlackAuthNode
)
from agent.function_nodes.x_arcade import (
    XPostTweetNode, XGetTweetsNode, XGetUserProfileNode, XLikeTweetNode, XAuthNode
)
from agent.function_nodes.linkedin_arcade import (
    LinkedInPostUpdateNode, LinkedInGetProfileNode, LinkedInSendMessageNode,
    LinkedInGetConnectionsNode, LinkedInAuthNode
)
from agent.function_nodes.discord_arcade import (
    DiscordSendMessageNode, DiscordGetChannelsNode, DiscordGetMessagesNode,
    DiscordCreateChannelNode, DiscordAuthNode
)
from agent.utils.arcade_client import ArcadeClientError


class TestGmailArcadeNodes:
    """Test cases for Gmail Arcade function nodes"""
    
    def test_gmail_send_email_node_prep(self):
        """Test GmailSendEmailNode prep method"""
        node = GmailSendEmailNode()
        shared = {
            "user_id": "test_user",
            "recipient": "test@example.com",
            "subject": "Test Subject",
            "body": "Test Body",
            "cc": ["cc@example.com"],
            "bcc": ["bcc@example.com"]
        }
        
        user_id, email_params = node.prep(shared)
        
        assert user_id == "test_user"
        assert email_params["recipient"] == "test@example.com"
        assert email_params["subject"] == "Test Subject"
        assert email_params["body"] == "Test Body"
        assert email_params["cc"] == ["cc@example.com"]
        assert email_params["bcc"] == ["bcc@example.com"]

    def test_gmail_send_email_node_prep_missing_user_id(self):
        """Test GmailSendEmailNode prep method with missing user_id"""
        node = GmailSendEmailNode()
        shared = {"recipient": "test@example.com"}
        
        with pytest.raises(ValueError, match="user_id is required"):
            node.prep(shared)

    def test_gmail_send_email_node_prep_missing_recipient(self):
        """Test GmailSendEmailNode prep method with missing recipient"""
        node = GmailSendEmailNode()
        shared = {"user_id": "test_user"}
        
        with pytest.raises(ValueError, match="recipient is required"):
            node.prep(shared)

    @patch('agent.function_nodes.gmail_arcade.call_arcade_tool')
    def test_gmail_send_email_node_exec(self, mock_call_arcade):
        """Test GmailSendEmailNode exec method"""
        mock_call_arcade.return_value = "Email sent successfully"
        
        node = GmailSendEmailNode()
        inputs = ("test_user", {
            "recipient": "test@example.com",
            "subject": "Test Subject",
            "body": "Test Body"
        })
        
        result = node.exec(inputs)
        
        assert result == "Email sent successfully"
        mock_call_arcade.assert_called_once_with(
            user_id="test_user",
            platform="gmail",
            action="send_email",
            parameters=inputs[1]
        )

    @patch('agent.function_nodes.gmail_arcade.call_arcade_tool')
    def test_gmail_send_email_node_exec_error(self, mock_call_arcade):
        """Test GmailSendEmailNode exec method with error"""
        mock_call_arcade.side_effect = ArcadeClientError("API Error")
        
        node = GmailSendEmailNode()
        inputs = ("test_user", {"recipient": "test@example.com"})
        
        with pytest.raises(RuntimeError, match="Failed to send email via Arcade"):
            node.exec(inputs)

    def test_gmail_send_email_node_post(self):
        """Test GmailSendEmailNode post method"""
        node = GmailSendEmailNode()
        shared = {}
        prep_res = ("test_user", {
            "recipient": "test@example.com",
            "subject": "Test Subject"
        })
        exec_res = "Email sent successfully"
        
        result = node.post(shared, prep_res, exec_res)
        
        assert result == "default"
        assert shared["gmail_send_result"] == "Email sent successfully"
        assert shared["last_email_sent"]["recipient"] == "test@example.com"
        assert shared["last_email_sent"]["subject"] == "Test Subject"

    def test_gmail_read_emails_node_prep(self):
        """Test GmailReadEmailsNode prep method"""
        node = GmailReadEmailsNode()
        shared = {
            "user_id": "test_user",
            "max_results": 20,
            "unread_only": True,
            "label": "INBOX"
        }
        
        user_id, read_params = node.prep(shared)
        
        assert user_id == "test_user"
        assert read_params["max_results"] == 20
        assert read_params["unread_only"] is True
        assert read_params["label"] == "INBOX"

    @patch('agent.function_nodes.gmail_arcade.call_arcade_tool')
    def test_gmail_read_emails_node_exec(self, mock_call_arcade):
        """Test GmailReadEmailsNode exec method"""
        mock_call_arcade.return_value = [{"id": "1", "subject": "Test"}]
        
        node = GmailReadEmailsNode()
        inputs = ("test_user", {"max_results": 10})
        
        result = node.exec(inputs)
        
        assert len(result) == 1
        assert result[0]["subject"] == "Test"


class TestSlackArcadeNodes:
    """Test cases for Slack Arcade function nodes"""
    
    def test_slack_send_message_node_prep(self):
        """Test SlackSendMessageNode prep method"""
        node = SlackSendMessageNode()
        shared = {
            "user_id": "test_user",
            "channel": "#general",
            "message": "Hello team!",
            "thread_ts": "1234567890.123456"
        }
        
        user_id, message_params = node.prep(shared)
        
        assert user_id == "test_user"
        assert message_params["channel"] == "#general"
        assert message_params["message"] == "Hello team!"
        assert message_params["thread_ts"] == "1234567890.123456"

    def test_slack_send_message_node_prep_missing_channel(self):
        """Test SlackSendMessageNode prep method with missing channel"""
        node = SlackSendMessageNode()
        shared = {"user_id": "test_user", "message": "Hello"}
        
        with pytest.raises(ValueError, match="channel is required"):
            node.prep(shared)

    @patch('agent.function_nodes.slack_arcade.call_arcade_tool')
    def test_slack_send_message_node_exec(self, mock_call_arcade):
        """Test SlackSendMessageNode exec method"""
        mock_call_arcade.return_value = {"ts": "1234567890.123456"}
        
        node = SlackSendMessageNode()
        inputs = ("test_user", {
            "channel": "#general",
            "message": "Hello team!"
        })
        
        result = node.exec(inputs)
        
        assert result["ts"] == "1234567890.123456"
        mock_call_arcade.assert_called_once_with(
            user_id="test_user",
            platform="slack",
            action="send_message",
            parameters=inputs[1]
        )

    def test_slack_get_channels_node_prep(self):
        """Test SlackGetChannelsNode prep method"""
        node = SlackGetChannelsNode()
        shared = {
            "user_id": "test_user",
            "types": ["public_channel"],
            "exclude_archived": True
        }
        
        user_id, channel_params = node.prep(shared)
        
        assert user_id == "test_user"
        assert channel_params["types"] == ["public_channel"]
        assert channel_params["exclude_archived"] is True


class TestXArcadeNodes:
    """Test cases for X (Twitter) Arcade function nodes"""
    
    def test_x_post_tweet_node_prep(self):
        """Test XPostTweetNode prep method"""
        node = XPostTweetNode()
        shared = {
            "user_id": "test_user",
            "text": "Hello world! 🌍",
            "reply_to": "1234567890",
            "media_ids": ["media123"]
        }
        
        user_id, tweet_params = node.prep(shared)
        
        assert user_id == "test_user"
        assert tweet_params["text"] == "Hello world! 🌍"
        assert tweet_params["reply_to"] == "1234567890"
        assert tweet_params["media_ids"] == ["media123"]

    def test_x_post_tweet_node_prep_no_content(self):
        """Test XPostTweetNode prep method with no content"""
        node = XPostTweetNode()
        shared = {"user_id": "test_user"}
        
        with pytest.raises(ValueError, match="Either text or media_ids is required"):
            node.prep(shared)

    @patch('agent.function_nodes.x_arcade.call_arcade_tool')
    def test_x_post_tweet_node_exec(self, mock_call_arcade):
        """Test XPostTweetNode exec method"""
        mock_call_arcade.return_value = {"id": "1234567890", "text": "Hello world!"}
        
        node = XPostTweetNode()
        inputs = ("test_user", {"text": "Hello world!"})
        
        result = node.exec(inputs)
        
        assert result["id"] == "1234567890"
        assert result["text"] == "Hello world!"

    def test_x_get_user_profile_node_prep(self):
        """Test XGetUserProfileNode prep method"""
        node = XGetUserProfileNode()
        shared = {
            "user_id": "test_user",
            "target_username": "elonmusk",
            "include_entities": True
        }
        
        user_id, profile_params = node.prep(shared)
        
        assert user_id == "test_user"
        assert profile_params["target_username"] == "elonmusk"
        assert profile_params["include_entities"] is True

    def test_x_get_user_profile_node_prep_no_target(self):
        """Test XGetUserProfileNode prep method with no target"""
        node = XGetUserProfileNode()
        shared = {"user_id": "test_user"}
        
        with pytest.raises(ValueError, match="Either target_username or target_user_id is required"):
            node.prep(shared)


class TestLinkedInArcadeNodes:
    """Test cases for LinkedIn Arcade function nodes"""
    
    def test_linkedin_post_update_node_prep(self):
        """Test LinkedInPostUpdateNode prep method"""
        node = LinkedInPostUpdateNode()
        shared = {
            "user_id": "test_user",
            "text": "Excited to share my latest project! 🚀",
            "visibility": "PUBLIC",
            "media_url": "https://example.com/image.jpg"
        }
        
        user_id, update_params = node.prep(shared)
        
        assert user_id == "test_user"
        assert update_params["text"] == "Excited to share my latest project! 🚀"
        assert update_params["visibility"] == "PUBLIC"
        assert update_params["media_url"] == "https://example.com/image.jpg"

    def test_linkedin_post_update_node_prep_invalid_visibility(self):
        """Test LinkedInPostUpdateNode prep method with invalid visibility"""
        node = LinkedInPostUpdateNode()
        shared = {
            "user_id": "test_user",
            "text": "Test post",
            "visibility": "INVALID"
        }
        
        user_id, update_params = node.prep(shared)
        
        # Should default to PUBLIC for invalid visibility
        assert update_params["visibility"] == "PUBLIC"

    @patch('agent.function_nodes.linkedin_arcade.call_arcade_tool')
    def test_linkedin_post_update_node_exec(self, mock_call_arcade):
        """Test LinkedInPostUpdateNode exec method"""
        mock_call_arcade.return_value = {"activity": "urn:li:activity:123"}
        
        node = LinkedInPostUpdateNode()
        inputs = ("test_user", {"text": "Test post"})
        
        result = node.exec(inputs)
        
        assert result["activity"] == "urn:li:activity:123"

    def test_linkedin_send_message_node_prep(self):
        """Test LinkedInSendMessageNode prep method"""
        node = LinkedInSendMessageNode()
        shared = {
            "user_id": "test_user",
            "recipient_id": "connection123",
            "message": "Hi! I'd love to connect.",
            "subject": "Great post!"
        }
        
        user_id, message_params = node.prep(shared)
        
        assert user_id == "test_user"
        assert message_params["recipient_id"] == "connection123"
        assert message_params["message"] == "Hi! I'd love to connect."
        assert message_params["subject"] == "Great post!"


class TestDiscordArcadeNodes:
    """Test cases for Discord Arcade function nodes"""
    
    def test_discord_send_message_node_prep(self):
        """Test DiscordSendMessageNode prep method"""
        node = DiscordSendMessageNode()
        shared = {
            "user_id": "test_user",
            "channel_id": "1234567890123456789",
            "message": "Hello Discord! 🎮",
            "embed": {"title": "Test Embed"}
        }
        
        user_id, message_params = node.prep(shared)
        
        assert user_id == "test_user"
        assert message_params["channel_id"] == "1234567890123456789"
        assert message_params["message"] == "Hello Discord! 🎮"
        assert message_params["embed"]["title"] == "Test Embed"

    def test_discord_send_message_node_prep_no_content(self):
        """Test DiscordSendMessageNode prep method with no content"""
        node = DiscordSendMessageNode()
        shared = {
            "user_id": "test_user",
            "channel_id": "1234567890123456789"
        }
        
        with pytest.raises(ValueError, match="Either message, embed, embeds, or files is required"):
            node.prep(shared)

    @patch('agent.function_nodes.discord_arcade.call_arcade_tool')
    def test_discord_send_message_node_exec(self, mock_call_arcade):
        """Test DiscordSendMessageNode exec method"""
        mock_call_arcade.return_value = {"id": "987654321", "content": "Hello Discord!"}
        
        node = DiscordSendMessageNode()
        inputs = ("test_user", {
            "channel_id": "1234567890123456789",
            "message": "Hello Discord!"
        })
        
        result = node.exec(inputs)
        
        assert result["id"] == "987654321"
        assert result["content"] == "Hello Discord!"

    def test_discord_create_channel_node_prep(self):
        """Test DiscordCreateChannelNode prep method"""
        node = DiscordCreateChannelNode()
        shared = {
            "user_id": "test_user",
            "guild_id": "1234567890123456789",
            "name": "new-channel",
            "type": "text",
            "topic": "Channel for discussions"
        }
        
        user_id, create_params = node.prep(shared)
        
        assert user_id == "test_user"
        assert create_params["guild_id"] == "1234567890123456789"
        assert create_params["name"] == "new-channel"
        assert create_params["type"] == "text"
        assert create_params["topic"] == "Channel for discussions"

    def test_discord_create_channel_node_prep_invalid_type(self):
        """Test DiscordCreateChannelNode prep method with invalid type"""
        node = DiscordCreateChannelNode()
        shared = {
            "user_id": "test_user",
            "guild_id": "1234567890123456789",
            "name": "new-channel",
            "type": "invalid_type"
        }
        
        user_id, create_params = node.prep(shared)
        
        # Should default to 'text' for invalid type
        assert create_params["type"] == "text"


class TestArcadeAuthNodes:
    """Test cases for all Arcade authentication nodes"""
    
    @patch('agent.function_nodes.gmail_arcade.ArcadeClient')
    def test_gmail_auth_node_exec_already_authenticated(self, mock_client_class):
        """Test GmailAuthNode exec method when user is already authenticated"""
        mock_client = Mock()
        mock_client.is_user_authenticated.return_value = True
        mock_client_class.return_value = mock_client
        
        node = GmailAuthNode()
        inputs = ("test_user", {"scopes": ["gmail.send"]})
        
        result = node.exec(inputs)
        
        assert result["status"] == "already_authenticated"
        assert result["user_id"] == "test_user"

    @patch('agent.function_nodes.slack_arcade.ArcadeClient')
    def test_slack_auth_node_exec_requires_auth(self, mock_client_class):
        """Test SlackAuthNode exec method when authentication is required"""
        mock_client = Mock()
        mock_client.is_user_authenticated.return_value = False
        
        mock_auth_response = Mock()
        mock_auth_response.status = "requires_auth"
        mock_auth_response.url = "https://slack.com/oauth/authorize"
        mock_client.start_auth.return_value = mock_auth_response
        
        mock_completed_response = Mock()
        mock_completed_response.status = "completed"
        mock_completed_response.url = "https://slack.com/oauth/authorize"
        mock_client.wait_for_auth_completion.return_value = mock_completed_response
        
        mock_client_class.return_value = mock_client
        
        node = SlackAuthNode()
        inputs = ("test_user", {"scopes": ["chat:write"]})
        
        result = node.exec(inputs)
        
        assert result["status"] == "completed"
        assert result["user_id"] == "test_user"
        assert "auth_url" in result

    @patch('agent.function_nodes.x_arcade.ArcadeClient')
    def test_x_auth_node_exec_error(self, mock_client_class):
        """Test XAuthNode exec method with error"""
        mock_client = Mock()
        mock_client.is_user_authenticated.side_effect = ArcadeClientError("Auth error")
        mock_client_class.return_value = mock_client
        
        node = XAuthNode()
        inputs = ("test_user", {"scopes": ["tweet.write"]})
        
        with pytest.raises(RuntimeError, match="Failed to authenticate with X via Arcade"):
            node.exec(inputs)


class TestArcadeNodeIntegration:
    """Integration tests for Arcade nodes"""
    
    @patch('agent.function_nodes.gmail_arcade.call_arcade_tool')
    def test_gmail_workflow_integration(self, mock_call_arcade):
        """Test complete Gmail workflow integration"""
        mock_call_arcade.return_value = "Email sent successfully"
        
        # Test complete workflow
        node = GmailSendEmailNode()
        shared = {
            "user_id": "test_user",
            "recipient": "test@example.com",
            "subject": "Integration Test",
            "body": "This is a test email"
        }
        
        # Run complete node workflow
        action = node.run(shared)
        
        assert action == "default"
        assert shared["gmail_send_result"] == "Email sent successfully"
        assert shared["last_email_sent"]["recipient"] == "test@example.com"

    @patch('agent.function_nodes.slack_arcade.call_arcade_tool')
    def test_slack_workflow_integration(self, mock_call_arcade):
        """Test complete Slack workflow integration"""
        mock_call_arcade.return_value = {"ts": "1234567890.123456"}
        
        node = SlackSendMessageNode()
        shared = {
            "user_id": "test_user",
            "channel": "#general",
            "message": "Integration test message"
        }
        
        action = node.run(shared)
        
        assert action == "default"
        assert shared["slack_send_result"]["ts"] == "1234567890.123456"

    def test_node_error_handling(self):
        """Test error handling across all nodes"""
        # Test missing user_id across different nodes
        nodes_to_test = [
            GmailSendEmailNode(),
            SlackSendMessageNode(),
            XPostTweetNode(),
            LinkedInPostUpdateNode(),
            DiscordSendMessageNode()
        ]
        
        for node in nodes_to_test:
            shared = {"some_field": "some_value"}  # Missing user_id
            
            with pytest.raises(ValueError, match="user_id is required"):
                node.prep(shared)


if __name__ == "__main__":
    pytest.main([__file__])