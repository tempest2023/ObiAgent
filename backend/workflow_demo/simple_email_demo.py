#!/usr/bin/env python3
"""
Simple Email Workflow Demo

This demo showcases basic Gmail operations using Google Arcade nodes:
1. Check authentication status
2. Send a welcome email
3. Read recent emails
4. Search for specific emails

Usage:
    python simple_email_demo.py
    python simple_email_demo.py --demo  # Demo mode (no real API calls)
"""

import asyncio
import sys
import os
import logging
from typing import Dict, Any

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pocketflow import Flow, Node
from agent.function_nodes.gmail_arcade import (
    GmailAuthNode,
    GmailSendEmailNode,
    GmailReadEmailsNode,
    GmailSearchEmailsNode
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Demo mode flag
DEMO_MODE = '--demo' in sys.argv

class DemoSetupNode(Node):
    """Initialize the demo with user information and demo settings"""
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare demo settings"""
        return {
            "demo_mode": DEMO_MODE,
            "user_id": "demo_user_123"
        }
    
    def exec(self, prep_res: Dict[str, Any]):
        """Set up demo environment"""
        logger.info("🎭 Setting up Simple Email Demo")
        
        if prep_res["demo_mode"]:
            logger.info("🎪 Running in DEMO MODE - no real API calls will be made")
            return {
                "status": "demo_initialized",
                "message": "Demo mode active - simulating all operations"
            }
        else:
            logger.info("🔴 Running in LIVE MODE - real API calls will be made")
            return {
                "status": "live_initialized",
                "message": "Live mode active - using real Arcade API"
            }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]):
        """Store demo configuration"""
        shared["demo_mode"] = prep_res["demo_mode"]
        shared["user_id"] = prep_res["user_id"]
        shared["setup_result"] = exec_res
        
        # Set up demo data if in demo mode
        if prep_res["demo_mode"]:
            shared["demo_responses"] = {
                "auth_status": {
                    "status": "authenticated",
                    "user_id": prep_res["user_id"]
                },
                "email_sent": {
                    "message_id": "demo_msg_12345",
                    "status": "sent"
                },
                "emails_read": [
                    {
                        "id": "email_001",
                        "subject": "Welcome to our service",
                        "sender": "welcome@example.com",
                        "snippet": "Thank you for joining us..."
                    },
                    {
                        "id": "email_002", 
                        "subject": "Your account is ready",
                        "sender": "support@example.com",
                        "snippet": "Your account has been activated..."
                    }
                ],
                "search_results": [
                    {
                        "id": "email_003",
                        "subject": "Important update",
                        "sender": "updates@example.com",
                        "snippet": "We have an important update..."
                    }
                ]
            }
        
        return "setup_complete"

class DemoGmailAuthNode(GmailAuthNode):
    """Gmail Auth Node with demo mode support"""
    
    def exec(self, inputs):
        """Execute authentication with demo mode handling"""
        if hasattr(self, 'demo_mode') and self.demo_mode:
            user_id, auth_params = inputs
            logger.info(f"🎭 DEMO: Simulating Gmail authentication for user {user_id}")
            return {
                "status": "already_authenticated",
                "user_id": user_id,
                "demo": True
            }
        else:
            return super().exec(inputs)
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare with demo mode awareness"""
        self.demo_mode = shared.get("demo_mode", False)
        return super().prep(shared)

class DemoGmailSendEmailNode(GmailSendEmailNode):
    """Gmail Send Email Node with demo mode support"""
    
    def exec(self, inputs):
        """Execute email sending with demo mode handling"""
        if hasattr(self, 'demo_mode') and self.demo_mode:
            user_id, email_params = inputs
            logger.info(f"🎭 DEMO: Simulating sending email to {email_params['recipient']}")
            return {
                "message_id": "demo_msg_12345",
                "status": "sent",
                "demo": True
            }
        else:
            return super().exec(inputs)
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare with demo mode awareness"""
        self.demo_mode = shared.get("demo_mode", False)
        return super().prep(shared)

class DemoGmailReadEmailsNode(GmailReadEmailsNode):
    """Gmail Read Emails Node with demo mode support"""
    
    def exec(self, inputs):
        """Execute email reading with demo mode handling"""
        if hasattr(self, 'demo_mode') and self.demo_mode:
            user_id, read_params = inputs
            logger.info(f"🎭 DEMO: Simulating reading {read_params['max_results']} emails")
            return [
                {
                    "id": "email_001",
                    "subject": "Welcome to our service",
                    "sender": "welcome@example.com",
                    "snippet": "Thank you for joining us...",
                    "demo": True
                },
                {
                    "id": "email_002",
                    "subject": "Your account is ready", 
                    "sender": "support@example.com",
                    "snippet": "Your account has been activated...",
                    "demo": True
                }
            ]
        else:
            return super().exec(inputs)
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare with demo mode awareness"""
        self.demo_mode = shared.get("demo_mode", False)
        return super().prep(shared)

class DemoGmailSearchEmailsNode(GmailSearchEmailsNode):
    """Gmail Search Emails Node with demo mode support"""
    
    def exec(self, inputs):
        """Execute email search with demo mode handling"""
        if hasattr(self, 'demo_mode') and self.demo_mode:
            user_id, search_params = inputs
            logger.info(f"🎭 DEMO: Simulating search for '{search_params['query']}'")
            return [
                {
                    "id": "email_003",
                    "subject": "Important update",
                    "sender": "updates@example.com",
                    "snippet": "We have an important update...",
                    "demo": True
                }
            ]
        else:
            return super().exec(inputs)
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare with demo mode awareness"""
        self.demo_mode = shared.get("demo_mode", False)
        return super().prep(shared)

class EmailWorkflowSummaryNode(Node):
    """Summarize the email workflow results"""
    
    def prep(self, shared: Dict[str, Any]):
        """Gather all workflow results"""
        return {
            "auth_status": shared.get("gmail_auth_status", {}),
            "email_sent": shared.get("gmail_send_result", {}),
            "emails_read": shared.get("gmail_emails", []),
            "search_results": shared.get("gmail_search_results", []),
            "demo_mode": shared.get("demo_mode", False)
        }
    
    def exec(self, prep_res: Dict[str, Any]):
        """Generate workflow summary"""
        logger.info("📋 Generating Email Workflow Summary")
        
        summary = {
            "workflow_name": "Simple Email Demo",
            "demo_mode": prep_res["demo_mode"],
            "results": {
                "authentication": prep_res["auth_status"],
                "email_sent": prep_res["email_sent"],
                "emails_read_count": len(prep_res["emails_read"]),
                "search_results_count": len(prep_res["search_results"])
            }
        }
        
        # Log summary
        logger.info(f"✅ Authentication Status: {prep_res['auth_status'].get('status', 'unknown')}")
        logger.info(f"✅ Email Sent: {prep_res['email_sent'].get('status', 'unknown')}")
        logger.info(f"✅ Emails Read: {len(prep_res['emails_read'])} messages")
        logger.info(f"✅ Search Results: {len(prep_res['search_results'])} messages")
        
        return summary
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]):
        """Store the final summary"""
        shared["workflow_summary"] = exec_res
        logger.info("🎉 Simple Email Demo completed successfully!")
        return "workflow_complete"

def create_email_workflow():
    """Create and return the email workflow"""
    
    # Create nodes
    setup_node = DemoSetupNode()
    auth_node = DemoGmailAuthNode()
    send_email_node = DemoGmailSendEmailNode()
    read_emails_node = DemoGmailReadEmailsNode()
    search_emails_node = DemoGmailSearchEmailsNode()
    summary_node = EmailWorkflowSummaryNode()
    
    # Connect nodes in sequence
    setup_node >> auth_node >> send_email_node >> read_emails_node >> search_emails_node >> summary_node
    
    # Create flow
    return Flow(start=setup_node)

def main():
    """Main function to run the simple email demo"""
    print("🎭 Simple Email Workflow Demo")
    print("=" * 50)
    
    if DEMO_MODE:
        print("🎪 Running in DEMO MODE")
        print("   No real API calls will be made")
    else:
        print("🔴 Running in LIVE MODE")
        print("   Real Gmail API calls will be made")
        print("   Make sure ARCADE_API_KEY is set!")
    
    print()
    
    # Create shared store
    shared = {
        "user_id": "demo_user_123",
        "recipient": "demo@example.com",
        "subject": "Hello from Simple Email Demo!",
        "body": "This is a test email sent from the PocketFlow Simple Email Demo workflow.",
        "max_results": 5,
        "search_query": "important update"
    }
    
    try:
        # Create and run the workflow
        workflow = create_email_workflow()
        result = workflow.run(shared)
        
        print("\n📋 Final Results:")
        print(f"   Workflow Action: {result}")
        
        if "workflow_summary" in shared:
            summary = shared["workflow_summary"]
            print(f"   Authentication: {summary['results']['authentication'].get('status', 'unknown')}")
            print(f"   Email Sent: {summary['results']['email_sent'].get('status', 'unknown')}")
            print(f"   Emails Read: {summary['results']['emails_read_count']}")
            print(f"   Search Results: {summary['results']['search_results_count']}")
        
        print("\n🎉 Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())