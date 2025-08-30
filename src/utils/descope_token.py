import os
import requests
from typing import List, Optional

def get_descope_token(audience: str, scopes: List[str], user_id: Optional[str] = None) -> str:
    """
    Request a scoped access token from Descope for agent-to-agent communication.
    This is a simplified utility for demo purposes.
    """
    project_id = os.getenv("DESCOPE_PROJECT_ID")
    management_key = os.getenv("DESCOPE_MANAGEMENT_KEY")
    
    # For development/demo, use mock credentials if real ones aren't available
    if not project_id or not management_key or project_id == "demo_project_id":
        project_id = "demo_project_id"
        management_key = "demo_management_key"

    # This is a placeholder for the real Descope token request
    # In production, use Descope's SDK or API to request a token with the right scopes
    # For demo, return a mock JWT with the required claims
    import jwt
    import datetime
    payload = {
        "iss": f"https://api.descope.com/{project_id}",
        "sub": user_id or "planner_agent_001",
        "aud": audience,
        "scopes": scopes,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
        "iat": datetime.datetime.utcnow(),
        "azp": "planner_agent_001"
    }
    token = jwt.encode(payload, management_key, algorithm="HS256")
    return token
