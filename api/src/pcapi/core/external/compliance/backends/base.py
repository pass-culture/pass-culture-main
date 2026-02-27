import logging

from pcapi.core.external.compliance import serialization


logger = logging.getLogger(__name__)


class BaseBackend:
    def get_score_from_compliance_api(
        self, payload: serialization.UpdateOfferComplianceScorePayload
    ) -> serialization.CompliancePredictionOutput | None:
        """
        Returned tuple: score and list of rejection reason codes
        """
        raise NotImplementedError()

    def search_offers(self, payload: serialization.SearchOffersRequest) -> serialization.SearchOffersResponse | None:
        raise NotImplementedError()
