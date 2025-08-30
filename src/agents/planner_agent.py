from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import re
from ..models.schedule import ScheduleEvent
from .base_agent import BaseAgent, AgentResponse

class PlannerAgent(BaseAgent):
    """
    An agent responsible for parsing scheduling requests and creating calendar events.
    """
    scheduled_events: List[ScheduleEvent] = []
    
    def __init__(self):
        super().__init__(
            agent_id="planner_agent_001",
            name="Planner Agent",
            description="Parses user requests and creates calendar events"
        )
        
    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Process the user's scheduling request and create a calendar event.
        
        Args:
            input_data: Should contain 'user_request' and 'user_id'
            
        Returns:
            AgentResponse with the created event details or an error message
        """
        try:
            # Validate input
            if not await self.validate_input(input_data):
                return AgentResponse(
                    success=False,
                    error="Invalid input data"
                )
                
            # Extract event details from the user request
            event_details = self._parse_schedule_request(input_data["user_request"])
            
            # Create a ScheduleEvent
            event = ScheduleEvent(
                title=event_details["title"],
                start_time=event_details["start_time"],
                end_time=event_details["end_time"],
                user_id=input_data["user_id"],
                description=event_details.get("description", ""),
                location=event_details.get("location", ""),
                participants=event_details.get("participants", [])
            )

            # Check for overlapping events
            for existing_event in self.scheduled_events:
                if event.start_time == existing_event.start_time:
                    return AgentResponse(
                        success=False,
                        error=f"An event is already scheduled at this time: {existing_event.title} at {existing_event.start_time}"
                    )
            
            # Add the new event to the list of scheduled events
            self.scheduled_events.append(event)
            
            return AgentResponse(
                success=True,
                data={
                    "event": event.dict(),
                    "notification_required": True,
                    "notification_time": self._calculate_notification_time(
                        event.start_time,
                        event_details.get("reminder_minutes", 30)
                    )
                }
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"Failed to process schedule request: {str(e)}"
            )
    
    def _parse_schedule_request(self, request_text: str) -> Dict[str, Any]:
        """
        Parse natural language request into structured event data.
        
        In a real implementation, this would use NLP to extract details.
        For now, we'll use simple pattern matching.
        """
        # This is a simplified implementation
        # In a real app, you'd use NLP to extract these details
        
        # Default values
        title = "Meeting"
        now = datetime.now()
        start_time = now + timedelta(hours=1)
        duration_minutes = 60
        reminder_minutes = 30

        # Check for "tomorrow"
        if 'tomorrow' in request_text.lower():
            start_time = start_time + timedelta(days=1)
        
        # Simple pattern matching (simplified for example)
        time_match = re.search(r'(\d{1,2}):?(\d{2})?\s*(am|pm|AM|PM)', request_text, re.IGNORECASE)
        if time_match:
            # Simplified time parsing
            hour = int(time_match.group(1))
            minute = int(time_match.group(2) or '00')
            if 'pm' in time_match.group(0).lower() and hour < 12:
                hour += 12
            start_time = start_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Look for duration
        duration_match = re.search(r'(\d+)\s*(minute|hour|hr)', request_text, re.IGNORECASE)
        if duration_match:
            duration = int(duration_match.group(1))
            if 'hour' in duration_match.group(2).lower():
                duration_minutes = duration * 60
            else:
                duration_minutes = duration
        
        # Look for title
        title_match = re.search(r'(?:schedule|plan|set up|create)\s+(?:a|an)?\s*(.*?)(?=\s+(?:at|on|for|tomorrow|today|\d))', request_text, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
        
        # Calculate end time
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Look for reminder time
        reminder_match = re.search(r'(?:remind|notify|alert).*?(\d+)\s*(minute|hour|hr)', request_text, re.IGNORECASE)
        if reminder_match:
            reminder = int(reminder_match.group(1))
            if 'hour' in reminder_match.group(2).lower():
                reminder_minutes = reminder * 60
            else:
                reminder_minutes = reminder
        
        return {
            "title": title,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "reminder_minutes": reminder_minutes,
            "description": f"Scheduled from user request: {request_text}"
        }
    
    def _calculate_notification_time(self, event_time_str: str, minutes_before: int) -> str:
        """Calculate when the notification should be sent."""
        event_time = datetime.fromisoformat(event_time_str)
        return (event_time - timedelta(minutes=minutes_before)).isoformat()
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate the input data."""
        required_fields = ["user_request", "user_id"]
        return all(field in input_data for field in required_fields)