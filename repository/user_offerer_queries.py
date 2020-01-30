from models import UserOfferer, User


def find_user_offerer_email(user_offerer_id):
    return UserOfferer.query \
        .filter_by(id=user_offerer_id) \
        .join(User) \
        .with_entities(User.email) \
        .first()[0]


def filter_query_where_user_is_user_offerer_and_is_validated(query, user):
    return query \
        .join(UserOfferer) \
        .filter_by(user=user) \
        .filter(UserOfferer.validationToken == None)


def filter_query_where_user_is_user_offerer_and_is_not_validated(query, user):
    return query \
        .join(UserOfferer) \
        .filter_by(user=user) \
        .filter(UserOfferer.validationToken != None)


def count_user_offerers_by_offerer(offerer):
    return UserOfferer.query \
        .filter_by(offerer=offerer) \
        .count()


def find_one_or_none_by_user_id(user_id):
    return UserOfferer.query.filter_by(userId=user_id).one_or_none()


def find_one_or_none_by_offerer_id(offerer_id):
    return UserOfferer.query.filter_by(offererId=offerer_id).one_or_none()


def find_one_or_none_by_user_id_and_offerer_id(user_id: int, offerer_id: int) -> UserOfferer:
    return UserOfferer.query \
        .filter_by(userId=user_id, offererId=offerer_id) \
        .one_or_none()


def count_pro_attached_to_offerer(offerer_id: int) -> int:
    return UserOfferer.query.filter_by(offererId=offerer_id).count()
