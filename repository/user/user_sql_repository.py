from domain.user.user import User
from domain.user.user_repository import UserRepository
from models.db import db


class UserSQLRepository(UserRepository):
    def find_user_by_id(self, user_id: int) -> User:
        user_model = db.session.query(UserSQLEntity).get(user_id)

        user = User()
        return user
