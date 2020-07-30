from models.user_sql_entity import UserSQLEntity
from models.user_offerer import UserOfferer
from sandboxes.scripts.utils.helpers import get_pro_helper


def get_pro_validated_no_reset_password_token_user():
    query = UserSQLEntity.query.filter(
        (UserSQLEntity.validationToken == None) & \
        (UserSQLEntity.resetPasswordToken == None)
    )
    query = query.join(UserOfferer)
    user = query.first()

    return {
        "user": get_pro_helper(user)
    }

def get_pro_validated_with_reset_password_token_user():
    query = UserSQLEntity.query.filter(
        (UserSQLEntity.validationToken == None) & \
        (UserSQLEntity.resetPasswordToken != None)
    )
    query = query.join(UserOfferer)
    user = query.first()

    return {
        "user": get_pro_helper(user)
    }
