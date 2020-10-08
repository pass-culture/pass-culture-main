from pcapi.domain.beneficiary.beneficiary import Beneficiary
from pcapi.models import UserSQLEntity


def to_domain(user_sql_entity: UserSQLEntity) -> Beneficiary:
    return Beneficiary(
        identifier=user_sql_entity.id,
        can_book_free_offers=user_sql_entity.canBookFreeOffers,
        email=user_sql_entity.email,
        first_name=user_sql_entity.firstName,
        last_name=user_sql_entity.lastName,
        department_code=user_sql_entity.departementCode,
        wallet_balance=user_sql_entity.wallet_balance,
        reset_password_token=user_sql_entity.resetPasswordToken
    )
