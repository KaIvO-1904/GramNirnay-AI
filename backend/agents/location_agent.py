from typing import Any, Dict, Optional
from .base import BaseAgent, AgentResponse, AgentStatus, NextAction
from ..location.service import LocationService
from ..location.models import LocationIdentity

class LocationAgent(BaseAgent):
    def __init__(self, location_service: LocationService):
        super().__init__("LocationAgent")
        self.location_service = location_service

    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Intent/GPS -> Canonical Location Identity
        """
        try:
            query = input_data.get("location_query")
            lat = input_data.get("lat")
            lng = input_data.get("lng")

            if lat and lng:
                res = self.location_service.resolve_gps(lat, lng)
            elif query:
                # For simplicity, we assume the first candidate is picked or
                # the query is a known ID.
                candidates = self.location_service.search_place(query)
                if not candidates:
                    return AgentResponse(
                        status=AgentStatus.AMBIGUOUS,
                        confidence=0.0,
                        next_action=NextAction.ASK_USER,
                        errors=["No location candidates found"]
                    )
                # Mock selection of first candidate
                res = self.location_service.resolve_location(
                    candidates[0].provider_id, candidates[0].source
                )
            else:
                return AgentResponse(
                    status=AgentStatus.INCOMPLETE,
                    confidence=0.0,
                    next_action=NextAction.ASK_USER,
                    errors=["No location data provided"]
                )

            return AgentResponse(
                status=AgentStatus.SUCCESS,
                confidence=1.0,
                result=res,
                evidence=["LOCATION_SERVICE"],
                next_action=NextAction.PROCEED
            )
        except Exception as e:
            return AgentResponse(
                status=AgentStatus.FAILURE,
                confidence=0.0,
                next_action=NextAction.RETRY,
                errors=[str(e)]
            )
