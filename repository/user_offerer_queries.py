from models import UserOfferer, User


def find_user_offerer_email(user_offerer_id):
    return UserOfferer.query.filter_by(id=user_offerer_id).join(User).with_entities(User.email).first()[0]