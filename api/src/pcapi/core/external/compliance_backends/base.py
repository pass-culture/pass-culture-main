import logging

from pcapi.tasks.serialization import compliance_tasks


logger = logging.getLogger(__name__)


class BaseBackend:
    def get_score_from_compliance_api(
        self, payload: compliance_tasks.GetComplianceScoreRequest
    ) -> compliance_tasks.CompliancePredictionOutput | None:
        """
        Returned tuple: score and list of rejection reason codes
        """
        raise NotImplementedError()

    def search_offers(
        self, payload: compliance_tasks.SearchOffersRequest
    ) -> compliance_tasks.SearchOffersResponse | None:
        raise NotImplementedError()
