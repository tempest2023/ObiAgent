#!/usr/bin/env python3
"""
Social Media Workflow Demo

This demo showcases multi-platform content distribution using Google Arcade nodes:
1. Create content for distribution
2. Post to Twitter/X
3. Post to LinkedIn
4. Send email summary
5. Generate activity report

Usage:
    python social_media_demo.py
    python social_media_demo.py --demo  # Demo mode (no real API calls)
"""

import sys
import os
import logging
from typing import Dict, Any

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pocketflow import Flow, Node
from agent.function_nodes.x_arcade import XPostTweetNode, XAuthNode
from agent.function_nodes.linkedin_arcade import LinkedInPostUpdateNode, LinkedInAuthNode
from agent.function_nodes.gmail_arcade import GmailSendEmailNode, GmailAuthNode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Demo mode flag
DEMO_MODE = '--demo' in sys.argv

class ContentCreatorNode(Node):
    """Create content for social media distribution"""
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare content creation parameters"""
        return {
            "topic": shared.get("content_topic", "AI and Technology"),
            "demo_mode": shared.get("demo_mode", False)
        }
    
    def exec(self, prep_res: Dict[str, Any]):
        """Generate content for different platforms"""
        logger.info(f"✍️ Creating content about: {prep_res['topic']}")
        
        # Generate platform-specific content
        content = {
            "twitter": {
                "text": f"🚀 Exciting developments in {prep_res['topic']}! The future is here and it's incredible. #TechUpdate #Innovation",
                "hashtags": ["#TechUpdate", "#Innovation", "#AI"]
            },
            "linkedin": {
                "text": f"""🌟 The Future of {prep_res['topic']}

I'm excited to share some insights about the rapid advancement in {prep_res['topic']}. This technology is transforming how we work and live.

Key highlights:
• Revolutionary capabilities emerging
• Practical applications expanding
• Opportunities for innovation growing

What are your thoughts on these developments? I'd love to hear your perspective!

#Technology #Innovation #Future""",
                "hashtags": ["#Technology", "#Innovation", "#Future"]
            },
            "email": {
                "subject": f"Weekly Update: {prep_res['topic']} Insights",
                "body": f"""Hello,

I wanted to share some exciting developments in {prep_res['topic']} that I've been following this week.

The pace of innovation continues to accelerate, and I believe we're seeing transformative changes that will impact various industries.

I've also shared some thoughts on this topic across our social media channels. Feel free to join the conversation!

Best regards,
The Social Media Team

P.S. This message was sent through our automated content distribution workflow.
"""
            }
        }
        
        if prep_res["demo_mode"]:
            content["demo"] = True
            logger.info("🎭 DEMO: Generated sample content for all platforms")
        
        return content
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]):
        """Store the generated content"""
        shared["content"] = exec_res
        logger.info("📝 Content created for Twitter, LinkedIn, and Email")
        return "content_ready"

class DemoXPostTweetNode(XPostTweetNode):
    """X/Twitter Post Node with demo mode support"""
    
    def exec(self, inputs):
        """Execute tweet posting with demo mode handling"""
        if hasattr(self, 'demo_mode') and self.demo_mode:
            user_id, tweet_params = inputs
            logger.info(f"🎭 DEMO: Simulating Twitter post: {tweet_params['text'][:50]}...")
            return {
                "tweet_id": "demo_tweet_12345",
                "status": "posted",
                "demo": True
            }
        else:
            return super().exec(inputs)
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare with demo mode awareness"""
        self.demo_mode = shared.get("demo_mode", False)
        return super().prep(shared)

class DemoLinkedInPostUpdateNode(LinkedInPostUpdateNode):
    """LinkedIn Post Node with demo mode support"""
    
    def exec(self, inputs):
        """Execute LinkedIn posting with demo mode handling"""
        if hasattr(self, 'demo_mode') and self.demo_mode:
            user_id, post_params = inputs
            logger.info(f"🎭 DEMO: Simulating LinkedIn post: {post_params['text'][:50]}...")
            return {
                "post_id": "demo_linkedin_12345",
                "status": "posted",
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
            logger.info(f"🎭 DEMO: Simulating email to {email_params['recipient']}")
            return {
                "message_id": "demo_email_12345",
                "status": "sent",
                "demo": True
            }
        else:
            return super().exec(inputs)
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare with demo mode awareness"""
        self.demo_mode = shared.get("demo_mode", False)
        return super().prep(shared)

class SocialMediaReportNode(Node):
    """Generate a report of all social media activities"""
    
    def prep(self, shared: Dict[str, Any]):
        """Gather all social media activity results"""
        return {
            "content": shared.get("content", {}),
            "twitter_result": shared.get("x_post_result", {}),
            "linkedin_result": shared.get("linkedin_post_result", {}),
            "email_result": shared.get("gmail_send_result", {}),
            "demo_mode": shared.get("demo_mode", False)
        }
    
    def exec(self, prep_res: Dict[str, Any]):
        """Generate comprehensive activity report"""
        logger.info("📊 Generating Social Media Activity Report")
        
        report = {
            "campaign_name": "Multi-Platform Content Distribution",
            "timestamp": "2024-01-15 10:30:00",
            "platforms": {
                "twitter": {
                    "posted": prep_res["twitter_result"].get("status") == "posted",
                    "post_id": prep_res["twitter_result"].get("tweet_id"),
                    "content_length": len(prep_res["content"].get("twitter", {}).get("text", ""))
                },
                "linkedin": {
                    "posted": prep_res["linkedin_result"].get("status") == "posted",
                    "post_id": prep_res["linkedin_result"].get("post_id"),
                    "content_length": len(prep_res["content"].get("linkedin", {}).get("text", ""))
                },
                "email": {
                    "sent": prep_res["email_result"].get("status") == "sent",
                    "message_id": prep_res["email_result"].get("message_id"),
                    "subject": prep_res["content"].get("email", {}).get("subject", "")
                }
            },
            "summary": {
                "total_platforms": 3,
                "successful_posts": 0,
                "demo_mode": prep_res["demo_mode"]
            }
        }
        
        # Count successful posts
        for platform, data in report["platforms"].items():
            if data.get("posted") or data.get("sent"):
                report["summary"]["successful_posts"] += 1
        
        # Log report details
        logger.info(f"📈 Campaign Results:")
        logger.info(f"   Twitter: {'✅ Posted' if report['platforms']['twitter']['posted'] else '❌ Failed'}")
        logger.info(f"   LinkedIn: {'✅ Posted' if report['platforms']['linkedin']['posted'] else '❌ Failed'}")
        logger.info(f"   Email: {'✅ Sent' if report['platforms']['email']['sent'] else '❌ Failed'}")
        logger.info(f"   Success Rate: {report['summary']['successful_posts']}/{report['summary']['total_platforms']}")
        
        return report
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]):
        """Store the final report"""
        shared["social_media_report"] = exec_res
        logger.info("🎉 Social Media Workflow completed successfully!")
        return "campaign_complete"

def create_social_media_workflow():
    """Create and return the social media workflow"""
    
    # Create nodes
    content_creator = ContentCreatorNode()
    twitter_post = DemoXPostTweetNode()
    linkedin_post = DemoLinkedInPostUpdateNode()
    email_send = DemoGmailSendEmailNode()
    report_generator = SocialMediaReportNode()
    
    # Connect nodes - content creation first, then parallel posting, then report
    content_creator >> twitter_post
    content_creator >> linkedin_post
    content_creator >> email_send
    
    # All posts connect to report generator
    twitter_post >> report_generator
    linkedin_post >> report_generator
    email_send >> report_generator
    
    # Create flow
    return Flow(start=content_creator)

def main():
    """Main function to run the social media demo"""
    print("🎭 Social Media Workflow Demo")
    print("=" * 50)
    
    if DEMO_MODE:
        print("🎪 Running in DEMO MODE")
        print("   No real API calls will be made")
    else:
        print("🔴 Running in LIVE MODE")
        print("   Real social media API calls will be made")
        print("   Make sure ARCADE_API_KEY is set!")
    
    print()
    
    # Create shared store
    shared = {
        "demo_mode": DEMO_MODE,
        "user_id": "demo_user_123",
        "content_topic": "Artificial Intelligence and Machine Learning",
        # Twitter content
        "text": "",  # Will be populated by content creator
        # LinkedIn content
        "post_text": "",  # Will be populated by content creator
        # Email content
        "recipient": "team@example.com",
        "subject": "",  # Will be populated by content creator
        "body": ""  # Will be populated by content creator
    }
    
    try:
        # Create and run the workflow
        workflow = create_social_media_workflow()
        result = workflow.run(shared)
        
        print("\n📋 Final Results:")
        print(f"   Workflow Action: {result}")
        
        if "social_media_report" in shared:
            report = shared["social_media_report"]
            print(f"   Campaign: {report['campaign_name']}")
            print(f"   Platforms: {report['summary']['total_platforms']}")
            print(f"   Successful Posts: {report['summary']['successful_posts']}")
            print(f"   Success Rate: {report['summary']['successful_posts']}/{report['summary']['total_platforms']}")
            
            # Show platform details
            print("\n📊 Platform Details:")
            for platform, data in report["platforms"].items():
                status = "✅ Success" if (data.get("posted") or data.get("sent")) else "❌ Failed"
                print(f"   {platform.title()}: {status}")
        
        print("\n🎉 Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())