import logging

from pcapi.tasks.serialization.compliance_tasks import GetComplianceScoreRequest


logger = logging.getLogger(__name__)


class BaseBackend:
    def get_score_from_compliance_api(self, payload: GetComplianceScoreRequest) -> int | None:
        raise NotImplementedError()
