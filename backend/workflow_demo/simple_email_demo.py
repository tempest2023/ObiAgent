#!/usr/bin/env python3
"""
Simple Email Workflow Demo (Function Nodes Only)

This demo showcases basic Gmail operations using真实 function_nodes:
1. Authenticate
2. Send a welcome email
3. Read recent emails
4. Search for specific emails

Usage:
    python simple_email_demo.py
"""
import os
from pocketflow import Flow
from agent.function_nodes.gmail_arcade import GmailAuthNode, GmailSendEmailNode, GmailReadEmailsNode, GmailSearchEmailsNode

def check_api_key():
    if not os.environ.get("ARCADE_API_KEY"):
        print("[ERROR] ARCADE_API_KEY is not set. Please export your Arcade API key.")
        exit(1)

def create_email_workflow():
    auth = GmailAuthNode()
    send = GmailSendEmailNode()
    read = GmailReadEmailsNode()
    search = GmailSearchEmailsNode()
    auth >> send >> read >> search
    return Flow(start=auth)

def main():
    check_api_key()
    shared = {
        "user_id": "demo_user_123",
        "recipient": "demo@example.com",
        "subject": "Hello from Simple Email Demo!",
        "body": "This is a test email sent from the PocketFlow Simple Email Demo workflow.",
        "max_results": 5,
        "search_query": "important update"
    }
    try:
        workflow = create_email_workflow()
        result = workflow.run(shared)
        print("\n[RESULT] Email workflow completed.")
        print("Authentication status:", shared.get("gmail_auth_status"))
        print("Email sent result:", shared.get("gmail_send_result"))
        print("Emails read:", shared.get("gmail_emails"))
        print("Search results:", shared.get("gmail_search_results"))
    except ImportError as e:
        print("Lack gmail_arcade nodes to run")
        exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        exit(1)

if __name__ == "__main__":
    main()