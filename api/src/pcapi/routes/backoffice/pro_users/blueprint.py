from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from markupsafe import Markup
import sqlalchemy as sa
from werkzeug.exceptions import NotFound

from pcapi.core import mails as mails_api
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.history import repository as history_repository
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import api as users_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as users_models
from pcapi.core.users.email import update as email_update
from pcapi.models import db
from pcapi.routes.backoffice import utils
from pcapi.routes.backoffice.forms import empty as empty_forms
from pcapi.routes.backoffice.forms import search as search_forms
from pcapi.routes.backoffice.forms.search import TypeOptions
from pcapi.routes.backoffice.pro_users import forms as pro_users_forms
from pcapi.routes.backoffice.users import forms as user_forms
from pcapi.tasks.batch_tasks import DeleteBatchUserAttributesRequest
from pcapi.tasks.batch_tasks import delete_user_attributes_task
from pcapi.utils import email as email_utils


pro_user_blueprint = utils.child_backoffice_blueprint(
    "pro_user",
    __name__,
    url_prefix="/pro/user/<int:user_id>",
    permission=perm_models.Permissions.READ_PRO_ENTITY,
)


@pro_user_blueprint.route("", methods=["GET"])
def get(user_id: int) -> utils.BackofficeResponse:
    # Make sure user is pro
    user = (
        users_api.get_pro_account_base_query(user_id)
        .options(
            sa.orm.joinedload(users_models.User.UserOfferers).load_only(offerers_models.UserOfferer.validationStatus)
        )
        .one_or_none()
    )
    if not user:
        flash("Cet utilisateur n'a pas de compte pro ou n'existe pas", "warning")
        return redirect(url_for("backoffice_web.search_pro"), code=303)

    form = pro_users_forms.EditProUserForm(
        first_name=user.firstName,
        last_name=user.lastName,
        email=user.email,
        phone_number=user.phoneNumber,
        postal_code=user.postalCode,
    )
    dst = url_for(".update_pro_user", user_id=user.id)

    if request.args.get("q") and request.args.get("search_rank"):
        utils.log_backoffice_tracking_data(
            event_name="ConsultCard",
            extra_data={
                "searchType": "ProSearch",
                "searchProType": TypeOptions.USER.name,
                "searchQuery": request.args.get("q"),
                "searchRank": request.args.get("search_rank"),
                "searchNbResults": request.args.get("total_items"),
            },
        )

    return render_template(
        "pro_user/get.html",
        search_form=search_forms.CompactProSearchForm(q=request.args.get("q"), pro_type=TypeOptions.USER.name),
        search_dst=url_for("backoffice_web.search_pro"),
        user=user,
        form=form,
        dst=dst,
        empty_form=empty_forms.EmptyForm(),
        **user_forms.get_toggle_suspension_args(user, suspension_type=user_forms.SuspensionUserType.PRO),
        **_get_delete_kwargs(user),
    )


@pro_user_blueprint.route("/details", methods=["GET"])
def get_details(user_id: int) -> utils.BackofficeResponse:
    user = users_api.get_pro_account_base_query(user_id).one_or_none()
    if not user:
        raise NotFound()

    actions = history_repository.find_all_actions_by_user(user_id)
    can_add_comment = utils.has_current_user_permission(perm_models.Permissions.MANAGE_PRO_ENTITY)
    user_offerers = (
        offerers_models.UserOfferer.query.filter_by(userId=user_id)
        .order_by(offerers_models.UserOfferer.dateCreated)
        .options(sa.orm.joinedload(offerers_models.UserOfferer.offerer))
        .all()
    )

    form = pro_users_forms.CommentForm()
    dst = url_for("backoffice_web.pro_user.comment_pro_user", user_id=user.id)

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
    user = users_api.get_pro_account_base_query(user_id).one_or_none()
    if not user:
        raise NotFound()

    form = pro_users_forms.EditProUserForm()
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


@pro_user_blueprint.route("/delete", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def delete(user_id: int) -> utils.BackofficeResponse:
    user = users_api.get_pro_account_base_query(user_id).one_or_none()
    if not user:
        raise NotFound()

    if not _user_can_be_deleted(user):
        flash("Le compte est rattaché à une structure", "warning")
        return redirect(url_for("backoffice_web.pro_user.get", user_id=user_id), code=303)

    form = pro_users_forms.DeleteProUser()
    if not form.validate():
        flash("Le formulaire n'est pas valide", "warning")
        return redirect(url_for("backoffice_web.pro_user.get", user_id=user_id), code=303)

    if not form.email.data == user.email:
        flash("L'email saisi ne correspond pas à celui du compte", "warning")
        return redirect(url_for("backoffice_web.pro_user.get", user_id=user_id), code=303)

    # clear from mailing list
    if not offerers_models.Venue.query.filter(offerers_models.Venue.bookingEmail == user.email).limit(1).count():
        mails_api.delete_contact(user.email)

    # clear from push notifications
    payload = DeleteBatchUserAttributesRequest(user_id=user.id)
    delete_user_attributes_task.delay(payload)

    users_models.User.query.filter(users_models.User.id == user_id).delete()
    db.session.commit()
    flash("Le compte a bien été supprimé", "success")
    return redirect(url_for("backoffice_web.search_pro"), code=303)


@pro_user_blueprint.route("/comment", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def comment_pro_user(user_id: int) -> utils.BackofficeResponse:
    user = users_api.get_pro_account_base_query(user_id).one_or_none()
    if not user:
        raise NotFound()

    form = pro_users_forms.CommentForm()
    if not form.validate():
        flash(utils.build_form_error_msg(form), "warning")
        return redirect(url_for("backoffice_web.pro_user.get", user_id=user_id), code=302)

    users_api.add_comment_to_user(user=user, author_user=current_user, comment=form.comment.data)
    flash("Commentaire enregistré", "success")

    return redirect(url_for("backoffice_web.pro_user.get", user_id=user_id), code=303)


@pro_user_blueprint.route("/validate-email", methods=["POST"])
@utils.permission_required(perm_models.Permissions.MANAGE_PRO_ENTITY)
def validate_pro_user_email(user_id: int) -> utils.BackofficeResponse:
    user = users_api.get_pro_account_base_query(user_id).one_or_none()
    if not user:
        raise NotFound()

    if user.isEmailValidated:
        flash(Markup("L'email {email} est déjà validé !").format(email=user.email), "warning")
    else:
        users_api.validate_pro_user_email(user=user, author_user=current_user)
        flash(Markup("L'email {email} est validé !").format(email=user.email), "success")
    return redirect(url_for("backoffice_web.pro_user.get", user_id=user_id), code=303)


def _user_can_be_deleted(user: users_models.User) -> bool:
    return user.has_non_attached_pro_role and len(user.roles) == 1 and not user.UserOfferers


def _get_delete_kwargs(user: users_models.User) -> dict:
    kwargs = {
        "can_be_deleted": _user_can_be_deleted(user),
        "delete_dest": url_for("backoffice_web.pro_user.delete", user_id=user.id),
        "delete_form": pro_users_forms.DeleteProUser(),
    }
    return kwargs
