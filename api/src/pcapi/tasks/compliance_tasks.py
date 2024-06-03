import logging

from pcapi import settings
from pcapi.core.external import compliance
from pcapi.tasks.decorator import task
from pcapi.tasks.serialization.compliance_tasks import GetComplianceScoreRequest


logger = logging.getLogger(__name__)


@task(settings.GCP_COMPLIANCE_API_PRIMARY_QUEUE_NAME, "/compliance/scoring-primary")  # type: ignore[arg-type]
def update_offer_compliance_score_primary_task(payload: GetComplianceScoreRequest) -> None:
    compliance.make_update_offer_compliance_score(payload)


@task(settings.GCP_COMPLIANCE_API_SECONDARY_QUEUE_NAME, "/compliance/scoring-secondary")  # type: ignore[arg-type]
def update_offer_compliance_score_secondary_task(payload: GetComplianceScoreRequest) -> None:
    compliance.make_update_offer_compliance_score(payload)
