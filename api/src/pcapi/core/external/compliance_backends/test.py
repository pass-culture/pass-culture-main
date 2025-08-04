import logging

from pcapi.tasks.serialization.compliance_tasks import CombinedComplianceOutput
from pcapi.tasks.serialization.compliance_tasks import GetComplianceScoreRequest

from .base import BaseBackend


logger = logging.getLogger(__name__)


class TestBackend(BaseBackend):
    def get_score_from_compliance_api(self, payload: GetComplianceScoreRequest) -> CombinedComplianceOutput | None:
        logger.info("A request to Compliance API would be sent to get the score of the offer.")
        return None
