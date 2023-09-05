from operator import attrgetter

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import load_only
from werkzeug.exceptions import Forbidden

from pcapi.core.bookings import models as bookings_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import models as users_models
from pcapi.routes.backoffice_v3 import utils
from pcapi.routes.backoffice_v3.users import forms


# This blueprint is for common actions on User, which can be beneficiary, pro, admin...
# Currently targets actions related to "Fraude & Conformité"
users_blueprint = utils.child_backoffice_blueprint(
    "users",
    __name__,
    url_prefix="/users",
)


def _redirect_to_user_page(user: users_models.User) -> utils.BackofficeResponse:
    # Actions should always come from user details page
    if request.referrer:
        return redirect(request.referrer, code=303)

    # Fallback in case referrer is missing (maybe because of browser settings)
    if user.UserOfferers:
        return redirect(url_for("backoffice_v3_web.pro_user.get", user_id=user.id), code=303)

    return redirect(url_for("backoffice_v3_web.public_accounts.get_public_account", user_id=user.id), code=303)


def _check_user_role_vs_backoffice_permission(user: users_models.User) -> None:
    if user.has_pro_role or user.has_non_attached_pro_role:
        if not utils.has_current_user_permission(perm_models.Permissions.PRO_FRAUD_ACTIONS):
            raise Forbidden()
    else:  # not pro
        if not utils.has_current_user_permission(perm_models.Permissions.BENEFICIARY_FRAUD_ACTIONS):
            raise Forbidden()


@users_blueprint.route("/<int:user_id>/suspend", methods=["POST"])
@utils.permission_required_in([perm_models.Permissions.SUSPEND_USER, perm_models.Permissions.PRO_FRAUD_ACTIONS])
def suspend_user(user_id: int) -> utils.BackofficeResponse:
    user = users_models.User.query.get_or_404(user_id)
    _check_user_role_vs_backoffice_permission(user)

    form = forms.SuspendUserForm()
    if form.validate():
        users_api.suspend_account(
            user, users_constants.SuspensionReason[form.reason.data], current_user, comment=form.comment.data
        )
        flash(f"Le compte de l'utilisateur {user.email} ({user.id}) a été suspendu", "success")
    else:
        flash("Les données envoyées sont invalides", "warning")

    return _redirect_to_user_page(user)


@users_blueprint.route("/<int:user_id>/unsuspend", methods=["POST"])
@utils.permission_required_in([perm_models.Permissions.UNSUSPEND_USER, perm_models.Permissions.PRO_FRAUD_ACTIONS])
def unsuspend_user(user_id: int) -> utils.BackofficeResponse:
    user = users_models.User.query.get_or_404(user_id)
    _check_user_role_vs_backoffice_permission(user)

    form = forms.UnsuspendUserForm()
    if form.validate():
        users_api.unsuspend_account(user, current_user, comment=form.comment.data)
        flash(f"Le compte de l'utilisateur {user.email} ({user.id}) a été réactivé", "success")
    else:
        flash("Les données envoyées sont invalides", "warning")

    return _redirect_to_user_page(user)


def _render_batch_suspend_users_form(form: forms.BatchSuspendUsersForm) -> str:
    return render_template(
        "components/turbo/modal_form.html",
        form=form,
        dst=url_for(".batch_suspend_users"),
        div_id="batch-suspend-users-form",
        title="Suspendre des utilisateurs en masse",
        information="Ajouter tous les ID d'utilisateurs à suspendre séparés par des virgules",
        button_text="Continuer",
        data_turbo="true",
    )


@users_blueprint.route("/batch-suspend-form", methods=["GET"])
@utils.permission_required(perm_models.Permissions.BENEFICIARY_FRAUD_ACTIONS)
def get_batch_suspend_users_form() -> utils.BackofficeResponse:
    form = forms.BatchSuspendUsersForm(suspension_type=forms.SuspensionUserType.PUBLIC)
    return _render_batch_suspend_users_form(form)


def _check_users_to_suspend(ids_list: set[int]) -> tuple[list[users_models.User], list[str]]:
    users: list[users_models.User] = (
        users_models.User.query.filter(users_models.User.id.in_(ids_list))
        .options(
            load_only(users_models.User.email, users_models.User.id, users_models.User.roles),
            joinedload(users_models.User.userBookings).load_only(bookings_models.Booking.status),
        )
        .all()
    )

    errors = []

    if len(users) != len(ids_list):
        ids_not_found = ids_list - {user.id for user in users}
        errors.append(f"ID non trouvés : {', '.join(str(id_) for id_ in sorted(ids_not_found))}")

    admins = [user for user in users if user.has_admin_role]
    if admins:
        data = ", ".join(f"{user.id} ({user.email})" for user in sorted(admins, key=attrgetter("id")))
        errors.append(f"ID correspondant à un utilisateur admin : {data}")

    pros = [user for user in users if user.has_pro_role or user.has_non_attached_pro_role]
    if pros:
        data = ", ".join(f"{user.id} ({user.email})" for user in sorted(pros, key=attrgetter("id")))
        errors.append(f"ID correspondant à un utilisateur pro : {data}")

    return users, errors


@users_blueprint.route("/batch-suspend", methods=["POST"])
@utils.permission_required(perm_models.Permissions.BENEFICIARY_FRAUD_ACTIONS)
def batch_suspend_users() -> utils.BackofficeResponse:
    form = forms.BatchSuspendUsersForm()
    if not form.validate():
        return _render_batch_suspend_users_form(form), 400

    users, errors = _check_users_to_suspend(form.get_user_ids())
    if errors:
        form.user_ids.errors += errors
        return _render_batch_suspend_users_form(form), 400

    cancellable_bookings_count = len(
        [
            booking
            for user in users
            for booking in user.userBookings
            if booking.status == bookings_models.BookingStatus.CONFIRMED
        ]
    )
    return render_template(
        "accounts/batch_suspend.html",
        form=form,
        dst=url_for(".confirm_batch_suspend_users"),
        div_id="batch-suspend-users-form",
        users_count=len(users),
        cancellable_bookings_count=cancellable_bookings_count,
    )


@users_blueprint.route("/batch-suspend/confirm", methods=["POST"])
@utils.permission_required(perm_models.Permissions.BENEFICIARY_FRAUD_ACTIONS)
def confirm_batch_suspend_users() -> utils.BackofficeResponse:
    form = forms.BatchSuspendUsersForm()
    if not form.validate():
        return _render_batch_suspend_users_form(form), 400

    users, errors = _check_users_to_suspend(form.get_user_ids())
    if errors:
        form.user_ids.errors += errors
        return _render_batch_suspend_users_form(form), 400

    for user in users:
        users_api.suspend_account(
            user, users_constants.SuspensionReason[form.reason.data], current_user, comment=form.comment.data
        )

    if len(users) > 1:
        flash(f"{len(users)} comptes d'utilisateurs ont été suspendus", "success")
    else:
        flash(f"{len(users)} compte d'utilisateur a été suspendu", "success")

    return redirect(url_for("backoffice_v3_web.fraud.list_blacklisted_domain_names"))
