#!/usr/bin/env python3
"""
Customer Support Workflow Demo (Function Nodes Only)

This demo showcases multi-channel customer support using真实 function_nodes:
1. Read emails for customer inquiries
2. Send acknowledgment emails
3. Send Slack notification to support team

Usage:
    python customer_support_demo.py
"""
import sys
import os
from pocketflow import Flow
from agent.function_nodes.gmail_arcade import GmailReadEmailsNode, GmailSendEmailNode
from agent.function_nodes.slack_arcade import SlackSendMessageNode

def check_api_key():
    if not os.environ.get("ARCADE_API_KEY"):
        print("[ERROR] ARCADE_API_KEY is not set. Please export your Arcade API key.")
        exit(1)

def create_customer_support_workflow():
    read_emails = GmailReadEmailsNode()
    send_email = GmailSendEmailNode()
    slack_notify = SlackSendMessageNode()
    read_emails >> send_email >> slack_notify
    return Flow(start=read_emails)

def main():
    check_api_key()
    shared = {
        "user_id": "support_agent_123",
        "max_results": 5,
        "recipient": "customer@example.com",
        "subject": "Support Request Received",
        "body": "Thank you for contacting support. We have received your inquiry and will respond soon.",
        "channel": "#customer-support",
        "message": "A new customer inquiry has been received and acknowledged."
    }
    try:
        workflow = create_customer_support_workflow()
        result = workflow.run(shared)
        print("\n[RESULT] Customer support workflow completed.")
        print("Emails read:", shared.get("gmail_emails"))
        print("Email send result:", shared.get("gmail_send_result"))
        print("Slack notify result:", shared.get("slack_send_result"))
    except ImportError as e:
        print("Lack gmail_arcade or slack_arcade nodes to run")
        exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        exit(1)

if __name__ == "__main__":
    main()