from domain.beneficiary.beneficiary import Beneficiary
from domain.beneficiary.beneficiary_exceptions import BeneficiaryDoesntExist
from domain.beneficiary_pre_subscription.beneficiary_pre_subscription import \
    BeneficiaryPreSubscription
from domain.beneficiary.beneficiary_repository import BeneficiaryRepository
from infrastructure.repository.beneficiary import beneficiary_pre_subscription_sql_converter, \
    beneficiary_sql_converter
from models import UserSQLEntity
from models.db import db
from repository import repository


class BeneficiarySQLRepository(BeneficiaryRepository):
    def find_beneficiary_by_user_id(self, user_id: int) -> Beneficiary:
        user_sql_entity = db.session.query(UserSQLEntity) \
            .get(user_id)

        if user_sql_entity is None:
            raise BeneficiaryDoesntExist()

        return beneficiary_sql_converter.to_domain(user_sql_entity)

    @classmethod
    def save(cls, beneficiary_pre_subscription: BeneficiaryPreSubscription) -> Beneficiary:
        user_sql_entity = beneficiary_pre_subscription_sql_converter.to_model(beneficiary_pre_subscription)

        repository.save(user_sql_entity)

        return beneficiary_sql_converter.to_domain(user_sql_entity)

    @classmethod
    def reject(cls, beneficiary_pre_subscription: BeneficiaryPreSubscription, detail: str) -> None:
        beneficiary_import = beneficiary_pre_subscription_sql_converter \
            .to_rejected_model(beneficiary_pre_subscription, detail=detail)

        repository.save(beneficiary_import)
