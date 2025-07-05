"""
Unit tests for Arcade function nodes

This module contains tests for the Arcade platform integration nodes,
focusing on basic functionality and error handling.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Test basic imports first
def test_imports():
    """Test that all Arcade modules can be imported"""
    try:
        from agent.utils.arcade_client import ArcadeClient, call_arcade_tool
        from agent.function_nodes.gmail_arcade import GmailSendEmailNode
        from agent.function_nodes.slack_arcade import SlackSendMessageNode
        from agent.function_nodes.x_arcade import XPostTweetNode
        from agent.function_nodes.linkedin_arcade import LinkedInPostUpdateNode
        from agent.function_nodes.discord_arcade import DiscordSendMessageNode
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

class TestArcadeClient(unittest.TestCase):
    """Test the ArcadeClient utility"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock the API key
        os.environ['ARCADE_API_KEY'] = 'test_key_123'
    
    def test_client_initialization(self):
        """Test ArcadeClient initialization"""
        from agent.utils.arcade_client import ArcadeClient
        
        client = ArcadeClient()
        self.assertIsNotNone(client.api_key)
        self.assertEqual(client.api_key, 'test_key_123')
    
    def test_platform_tool_mapping(self):
        """Test platform tool name mapping"""
        from agent.utils.arcade_client import ArcadeClient
        
        client = ArcadeClient()
        
        # Test valid platform and action
        tool_name = client.get_platform_tool_name('gmail', 'send_email')
        self.assertEqual(tool_name, 'gmail_send_email')
        
        # Test invalid platform
        with self.assertRaises(ValueError):
            client.get_platform_tool_name('invalid_platform', 'send_email')
        
        # Test invalid action
        with self.assertRaises(ValueError):
            client.get_platform_tool_name('gmail', 'invalid_action')

class TestGmailNodes(unittest.TestCase):
    """Test Gmail Arcade nodes"""
    
    def setUp(self):
        """Set up test environment"""
        os.environ['ARCADE_API_KEY'] = 'test_key_123'
    
    @patch('agent.utils.arcade_client.ArcadeClient._make_request')
    def test_gmail_send_email_prep(self, mock_request):
        """Test Gmail send email node preparation"""
        from agent.function_nodes.gmail_arcade import GmailSendEmailNode
        
        node = GmailSendEmailNode()
        shared = {
            'user_id': 'test_user',
            'recipient': 'test@example.com',
            'subject': 'Test Subject',
            'body': 'Test Body'
                 }
         
         result = node.prep(shared)
         
         # Check that prep returns the expected data (tuple of user_id, params)
         self.assertIsInstance(result, tuple)
         self.assertEqual(len(result), 2)
         user_id, email_params = result
         self.assertEqual(user_id, 'test_user')
         self.assertEqual(email_params.get('recipient'), 'test@example.com')
    
    @patch('agent.utils.arcade_client.ArcadeClient._make_request')
    def test_gmail_send_email_exec(self, mock_request):
        """Test Gmail send email execution"""
        from agent.function_nodes.gmail_arcade import GmailSendEmailNode
        
        # Mock the API response
        mock_request.return_value = {
            'status': 'success',
            'message_id': '12345',
            'message': 'Email sent successfully'
        }
        
        node = GmailSendEmailNode()
        prep_data = {
            'user_id': 'test_user',
            'recipient': 'test@example.com',
            'subject': 'Test Subject',
            'body': 'Test Body'
        }
        
        result = node.exec(prep_data)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['status'], 'success')

class TestSlackNodes(unittest.TestCase):
    """Test Slack Arcade nodes"""
    
    def setUp(self):
        """Set up test environment"""
        os.environ['ARCADE_API_KEY'] = 'test_key_123'
    
    @patch('agent.utils.arcade_client.ArcadeClient._make_request')
    def test_slack_send_message_prep(self, mock_request):
        """Test Slack send message node preparation"""
        from agent.function_nodes.slack_arcade import SlackSendMessageNode
        
        node = SlackSendMessageNode()
        shared = {
            'user_id': 'test_user',
            'channel': '#general',
            'message': 'Hello Slack!'
        }
        
        result = node.prep(shared)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['user_id'], 'test_user')
        self.assertEqual(result['channel'], '#general')

class TestXNodes(unittest.TestCase):
    """Test X (Twitter) Arcade nodes"""
    
    def setUp(self):
        """Set up test environment"""
        os.environ['ARCADE_API_KEY'] = 'test_key_123'
    
    @patch('agent.utils.arcade_client.ArcadeClient._make_request')
    def test_x_post_tweet_prep(self, mock_request):
        """Test X post tweet node preparation"""
        from agent.function_nodes.x_arcade import XPostTweetNode
        
        node = XPostTweetNode()
        shared = {
            'user_id': 'test_user',
            'text': 'Hello Twitter!'
        }
        
        result = node.prep(shared)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['user_id'], 'test_user')
        self.assertEqual(result['text'], 'Hello Twitter!')

class TestLinkedInNodes(unittest.TestCase):
    """Test LinkedIn Arcade nodes"""
    
    def setUp(self):
        """Set up test environment"""
        os.environ['ARCADE_API_KEY'] = 'test_key_123'
    
    @patch('agent.utils.arcade_client.ArcadeClient._make_request')
    def test_linkedin_post_update_prep(self, mock_request):
        """Test LinkedIn post update node preparation"""
        from agent.function_nodes.linkedin_arcade import LinkedInPostUpdateNode
        
        node = LinkedInPostUpdateNode()
        shared = {
            'user_id': 'test_user',
            'text': 'Hello LinkedIn!'
        }
        
        result = node.prep(shared)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['user_id'], 'test_user')
        self.assertEqual(result['text'], 'Hello LinkedIn!')

class TestDiscordNodes(unittest.TestCase):
    """Test Discord Arcade nodes"""
    
    def setUp(self):
        """Set up test environment"""
        os.environ['ARCADE_API_KEY'] = 'test_key_123'
    
    @patch('agent.utils.arcade_client.ArcadeClient._make_request')
    def test_discord_send_message_prep(self, mock_request):
        """Test Discord send message node preparation"""
        from agent.function_nodes.discord_arcade import DiscordSendMessageNode
        
        node = DiscordSendMessageNode()
        shared = {
            'user_id': 'test_user',
            'channel_id': '1234567890',
            'message': 'Hello Discord!'
        }
        
        result = node.prep(shared)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['user_id'], 'test_user')
        self.assertEqual(result['channel_id'], '1234567890')

def run_basic_tests():
    """Run basic functionality tests"""
    print("🧪 Running basic Arcade integration tests...")
    
    # Test imports first
    if not test_imports():
        return False
    
    # Run unit tests
    try:
        # Create a test suite
        suite = unittest.TestSuite()
        
        # Add test cases
        suite.addTest(TestArcadeClient('test_client_initialization'))
        suite.addTest(TestArcadeClient('test_platform_tool_mapping'))
        suite.addTest(TestGmailNodes('test_gmail_send_email_prep'))
        suite.addTest(TestSlackNodes('test_slack_send_message_prep'))
        suite.addTest(TestXNodes('test_x_post_tweet_prep'))
        suite.addTest(TestLinkedInNodes('test_linkedin_post_update_prep'))
        suite.addTest(TestDiscordNodes('test_discord_send_message_prep'))
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        if result.wasSuccessful():
            print("✅ All basic tests passed!")
            return True
        else:
            print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
            return False
            
    except Exception as e:
        print(f"❌ Test execution error: {e}")
        return False

if __name__ == '__main__':
    # Run the basic tests
    success = run_basic_tests()
    sys.exit(0 if success else 1)