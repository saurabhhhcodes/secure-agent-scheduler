from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from .base_agent import BaseAgent, AgentResponse
from pydantic import BaseModel, HttpUrl, ConfigDict
import os
import logging
import asyncio
import json
from enum import Enum

# Import Descope SDK with graceful fallback
try:
    from descope import (
        DescopeClient,
        AuthException,
        REFRESH_SESSION_TOKEN_NAME,
        SESSION_TOKEN_NAME,
    )
except ImportError:
    # For development when Descope dependencies conflict
    DescopeClient = None
    AuthException = Exception
    REFRESH_SESSION_TOKEN_NAME = "DS"
    SESSION_TOKEN_NAME = "DSR"

logger = logging.getLogger(__name__)

class NotificationType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SLACK = "slack"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DELIVERED = "delivered"

class NotificationRequest(BaseModel):
    """Model for notification requests."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    event_id: str
    user_id: str
    title: str
    message: str
    notification_time: str
    notification_type: NotificationType = NotificationType.EMAIL
    recipients: List[Dict[str, str]] = []
    metadata: Dict[str, Any] = {}

class NotifierAgent(BaseAgent):
    """Handles secure notifications with OAuth token validation using Descope."""
    
    def __init__(self):
        super().__init__(
            agent_id="notifier_001",
            name="Notifier Agent",
            description="Sends secure notifications with OAuth validation using Descope"
        )
        
        # Initialize Descope client
        self.descope_project_id = os.getenv("DESCOPE_PROJECT_ID")
        self.descope_management_key = os.getenv("DESCOPE_MANAGEMENT_KEY")
        self.descope_client = self._init_descope_client()
        
        # Token validation settings
        self.required_claims = {
            "iss": f"https://api.descope.com/{self.descope_project_id}",
            "token_type": "bearer"
        }
        
        # Required scopes for different notification types
        self.required_scopes = {
            NotificationType.EMAIL: ["notifications:email:send"],
            NotificationType.SMS: ["notifications:sms:send"],
            NotificationType.PUSH: ["notifications:push:send"],
            NotificationType.SLACK: ["notifications:slack:send"]
        }
    
    def _init_descope_client(self):
        """Initialize and return a Descope client."""
        try:
            if not self.descope_project_id or not self.descope_management_key:
                logger.warning("Missing Descope credentials. Using mock client.")
                return None
                
            return DescopeClient(
                project_id=self.descope_project_id,
                management_key=self.descope_management_key
            )
        except Exception as e:
            logger.error(f"Failed to initialize Descope client: {str(e)}")
            return None
    
    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Process a notification request with token validation.
        
        Args:
            input_data: Should contain:
                - token: JWT token for authentication
                - event_id: ID of the related event
                - user_id: ID of the user who initiated the action
                - title: Notification title
                - message: Notification content
                - notification_time: When to send the notification (ISO format)
                - notification_type: Type of notification (email, sms, etc.)
                - recipients: List of recipient dictionaries
                - metadata: Additional data for the notification
                
        Returns:
            AgentResponse with notification status or error
        """
        try:
            # Validate input
            if not await self.validate_input(input_data):
                return AgentResponse(
                    success=False,
                    error="Invalid input data"
                )
            
            # Validate the token and extract claims
            token = input_data.get("token")
            try:
                claims = await self._validate_token(token)
                if not claims:
                    return AgentResponse(
                        success=False,
                        error="Invalid or expired token"
                    )
                
                # Check if the token has the required scopes for this notification type
                notification_type = NotificationType(input_data.get("notification_type", "email"))
                if not self._has_required_scopes(claims, notification_type):
                    return AgentResponse(
                        success=False,
                        error="Insufficient permissions"
                    )
                
                # Process the notification
                notification = NotificationRequest(**input_data)
                result = await self._send_notification(notification, claims)
                
                return AgentResponse(
                    success=True,
                    data={
                        "notification_id": result.get("notification_id"),
                        "status": result.get("status"),
                        "sent_at": datetime.now(timezone.utc).isoformat(),
                        "recipients": [r.get("id") for r in notification.recipients]
                    }
                )
                
            except AuthException as e:
                logger.error(f"Authentication error: {str(e)}")
                return AgentResponse(
                    success=False,
                    error=f"Authentication failed: {str(e)}"
                )
                
        except Exception as e:
            logger.error(f"Error processing notification: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                error=f"Failed to process notification: {str(e)}"
            )
    
    async def _validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate the JWT token with Descope and return its claims.
        
        Args:
            token: JWT token to validate
            
        Returns:
            Token claims if valid, None otherwise
        """
        # Development mode - bypass token validation for demo
        if os.getenv("DEBUG", "False").lower() == "true":
            logger.info("Debug mode: bypassing token validation")
            return {
                "sub": "demo_user", 
                "scopes": ["notifications:email:send", "notifications:sms:send", "notifications:push:send"],
                "aud": "notifier_agent_001",
                "iss": f"https://api.descope.com/{self.descope_project_id or 'demo'}"
            }
            
        if not token:
            return None
            
        if not self.descope_client:
            logger.warning("No Descope client available. Skipping token validation.")
            return {"sub": "mock_user", "scopes": ["notifications:email:send"]}  # For testing
            
        try:
            # Validate the token and get the claims
            jwt_response = self.descope_client.validate_session(token)
            if not jwt_response or not jwt_response.get("token"):
                return None
                
            return jwt_response["token"]
            
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return None
    
    def _has_required_scopes(self, claims: Dict[str, Any], notification_type: NotificationType) -> bool:
        """Check if the token has the required scopes for the notification type."""
        if not claims:
            return False
            
        # Get required scopes for this notification type
        required_scopes = set(self.required_scopes.get(notification_type, []))
        if not required_scopes:
            return False
            
        # Get scopes from token claims
        token_scopes = set(claims.get("scopes", []))
        
        # Check if all required scopes are present
        return required_scopes.issubset(token_scopes)
    
    async def _send_notification(self, notification: NotificationRequest, claims: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a notification using the appropriate channel.
        
        In a real implementation, this would integrate with actual notification services.
        """
        # This is a simplified implementation
        # In production, you would integrate with email/SMS/push notification services here
        
        notification_id = f"notif_{datetime.now(timezone.utc).timestamp()}"
        
        logger.info(
            f"Sending {notification.notification_type} notification to {len(notification.recipients)} recipients: "
            f"{notification.title} - {notification.message}"
        )
        
        # Simulate sending the notification
        await asyncio.sleep(0.5)  # Simulate network delay
        
        return {
            "notification_id": notification_id,
            "status": NotificationStatus.SENT,
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "recipients": [r.get("id") for r in notification.recipients]
        }
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate the input data for the notification request."""
        required_fields = ["token", "event_id", "user_id", "title", "message", "notification_time"]
        return all(field in input_data for field in required_fields)

# For testing
if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def test_notifier():
        notifier = NotifierAgent()
        
        test_data = {
            "token": "test_token",
            "event_id": "test_event_123",
            "user_id": "test_user_123",
            "title": "Test Notification",
            "message": "This is a test notification.",
            "notification_time": "2023-06-15T14:00:00Z",
            "notification_type": "email",
            "recipients": [{"id": "user1@example.com", "type": "email"}],
            "metadata": {"priority": "high"}
        }
        
        result = await notifier.process(test_data)
        print(json.dumps(result.dict(), indent=2))
    
    asyncio.run(test_notifier())
