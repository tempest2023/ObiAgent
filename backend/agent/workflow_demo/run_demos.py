#!/usr/bin/env python3
"""
Demo Launcher Script

This script provides an easy way to run all workflow demos with a simple menu interface.

Usage:
    python run_demos.py
    python run_demos.py --demo  # Run all demos in demo mode
"""

import sys
import os
import importlib
import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_api_key():
    if not os.environ.get("ARCADE_API_KEY"):
        print("[ERROR] ARCADE_API_KEY is not set. Please export your Arcade API key.")
        return False
    return True

def run_demo(module_name, display_name):
    print(f"\n=== Running: {display_name} ===")
    if not check_api_key():
        print(f"[SKIP] {display_name}: ARCADE_API_KEY not set.")
        return
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, "main"):
            module.main()
        else:
            print(f"[ERROR] {display_name}: No main() function found.")
    except ImportError as e:
        print(f"Lack required nodes to run {display_name}")
    except Exception as e:
        print(f"[ERROR] {display_name}: {e}")

def main():
    demos = [
        ("backend.workflow_demo.content_research_demo", "Content Research Demo"),
        ("backend.workflow_demo.simple_email_demo", "Simple Email Demo"),
        ("backend.workflow_demo.social_media_demo", "Social Media Demo"),
        ("backend.workflow_demo.team_communication_demo", "Team Communication Demo"),
        ("backend.workflow_demo.customer_support_demo", "Customer Support Demo"),
    ]
    for module_name, display_name in demos:
        run_demo(module_name, display_name)

if __name__ == "__main__":
    main()