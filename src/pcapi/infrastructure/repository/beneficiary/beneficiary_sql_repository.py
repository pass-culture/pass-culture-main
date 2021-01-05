from pcapi.core.users.models import UserSQLEntity
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription import BeneficiaryPreSubscription
from pcapi.infrastructure.repository.beneficiary import beneficiary_pre_subscription_sql_converter
from pcapi.repository import repository


class BeneficiarySQLRepository:
    @classmethod
    def save(cls, beneficiary_pre_subscription: BeneficiaryPreSubscription) -> UserSQLEntity:
        user_sql_entity = beneficiary_pre_subscription_sql_converter.to_model(beneficiary_pre_subscription)
        repository.save(user_sql_entity)
        return user_sql_entity

    @classmethod
    def reject(cls, beneficiary_pre_subscription: BeneficiaryPreSubscription, detail: str) -> None:
        beneficiary_import = beneficiary_pre_subscription_sql_converter.to_rejected_model(
            beneficiary_pre_subscription, detail=detail
        )
        repository.save(beneficiary_import)
