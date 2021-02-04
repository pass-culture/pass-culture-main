from typing import List

from sqlalchemy import distinct
from sqlalchemy.orm import query
from sqlalchemy.sql.functions import func
from wtforms import Form
from wtforms import StringField
from wtforms.fields.html5 import DateField
from wtforms.fields.html5 import TelField
from wtforms.form import BaseForm
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import Optional

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.core.users.models import User
from pcapi.domain.password import generate_reset_token
from pcapi.domain.password import random_password
from pcapi.models import UserOfferer


class PartnerUserView(BaseAdminView):
    can_edit = True
    can_create = True
    column_list = [
        "id",
        "firstName",
        "lastName",
        "publicName",
        "email",
        "dateOfBirth",
        "departementCode",
        "phoneNumber",
        "postalCode",
        "resetPasswordToken",
    ]
    column_labels = dict(
        email="Email",
        firstName="Prénom",
        lastName="Nom",
        publicName="Nom d'utilisateur",
        dateOfBirth="Date de naissance",
        departementCode="Département",
        phoneNumber="Numéro de téléphone",
        postalCode="Code postal",
        resetPasswordToken="Jeton de réinitialisation du mot de passe",
    )
    column_searchable_list = ["id", "publicName", "email", "firstName", "lastName"]
    column_filters: List[str] = []

    form_columns = ["email", "firstName", "lastName", "dateOfBirth", "departementCode", "postalCode", "phoneNumber"]

    def scaffold_form(self) -> BaseForm:
        form_class = super().scaffold_form()
        form_class.firstName = StringField("Prenom", [DataRequired()])
        form_class.lastName = StringField("Nom", [DataRequired()])
        form_class.dateOfBirth = DateField("Date de naissance", [Optional()])
        form_class.departementCode = StringField(
            "Département", [DataRequired(), Length(min=2, max=3, message="Mauvais format de département")]
        )
        form_class.phoneNumber = TelField(
            "Numéro de téléphone", [Optional(), Length(min=0, max=20, message="Numéro de téléphone invalide")]
        )

        return form_class

    def on_model_change(self, form: Form, model: User, is_created: bool) -> None:
        if is_created:
            model.password = random_password()
            generate_reset_token(model, 24 * 14)

        model.publicName = f"{model.firstName} {model.lastName}"
        model.isBeneficiary = False
        model.isAdmin = False

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
