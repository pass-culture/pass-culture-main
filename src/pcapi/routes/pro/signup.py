from flask import jsonify
from flask import request

from pcapi.core.users.api import create_pro_user
from pcapi.flask_app import private_api
from pcapi.routes.serialization import as_dict
from pcapi.utils.includes import USER_INCLUDES
from pcapi.validation.routes.users import check_valid_signup_pro


# @debt api-migration
@private_api.route("/users/signup/pro", methods=["POST"])
def signup_pro():
    check_valid_signup_pro(request)
    new_user = create_pro_user(request)

    return jsonify(as_dict(new_user, includes=USER_INCLUDES)), 201
