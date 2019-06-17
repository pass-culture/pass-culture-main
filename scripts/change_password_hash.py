from typing import Callable, List

from sqlalchemy import func

from domain.password import random_password
from models import User, PcObject


def get_all_users_for_password_change():
    return User.query.filter(func.length(User.password) != 60).all()


def set_new_password_for(get_users: Callable[..., List[User]] = get_all_users_for_password_change):
    users = get_users()
    for user in users:
        user.password = random_password()
    PcObject.save(*users)
