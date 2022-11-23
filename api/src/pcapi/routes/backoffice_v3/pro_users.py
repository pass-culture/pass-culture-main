from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for

import pcapi.core.offerers.models as offerers_models
import pcapi.core.permissions.models as perm_models
import pcapi.core.users.models as users_models

from . import utils


pro_user_blueprint = utils.child_backoffice_blueprint(
    "pro_user",
    __name__,
    url_prefix="/pro/pro_user/<int:user_id>",
    permission=perm_models.Permissions.READ_PRO_ENTITY,
)


@pro_user_blueprint.route("", methods=["GET"])
def get(user_id: int) -> utils.BackofficeResponse:
    # TODO (vroullier) 24-11-2022 : use User.roles once it is updated
    # Make sure user is pro
    user = (
        users_models.User.query.join(offerers_models.UserOfferer).filter(users_models.User.id == user_id).one_or_none()
    )
    if not user:
        flash("Cet utilisateur n'a pas de compte pro ou n'existe pas", "warning")
        return redirect(url_for("backoffice_v3_web.search_pro"), code=303)

    return render_template("pro_user/get.html", user=user)
