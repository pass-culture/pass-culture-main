import csv
from io import TextIOWrapper
import pathlib

from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from flask_admin import expose
from flask_admin.form import SecureForm
from flask_login import current_user
from werkzeug import Response
from wtforms import FileField

from pcapi.admin.base_configuration import BaseCustomAdminView
from pcapi.scripts.suspend_fraudulent_beneficiary_users import suspend_fraudulent_beneficiary_users_by_ids


ALLOWED_EXTENSIONS = {".csv"}


def allowed_file(filename):
    return pathlib.Path(filename).suffix in ALLOWED_EXTENSIONS


class SuspendFraudulentUsersByIdsForm(SecureForm):
    user_ids_csv = FileField("Importer un fichier CSV contenant une seule colonne des utilisateurs à suspendre")


class SuspendFraudulentUsersByUserIdsView(BaseCustomAdminView):
    @expose("/", methods=["GET", "POST"])
    def search(self) -> Response:
        form = SuspendFraudulentUsersByIdsForm()
        fraudulent_users = []
        nb_cancelled_bookings = 0
        if request.method == "POST":
            if not self.check_super_admins():
                flash("Vous n'avez pas les droits pour effectuer cette opération", "error")
                return redirect(url_for("admin.index"))
            form = SuspendFraudulentUsersByIdsForm(request.form)
            form.validate()
            user_ids_csv_file = request.files["user_ids_csv"]
            if user_ids_csv_file and allowed_file(user_ids_csv_file.filename):
                user_ids_csv_file = TextIOWrapper(user_ids_csv_file, encoding="ascii")
                csv_rows = csv.reader(user_ids_csv_file)
                user_ids = [int(row[0]) for row in csv_rows if row[0].isdigit()]
                result = suspend_fraudulent_beneficiary_users_by_ids(user_ids, current_user, dry_run=False)
                fraudulent_users = result["fraudulent_users"]
                nb_cancelled_bookings = result["nb_cancelled_bookings"]
                if not fraudulent_users:
                    flash("Aucun utilisateur n'a été suspendu", "error")
            else:
                flash(
                    "Veuillez renseigner un fichier csv contenant les identifiants des utilisateurs à suspendre",
                    "error",
                )

        return self.render(
            "admin/suspend_fraudulent_users_by_user_ids.html",
            form=form,
            fraudulent_users=fraudulent_users,
            nb_fraud_users=len(fraudulent_users),
            nb_cancelled_bookings=nb_cancelled_bookings,
        )
