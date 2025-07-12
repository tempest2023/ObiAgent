#!/usr/bin/env python3
"""
Customer Support Workflow Demo

This demo showcases multi-channel customer support using Google Arcade nodes:
1. Monitor Gmail for customer inquiries
2. Categorize and prioritize inquiries
3. Route responses to appropriate channels
4. Send acknowledgment emails
5. Generate support metrics report

Usage:
    python customer_support_demo.py
    python customer_support_demo.py --demo  # Demo mode (no real API calls)
"""

import sys
import os
import logging
from typing import Dict, Any, List

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pocketflow import Flow, Node
from agent.function_nodes.gmail_arcade import (
    GmailReadEmailsNode, 
    GmailSendEmailNode, 
    GmailSearchEmailsNode,
    GmailAuthNode
)
from agent.function_nodes.slack_arcade import SlackSendMessageNode, SlackAuthNode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Demo mode flag
DEMO_MODE = '--demo' in sys.argv

class CustomerInquiryMonitorNode(Node):
    """Monitor customer inquiries from various channels"""
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare monitoring parameters"""
        return {
            "max_emails": shared.get("max_emails", 10),
            "demo_mode": shared.get("demo_mode", False)
        }
    
    def exec(self, prep_res: Dict[str, Any]):
        """Monitor for new customer inquiries"""
        logger.info("📧 Monitoring customer inquiries...")
        
        if prep_res["demo_mode"]:
            # Generate demo customer inquiries
            inquiries = [
                {
                    "id": "inquiry_001",
                    "sender": "customer1@example.com",
                    "subject": "Problem with login",
                    "body": "I can't log into my account. Please help.",
                    "priority": "high",
                    "category": "technical",
                    "timestamp": "2024-01-15 09:30:00"
                },
                {
                    "id": "inquiry_002",
                    "sender": "customer2@example.com",
                    "subject": "Billing question",
                    "body": "I have a question about my last invoice.",
                    "priority": "medium",
                    "category": "billing",
                    "timestamp": "2024-01-15 10:15:00"
                },
                {
                    "id": "inquiry_003",
                    "sender": "customer3@example.com",
                    "subject": "Feature request",
                    "body": "Would love to see dark mode support.",
                    "priority": "low",
                    "category": "feature_request",
                    "timestamp": "2024-01-15 11:00:00"
                }
            ]
            logger.info(f"🎭 DEMO: Generated {len(inquiries)} sample customer inquiries")
            return inquiries
        else:
            # In live mode, this would read actual emails
            return []
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: List[Dict[str, Any]]):
        """Store customer inquiries"""
        shared["customer_inquiries"] = exec_res
        shared["inquiry_count"] = len(exec_res)
        logger.info(f"📥 Found {len(exec_res)} customer inquiries")
        return "inquiries_found" if exec_res else "no_inquiries"

class InquiryCategorizerNode(Node):
    """Categorize and prioritize customer inquiries"""
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare categorization parameters"""
        return {
            "inquiries": shared.get("customer_inquiries", []),
            "demo_mode": shared.get("demo_mode", False)
        }
    
    def exec(self, prep_res: Dict[str, Any]):
        """Categorize inquiries by type and priority"""
        logger.info("🏷️ Categorizing customer inquiries...")
        
        inquiries = prep_res["inquiries"]
        categorized = {
            "high_priority": [],
            "medium_priority": [],
            "low_priority": [],
            "technical": [],
            "billing": [],
            "feature_request": [],
            "general": []
        }
        
        for inquiry in inquiries:
            # Categorize by priority
            priority = inquiry.get("priority", "medium")
            categorized[f"{priority}_priority"].append(inquiry)
            
            # Categorize by type
            category = inquiry.get("category", "general")
            categorized[category].append(inquiry)
        
        if prep_res["demo_mode"]:
            logger.info("🎭 DEMO: Categorized inquiries by priority and type")
        
        return categorized
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]):
        """Store categorized inquiries"""
        shared["categorized_inquiries"] = exec_res
        
        # Log categorization results
        logger.info("📊 Categorization Results:")
        logger.info(f"   High Priority: {len(exec_res['high_priority'])}")
        logger.info(f"   Medium Priority: {len(exec_res['medium_priority'])}")
        logger.info(f"   Low Priority: {len(exec_res['low_priority'])}")
        logger.info(f"   Technical: {len(exec_res['technical'])}")
        logger.info(f"   Billing: {len(exec_res['billing'])}")
        logger.info(f"   Feature Requests: {len(exec_res['feature_request'])}")
        
        return "categorized"

class AutoResponseNode(Node):
    """Generate automatic responses for customer inquiries"""
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare auto-response parameters"""
        return {
            "categorized_inquiries": shared.get("categorized_inquiries", {}),
            "demo_mode": shared.get("demo_mode", False)
        }
    
    def exec(self, prep_res: Dict[str, Any]):
        """Generate appropriate responses"""
        logger.info("🤖 Generating automatic responses...")
        
        responses = []
        categorized = prep_res["categorized_inquiries"]
        
        # Generate responses for high priority inquiries
        for inquiry in categorized.get("high_priority", []):
            response = {
                "inquiry_id": inquiry["id"],
                "recipient": inquiry["sender"],
                "subject": f"Re: {inquiry['subject']} - Urgent Support",
                "body": f"""Dear Valued Customer,

Thank you for contacting us regarding: {inquiry['subject']}

We have received your inquiry and understand the urgency. Our technical team is actively working on your issue and will provide a solution within 2 hours.

Your ticket number is: {inquiry['id']}

We appreciate your patience and will keep you updated on our progress.

Best regards,
Customer Support Team
""",
                "priority": "high",
                "type": "urgent_response"
            }
            responses.append(response)
        
        # Generate responses for medium priority inquiries
        for inquiry in categorized.get("medium_priority", []):
            response = {
                "inquiry_id": inquiry["id"],
                "recipient": inquiry["sender"],
                "subject": f"Re: {inquiry['subject']} - We're Here to Help",
                "body": f"""Dear Customer,

Thank you for reaching out to us about: {inquiry['subject']}

We have received your inquiry and will respond within 24 hours with a detailed solution.

Your ticket number is: {inquiry['id']}

In the meantime, please feel free to check our FAQ section or contact us if you have any urgent concerns.

Best regards,
Customer Support Team
""",
                "priority": "medium",
                "type": "standard_response"
            }
            responses.append(response)
        
        # Generate responses for low priority inquiries
        for inquiry in categorized.get("low_priority", []):
            response = {
                "inquiry_id": inquiry["id"],
                "recipient": inquiry["sender"],
                "subject": f"Re: {inquiry['subject']} - Thank You for Your Feedback",
                "body": f"""Dear Customer,

Thank you for your message about: {inquiry['subject']}

We appreciate your feedback and suggestions. Our team will review your request and get back to you within 48 hours.

Your ticket number is: {inquiry['id']}

We value your input and look forward to serving you better.

Best regards,
Customer Support Team
""",
                "priority": "low",
                "type": "acknowledgment"
            }
            responses.append(response)
        
        if prep_res["demo_mode"]:
            logger.info(f"🎭 DEMO: Generated {len(responses)} automatic responses")
        
        return responses
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: List[Dict[str, Any]]):
        """Store generated responses"""
        shared["auto_responses"] = exec_res
        logger.info(f"📤 Generated {len(exec_res)} automatic responses")
        return "responses_generated"

class DemoGmailSendEmailNode(GmailSendEmailNode):
    """Gmail Send Email Node with demo mode support"""
    
    def exec(self, inputs):
        """Execute email sending with demo mode handling"""
        if hasattr(self, 'demo_mode') and self.demo_mode:
            user_id, email_params = inputs
            logger.info(f"🎭 DEMO: Simulating email to {email_params['recipient']}")
            return {
                "message_id": f"demo_response_{hash(email_params['recipient']) % 10000}",
                "status": "sent",
                "demo": True
            }
        else:
            return super().exec(inputs)
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare with demo mode awareness"""
        self.demo_mode = shared.get("demo_mode", False)
        return super().prep(shared)

class ResponseSenderNode(Node):
    """Send auto-generated responses to customers"""
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare response sending parameters"""
        return {
            "responses": shared.get("auto_responses", []),
            "demo_mode": shared.get("demo_mode", False)
        }
    
    def exec(self, prep_res: Dict[str, Any]):
        """Send responses to customers"""
        logger.info("📧 Sending customer responses...")
        
        responses = prep_res["responses"]
        sent_results = []
        
        for response in responses:
            if prep_res["demo_mode"]:
                # Simulate sending
                result = {
                    "inquiry_id": response["inquiry_id"],
                    "recipient": response["recipient"],
                    "status": "sent",
                    "message_id": f"demo_msg_{hash(response['recipient']) % 10000}",
                    "demo": True
                }
                logger.info(f"🎭 DEMO: Sent response to {response['recipient']}")
            else:
                # In live mode, this would send actual emails
                result = {
                    "inquiry_id": response["inquiry_id"],
                    "recipient": response["recipient"],
                    "status": "pending",
                    "message_id": None
                }
            
            sent_results.append(result)
        
        return sent_results
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: List[Dict[str, Any]]):
        """Store sending results"""
        shared["response_results"] = exec_res
        sent_count = len([r for r in exec_res if r["status"] == "sent"])
        logger.info(f"📤 Sent {sent_count} customer responses")
        return "responses_sent"

class DemoSlackSendMessageNode(SlackSendMessageNode):
    """Slack Send Message Node with demo mode support"""
    
    def exec(self, inputs):
        """Execute Slack message sending with demo mode handling"""
        if hasattr(self, 'demo_mode') and self.demo_mode:
            user_id, message_params = inputs
            logger.info(f"🎭 DEMO: Simulating Slack message to {message_params['channel']}")
            return {
                "message_id": "demo_slack_support_msg",
                "status": "sent",
                "demo": True
            }
        else:
            return super().exec(inputs)
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare with demo mode awareness"""
        self.demo_mode = shared.get("demo_mode", False)
        return super().prep(shared)

class SupportMetricsNode(Node):
    """Generate customer support metrics and reports"""
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare metrics parameters"""
        return {
            "inquiry_count": shared.get("inquiry_count", 0),
            "categorized_inquiries": shared.get("categorized_inquiries", {}),
            "response_results": shared.get("response_results", []),
            "demo_mode": shared.get("demo_mode", False)
        }
    
    def exec(self, prep_res: Dict[str, Any]):
        """Generate comprehensive support metrics"""
        logger.info("📊 Generating customer support metrics...")
        
        categorized = prep_res["categorized_inquiries"]
        response_results = prep_res["response_results"]
        
        metrics = {
            "summary": {
                "total_inquiries": prep_res["inquiry_count"],
                "responses_sent": len([r for r in response_results if r["status"] == "sent"]),
                "response_rate": 0,
                "demo_mode": prep_res["demo_mode"]
            },
            "by_priority": {
                "high": len(categorized.get("high_priority", [])),
                "medium": len(categorized.get("medium_priority", [])),
                "low": len(categorized.get("low_priority", []))
            },
            "by_category": {
                "technical": len(categorized.get("technical", [])),
                "billing": len(categorized.get("billing", [])),
                "feature_request": len(categorized.get("feature_request", [])),
                "general": len(categorized.get("general", []))
            },
            "performance": {
                "average_response_time": "< 1 hour",
                "satisfaction_score": "4.5/5",
                "resolution_rate": "95%"
            }
        }
        
        # Calculate response rate
        if prep_res["inquiry_count"] > 0:
            metrics["summary"]["response_rate"] = f"{metrics['summary']['responses_sent']}/{prep_res['inquiry_count']}"
        
        # Log metrics
        logger.info("📈 Support Metrics:")
        logger.info(f"   Total Inquiries: {metrics['summary']['total_inquiries']}")
        logger.info(f"   Responses Sent: {metrics['summary']['responses_sent']}")
        logger.info(f"   Response Rate: {metrics['summary']['response_rate']}")
        logger.info(f"   High Priority: {metrics['by_priority']['high']}")
        logger.info(f"   Technical Issues: {metrics['by_category']['technical']}")
        
        return metrics
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]):
        """Store support metrics"""
        shared["support_metrics"] = exec_res
        
        # Send metrics to support team via Slack
        shared["message"] = f"""📊 **Customer Support Daily Report**

📈 **Today's Metrics:**
• Total Inquiries: {exec_res['summary']['total_inquiries']}
• Responses Sent: {exec_res['summary']['responses_sent']}
• Response Rate: {exec_res['summary']['response_rate']}

🎯 **By Priority:**
• High: {exec_res['by_priority']['high']}
• Medium: {exec_res['by_priority']['medium']}
• Low: {exec_res['by_priority']['low']}

📋 **By Category:**
• Technical: {exec_res['by_category']['technical']}
• Billing: {exec_res['by_category']['billing']}
• Feature Requests: {exec_res['by_category']['feature_request']}
• General: {exec_res['by_category']['general']}

Great work team! 🎉"""
        shared["channel"] = "#customer-support"
        
        logger.info("🎉 Customer Support Workflow completed successfully!")
        return "metrics_complete"

def create_customer_support_workflow():
    """Create and return the customer support workflow"""
    
    # Create nodes
    monitor = CustomerInquiryMonitorNode()
    categorizer = InquiryCategorizerNode()
    auto_responder = AutoResponseNode()
    response_sender = ResponseSenderNode()
    slack_notify = DemoSlackSendMessageNode()
    metrics = SupportMetricsNode()
    
    # Connect nodes in sequence
    monitor >> categorizer >> auto_responder >> response_sender >> metrics >> slack_notify
    
    # Create flow
    return Flow(start=monitor)

def main():
    """Main function to run the customer support demo"""
    print("🎭 Customer Support Workflow Demo")
    print("=" * 50)
    
    if DEMO_MODE:
        print("🎪 Running in DEMO MODE")
        print("   No real API calls will be made")
    else:
        print("🔴 Running in LIVE MODE")
        print("   Real customer support API calls will be made")
        print("   Make sure ARCADE_API_KEY is set!")
    
    print()
    
    # Create shared store
    shared = {
        "demo_mode": DEMO_MODE,
        "user_id": "support_agent_123",
        "max_emails": 10,
        # These will be populated by the workflow
        "customer_inquiries": [],
        "categorized_inquiries": {},
        "auto_responses": [],
        "response_results": [],
        "support_metrics": {}
    }
    
    try:
        # Create and run the workflow
        workflow = create_customer_support_workflow()
        result = workflow.run(shared)
        
        print("\n📋 Final Results:")
        print(f"   Workflow Action: {result}")
        
        if "support_metrics" in shared:
            metrics = shared["support_metrics"]
            print(f"   Total Inquiries: {metrics['summary']['total_inquiries']}")
            print(f"   Responses Sent: {metrics['summary']['responses_sent']}")
            print(f"   Response Rate: {metrics['summary']['response_rate']}")
            
            # Show priority breakdown
            print("\n📊 Priority Breakdown:")
            for priority, count in metrics["by_priority"].items():
                print(f"   {priority.title()}: {count}")
            
            # Show category breakdown
            print("\n📋 Category Breakdown:")
            for category, count in metrics["by_category"].items():
                print(f"   {category.replace('_', ' ').title()}: {count}")
        
        print("\n🎉 Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())