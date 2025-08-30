from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class ScheduleEvent(BaseModel):
    """Represents a scheduled event in the system."""
    event_id: str = Field(default_factory=lambda: f"evt_{datetime.utcnow().timestamp()}")
    title: str
    description: str = ""
    start_time: str  # ISO format datetime string
    end_time: str    # ISO format datetime string
    location: str = ""
    user_id: str
    participants: List[str] = []
    status: str = "scheduled"  # scheduled, in-progress, completed, cancelled
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: dict = Field(default_factory=dict)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "event_id": "evt_1234567890",
                "title": "Team Meeting",
                "description": "Weekly sync",
                "start_time": "2023-06-15T14:00:00Z",
                "end_time": "2023-06-15T15:00:00Z",
                "location": "Conference Room A",
                "user_id": "user_123",
                "participants": ["user_456", "user_789"],
                "status": "scheduled",
                "created_at": "2023-06-14T10:00:00Z",
                "updated_at": "2023-06-14T10:00:00Z",
                "metadata": {"reminder_sent": False}
            }
        }
    )
