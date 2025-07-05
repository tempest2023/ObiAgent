"""
Basic tests for Arcade function nodes

Simple functionality tests that focus on imports and basic operations.
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_arcade_imports():
    """Test that all Arcade modules can be imported"""
    try:
        # Test arcade client import
        from agent.utils.arcade_client import ArcadeClient, call_arcade_tool
        print("✅ Arcade client imported successfully")
        
        # Test Gmail nodes
        from agent.function_nodes.gmail_arcade import (
            GmailSendEmailNode, GmailReadEmailsNode, GmailSearchEmailsNode, GmailAuthNode
        )
        print("✅ Gmail nodes imported successfully")
        
        # Test Slack nodes
        from agent.function_nodes.slack_arcade import (
            SlackSendMessageNode, SlackGetChannelsNode, SlackGetMessagesNode, 
            SlackUploadFileNode, SlackAuthNode
        )
        print("✅ Slack nodes imported successfully")
        
        # Test X nodes
        from agent.function_nodes.x_arcade import (
            XPostTweetNode, XGetTweetsNode, XGetUserProfileNode, XLikeTweetNode, XAuthNode
        )
        print("✅ X nodes imported successfully")
        
        # Test LinkedIn nodes
        from agent.function_nodes.linkedin_arcade import (
            LinkedInPostUpdateNode, LinkedInGetProfileNode, LinkedInSendMessageNode,
            LinkedInGetConnectionsNode, LinkedInAuthNode
        )
        print("✅ LinkedIn nodes imported successfully")
        
        # Test Discord nodes
        from agent.function_nodes.discord_arcade import (
            DiscordSendMessageNode, DiscordGetChannelsNode, DiscordGetMessagesNode,
            DiscordCreateChannelNode, DiscordAuthNode
        )
        print("✅ Discord nodes imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_arcade_client_basic():
    """Test basic ArcadeClient functionality"""
    # Set up environment
    os.environ['ARCADE_API_KEY'] = 'test_key_123'
    
    from agent.utils.arcade_client import ArcadeClient
    
    # Test client creation
    client = ArcadeClient()
    print("✅ ArcadeClient created successfully")
    
    # Test platform tool mapping
    tool_name = client.get_platform_tool_name('gmail', 'send_email')
    assert tool_name == 'gmail_send_email', f"Expected 'gmail_send_email', got '{tool_name}'"
    print("✅ Platform tool mapping works correctly")

def test_node_creation():
    """Test that nodes can be created"""
    os.environ['ARCADE_API_KEY'] = 'test_key_123'
    
    from agent.function_nodes.gmail_arcade import GmailSendEmailNode
    from agent.function_nodes.slack_arcade import SlackSendMessageNode
    from agent.function_nodes.x_arcade import XPostTweetNode
    from agent.function_nodes.linkedin_arcade import LinkedInPostUpdateNode
    from agent.function_nodes.discord_arcade import DiscordSendMessageNode
    
    # Create nodes
    gmail_node = GmailSendEmailNode()
    slack_node = SlackSendMessageNode()
    x_node = XPostTweetNode()
    linkedin_node = LinkedInPostUpdateNode()
    discord_node = DiscordSendMessageNode()
    
    print("✅ All nodes created successfully")
    
    # Test that they have the required methods
    for node in [gmail_node, slack_node, x_node, linkedin_node, discord_node]:
        assert hasattr(node, 'prep'), f"Node {type(node).__name__} missing prep method"
        assert hasattr(node, 'exec'), f"Node {type(node).__name__} missing exec method"
        assert hasattr(node, 'post'), f"Node {type(node).__name__} missing post method"
    
    print("✅ All nodes have required methods")

def test_node_prep_methods():
    """Test node prep methods with basic data"""
    os.environ['ARCADE_API_KEY'] = 'test_key_123'
    
    from agent.function_nodes.gmail_arcade import GmailSendEmailNode
    
    # Test Gmail node prep
    node = GmailSendEmailNode()
    shared = {
        'user_id': 'test_user',
        'recipient': 'test@example.com',
        'subject': 'Test Subject',
        'body': 'Test Body'
    }
    
    result = node.prep(shared)
    assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
    assert len(result) == 2, f"Expected tuple of length 2, got {len(result)}"
    
    user_id, params = result
    assert user_id == 'test_user', f"Expected 'test_user', got '{user_id}'"
    assert 'recipient' in params, "Missing recipient in params"
    
    print("✅ Gmail node prep method works correctly")

def run_all_tests():
    """Run all basic tests"""
    print("🧪 Running basic Arcade integration tests...")
    
    tests = [
        ("Import Test", test_arcade_imports),
        ("ArcadeClient Test", test_arcade_client_basic),
        ("Node Creation Test", test_node_creation),
        ("Node Prep Test", test_node_prep_methods),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("💥 Some tests failed!")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)