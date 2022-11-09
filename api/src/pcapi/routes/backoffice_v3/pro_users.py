from flask import render_template

import pcapi.core.permissions.models as perm_models
import pcapi.core.users.models as users_models

from . import utils


pro_user_blueprint = utils.child_backoffice_blueprint(
    "pro_user",
    __name__,
    url_prefix="/pro/user/<int:user_id>",
    permission=perm_models.Permissions.READ_PRO_ENTITY,
)


@pro_user_blueprint.route("", methods=["GET"])
def get(user_id: int) -> utils.BackofficeResponse:
    pro_user = users_models.User.query.get_or_404(user_id)
    return render_template("pro_user/get.html", row=pro_user)
