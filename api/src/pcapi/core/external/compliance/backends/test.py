import logging

from pcapi.core.external.compliance import serialization

from .base import BaseBackend


logger = logging.getLogger(__name__)


class TestBackend(BaseBackend):
    def get_score_from_compliance_api(
        self, payload: serialization.GetComplianceScoreRequest | serialization.UpdateOfferComplianceScorePayload
    ) -> serialization.CompliancePredictionOutput | None:
        logger.info("A request to Compliance API would be sent to get the score of the offer.")
        return None

    def search_offers(self, payload: serialization.SearchOffersRequest) -> serialization.SearchOffersResponse | None:
        logger.info("A request to Compliance API would be sent to search offers with llm.")
        return None
