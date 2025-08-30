#!/usr/bin/env python3
"""
Interactive test interface for the Multi-Agent Scheduler System
Allows manual testing with custom inputs
"""

import requests
import json
from datetime import datetime
import sys

def print_banner():
    """Print a nice banner"""
    print("=" * 60)
    print("🤖 INTERACTIVE MULTI-AGENT SYSTEM TESTER")
    print("=" * 60)
    print("Test your natural language scheduling requests!")
    print("Type 'quit' to exit, 'help' for examples")
    print()

def print_help():
    """Print help with examples"""
    print("\n💡 EXAMPLE REQUESTS:")
    print("  • 'Schedule team meeting tomorrow at 2 PM for 1 hour'")
    print("  • 'Set up client call Friday 10:30 AM for 90 minutes'") 
    print("  • 'Doctor appointment next Monday 3:15 PM'")
    print("  • 'Board meeting quarterly review next week Tuesday 9 AM for 3 hours'")
    print("  • 'Sprint planning session Thursday 1 PM for 2 hours with reminder 15 minutes before'")
    print()

def make_request(user_request, user_id="interactive_user"):
    """Make a request to the scheduling API"""
    url = "http://localhost:8000/api/schedule"
    
    payload = {
        "user_request": user_request,
        "user_id": user_id,
        "metadata": {
            "source": "interactive_test",
            "timestamp": datetime.now().isoformat()
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection error: {str(e)}"}, 500

def format_response(response_data, status_code):
    """Format the API response nicely"""
    if status_code != 200:
        print(f"❌ ERROR (HTTP {status_code})")
        print(f"   {response_data.get('error', 'Unknown error')}")
        return
    
    if response_data.get('success'):
        print("✅ SUCCESS!")
        
        # Event details
        event = response_data.get('event', {})
        print(f"📅 Event: {event.get('title', 'N/A')}")
        print(f"⏰ Time: {event.get('start_time', 'N/A')} - {event.get('end_time', 'N/A')}")
        print(f"👤 User: {event.get('user_id', 'N/A')}")
        print(f"🆔 Event ID: {event.get('event_id', 'N/A')}")
        
        # Notification details
        notification = response_data.get('notification')
        if notification:
            print(f"🔔 Notification: {notification.get('status', 'N/A')} ({notification.get('notification_id', 'N/A')})")
            print(f"📧 Recipients: {len(notification.get('recipients', []))} recipient(s)")
        
        # Description
        if event.get('description'):
            print(f"📝 Description: {event['description']}")
            
    else:
        print("❌ FAILED")
        print(f"   Error: {response_data.get('error', 'Unknown error')}")

def check_service():
    """Check if the service is running"""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"💚 Service Status: {data.get('status', 'unknown')}")
            print(f"🕐 Server Time: {data.get('timestamp', 'unknown')}")
            return True
        else:
            print(f"⚠️  Service responded with HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to service: {str(e)}")
        print("   Make sure the server is running: uvicorn src.main:app --reload")
        return False

def main():
    """Main interactive loop"""
    print_banner()
    
    # Check service
    if not check_service():
        sys.exit(1)
    
    print("Ready to test! 🚀")
    print()
    
    while True:
        try:
            # Get user input
            user_input = input("📝 Enter your scheduling request: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if user_input.lower() in ['help', 'h']:
                print_help()
                continue
            
            # Make the request
            print(f"\n🔄 Processing: '{user_input}'")
            print("..." + "." * len(user_input))
            
            response_data, status_code = make_request(user_input)
            
            # Format and display response
            format_response(response_data, status_code)
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"💥 Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
