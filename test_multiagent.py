#!/usr/bin/env python3
"""
Comprehensive test script for the Multi-Agent Scheduler System
Tests the complete workflow: API → Orchestrator → Planner Agent → Notifier Agent
"""

import asyncio
import sys
import json
from datetime import datetime
from typing import Dict, Any

# Add src to path for imports
sys.path.append('src')

from src.main import app
from src.services.orchestrator import Orchestrator
from src.agents.planner_agent import PlannerAgent
from src.agents.notifier_agent import NotifierAgent

async def test_individual_agents():
    """Test each agent individually"""
    print("🤖 TESTING INDIVIDUAL AGENTS")
    print("=" * 50)
    
    # Test Planner Agent
    print("\n🧠 Testing Planner Agent...")
    planner = PlannerAgent()
    
    test_input = {
        "user_request": "Schedule board meeting next Tuesday at 2 PM for 3 hours",
        "user_id": "test_user_001"
    }
    
    planner_result = await planner.process(test_input)
    
    if planner_result.success:
        print("✅ Planner Agent SUCCESS")
        print(f"   📅 Title: {planner_result.data['event']['title']}")
        print(f"   ⏰ Start: {planner_result.data['event']['start_time']}")
        print(f"   ⏰ End: {planner_result.data['event']['end_time']}")
        print(f"   🔔 Notification needed: {planner_result.data.get('notification_required', False)}")
    else:
        print(f"❌ Planner Agent FAILED: {planner_result.error}")
        return False
    
    # Test Notifier Agent
    print("\n🔔 Testing Notifier Agent...")
    notifier = NotifierAgent()
    
    notification_input = {
        "token": "demo_token",
        "event_id": "test_event_123",
        "user_id": "test_user_001",
        "title": "Test Notification",
        "message": "This is a test notification from the multi-agent system",
        "notification_time": "2025-08-28T14:00:00",
        "notification_type": "email",
        "recipients": [{"id": "test@example.com", "type": "email"}],
        "metadata": {"test": True}
    }
    
    notifier_result = await notifier.process(notification_input)
    
    if notifier_result.success:
        print("✅ Notifier Agent SUCCESS")
        print(f"   📧 Notification ID: {notifier_result.data['notification_id']}")
        print(f"   ✅ Status: {notifier_result.data['status']}")
        print(f"   👥 Recipients: {notifier_result.data['recipients']}")
    else:
        print(f"❌ Notifier Agent FAILED: {notifier_result.error}")
        return False
    
    return True

async def test_orchestrator():
    """Test the complete orchestrator workflow"""
    print("\n🎼 TESTING ORCHESTRATOR WORKFLOW")
    print("=" * 50)
    
    orchestrator = Orchestrator()
    
    test_cases = [
        {
            "name": "Executive Meeting",
            "request": "Schedule executive committee meeting tomorrow at 11 AM for 2 hours",
            "user_id": "exec_001"
        },
        {
            "name": "Training Session", 
            "request": "Set up AI training workshop next Friday at 2:30 PM for 4 hours with reminder 1 hour before",
            "user_id": "trainer_002"
        },
        {
            "name": "Quick Standup",
            "request": "Daily standup today 9 AM 15 minutes",
            "user_id": "scrum_master_003"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_case['name']}")
        print(f"   📝 Request: '{test_case['request']}'")
        
        try:
            result = await orchestrator.process_request(
                user_request=test_case['request'],
                user_id=test_case['user_id']
            )
            
            if result['success']:
                print("   ✅ SUCCESS!")
                event = result['event']
                notification = result.get('notification')
                
                print(f"   📅 Event: {event['title']}")
                print(f"   ⏰ Time: {event['start_time']} - {event['end_time']}")
                print(f"   👤 User: {event['user_id']}")
                
                if notification:
                    print(f"   🔔 Notification: {notification['status']} ({notification['notification_id']})")
                
                results.append({'case': test_case['name'], 'status': 'SUCCESS', 'result': result})
            else:
                print(f"   ❌ FAILED: {result['error']}")
                results.append({'case': test_case['name'], 'status': 'FAILED', 'error': result['error']})
                
        except Exception as e:
            print(f"   💥 EXCEPTION: {str(e)}")
            results.append({'case': test_case['name'], 'status': 'EXCEPTION', 'error': str(e)})
    
    return results

def test_natural_language_parsing():
    """Test the natural language parsing capabilities"""
    print("\n🗣️ TESTING NATURAL LANGUAGE PARSING")
    print("=" * 50)
    
    # Test various natural language patterns
    test_phrases = [
        "Meet with client tomorrow 3 PM",
        "Schedule dentist appointment next Monday at 10:30 AM for 1 hour",
        "Team standup daily at 9 AM for 15 minutes", 
        "Board meeting quarterly review next Friday 2 PM 3 hours",
        "Coffee with John Thursday 4:30 PM",
        "Conference call with vendors Wednesday 11:00 AM for 90 minutes with 30 minute reminder"
    ]
    
    # This tests the parsing logic in the planner agent
    from src.agents.planner_agent import PlannerAgent
    planner = PlannerAgent()
    
    for i, phrase in enumerate(test_phrases, 1):
        print(f"\n📝 Test {i}: '{phrase}'")
        try:
            parsed_data = planner._parse_schedule_request(phrase)
            print(f"   📅 Title: {parsed_data['title']}")
            print(f"   ⏰ Start: {parsed_data['start_time']}")
            print(f"   ⏰ End: {parsed_data['end_time']}")
            print(f"   🔔 Reminder: {parsed_data['reminder_minutes']} minutes before")
        except Exception as e:
            print(f"   ❌ Parsing failed: {str(e)}")

async def run_comprehensive_test():
    """Run all tests"""
    print("🚀 COMPREHENSIVE MULTI-AGENT SYSTEM TEST")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().isoformat()}")
    print()
    
    # Test 1: Individual Agents
    agents_ok = await test_individual_agents()
    
    # Test 2: Natural Language Parsing
    test_natural_language_parsing()
    
    # Test 3: Complete Orchestrator Workflow
    orchestrator_results = await test_orchestrator()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Individual Agents: {'PASSED' if agents_ok else 'FAILED'}")
    
    successful_orchestrator_tests = len([r for r in orchestrator_results if r['status'] == 'SUCCESS'])
    total_orchestrator_tests = len(orchestrator_results)
    
    print(f"✅ Orchestrator Tests: {successful_orchestrator_tests}/{total_orchestrator_tests} PASSED")
    
    if successful_orchestrator_tests == total_orchestrator_tests and agents_ok:
        print("\n🎉 ALL TESTS PASSED! Multi-Agent System is working perfectly!")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    # Run the comprehensive test
    print("Starting Multi-Agent System Test Suite...")
    success = asyncio.run(run_comprehensive_test())
    
    if success:
        print("\n🏆 Multi-Agent System is HACKATHON READY! 🏆")
        sys.exit(0)
    else:
        print("\n🔧 Some issues found. Please review the test results.")
        sys.exit(1)
