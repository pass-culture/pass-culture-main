from typing import Optional

from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription.models import BeneficiaryPreSubscription
from pcapi.core.users import api as users_api
from pcapi.core.users.external import update_external_user
from pcapi.core.users.models import User
from pcapi.infrastructure.repository.beneficiary import beneficiary_pre_subscription_sql_converter
from pcapi.repository import repository


class BeneficiarySQLRepository:
    @classmethod
    def save(cls, beneficiary_pre_subscription: BeneficiaryPreSubscription, user: Optional[User] = None) -> User:
        user_sql_entity = beneficiary_pre_subscription_sql_converter.to_model(beneficiary_pre_subscription, user=user)
        users_api.attach_beneficiary_import_details(user_sql_entity, beneficiary_pre_subscription)
        repository.save(user_sql_entity)

        if not users_api.steps_to_become_beneficiary(user_sql_entity):
            user_sql_entity = subscription_api.check_and_activate_beneficiary(
                user_sql_entity.id, beneficiary_pre_subscription.deposit_source
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
