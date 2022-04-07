from flask_admin.helpers import get_form_data
from flask_login import current_user
from wtforms import Form
from wtforms import SelectField
from wtforms import StringField
from wtforms import TextAreaField

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.domain.user_activation import IMPORT_STATUS_MODIFICATION_RULE
from pcapi.domain.user_activation import is_import_status_change_allowed
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.repository import repository


class BeneficiaryImportView(BaseAdminView):
    can_edit = True
    column_list = [
        "beneficiary.firstName",
        "beneficiary.lastName",
        "beneficiary.email",
        "beneficiary.postalCode",
        "source",
        "sourceId",
        "applicationId",
        "currentStatus",
        "updatedAt",
        "detail",
        "authorEmail",
    ]
    column_labels = {
        "applicationId": "Id de dossier",
        "authorEmail": "Statut modifié par",
        "beneficiary.lastName": "Nom",
        "beneficiary.firstName": "Prénom",
        "beneficiary.postalCode": "Code postal",
        "beneficiary.email": "Adresse e-mail",
        "currentStatus": "Statut",
        "detail": "Détail",
        "source_id": "Id de la procédure",
        "source": "Source du dossier",
        "updatedAt": "Date",
    }
    column_searchable_list = ["beneficiary.email", "applicationId"]
    column_filters = ["currentStatus"]
    column_sortable_list = [
        "beneficiary.email",
        "beneficiary.firstName",
        "beneficiary.lastName",
        "beneficiary.postalCode",
        "applicationId",
        "source",
        "sourceId",
        "currentStatus",
        "updatedAt",
        "detail",
        "authorEmail",
    ]

    def edit_form(self, obj=None) -> Form:  # type: ignore [no-untyped-def]
        class _NewStatusForm(Form):
            beneficiary = StringField(
                "Bénéficiaire",
                default=obj.beneficiary.email if obj.beneficiary else "N/A",
                render_kw={"readonly": True},
            )
            applicationId = StringField("Dossier DMS", default=obj.applicationId, render_kw={"readonly": True})
            statuses = TextAreaField(
                "Statuts précédents", default=obj.history, render_kw={"readonly": True, "rows": len(obj.statuses)}
            )
            detail = StringField("Raison du changement de statut")
            status = SelectField(
                "Nouveau statut",
                choices=[(status.name, status.value) for status in ImportStatus],
                default=obj.currentStatus.value,
            )

        return _NewStatusForm(get_form_data())

    def update_model(self, new_status_form: Form, beneficiary_import: BeneficiaryImport) -> None:
        new_status = ImportStatus(new_status_form.status.data)

        if is_import_status_change_allowed(beneficiary_import.currentStatus, new_status):  # type: ignore [arg-type]
            beneficiary_import.setStatus(new_status, detail=new_status_form.detail.data, author=current_user)
            repository.save(beneficiary_import)
        else:
            new_status_form.status.errors.append(IMPORT_STATUS_MODIFICATION_RULE)
