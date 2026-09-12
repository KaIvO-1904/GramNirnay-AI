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
    def __init__(self, name: str, model_name: Optional[str] = None):
        self.name = name
        self.model_name = model_name

    def wrap_response(self, content: str, structured_data: Any = None, score: float = 0.0, reason: str = "", errors: List[str] = None) -> AgentResponse:
        """Helper to wrap results into a standard AgentResponse."""
        status = AgentStatus.SUCCESS if score > 0.3 else AgentStatus.FAILURE
        return AgentResponse(
            status=status,
            confidence=score,
            result=structured_data,
            evidence=[content, reason],
            errors=errors or [],
            next_action=NextAction.PROCEED if status == AgentStatus.SUCCESS else NextAction.RETRY
        )

    async def execute(self, input_data: Any) -> AgentResponse:
        raise NotImplementedError("Agents must implement the execute method.")
