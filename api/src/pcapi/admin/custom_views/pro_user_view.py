from flask_admin.form import rules
from flask_sqlalchemy import BaseQuery
from sqlalchemy.sql.expression import distinct
from sqlalchemy.sql.functions import func
from wtforms import Form
from wtforms.fields import Field
from wtforms.fields import StringField
from wtforms.validators import DataRequired
from wtforms.validators import ValidationError

from pcapi.admin.base_configuration import BaseAdminView
import pcapi.admin.rules as pcapi_rules
from pcapi.admin.validators import PhoneNumberValidator
from pcapi.core.external.attributes.api import update_external_pro
import pcapi.core.offerers.models as offerers_models
from pcapi.core.users.models import User
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.utils.email import sanitize_email

from .mixins.suspension_mixin import SuspensionMixin


def unique_siren(form: Form, field: Field) -> None:
    if offerers_models.Offerer.query.filter_by(siren=field.data).one_or_none():
        raise ValidationError("Une structure avec le même Siren existe déjà.")


def filter_email(value: str | None) -> str | None:
    if not value:
        return value
    return sanitize_email(value)


def create_offerer(form: Form) -> offerers_models.Offerer:
    offerer = offerers_models.Offerer()
    offerer.siren = form.offererSiren.data
    offerer.name = form.offererName.data
    offerer.postalCode = form.offererPostalCode.data
    offerer.city = form.offererCity.data
    offerer.validationStatus = ValidationStatus.VALIDATED

    return offerer


def create_user_offerer(user: User, offerer: offerers_models.Offerer) -> offerers_models.UserOfferer:
    user_offerer = offerers_models.UserOfferer()
    user_offerer.user = user
    user_offerer.offerer = offerer
    user_offerer.validationStatus = ValidationStatus.VALIDATED

    return user_offerer


class ProUserView(SuspensionMixin, BaseAdminView):
    can_edit = True
    can_create = False
    can_view_details = True

    column_list = [
        "id",
        "isActive",
        "email",
        "firstName",
        "lastName",
        "dateOfBirth",
        "departementCode",
        "phoneNumber",
        "postalCode",
        "isEmailValidated",
        "validationToken",
        "actions",
    ]
    column_labels = dict(
        comment="Commentaire",
        email="Email",
        isActive="Est activé",
        firstName="Prénom",
        lastName="Nom",
        dateOfBirth="Date de naissance",
        departementCode="Département",
        phoneNumber="Numéro de téléphone",
        postalCode="Code postal",
        isEmailValidated="Email validé ?",
        validationToken="Jeton de validation d'adresse email",
        has_beneficiary_role="Bénéficiaire 18 ans ?",
        has_underage_beneficiary_role="Bénéficiaire 15-17 ?",
        suspension_history="Historique de suspension",
    )
    column_searchable_list = ["id", "email", "firstName", "lastName"]
    column_filters = ["postalCode", "has_beneficiary_role", "has_underage_beneficiary_role", "isEmailValidated"]
    column_details_list = ["suspension_history", "comment"]

    form_create_rules = (
        rules.Header("Utilisateur créé :"),
        "email",
        "firstName",
        "lastName",
        "phoneNumber",
        "dateOfBirth",
        "departementCode",
        "postalCode",
        rules.Header("Structure créée :"),
        "offererSiren",
        "offererName",
        "offererPostalCode",
        "offererCity",
        pcapi_rules.HiddenField("comment"),
        pcapi_rules.HiddenField("csrf_token"),
    )

    @property
    def form_columns(self):  # type: ignore [no-untyped-def]
        fields = (
            "email",
            "firstName",
            "lastName",
            "dateOfBirth",
            "departementCode",
            "postalCode",
            "phoneNumber",
        )
        if self.check_super_admins():
            fields += ("comment",)
        return fields

    def get_edit_form(self) -> Form:
        form = super().get_form()
        form.email = StringField("Email", [DataRequired()], filters=[filter_email])
        form.phoneNumber = StringField("Numéro de téléphone", [PhoneNumberValidator()])
        return form

    def after_model_change(self, form: Form, model: User, is_created: bool) -> None:
        super().after_model_change(form, model, is_created)

        update_external_pro(model.email)

    def get_query(self) -> BaseQuery:
        return User.query.join(offerers_models.UserOfferer).distinct(User.id).from_self()

    def get_count_query(self) -> BaseQuery:
        return self.session.query(func.count(distinct(User.id))).select_from(User).join(offerers_models.UserOfferer)
