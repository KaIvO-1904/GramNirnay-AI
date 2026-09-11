from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar
from ..core.schemas.base import GramNirnayError

T = TypeVar("T")

class BaseService(ABC, Generic[T]):
    """Base class for all deterministic services."""

    @abstractmethod
    def execute(self, *args, **kwargs) -> T:
        """Execute the primary logic of the service."""
        pass

    def handle_error(self, error: Exception, custom_message: str = "Service execution failed"):
        """Standardized error wrapping for services."""
        if isinstance(error, GramNirnayError):
            raise error
        raise GramNirnayError(
            code="SERVICE_ERROR",
            message=f"{custom_message}: {str(error)}",
            is_deterministic=True
        )
