from typing import Callable, List

from sqlalchemy import func

from domain.password import random_password
from models import User, PcObject


def get_all_users_with_non_standard_passwords():
    normal_password_length = 60
    return User.query.filter(func.length(User.password) != normal_password_length).all()


def set_new_password_for(get_users: Callable[..., List[User]] = get_all_users_with_non_standard_passwords):
    users = get_users()
    for user in users:
        user.password = random_password()
    PcObject.save(*users)
