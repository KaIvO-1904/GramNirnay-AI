from pydantic import BaseModel, Field
from typing import Any, List, Optional, Generic, TypeVar
from enum import Enum

T = TypeVar('T')

class AgentStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    AMBIGUOUS = "AMBIGUOUS"
    INCOMPLETE = "INCOMPLETE"

class NextAction(str, Enum):
    PROCEED = "PROCEED"
    RETRY = "RETRY"
    ASK_USER = "ASK_USER"
    TERMINATE = "TERMINATE"

class AgentResponse(BaseModel, Generic[T]):
    status: AgentStatus
    confidence: float = Field(..., ge=0.0, le=1.0)
    result: Optional[T] = None
    evidence: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    next_action: NextAction

class BaseAgent:
    """
    Base class for all agents. Ensures structured communication.
    """
    def __init__(self, name: str):
        self.name = name

    async def execute(self, input_data: Any) -> AgentResponse:
        raise NotImplementedError("Agents must implement the execute method.")
