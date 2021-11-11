from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from flask_admin import expose
from flask_admin.actions import action
from flask_admin.form import SecureForm
from flask_login import current_user
from markupsafe import Markup
from werkzeug.exceptions import Forbidden
import wtforms.validators

from pcapi import settings
import pcapi.core.users.api as users_api
import pcapi.core.users.constants as users_constants
from pcapi.core.users.models import User


class SuspensionForm(SecureForm):
    reason = wtforms.SelectField(
        "Raison de la suspension",
        choices=(("", "---"),) + users_constants.SUSPENSION_REASON_CHOICES,
        validators=[wtforms.validators.InputRequired()],
    )


class UnsuspensionForm(SecureForm):
    pass  # empty form, only has the CSRF token field


def _allow_suspension_and_unsuspension(user):
    if not settings.IS_PROD:
        return True
    return user.email in settings.SUPER_ADMIN_EMAIL_ADDRESSES


def _action_links(view, context, model, name):
    if not _allow_suspension_and_unsuspension(current_user):
        return None

    if model.isActive:
        url = url_for(".suspend_user_view")
        text = "Suspendre…"
    else:
        url = url_for(".unsuspend_user_view")
        text = "Réactiver…"

    return Markup('<a href="{url}?user_id={model_id}">{text}</a>').format(
        url=url,
        model_id=model.id,
        text=text,
    )


class SuspensionMixin:
    """Provide links in the "actions" column to suspend or unsuspend any
    user with a confirmation form.
    """

    @property
    def column_formatters(self):
        formatters = super().column_formatters
        formatters.update(actions=_action_links)
        return formatters

    @property
    def user_list_url(self):
        return url_for(".index_view")

    @action("unsuspend_selection", "Réactiver la sélection")
    def action_bulk_edit(self, ids):
        if not _allow_suspension_and_unsuspension(current_user):
            return Forbidden()

        users_api.bulk_unsuspend_account(ids, current_user)
        flash("Les comptes utilisateurs ont été réactivés. Leur mot de passe a été réinitialisé.")
        return redirect(self.user_list_url)

    @expose("suspend", methods=["GET", "POST"])
    def suspend_user_view(self):
        if not _allow_suspension_and_unsuspension(current_user):
            return Forbidden()

        user_id = request.args["user_id"]
        user = User.query.get(user_id)

        if request.method == "POST":
            form = SuspensionForm(request.form)
            if form.validate():
                flash(f"Le compte de l'utilisateur {user.email} ({user.id}) a été suspendu.")
                reason = {r.value: r for r in users_constants.SuspensionReason}[form.data["reason"]]
                users_api.suspend_account(user, reason, current_user)
                return redirect(self.user_list_url)
        else:
            form = SuspensionForm()

        context = {
            "cancel_link_url": self.user_list_url,
            "user": user,
            "form": form,
        }
        return self.render("admin/confirm_suspension.html", **context)

    @expose("unsuspend", methods=["GET", "POST"])
    def unsuspend_user_view(self):
        if not _allow_suspension_and_unsuspension(current_user):
            return Forbidden()

        user_id = request.args["user_id"]
        user = User.query.get(user_id)

        if request.method == "POST":
            form = UnsuspensionForm(request.form)
            if form.validate():
                flash(f"Le compte de l'utilisateur {user.email} ({user.id}) a été réactivé.")
                users_api.unsuspend_account(user, current_user)
                return redirect(self.user_list_url)
        else:
            form = UnsuspensionForm()

        context = {
            "cancel_link_url": self.user_list_url,
            "user": user,
            "form": form,
        }
        return self.render("admin/confirm_unsuspension.html", **context)
