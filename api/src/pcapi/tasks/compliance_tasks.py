import logging

from pcapi import settings
from pcapi.core.external.compliance import api
from pcapi.core.external.compliance.serialization import GetComplianceScoreRequest
from pcapi.tasks.decorator import task


logger = logging.getLogger(__name__)


@task(settings.GCP_COMPLIANCE_API_PRIMARY_QUEUE_NAME, "/compliance/scoring-primary")
def update_offer_compliance_score_primary_task(payload: GetComplianceScoreRequest) -> None:
    api.make_update_offer_compliance_score(payload)


@task(settings.GCP_COMPLIANCE_API_SECONDARY_QUEUE_NAME, "/compliance/scoring-secondary")
def update_offer_compliance_score_secondary_task(payload: GetComplianceScoreRequest) -> None:
    api.make_update_offer_compliance_score(payload)
