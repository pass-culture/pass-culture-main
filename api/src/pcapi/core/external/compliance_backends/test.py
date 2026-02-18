import logging

from pcapi.tasks.serialization import compliance_tasks

from .base import BaseBackend


logger = logging.getLogger(__name__)


class TestBackend(BaseBackend):
    def get_score_from_compliance_api(
        self, payload: compliance_tasks.GetComplianceScoreRequest
    ) -> compliance_tasks.CompliancePredictionOutput | None:
        logger.info("A request to Compliance API would be sent to get the score of the offer.")
        return None

    def search_offers(
        self, payload: compliance_tasks.SearchOffersRequest
    ) -> compliance_tasks.SearchOffersResponse | None:
        logger.info("A request to Compliance API would be sent to search offers with llm.")
        return None
