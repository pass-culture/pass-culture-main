from flask import flash
from flask import request
from flask_admin.base import expose
from flask_admin.form import SecureForm
from flask_login import current_user
from werkzeug import Response
from wtforms import StringField
from wtforms.validators import DataRequired

from pcapi.admin.base_configuration import BaseCustomAdminView
from pcapi.scripts.suspend_fraudulent_beneficiary_users import suspend_fraudulent_beneficiary_users_by_email_providers


class EmailDomainsForm(SecureForm):
    domains = StringField(
        "Noms de domaine",
        [
            DataRequired(),
        ],
    )


class SuspendFraudulentUsersByEmailProvidersView(BaseCustomAdminView):
    @expose("/", methods=["GET", "POST"])
    def search(self) -> Response:
        form = EmailDomainsForm()
        fraudulent_users = []
        nb_cancelled_bookings = 0
        if request.method == "POST":
            if not self.check_super_admins():
                flash("Vous n'avez pas les droits pour effectuer cette opération", "error")
            else:
                form = EmailDomainsForm(request.form)
                domains = form.domains.data
                if form.validate():
                    formatted_domains = domains.replace(" ", "").split(",")

                    result = suspend_fraudulent_beneficiary_users_by_email_providers(
                        formatted_domains, current_user, dry_run=False
                    )
                    fraudulent_users = result["fraudulent_users"]
                    nb_cancelled_bookings = result["nb_cancelled_bookings"]
                else:
                    flash("Veuillez renseigner au moins un nom de domaine", "error")

        return self.render(
            "admin/suspend_fraudulent_users_by_email_providers.html",
            form=form,
            fraudulent_users=fraudulent_users,
            nb_fraud_users=len(fraudulent_users),
            nb_cancelled_bookings=nb_cancelled_bookings,
        )
