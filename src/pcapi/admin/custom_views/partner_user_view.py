from typing import Optional

from flask.helpers import flash
from sqlalchemy import distinct
from sqlalchemy.orm import query
from sqlalchemy.sql.functions import func
from wtforms import Form
from wtforms import StringField
from wtforms import validators
from wtforms.fields.html5 import DateField
from wtforms.fields.html5 import TelField
from wtforms.form import BaseForm
from wtforms.validators import DataRequired
from wtforms.validators import Length

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.admin.custom_views.mixins.resend_validation_email_mixin import ResendValidationEmailMixin
from pcapi.admin.custom_views.mixins.suspension_mixin import SuspensionMixin
from pcapi.core.users.api import create_reset_password_token
from pcapi.core.users.api import fulfill_account_password
from pcapi.core.users.constants import RESET_PASSWORD_TOKEN_LIFE_TIME_EXTENDED
from pcapi.core.users.models import User
from pcapi.core.users.utils import sanitize_email
from pcapi.models import UserOfferer
from pcapi.utils.mailing import build_pc_webapp_reset_password_link


def filter_email(value: Optional[str]) -> Optional[str]:
    if not value:
        return value
    return sanitize_email(value)


class PartnerUserView(ResendValidationEmailMixin, SuspensionMixin, BaseAdminView):
    can_edit = True
    can_create = True
    column_list = [
        "id",
        "isActive",
        "firstName",
        "lastName",
        "publicName",
        "email",
        "dateOfBirth",
        "departementCode",
        "phoneNumber",
        "postalCode",
        "isEmailValidated",
        "actions",
    ]
    column_labels = dict(
        isActive="Est activé",
        email="Email",
        firstName="Prénom",
        lastName="Nom",
        publicName="Nom d'utilisateur",
        dateOfBirth="Date de naissance",
        departementCode="Département",
        phoneNumber="Numéro de téléphone",
        postalCode="Code postal",
        isEmailValidated="Email validé ?",
    )
    column_searchable_list = ["id", "publicName", "email", "firstName", "lastName"]
    column_filters = ["isEmailValidated"]

    form_columns = ["email", "firstName", "lastName", "dateOfBirth", "departementCode", "postalCode", "phoneNumber"]

    def scaffold_form(self) -> BaseForm:
        form_class = super().scaffold_form()
        form_class.email = StringField("Email", [DataRequired()], filters=[filter_email])
        form_class.firstName = StringField("Prenom", [DataRequired()])
        form_class.lastName = StringField("Nom", [DataRequired()])
        form_class.dateOfBirth = DateField("Date de naissance", [validators.Optional()])
        form_class.departementCode = StringField(
            "Département", [DataRequired(), Length(min=2, max=3, message="Mauvais format de département")]
        )
        form_class.phoneNumber = TelField(
            "Numéro de téléphone",
            [validators.Optional(), Length(min=0, max=20, message="Numéro de téléphone invalide")],
        )

        return form_class

    def on_model_change(self, form: Form, model: User, is_created: bool) -> None:
        if is_created:
            fulfill_account_password(model)
            model.needsToFillCulturalSurvey = False
            model.hasSeenTutorials = True

        model.publicName = f"{model.firstName} {model.lastName}"
        model.remove_admin_role()
        model.remove_beneficiary_role()

    def after_model_change(self, form: Form, model: User, is_created: bool) -> None:
        if is_created:
            resetPasswordToken = create_reset_password_token(
                model, token_life_time=RESET_PASSWORD_TOKEN_LIFE_TIME_EXTENDED
            )
            flash(
                f"Lien de réinitialisation du mot de passe : {build_pc_webapp_reset_password_link(resetPasswordToken.value)}"
            )

    def get_query(self) -> query:
        return (
            User.query.outerjoin(UserOfferer)
            .filter(UserOfferer.userId.is_(None))
            .filter(User.isBeneficiary.is_(False))
            .filter(User.isAdmin.is_(False))
        )

    def get_count_query(self) -> query:
        return (
            self.session.query(func.count(distinct(User.id)))
            .select_from(self.model)
            .outerjoin(UserOfferer)
            .filter(UserOfferer.userId.is_(None))
            .filter(User.isBeneficiary.is_(False))
            .filter(User.isAdmin.is_(False))
        )
