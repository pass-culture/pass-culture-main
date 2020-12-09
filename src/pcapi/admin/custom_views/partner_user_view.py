from typing import List

from sqlalchemy import distinct
from sqlalchemy.orm import query
from sqlalchemy.sql.functions import func
from wtforms import Form
from wtforms import StringField
from wtforms.fields.html5 import DateField
from wtforms.fields.html5 import EmailField
from wtforms.fields.html5 import IntegerField
from wtforms.fields.html5 import TelField
from wtforms.validators import DataRequired
from wtforms.validators import Optional

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.domain.password import random_password
from pcapi.models import UserOfferer
from pcapi.models.user_sql_entity import UserSQLEntity


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
    )
    column_searchable_list = ["id", "publicName", "email", "firstName", "lastName"]
    column_filters: List[str] = []

    form_columns = ["email", "firstName", "lastName", "dateOfBirth", "departementCode", "postalCode", "phoneNumber"]

    def scaffold_form(self):
        form_class = super().scaffold_form()
        form_class.email = EmailField("Email", [DataRequired()])
        form_class.firstName = StringField("Prenom", [DataRequired()])
        form_class.lastName = StringField("Nom", [DataRequired()])
        form_class.dateOfBirth = DateField("Date de naissance", [Optional()])
        form_class.departementCode = IntegerField("Département", [DataRequired()])
        form_class.postalCode = StringField("Code postal", [Optional()])
        form_class.phoneNumber = TelField("Numéro de téléphone", [Optional()])

        return form_class

    def on_model_change(self, form: Form, model: UserSQLEntity, is_created: bool) -> None:
        if is_created:
            model.password = random_password()

        model.publicName = f"{model.firstName} {model.lastName}"
        model.isBeneficiary = False
        model.isAdmin = False

    def get_query(self) -> query:
        return (
            UserSQLEntity.query.outerjoin(UserOfferer)
            .filter(UserOfferer.userId.is_(None))
            .filter(UserSQLEntity.isBeneficiary.is_(False))
            .filter(UserSQLEntity.isAdmin.is_(False))
        )

    def get_count_query(self) -> query:
        return (
            self.session.query(func.count(distinct(UserSQLEntity.id)))
            .select_from(self.model)
            .outerjoin(UserOfferer)
            .filter(UserOfferer.userId.is_(None))
            .filter(UserSQLEntity.isBeneficiary.is_(False))
            .filter(UserSQLEntity.isAdmin.is_(False))
        )
