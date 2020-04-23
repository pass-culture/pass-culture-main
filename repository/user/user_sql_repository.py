from domain.user.user import User
from domain.user.user_repository import UserRepository
from models import UserSQLEntity
from models.db import db


class UserSQLRepository(UserRepository):
    def find_user_by_id(self, user_id: int) -> User:
        user_sql_entity = db.session.query(UserSQLEntity) \
            .get(user_id)

        return User(
            identifier=user_sql_entity.id,
            can_book_free_offers=user_sql_entity.canBookFreeOffers
        )
