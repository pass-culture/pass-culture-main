from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from flask_login import current_user

from pcapi.core.permissions import models as perm_models
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import models as users_models

from . import utils
from .forms import user as user_forms


# This blueprint is for common actions on User, which can be beneficiary, pro, admin...
# Currently targets actions related to "Fraude & Conformité"
users_blueprint = utils.child_backoffice_blueprint(
    "users",
    __name__,
    url_prefix="/users/<int:user_id>",
    permission=perm_models.Permissions.REVIEW_SUSPEND_USER,
)


def _redirect_to_user_page(user: users_models.User) -> utils.BackofficeResponse:
    # Actions should always come from user details page
    if request.referrer:
        return redirect(request.referrer, code=303)

    # Fallback in case referrer is missing (maybe because of browser settings)
    if user.UserOfferers:
        return redirect(url_for("backoffice_v3_web.pro_user.get", user_id=user.id), code=303)

    return redirect(url_for("backoffice_v3_web.public_accounts.get_public_account", user_id=user.id), code=303)


@users_blueprint.route("/suspend", methods=["POST"])
def suspend_user(user_id: int) -> utils.BackofficeResponse:
    user = users_models.User.query.get_or_404(user_id)

    form = user_forms.SuspendUserForm()
    if form.validate():
        users_api.suspend_account(
            user, users_constants.SuspensionReason[form.reason.data], current_user, comment=form.comment.data
        )
        flash(f"Le compte de l'utilisateur {user.email} ({user.id}) a été suspendu", "success")
    else:
        flash("Les données envoyées sont invalides", "warning")

    return _redirect_to_user_page(user)


@users_blueprint.route("/unsuspend", methods=["POST"])
def unsuspend_user(user_id: int) -> utils.BackofficeResponse:
    user = users_models.User.query.get_or_404(user_id)

    form = user_forms.UnsuspendUserForm()
    if form.validate():
        users_api.unsuspend_account(user, current_user, comment=form.comment.data)
        flash(f"Le compte de l'utilisateur {user.email} ({user.id}) a été réactivé", "success")
    else:
        flash("Les données envoyées sont invalides", "warning")

    return _redirect_to_user_page(user)
