import logging

from pcapi.tasks.serialization.compliance_tasks import CombinedComplianceOutput
from pcapi.tasks.serialization.compliance_tasks import GetComplianceScoreRequest


logger = logging.getLogger(__name__)


class BaseBackend:
    def get_score_from_compliance_api(self, payload: GetComplianceScoreRequest) -> CombinedComplianceOutput | None:
        """
        Returned tuple: score and list of rejection reason codes
        """
        raise NotImplementedError()
