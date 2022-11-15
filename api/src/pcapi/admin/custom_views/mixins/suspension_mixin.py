from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from flask_admin import expose
from flask_admin.actions import action
from flask_admin.form import SecureForm
from flask_login import current_user
from markupsafe import Markup
from werkzeug.exceptions import Conflict
from werkzeug.exceptions import Forbidden
import wtforms.validators

from pcapi import settings
import pcapi.core.bookings.exceptions as bookings_exceptions
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


def _allow_suspension_and_unsuspension(user):  # type: ignore [no-untyped-def]
    if not settings.IS_PROD:
        return True
    return user.email in settings.SUPER_ADMIN_EMAIL_ADDRESSES


def _action_links(view, context, model, name):  # type: ignore [no-untyped-def]
    if not _allow_suspension_and_unsuspension(current_user):
        return None

    if model.isActive:
        url = url_for(".suspend_user_view")
        text = "Suspendre…"
    else:
        url = url_for(".unsuspend_user_view")
        text = "Réactiver…"
        if model.suspension_reason:
            text += "({}{})".format(
                model.suspension_date.strftime("%d/%m/%Y ") if model.suspension_date else "",
                dict(users_constants.SUSPENSION_REASON_CHOICES)[model.suspension_reason],
            )

    return Markup('<a href="{url}?user_id={model_id}">{text}</a>').format(
        url=url,
        model_id=model.id,
        text=text,
    )


def beneficiary_suspension_history_formatter(view, context, model, name) -> Markup:  # type: ignore [no-untyped-def]
    """
    Bullet list of suspension events which affected any user account (beneficiary, pro, admin).
    Formatting must take old suspensions into account (migrated from user table, without date and author).
    """
    suspension_history = model.suspension_history
    html = Markup("<ul>")

    for suspension_event in suspension_history:
        author_text = (
            f"par {suspension_event.actorUser.firstName} {suspension_event.actorUser.lastName}"
            if suspension_event.actorUser
            else ""
        )

        reason_text = (
            " : " + dict(users_constants.SUSPENSION_REASON_CHOICES)[suspension_event.reasonCode]
            if suspension_event.reasonCode
            else ""
        )

        html += Markup("<li>{} {} {} {}</li>").format(
            dict(users_constants.SUSPENSION_EVENT_TYPE_CHOICES)[suspension_event.eventType],
            suspension_event.eventDate.strftime("le %d/%m/%Y à %H:%M:%S") if suspension_event.eventDate else "",
            author_text,
            reason_text,
        )

    html += Markup("</ul>")
    return html


class SuspensionMixin:
    """Provide links in the "actions" column to suspend or unsuspend any
    user with a confirmation form.
    """

    @property
    def column_formatters(self):  # type: ignore [no-untyped-def]
        formatters = super().column_formatters
        formatters.update(suspension_history=beneficiary_suspension_history_formatter, actions=_action_links)
        return formatters

    @property
    def user_list_url(self):  # type: ignore [no-untyped-def]
        return url_for(".index_view")

    @action("unsuspend_selection", "Réactiver la sélection")
    def action_bulk_edit(self, ids):  # type: ignore [no-untyped-def]
        if not _allow_suspension_and_unsuspension(current_user):
            return Forbidden()

        users_api.bulk_unsuspend_account(ids, current_user)
        flash("Les comptes utilisateurs ont été réactivés. Leur mot de passe a été réinitialisé.")
        return redirect(self.user_list_url)

    @expose("suspend", methods=["GET", "POST"])
    def suspend_user_view(self):  # type: ignore [no-untyped-def]
        if not _allow_suspension_and_unsuspension(current_user):
            return Forbidden()

        user_id = request.args["user_id"]
        user = User.query.get(user_id)

        if request.method == "POST":
            form = SuspensionForm(request.form)
            if form.validate():
                flash(f"Le compte de l'utilisateur {user.email} ({user.id}) a été suspendu.")
                reason = {r.value: r for r in users_constants.SuspensionReason}[form.data["reason"]]

                try:
                    users_api.suspend_account(user, reason, current_user)
                except bookings_exceptions.BookingIsAlreadyCancelled:
                    return Conflict(description="Impossible d'annuler une des réservations (déjà annulée)")
                except bookings_exceptions.BookingIsAlreadyRefunded:
                    return Conflict(description="Impossible d'annuler une des réservations (déjà remboursée)")
                else:
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
    def unsuspend_user_view(self):  # type: ignore [no-untyped-def]
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
