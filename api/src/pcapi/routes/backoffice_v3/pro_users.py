from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for

import pcapi.core.offerers.models as offerers_models
import pcapi.core.permissions.models as perm_models
from pcapi.core.users import api as users_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import external as users_external
import pcapi.core.users.email.update as email_update
import pcapi.core.users.models as users_models
import pcapi.utils.email as email_utils

from . import utils
from .forms import pro_user as pro_user_forms


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

    form = pro_user_forms.EditProUserForm(
        first_name=user.firstName,
        last_name=user.lastName,
        email=user.email,
        phone_number=user.phoneNumber,
        postal_code=user.postalCode,
    )
    dst = url_for(".update_pro_user", user_id=user.id)

    can_edit_user = utils.has_current_user_permission(perm_models.Permissions.MANAGE_PRO_ENTITY)

    return render_template("pro_user/get.html", user=user, form=form, dst=dst, can_edit_user=can_edit_user)


@pro_user_blueprint.route("", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def update_pro_user(user_id: int) -> utils.BackofficeResponse:
    user = users_models.User.query.get_or_404(user_id)

    form = pro_user_forms.EditProUserForm()
    if not form.validate():
        dst = url_for(".update_pro_user", user_id=user_id)
        flash("Le formulaire n'est pas valide", "warning")
        return (
            render_template("pro_user/get.html", form=form, dst=dst, user=user, can_edit_user=True),
            400,
        )

    users_api.update_user_info(
        user,
        first_name=form.first_name.data,
        last_name=form.last_name.data,
        phone_number=form.phone_number.data,
        postal_code=form.postal_code.data,
    )

    if form.email.data and form.email.data != email_utils.sanitize_email(user.email):
        old_email = user.email
        try:
            email_update.request_email_update_from_admin(user, form.email.data)
        except users_exceptions.EmailExistsError:
            form.email.errors.append("L'email est déjà associé à un autre utilisateur")
            dst = url_for(".update_pro_user", user_id=user.id)
            return render_template("pro_user/get.html", form=form, dst=dst, user=user), 400

        users_external.update_external_user(user)

        users_external.update_external_pro(old_email)  # to delete previous user info from SendinBlue

    flash("Informations mises à jour", "success")
    return redirect(url_for(".get", user_id=user_id), code=303)
