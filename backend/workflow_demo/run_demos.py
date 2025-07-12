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
import subprocess
import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Demo mode flag
DEMO_MODE = '--demo' in sys.argv

# Available demos
DEMOS = [
    {
        "name": "Simple Email Demo",
        "file": "simple_email_demo.py",
        "description": "Demonstrates basic Gmail operations (send, read, search)",
        "features": ["Gmail authentication", "Email sending", "Inbox reading", "Email searching"]
    },
    {
        "name": "Social Media Demo",
        "file": "social_media_demo.py",
        "description": "Multi-platform content distribution workflow",
        "features": ["Twitter posting", "LinkedIn updates", "Email notifications", "Activity reporting"]
    },
    {
        "name": "Team Communication Demo",
        "file": "team_communication_demo.py",
        "description": "Coordinated team communications across platforms",
        "features": ["Slack messaging", "Gmail notifications", "Discord updates", "Project announcements"]
    },
    {
        "name": "Customer Support Demo",
        "file": "customer_support_demo.py",
        "description": "Multi-channel customer support workflow",
        "features": ["Inquiry monitoring", "Auto-responses", "Support metrics", "Team notifications"]
    },
    {
        "name": "Content Research Demo",
        "file": "content_research_demo.py",
        "description": "Research and content gathering workflow",
        "features": ["Email research", "Social media trends", "Content analysis", "Research reports"]
    }
]

def print_banner():
    """Print the demo launcher banner"""
    print("🎭 PocketFlow Google Arcade Node Demo Launcher")
    print("=" * 55)
    if DEMO_MODE:
        print("🎪 Running in DEMO MODE - No real API calls will be made")
    else:
        print("🔴 Running in LIVE MODE - Real API calls will be made")
        print("   Make sure ARCADE_API_KEY is set!")
    print()

def print_menu():
    """Print the demo selection menu"""
    print("📋 Available Demos:")
    print()
    
    for i, demo in enumerate(DEMOS, 1):
        print(f"{i}. {demo['name']}")
        print(f"   {demo['description']}")
        print(f"   Features: {', '.join(demo['features'])}")
        print()
    
    print("0. Run All Demos")
    print("q. Quit")
    print()

def run_demo(demo: Dict[str, str]) -> bool:
    """Run a specific demo"""
    print(f"🚀 Starting {demo['name']}...")
    print("-" * 50)
    
    try:
        # Construct command
        cmd = [sys.executable, demo["file"]]
        if DEMO_MODE:
            cmd.append("--demo")
        
        # Run the demo
        result = subprocess.run(cmd, check=True, capture_output=False)
        
        if result.returncode == 0:
            print(f"✅ {demo['name']} completed successfully!")
            return True
        else:
            print(f"❌ {demo['name']} failed with return code {result.returncode}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ {demo['name']} failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error running {demo['name']}: {e}")
        return False

def run_all_demos():
    """Run all demos in sequence"""
    print("🎯 Running All Demos...")
    print("=" * 30)
    
    results = []
    for demo in DEMOS:
        print(f"\n🔄 Starting {demo['name']}...")
        success = run_demo(demo)
        results.append((demo["name"], success))
        
        if success:
            print(f"✅ {demo['name']} - SUCCESS")
        else:
            print(f"❌ {demo['name']} - FAILED")
        
        print("-" * 30)
    
    # Print summary
    print("\n📊 Demo Run Summary:")
    print("=" * 30)
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {name}: {status}")
    
    print(f"\nOverall: {successful}/{total} demos completed successfully")
    
    if successful == total:
        print("🎉 All demos completed successfully!")
    else:
        print("⚠️  Some demos failed. Check the logs above for details.")

def get_user_choice() -> str:
    """Get user's menu choice"""
    while True:
        try:
            choice = input("Select demo (0-5 or 'q' to quit): ").strip().lower()
            
            if choice == 'q':
                return 'q'
            elif choice == '0':
                return '0'
            elif choice in ['1', '2', '3', '4', '5']:
                return choice
            else:
                print("❌ Invalid choice. Please enter 0-5 or 'q'")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            return 'q'
        except EOFError:
            print("\n\n👋 Goodbye!")
            return 'q'

def main():
    """Main demo launcher function"""
    print_banner()
    
    # Check if running in non-interactive mode
    if len(sys.argv) > 1 and sys.argv[1] not in ['--demo']:
        # If a specific demo is requested
        demo_name = sys.argv[1]
        for demo in DEMOS:
            if demo["file"] == demo_name or demo["name"].lower() == demo_name.lower():
                run_demo(demo)
                return
        
        print(f"❌ Demo '{demo_name}' not found")
        return
    
    while True:
        print_menu()
        choice = get_user_choice()
        
        if choice == 'q':
            print("👋 Goodbye!")
            break
        elif choice == '0':
            run_all_demos()
            input("\nPress Enter to continue...")
        else:
            demo_index = int(choice) - 1
            if 0 <= demo_index < len(DEMOS):
                run_demo(DEMOS[demo_index])
                input("\nPress Enter to continue...")
            else:
                print("❌ Invalid demo selection")
        
        print("\n" + "=" * 55 + "\n")

if __name__ == "__main__":
    main()