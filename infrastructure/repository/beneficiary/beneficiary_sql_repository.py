from domain.beneficiary.beneficiary import Beneficiary
from domain.beneficiary.beneficiary_exceptions import BeneficiaryDoesntExist
from domain.beneficiary.beneficiary_pre_subscription import \
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
        beneficiary_sql_entitiy = beneficiary_pre_subscription_sql_converter.to_model(beneficiary_pre_subscription)

        repository.save(beneficiary_sql_entitiy)

        return beneficiary_sql_converter.to_domain(beneficiary_sql_entitiy)

    @classmethod
    def reject(cls, beneficiary_pre_subscription: BeneficiaryPreSubscription, detail: str) -> None:
        beneficiary_sql_entitiy = beneficiary_pre_subscription_sql_converter \
            .to_rejected_model(beneficiary_pre_subscription, detail=detail)

        repository.save(beneficiary_sql_entitiy)
