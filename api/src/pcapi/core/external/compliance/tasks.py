from pcapi.celery_tasks.tasks import celery_async_task
from pcapi.core.external.compliance import api
from pcapi.core.external.compliance.serialization import UpdateOfferComplianceScorePayload


@celery_async_task(
    name="tasks.compliance.priority.update_compliance_score_primary",
    model=UpdateOfferComplianceScorePayload,
    rate_limit="8/s",
)
def update_offer_compliance_score_primary_task(payload: UpdateOfferComplianceScorePayload) -> None:
    api.make_update_offer_compliance_score(payload)


@celery_async_task(
    name="tasks.compliance.default.update_compliance_score_secondary",
    model=UpdateOfferComplianceScorePayload,
    rate_limit="6/s",
)
def update_offer_compliance_score_secondary_task(payload: UpdateOfferComplianceScorePayload) -> None:
    api.make_update_offer_compliance_score(payload)
