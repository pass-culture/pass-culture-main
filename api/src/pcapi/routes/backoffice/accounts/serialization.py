import abc
import datetime

import sqlalchemy as sa
from flask import url_for
from markupsafe import Markup
from pydantic import BaseModel as BaseModelV2

from pcapi import settings
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.subscription.dms import schemas as dms_schemas
from pcapi.core.users import constants as users_constants
from pcapi.core.users import models as users_models
from pcapi.core.users import utils as users_utils
from pcapi.routes.serialization import BaseModel


def get_fraud_check_eligibility_type(
    fraud_check: subscription_models.BeneficiaryFraudCheck,
) -> users_models.EligibilityType | None:
    if fraud_check.eligibilityType:
        return fraud_check.eligibilityType

    user = fraud_check.user

    if not user.dateOfBirth:
        return None

    age_at_fraud_check_date = users_utils.get_age_at_date(
        birth_date=user.dateOfBirth,
        specified_datetime=fraud_check.dateCreated,
        department_code=user.departementCode,
    )

    if user.dateCreated < settings.CREDIT_V3_DECREE_DATETIME:
        if age_at_fraud_check_date < users_constants.ELIGIBILITY_AGE_18:
            return users_models.EligibilityType.UNDERAGE
        return users_models.EligibilityType.AGE18

    return users_models.EligibilityType.AGE17_18


class SubscriptionItemModel(BaseModel):
    class Config:
        orm_mode = True
        use_enum_values = True

    type: subscription_schemas.SubscriptionStep
    status: subscription_schemas.SubscriptionItemStatus


class IdCheckItemModel(BaseModel):
    class Config:
        use_enum_values = True

    id: int
    type: subscription_models.FraudCheckType
    dateCreated: datetime.datetime
    thirdPartyId: str
    status: subscription_models.FraudCheckStatus | None
    reason: str | None
    reasonCodes: list[subscription_models.FraudReasonCode] | None
    technicalDetails: dict | None
    sourceId: str | None = None  # DMS only
    eligibilityType: users_models.EligibilityType | None
    applicable_eligibilities: list[users_models.EligibilityType]

    @classmethod
    def build(cls, fraud_check: subscription_models.BeneficiaryFraudCheck) -> "IdCheckItemModel":
        if fraud_check.resultContent:
            technical_data = fraud_check.source_data()
            technical_details = (
                technical_data.model_dump() if isinstance(technical_data, BaseModelV2) else technical_data.dict()
            )
        else:
            technical_details = None

        if fraud_check.type == subscription_models.FraudCheckType.DMS and fraud_check.resultContent is not None:
            dms_content = dms_schemas.DMSContent(**fraud_check.resultContent)
            source_id = str(dms_content.procedure_number)
        else:
            source_id = None

        if not fraud_check.is_id_check_ok_across_eligibilities_or_age:
            eligibility_type = get_fraud_check_eligibility_type(fraud_check)
            applicable_eligibilities = [eligibility_type] if eligibility_type else []
        else:
            applicable_eligibilities = fraud_check.applicable_eligibilities

        return cls(
            id=fraud_check.id,
            type=fraud_check.type,
            dateCreated=fraud_check.dateCreated,
            thirdPartyId=fraud_check.thirdPartyId,
            status=fraud_check.status,
            reason=fraud_check.reason,
            reasonCodes=fraud_check.reasonCodes,
            technicalDetails=technical_details,
            sourceId=source_id,
            eligibilityType=fraud_check.eligibilityType,
            applicable_eligibilities=applicable_eligibilities,
        )


class EligibilitySubscriptionHistoryModel(BaseModel):
    subscriptionItems: list[SubscriptionItemModel]
    idCheckHistory: list[IdCheckItemModel]


class BeneficiaryActivity(abc.ABC):
    """
    Used to put all user's chronicles, special events, etc in one table
    """

    @property
    @abc.abstractmethod
    def activityType(self) -> str:
        pass

    @property
    def activityDate(self) -> datetime.datetime | None:
        return None

    @property
    def comment(self) -> str | None:
        return None


class SpecialEventActivity(BeneficiaryActivity):
    def __init__(self, special_event_response: sa.engine.Row):
        self._special_event_response = special_event_response

    @property
    def activityType(self) -> str:
        return "Opération spéciale"

    @property
    def activityDate(self) -> datetime.datetime | None:
        return self._special_event_response.dateSubmitted

    @property
    def comment(self) -> str | None:
        from pcapi.routes.backoffice.filters import format_special_event_response_status  # avoid circular import

        comment = Markup(
            """Candidature à l'opération spéciale <a class="link-primary" href="{url}">{title}</a> : {status}"""
        ).format(
            url=url_for(
                "backoffice_web.operations.get_event_details", special_event_id=self._special_event_response.eventId
            ),
            title=self._special_event_response.title,
            status=format_special_event_response_status(self._special_event_response.status),
        )
        return comment


class ChronicleActivity(BeneficiaryActivity):
    def __init__(self, chronicle: sa.engine.Row):
        self._chronicle = chronicle

    @property
    def activityType(self) -> str:
        return "Chronique"

    @property
    def activityDate(self) -> datetime.datetime | None:
        return self._chronicle.dateCreated

    @property
    def comment(self) -> str | None:
        comment = Markup(
            """Rédaction d'une chronique sur <a class="link-primary" href="{url}">{title}</a> : {status}"""
        ).format(
            url=url_for("backoffice_web.chronicles.details", chronicle_id=self._chronicle.id),
            title=self._chronicle.title or "une œuvre",
            status="publiée" if self._chronicle.isPublished else "non publiée",
        )
        return comment
