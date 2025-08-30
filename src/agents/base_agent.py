from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class AgentResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class BaseAgent(ABC):
    def __init__(self, agent_id: str, name: str, description: str):
        self.agent_id = agent_id
        self.name = name
        self.description = description

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Process the input data and return a response.
        """
        pass

    def get_agent_info(self) -> Dict[str, str]:
        """
        Return basic information about the agent.
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description
        }

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate the input data before processing.
        Can be overridden by subclasses for specific validation logic.
        """
        return True
