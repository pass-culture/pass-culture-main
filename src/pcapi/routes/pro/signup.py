from typing import Tuple

from flask import request

from pcapi.core.users.api import create_pro_user
from pcapi.flask_app import private_api
from pcapi.validation.routes.users import check_valid_signup_pro


# @debt api-migration
@private_api.route("/users/signup/pro", methods=["POST"])
def signup_pro() -> Tuple[str, int]:
    check_valid_signup_pro(request)
    create_pro_user(request)

    return "", 204
