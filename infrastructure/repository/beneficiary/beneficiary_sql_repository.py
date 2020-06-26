from domain.beneficiary.beneficiary import Beneficiary
from domain.beneficiary.beneficiary_exceptions import BeneficiaryDoesntExist
from domain.beneficiary.beneficiary_repository import BeneficiaryRepository
from domain.beneficiary.beneficiary_pre_subscription import \
    BeneficiaryPreSubscription
from models import UserSQLEntity
from models.db import db
from infrastructure.repository.beneficiary import beneficiary_sql_converter, beneficiary_pre_subscription_sql_converter
from infrastructure.repository.beneficiary import \
    beneficiary_pre_subscription_sql_converter
from repository import repository


class BeneficiarySQLRepository(BeneficiaryRepository):
    def find_beneficiary_by_user_id(self, user_id: int) -> Beneficiary:
        user_sql_entity = db.session.query(UserSQLEntity) \
            .get(user_id)

        if user_sql_entity is None:
            raise BeneficiaryDoesntExist()

        return beneficiary_sql_converter.to_domain(user_sql_entity)

    @classmethod
    def save(cls, beneficiary_pre_subscription: BeneficiaryPreSubscription):
        beneficiary = beneficiary_pre_subscription_sql_converter.to_model(beneficiary_pre_subscription)

        repository.save(beneficiary)

        return beneficiary


    @classmethod
    def save_rejected(cls, beneficiary_pre_subscription: BeneficiaryPreSubscription, detail: str):
        beneficiary_import = beneficiary_pre_subscription_sql_converter.create_rejected_beneficiary_import(beneficiary_pre_subscription,
                                                                                                           detail=detail)

        repository.save(beneficiary_import)
