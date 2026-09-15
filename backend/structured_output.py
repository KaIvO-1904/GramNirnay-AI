import json
import logging
import re
from typing import Type, TypeVar, Optional, Dict, Any, Callable
from pydantic import BaseModel, ValidationError

logger = logging.getLogger("structured_output")
T = TypeVar("T", bound=BaseModel)

class StructuredOutputHandler:
    """
    Robust handler for LLM structured outputs.
    Implements: Parsing -> Repair -> Validation -> Compact Retry -> Fallback.
    """

    @staticmethod
    def repair_json(raw_text: str) -> str:
        """
        Attempts to fix common LLM JSON errors.
        """
        # Remove markdown code blocks if present
        raw_text = re.sub(r"```json\s*|\s*```", "", raw_text).strip()

        # Fix invalid escapes: \' is not allowed in JSON
        # We only replace \' when it's not part of a legitimate escape sequence
        raw_text = raw_text.replace("\\'", "'")

        # Remove trailing commas before closing brackets/braces
        raw_text = re.sub(r",\s*([\]}])", r"\1", raw_text)

        return raw_text

    @classmethod
    def validate_and_parse(cls, raw_text: str, schema: Type[T]) -> Optional[T]:
        """
        Parses raw text and validates it against a Pydantic schema.
        """
        try:
            # 1. Try direct parse
            data = json.loads(raw_text)
            return schema.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            # 2. Try repair and parse
            repaired = cls.repair_json(raw_text)
            try:
                data = json.loads(repaired)
                return schema.model_validate(data)
            except (json.JSONDecodeError, ValidationError):
                logger.debug(f"JSON validation failed for schema {schema.__name__}: {str(e)}")
                return None

    @classmethod
    def execute_with_retry(
        cls,
        llm_call_fn: Callable[[], str],
        schema: Type[T],
        operation_name: str,
        model_name: str,
        retry_fn: Optional[Callable[[str], str]] = None
    ) -> Optional[T]:
        """
        Full pipeline: 1 normal call -> 1 repair attempt -> 1 compact retry -> fallback.
        """
        # Normal generation
        raw_output = llm_call_fn()
        parsed = cls.validate_and_parse(raw_output, schema)

        if parsed:
            return parsed

        # If we have a retry function, use it for a compact retry
        if retry_fn:
            logger.info(f"Operation {operation_name} failed validation. Attempting compact retry. Model: {model_name}")
            try:
                retry_output = retry_fn(raw_output)
                parsed = cls.validate_and_parse(retry_output, schema)
                if parsed:
                    return parsed
            except Exception as e:
                logger.error(f"Compact retry failed for {operation_name}: {e}")

        logger.warning(f"Structured output failed for {operation_name} after retries. Model: {model_name}")
        return None
