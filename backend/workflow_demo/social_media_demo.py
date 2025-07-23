#!/usr/bin/env python3
"""
Social Media Workflow Demo (Function Nodes Only)

This demo showcases multi-platform content distribution using真实 function_nodes:
1. Post to Twitter/X
2. Post to LinkedIn
3. Send email summary

Usage:
    python social_media_demo.py
"""
import os
from pocketflow import Flow
from agent.function_nodes.x_arcade import XPostTweetNode
from agent.function_nodes.linkedin_arcade import LinkedInPostUpdateNode
from agent.function_nodes.gmail_arcade import GmailSendEmailNode

def check_api_key():
    if not os.environ.get("ARCADE_API_KEY"):
        print("[ERROR] ARCADE_API_KEY is not set. Please export your Arcade API key.")
        exit(1)

def create_social_media_workflow():
    twitter_post = XPostTweetNode()
    linkedin_post = LinkedInPostUpdateNode()
    email_send = GmailSendEmailNode()
    # 并行分支，全部用 function_nodes
    twitter_post >> email_send
    linkedin_post >> email_send
    return Flow(start=twitter_post)

def main():
    check_api_key()
    shared = {
        "user_id": "demo_user_123",
        "text": "Exciting developments in AI! #TechUpdate #AI",
        "visibility": "PUBLIC",
        "media_url": None,
        "recipient": "team@example.com",
        "subject": "Weekly Update: AI Insights",
        "body": "This is an automated update on AI developments."
    }
    try:
        workflow = create_social_media_workflow()
        result = workflow.run(shared)
        print("\n[RESULT] Social media workflow completed.")
        print("Twitter post result:", shared.get("x_post_result"))
        print("LinkedIn post result:", shared.get("linkedin_post_result"))
        print("Email send result:", shared.get("gmail_send_result"))
    except ImportError as e:
        print("Lack x_arcade, linkedin_arcade, or gmail_arcade nodes to run")
        exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        exit(1)

if __name__ == "__main__":
    main()