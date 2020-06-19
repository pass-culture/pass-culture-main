from domain.beneficiary.beneficiary import Beneficiary
from domain.beneficiary.beneficiary_exceptions import BeneficiaryDoesntExist
from domain.beneficiary.beneficiary_repository import BeneficiaryRepository
from models import UserSQLEntity
from models.db import db
from infrastructure.repository.beneficiary import beneficiary_sql_converter


class BeneficiarySQLRepository(BeneficiaryRepository):
    def find_beneficiary_by_user_id(self, user_id: int) -> Beneficiary:
        user_sql_entity = db.session.query(UserSQLEntity) \
            .get(user_id)

        if user_sql_entity is None:
            raise BeneficiaryDoesntExist()

        return beneficiary_sql_converter.to_domain(user_sql_entity)
