#!/usr/bin/env python3
"""
Team Communication Workflow Demo

This demo showcases coordinated team communications using Google Arcade nodes:
1. Create project update announcement
2. Send Slack notification to team channel
3. Send Gmail summary to stakeholders
4. Post Discord update to developer channel
5. Generate communication report

Usage:
    python team_communication_demo.py
    python team_communication_demo.py --demo  # Demo mode (no real API calls)
"""

import sys
import os
import logging
from typing import Dict, Any

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pocketflow import Flow, Node
from agent.function_nodes.slack_arcade import SlackSendMessageNode, SlackAuthNode
from agent.function_nodes.gmail_arcade import GmailSendEmailNode, GmailAuthNode
from agent.function_nodes.discord_arcade import DiscordSendMessageNode, DiscordAuthNode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Demo mode flag
DEMO_MODE = '--demo' in sys.argv

class ProjectUpdateCreatorNode(Node):
    """Create project update announcements for different communication channels"""
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare project update parameters"""
        return {
            "project_name": shared.get("project_name", "AI Assistant Platform"),
            "version": shared.get("version", "v2.1.0"),
            "status": shared.get("status", "completed"),
            "demo_mode": shared.get("demo_mode", False)
        }
    
    def exec(self, prep_res: Dict[str, Any]):
        """Generate project update content for different channels"""
        logger.info(f"📢 Creating project update for {prep_res['project_name']} {prep_res['version']}")
        
        # Generate channel-specific announcements
        announcements = {
            "slack": {
                "channel": "#general",
                "message": f"""🎉 **{prep_res['project_name']} {prep_res['version']} Update**

Great news team! Our latest release is now {prep_res['status']}! 

Key highlights:
• New features deployed successfully
• Performance improvements implemented
• Bug fixes and stability enhancements

Thanks to everyone who contributed to this release! 🚀

#ProjectUpdate #TeamWork"""
            },
            "gmail": {
                "recipient": "stakeholders@company.com",
                "subject": f"Project Update: {prep_res['project_name']} {prep_res['version']} - {prep_res['status'].title()}",
                "body": f"""Dear Stakeholders,

I'm pleased to inform you that {prep_res['project_name']} {prep_res['version']} has been successfully {prep_res['status']}.

## Project Summary
- **Project**: {prep_res['project_name']}
- **Version**: {prep_res['version']}
- **Status**: {prep_res['status'].title()}
- **Date**: January 15, 2024

## Key Achievements
✅ All planned features have been implemented
✅ Quality assurance testing completed
✅ Performance benchmarks exceeded expectations
✅ Security review passed

## Next Steps
- Monitor system performance
- Gather user feedback
- Plan for next iteration

Thank you for your continued support.

Best regards,
The Development Team

---
This message was sent through our automated project communication workflow.
"""
            },
            "discord": {
                "channel": "dev-updates",
                "message": f"""🔧 **Developer Update: {prep_res['project_name']} {prep_res['version']}**

Hey devs! 👋

Our latest build is {prep_res['status']} and ready for action!

**Technical Details:**
```
Version: {prep_res['version']}
Status: {prep_res['status'].title()}
Build: Stable
Tests: All passing ✅
```

**What's New:**
- Enhanced API performance
- Improved error handling
- Better logging and monitoring
- Updated documentation

Time to celebrate! 🎉 Great work everyone!

Feel free to reach out if you have any questions or need help with the new features.

Happy coding! 💻"""
            }
        }
        
        if prep_res["demo_mode"]:
            # Add demo flag to the metadata rather than the announcements dict
            logger.info("🎭 DEMO: Generated sample announcements for all channels")
        
        return announcements
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]):
        """Store the generated announcements"""
        shared["announcements"] = exec_res
        # Populate specific fields for each platform
        shared["message"] = exec_res["slack"]["message"]
        shared["channel"] = exec_res["slack"]["channel"]
        shared["recipient"] = exec_res["gmail"]["recipient"]
        shared["subject"] = exec_res["gmail"]["subject"]
        shared["body"] = exec_res["gmail"]["body"]
        shared["discord_message"] = exec_res["discord"]["message"]
        shared["discord_channel"] = exec_res["discord"]["channel"]
        
        logger.info("📝 Project announcements created for all communication channels")
        return "announcements_ready"

class DemoSlackSendMessageNode(SlackSendMessageNode):
    """Slack Send Message Node with demo mode support"""
    
    def exec(self, inputs):
        """Execute Slack message sending with demo mode handling"""
        if hasattr(self, 'demo_mode') and self.demo_mode:
            user_id, message_params = inputs
            logger.info(f"🎭 DEMO: Simulating Slack message to {message_params['channel']}")
            return {
                "message_id": "demo_slack_msg_12345",
                "status": "sent",
                "channel": message_params["channel"],
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

class DemoDiscordSendMessageNode(DiscordSendMessageNode):
    """Discord Send Message Node with demo mode support"""
    
    def exec(self, inputs):
        """Execute Discord message sending with demo mode handling"""
        if hasattr(self, 'demo_mode') and self.demo_mode:
            user_id, message_params = inputs
            logger.info(f"🎭 DEMO: Simulating Discord message to {message_params['channel']}")
            return {
                "message_id": "demo_discord_msg_12345",
                "status": "sent",
                "channel": message_params["channel"],
                "demo": True
            }
        else:
            return super().exec(inputs)
    
    def prep(self, shared: Dict[str, Any]):
        """Prepare with demo mode awareness"""
        self.demo_mode = shared.get("demo_mode", False)
        return super().prep(shared)

class CommunicationReportNode(Node):
    """Generate a comprehensive communication report"""
    
    def prep(self, shared: Dict[str, Any]):
        """Gather all communication results"""
        return {
            "project_name": shared.get("project_name", "Unknown Project"),
            "version": shared.get("version", "Unknown Version"),
            "slack_result": shared.get("slack_send_result", {}),
            "gmail_result": shared.get("gmail_send_result", {}),
            "discord_result": shared.get("discord_send_result", {}),
            "demo_mode": shared.get("demo_mode", False)
        }
    
    def exec(self, prep_res: Dict[str, Any]):
        """Generate comprehensive communication report"""
        logger.info("📊 Generating Team Communication Report")
        
        report = {
            "project_info": {
                "name": prep_res["project_name"],
                "version": prep_res["version"],
                "communication_timestamp": "2024-01-15 14:30:00"
            },
            "channels": {
                "slack": {
                    "sent": prep_res["slack_result"].get("status") == "sent",
                    "message_id": prep_res["slack_result"].get("message_id"),
                    "channel": prep_res["slack_result"].get("channel", "#general"),
                    "platform": "Slack"
                },
                "gmail": {
                    "sent": prep_res["gmail_result"].get("status") == "sent",
                    "message_id": prep_res["gmail_result"].get("message_id"),
                    "recipients": "stakeholders@company.com",
                    "platform": "Gmail"
                },
                "discord": {
                    "sent": prep_res["discord_result"].get("status") == "sent",
                    "message_id": prep_res["discord_result"].get("message_id"),
                    "channel": prep_res["discord_result"].get("channel", "dev-updates"),
                    "platform": "Discord"
                }
            },
            "summary": {
                "total_channels": 3,
                "successful_sends": 0,
                "failed_sends": 0,
                "demo_mode": prep_res["demo_mode"]
            }
        }
        
        # Count successful and failed sends
        for channel, data in report["channels"].items():
            if data.get("sent"):
                report["summary"]["successful_sends"] += 1
            else:
                report["summary"]["failed_sends"] += 1
        
        # Calculate success rate
        total = report["summary"]["total_channels"]
        success = report["summary"]["successful_sends"]
        report["summary"]["success_rate"] = f"{success}/{total}" if total > 0 else "0/0"
        
        # Log report details
        logger.info(f"📈 Communication Results for {prep_res['project_name']} {prep_res['version']}:")
        logger.info(f"   Slack: {'✅ Sent' if report['channels']['slack']['sent'] else '❌ Failed'}")
        logger.info(f"   Gmail: {'✅ Sent' if report['channels']['gmail']['sent'] else '❌ Failed'}")
        logger.info(f"   Discord: {'✅ Sent' if report['channels']['discord']['sent'] else '❌ Failed'}")
        logger.info(f"   Success Rate: {report['summary']['success_rate']}")
        
        return report
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]):
        """Store the final communication report"""
        shared["communication_report"] = exec_res
        logger.info("🎉 Team Communication Workflow completed successfully!")
        return "communication_complete"

def create_team_communication_workflow():
    """Create and return the team communication workflow"""
    
    # Create nodes
    update_creator = ProjectUpdateCreatorNode()
    slack_send = DemoSlackSendMessageNode()
    gmail_send = DemoGmailSendEmailNode()
    discord_send = DemoDiscordSendMessageNode()
    report_generator = CommunicationReportNode()
    
    # Connect nodes - update creation first, then parallel sending, then report
    update_creator >> slack_send
    update_creator >> gmail_send
    update_creator >> discord_send
    
    # All sends connect to report generator
    slack_send >> report_generator
    gmail_send >> report_generator
    discord_send >> report_generator
    
    # Create flow
    return Flow(start=update_creator)

def main():
    """Main function to run the team communication demo"""
    print("🎭 Team Communication Workflow Demo")
    print("=" * 50)
    
    if DEMO_MODE:
        print("🎪 Running in DEMO MODE")
        print("   No real API calls will be made")
    else:
        print("🔴 Running in LIVE MODE")
        print("   Real communication API calls will be made")
        print("   Make sure ARCADE_API_KEY is set!")
    
    print()
    
    # Create shared store
    shared = {
        "demo_mode": DEMO_MODE,
        "user_id": "demo_user_123",
        "project_name": "AI Assistant Platform",
        "version": "v2.1.0",
        "status": "completed",
        # These will be populated by the update creator
        "message": "",
        "channel": "",
        "recipient": "",
        "subject": "",
        "body": "",
        "discord_message": "",
        "discord_channel": ""
    }
    
    try:
        # Create and run the workflow
        workflow = create_team_communication_workflow()
        result = workflow.run(shared)
        
        print("\n📋 Final Results:")
        print(f"   Workflow Action: {result}")
        
        if "communication_report" in shared:
            report = shared["communication_report"]
            print(f"   Project: {report['project_info']['name']} {report['project_info']['version']}")
            print(f"   Channels: {report['summary']['total_channels']}")
            print(f"   Successful: {report['summary']['successful_sends']}")
            print(f"   Failed: {report['summary']['failed_sends']}")
            print(f"   Success Rate: {report['summary']['success_rate']}")
            
            # Show channel details
            print("\n📊 Channel Details:")
            for channel, data in report["channels"].items():
                status = "✅ Sent" if data.get("sent") else "❌ Failed"
                print(f"   {data['platform']}: {status}")
        
        print("\n🎉 Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())