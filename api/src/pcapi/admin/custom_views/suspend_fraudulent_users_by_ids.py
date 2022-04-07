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

from pcapi.admin.base_configuration import BaseCustomSuperAdminView
from pcapi.workers.suspend_fraudulent_beneficiary_users_by_ids_job import (
    suspend_fraudulent_beneficiary_users_by_ids_job,
)


ALLOWED_EXTENSIONS = {".csv"}


def allowed_file(filename):  # type: ignore [no-untyped-def]
    return pathlib.Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


class SuspendFraudulentUsersByIdsForm(SecureForm):
    user_ids_csv = FileField("Importer un fichier CSV contenant une seule colonne des utilisateurs à suspendre")


class SuspendFraudulentUsersByUserIdsView(BaseCustomSuperAdminView):
    @expose("/", methods=["GET", "POST"])
    def search(self) -> Response:
        form = SuspendFraudulentUsersByIdsForm()
        is_user_super_admin = self.check_super_admins()

        if request.method == "POST":
            if not is_user_super_admin:
                flash("Vous n'avez pas les droits pour effectuer cette opération", "error")
                return redirect(url_for("admin.index"))
            form = SuspendFraudulentUsersByIdsForm(request.form)
            form.validate()
            user_ids_csv_file = request.files["user_ids_csv"]
            if user_ids_csv_file and allowed_file(user_ids_csv_file.filename):
                user_ids_csv_file = TextIOWrapper(user_ids_csv_file, encoding="ascii")  # type: ignore [assignment, arg-type]
                csv_rows = csv.reader(user_ids_csv_file)  # type: ignore [arg-type]
                user_ids = [int(row[0]) for row in csv_rows if row and row[0].isdigit()]
                admin_user = current_user._get_current_object()
                suspend_fraudulent_beneficiary_users_by_ids_job.delay(user_ids, admin_user)
                flash(
                    "La suspension des utilisateurs via ids a bien été lancée, l'opération peut prendre plusieurs "
                    "minutes. Vous recevrez un mail récapitulatif à la fin de l'opération",
                    "info",
                )
            else:
                flash(
                    "Veuillez renseigner un fichier csv contenant les identifiants des utilisateurs à suspendre",
                    "error",
                )

        return self.render(
            "admin/suspend_fraudulent_users_by_user_ids.html",
            form=form,
            is_user_super_admin=is_user_super_admin,
        )
