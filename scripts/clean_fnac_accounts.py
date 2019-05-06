from models import User


def find_all_fnac_darty_users():
    return User.query.filter(User.email.endswith('@fnacdarty.com')).all()
