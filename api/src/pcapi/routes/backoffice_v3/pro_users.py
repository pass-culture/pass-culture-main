from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
import sqlalchemy as sa

from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.history import repository as history_repository
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import api as users_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as users_models
import pcapi.core.users.email.update as email_update
import pcapi.utils.email as email_utils

from . import utils
from .forms import empty as empty_forms
from .forms import pro_user as pro_user_forms
from .forms import search as search_forms
from .forms import user as user_forms
from .serialization.search import TypeOptions


pro_user_blueprint = utils.child_backoffice_blueprint(
    "pro_user",
    __name__,
    url_prefix="/pro/user/<int:user_id>",
    permission=perm_models.Permissions.READ_PRO_ENTITY,
)


@pro_user_blueprint.route("", methods=["GET"])
def get(user_id: int) -> utils.BackofficeResponse:
    # Make sure user is pro
    user = users_models.User.query.filter(
        sa.and_(users_models.User.id == user_id, (users_models.User.has_non_attached_pro_role.is_(True) | users_models.User.has_pro_role.is_(True)))  # type: ignore [attr-defined]
    ).one_or_none()
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

    return render_template(
        "pro_user/get.html",
        search_form=search_forms.ProSearchForm(pro_type=TypeOptions.USER.value),
        search_dst=url_for("backoffice_v3_web.search_pro"),
        user=user,
        form=form,
        dst=dst,
        empty_form=empty_forms.EmptyForm(),
        **user_forms.get_toggle_suspension_args(user),
    )


@pro_user_blueprint.route("/details", methods=["GET"])
def get_details(user_id: int) -> utils.BackofficeResponse:
    user = users_models.User.query.get_or_404(user_id)
    actions = history_repository.find_all_actions_by_user(user_id)
    can_add_comment = utils.has_current_user_permission(perm_models.Permissions.MANAGE_PRO_ENTITY)
    user_offerers = (
        offerers_models.UserOfferer.query.filter_by(userId=user_id)
        .order_by(offerers_models.UserOfferer.dateCreated)
        .options(sa.orm.joinedload(offerers_models.UserOfferer.offerer))
        .all()
    )

    form = pro_user_forms.CommentForm()
    dst = url_for("backoffice_v3_web.pro_user.comment_pro_user", user_id=user.id)

    return render_template(
        "pro_user/get/details.html",
        user=user,
        form=form,
        dst=dst,
        actions=actions,
        can_add_comment=can_add_comment,
        user_offerers=user_offerers,
        active_tab=request.args.get("active_tab", "history"),
    )


@pro_user_blueprint.route("/update", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def update_pro_user(user_id: int) -> utils.BackofficeResponse:
    user = users_models.User.query.get_or_404(user_id)

    form = pro_user_forms.EditProUserForm()
    if not form.validate():
        dst = url_for(".update_pro_user", user_id=user_id)
        flash("Le formulaire n'est pas valide", "warning")
        return render_template("pro_user/get.html", form=form, dst=dst, user=user), 400

    snapshot = users_api.update_user_info(
        user,
        author=current_user,
        first_name=form.first_name.data,
        last_name=form.last_name.data,
        phone_number=form.phone_number.data,
        postal_code=form.postal_code.data,
    )

    if form.email.data and form.email.data != email_utils.sanitize_email(user.email):
        old_email = user.email
        snapshot.set("email", old=old_email, new=form.email.data)

        try:
            email_update.request_email_update_from_admin(user, form.email.data)
        except users_exceptions.EmailExistsError:
            form.email.errors.append("L'email est déjà associé à un autre utilisateur")
            dst = url_for(".update_pro_user", user_id=user.id)
            return render_template("pro_user/get.html", form=form, dst=dst, user=user), 400

        external_attributes_api.update_external_pro(old_email)  # to delete previous user info from SendinBlue
        external_attributes_api.update_external_user(user)

    snapshot.log_update(save=True)

    flash("Informations mises à jour", "success")
    return redirect(url_for(".get", user_id=user_id), code=303)


@pro_user_blueprint.route("/comment", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def comment_pro_user(user_id: int) -> utils.BackofficeResponse:
    user = users_models.User.query.get_or_404(user_id)

    form = pro_user_forms.CommentForm()
    if not form.validate():
        flash("Les données envoyées comportent des erreurs", "warning")
        return redirect(url_for("backoffice_v3_web.pro_user.get", user_id=user_id), code=302)

    users_api.add_comment_to_user(user=user, author_user=current_user, comment=form.comment.data)
    flash("Commentaire enregistré", "success")

    return redirect(url_for("backoffice_v3_web.pro_user.get", user_id=user_id), code=303)


@pro_user_blueprint.route("/validate-email", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def validate_pro_user_email(user_id: int) -> utils.BackofficeResponse:
    user = users_models.User.query.get_or_404(user_id)
    if user.isEmailValidated:
        flash(f"L'e-mail {user.email} est déjà validé !", "warning")
    else:
        users_api.validate_pro_user_email(user=user, author_user=current_user)
        flash(f"L'e-mail {user.email} est validé !", "success")
    return redirect(url_for("backoffice_v3_web.pro_user.get", user_id=user_id), code=303)
