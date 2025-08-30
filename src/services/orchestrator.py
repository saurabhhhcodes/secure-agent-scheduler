from ..utils.audit_log import log_action
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from langgraph.graph import StateGraph, END
from langgraph.graph.message import AnyMessage
from ..agents.planner_agent import PlannerAgent
from ..agents.notifier_agent import NotifierAgent
from ..models.schedule import ScheduleEvent
from ..utils.descope_token import get_descope_token

class Orchestrator:
    """Orchestrates the flow between Planner and Notifier agents."""
    
    def __init__(self):
        self.planner = PlannerAgent()
        self.notifier = NotifierAgent()
        self.workflow = self._create_workflow()
    
    def _create_workflow(self):
        """Create the LangGraph workflow."""
        # Define the state graph
        workflow = StateGraph(Dict[str, Any])
        
        # Add nodes
        workflow.add_node("plan_event", self._plan_event)
        workflow.add_node("schedule_notification", self._schedule_notification)
        
        # Define the edges
        workflow.add_edge("plan_event", "schedule_notification")
        workflow.add_edge("schedule_notification", END)
        
        # Set entry point
        workflow.set_entry_point("plan_event")
        
        return workflow.compile()
    
    async def _plan_event(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Plan the event using the Planner agent."""
        result = await self.planner.process(state)
        log_action("planner_agent.process", {"input": state, "result": result.dict() if hasattr(result, 'dict') else str(result)})
        if not result.success:
            raise ValueError(f"Failed to plan event: {result.error}")
        event_data = result.data["event"]
        event = ScheduleEvent(**event_data)
        return {
            **state,
            "event": event.dict(),
            "notification_required": result.data.get("notification_required", False),
            "notification_time": result.data.get("notification_time")
        }
    
    async def _schedule_notification(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a notification using the Notifier agent."""
        if not state.get("notification_required", False):
            return state
        event = state["event"]
        notification_time = state["notification_time"]
        # Create notification request
        notification_data = {
            "event_id": event["event_id"],
            "user_id": event["user_id"],
            "title": f"Reminder: {event['title']}",
            "message": f"Don't forget: {event['title']} at {event['start_time']}",
            "notification_time": notification_time,
            "recipients": [{"id": event["user_id"], "type": "user"}],
            "metadata": {
                "event_type": "reminder",
                "event_id": event["event_id"]
            }
        }
        # Get a real Descope token for the Notifier Agent
        notification_data["token"] = get_descope_token(
            audience="notifier_agent_001",
            scopes=["notifications:email:send"],
            user_id=event["user_id"]
        )
        # Send to notifier
        result = await self.notifier.process(notification_data)
        log_action("notifier_agent.process", {"input": notification_data, "result": result.dict() if hasattr(result, 'dict') else str(result)})
        if not result.success:
            raise ValueError(f"Failed to schedule notification: {result.error}")
        return {
            **state,
            "notification": result.data
        }
    
    async def process_request(self, user_request: str, user_id: str) -> Dict[str, Any]:
        """Process a user request through the workflow."""
        initial_state = {
            "user_request": user_request,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Execute the workflow
            result = await self.workflow.ainvoke(initial_state)
            return {
                "success": True,
                "event": result.get("event"),
                "notification": result.get("notification"),
                "status": "completed"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }
