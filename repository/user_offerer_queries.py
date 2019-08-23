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


def query_filter_user_offerer_is_not_validated(query):
    return _query_filter_user_offerer_by_validation_status(query, False)


def query_filter_user_offerer_is_validated(query):
    return _query_filter_user_offerer_by_validation_status(query, True)


def _query_filter_user_offerer_by_validation_status(query, is_validated: bool):
    if is_validated is True:
        return query.filter(UserOfferer.validationToken == None)
    else:
        return query.filter(UserOfferer.validationToken != None)
