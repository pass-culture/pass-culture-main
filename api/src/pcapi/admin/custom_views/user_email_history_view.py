from flask import redirect
from flask import request
from flask import url_for
from flask.helpers import flash
from flask_admin import expose
from werkzeug import Response
from werkzeug.exceptions import BadRequestKeyError
from werkzeug.routing import BuildError

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.admin.custom_views.mixins.suspension_mixin import SuspensionMixin
from pcapi.core.users import api as users_api
from pcapi.core.users import exceptions as users_exceptions
from pcapi.core.users import models as users_models
from pcapi.core.users.email import repository as email_repository
from pcapi.core.users.models import UserEmailHistory


class UserEmailHistoryView(SuspensionMixin, BaseAdminView):
    list_template = "admin/list_user_email_history.html"

    column_list = [
        "userId",
        "oldEmail",
        "newEmail",
        "creationDate",
        "eventType",
    ]

    column_labels = dict(
        userId="User ID",
        oldEmail="Ancienne adresse email",
        oldDomainEmail="Ancien nom de domaine d'adresse email",
        newEmail="Nouvelle adresse email",
        newDomainEmail="Nouveau nom de domaine d'adresse email",
        creationDate="Date de création",
        eventType="Type d'événement",
    )

    column_searchable_list = [
        "userId",
        "oldEmail",
        "newEmail",
    ]

    column_filters = [
        "userId",
        "oldEmail",
        "oldDomainEmail",
        "newEmail",
        "newDomainEmail",
        "eventType",
    ]

    @expose("/")
    def index(self):  # type: ignore [no-untyped-def]
        self._template_args["enum_update_request_value"] = users_models.EmailHistoryEventTypeEnum.UPDATE_REQUEST.value
        return super().index_view()

    @expose("/validate_user_email/<int:entry_id>", methods=["POST"])
    def validate_user_email(self, entry_id: int) -> Response:
        """
        Manually validate a user's email update request, only if it has
        not already been validated (by the user himself or another
        superadmin).

        One can pass query parameters to set another redirect:
          * next (mandatory) ;
          * extra parameters (non mandatory).
        """
        if not self.check_super_admins():
            flash("Vous n'avez pas les droits suffisants pour effectuer cette action", "error")
            return redirect(url_for(".index_view"))

        entry = UserEmailHistory.query.get(entry_id)

        if email_repository.has_been_validated(entry):
            flash(
                f"L'adresse email {entry.newEmail} de l'utilisateur {entry.userId} avait déjà été validée",
                category="warning",
            )
        else:
            try:
                users_api.change_user_email(current_email=entry.oldEmail, new_email=entry.newEmail, by_admin=True)
            except users_exceptions.UserDoesNotExist:
                flash(f"L'utilisateur avec l'adresse email {entry.oldEmail} n'a pas été trouvé", category="error")
            except users_exceptions.EmailExistsError:
                flash(f"L'adresse {entry.newEmail} est déjà utilisée", category="error")
            else:
                flash(f"L'adresse email {entry.newEmail} de l'utilisateur {entry.userId} a bien été validée")

        try:
            extra = {param: value for param, value in request.args.items() if param != "next"}
            next_url = url_for(request.args["next"], **extra)
        except (BadRequestKeyError, BuildError):
            next_url = url_for(".index_view")

        return redirect(next_url)
