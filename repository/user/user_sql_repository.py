from domain.user.user import User
from domain.user.user_exceptions import UserDoesntExist
from domain.user.user_repository import UserRepository
from models import UserSQLEntity
from models.db import db
from repository.user import user_domain_adapter


class UserSQLRepository(UserRepository):
    def find_user_by_id(self, user_id: int) -> User:
        user_sql_entity = db.session.query(UserSQLEntity) \
            .get(user_id)

        if user_sql_entity is None:
            raise UserDoesntExist()

        return user_domain_adapter.to_domain(user_sql_entity)
