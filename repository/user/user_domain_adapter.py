from domain.user.user import User
from models import UserSQLEntity


def to_domain(user_sql_entity: UserSQLEntity) -> User:
    return User(
        identifier=user_sql_entity.id,
        can_book_free_offers=user_sql_entity.canBookFreeOffers,
        email=user_sql_entity.email,
        first_name=user_sql_entity.firstName,
        last_name=user_sql_entity.lastName,
        department_code=user_sql_entity.departementCode,
    )
