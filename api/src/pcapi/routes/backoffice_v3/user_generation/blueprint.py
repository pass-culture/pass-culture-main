from flask import render_template
from werkzeug.exceptions import NotFound

from pcapi.core.users import exceptions as users_exceptions
import pcapi.core.users.generator as users_generator
from pcapi.routes.backoffice_v3 import blueprint
from pcapi.routes.backoffice_v3 import utils


@blueprint.backoffice_v3_web.route("/admin/user-generator", methods=["GET"])
def generate_user() -> utils.BackofficeResponse:
    try:
        user = users_generator.generate_user()
    except users_exceptions.UserGenerationForbiddenException:
        raise NotFound()
    return render_template("admin/users_generator.html", user=user)
