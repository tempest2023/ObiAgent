#!/usr/bin/env python3
"""
Team Communication Workflow Demo (Function Nodes Only)

This demo showcases coordinated team communications using真实 function_nodes:
1. Send Slack notification to team channel
2. Send Gmail summary to stakeholders
3. Post Discord update to developer channel

Usage:
    python team_communication_demo.py
"""
import sys
import os
from pocketflow import Flow
from agent.function_nodes.slack_arcade import SlackSendMessageNode
from agent.function_nodes.gmail_arcade import GmailSendEmailNode
from agent.function_nodes.discord_arcade import DiscordSendMessageNode

def check_api_key():
    if not os.environ.get("ARCADE_API_KEY"):
        print("[ERROR] ARCADE_API_KEY is not set. Please export your Arcade API key.")
        exit(1)

def create_team_communication_workflow():
    slack_send = SlackSendMessageNode()
    gmail_send = GmailSendEmailNode()
    discord_send = DiscordSendMessageNode()
    # 并行分支，全部用 function_nodes
    slack_send >> gmail_send
    discord_send >> gmail_send
    return Flow(start=slack_send)

def main():
    check_api_key()
    shared = {
        "user_id": "demo_user_123",
        "channel": "#general",
        "message": "Project update: v2.1.0 released!",
        "recipient": "stakeholders@company.com",
        "subject": "Project Update: v2.1.0 Released",
        "body": "The latest version of our project has been released.",
        "discord_channel": "dev-updates",
        "discord_message": "Developer update: v2.1.0 is now live!"
    }
    try:
        workflow = create_team_communication_workflow()
        result = workflow.run(shared)
        print("\n[RESULT] Team communication workflow completed.")
        print("Slack send result:", shared.get("slack_send_result"))
        print("Gmail send result:", shared.get("gmail_send_result"))
        print("Discord send result:", shared.get("discord_send_result"))
    except ImportError as e:
        print("Lack slack_arcade, gmail_arcade, or discord_arcade nodes to run")
        exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        exit(1)

if __name__ == "__main__":
    main()