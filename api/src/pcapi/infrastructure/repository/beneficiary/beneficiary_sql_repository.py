from typing import Optional

from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription.models import BeneficiaryPreSubscription
from pcapi.core.users.external import update_external_user
from pcapi.core.users.models import User
from pcapi.infrastructure.repository.beneficiary import beneficiary_pre_subscription_sql_converter
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.repository import repository


class BeneficiarySQLRepository:
    @classmethod
    def save(cls, beneficiary_pre_subscription: BeneficiaryPreSubscription, user: Optional[User] = None) -> User:
        user_sql_entity = beneficiary_pre_subscription_sql_converter.to_model(beneficiary_pre_subscription, user=user)
        subscription_api.attach_beneficiary_import_details(
            beneficiary=user_sql_entity,
            application_id=beneficiary_pre_subscription.application_id,
            source_id=beneficiary_pre_subscription.source_id,
            source=next(
                source for source in BeneficiaryImportSources if source.value == beneficiary_pre_subscription.source
            ),
            eligibility_type=beneficiary_pre_subscription.eligibility_type,
            details=None,
            status=ImportStatus.CREATED,
        )
        repository.save(user_sql_entity)

        if subscription_api.can_activate_beneficiary(user, beneficiary_pre_subscription.eligibility_type):
            user_sql_entity = subscription_api.check_and_activate_beneficiary(
                user_sql_entity.id, has_activated_account=user is not None
            )
        else:
            update_external_user(user_sql_entity)

        return user_sql_entity

    @classmethod
    def reject(
        cls, beneficiary_pre_subscription: BeneficiaryPreSubscription, detail: str, user: Optional[User]
    ) -> None:
        beneficiary_import = beneficiary_pre_subscription_sql_converter.to_rejected_model(
            beneficiary_pre_subscription, detail=detail, user=user
        )
        repository.save(beneficiary_import)
