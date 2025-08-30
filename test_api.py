import asyncio
import json
from datetime import datetime, timedelta

from src.services.orchestrator import Orchestrator

async def test_schedule_meeting():
    """Test the scheduling of a meeting with a reminder."""
    print("Testing meeting scheduling...")
    
    # Initialize the orchestrator
    orchestrator = Orchestrator()
    
    # Test data
    user_request = "Schedule a team meeting for tomorrow at 2 PM for 1 hour about the Q3 report"
    user_id = "test_user_123"
    
    # Process the request
    print(f"Processing request: {user_request}")
    result = await orchestrator.process_request(user_request, user_id)
    
    # Print the result
    print("\nTest Results:")
    print(json.dumps(result, indent=2))
    
    # Basic assertions
    assert result["success"] is True, "Request should be successful"
    assert "event" in result, "Result should contain event details"
    assert "notification" in result, "Result should contain notification details"
    
    print("\nTest passed successfully!")

if __name__ == "__main__":
    asyncio.run(test_schedule_meeting())
