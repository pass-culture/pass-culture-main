from sqlalchemy.orm import query
from sqlalchemy.sql.expression import distinct
from sqlalchemy.sql.functions import func

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.models import UserOfferer
from pcapi.models.user_sql_entity import UserSQLEntity


class ProUserView(BaseAdminView):
    can_edit = True
    column_list = [
        "id",
        "isBeneficiary",
        "email",
        "firstName",
        "lastName",
        "publicName",
        "dateOfBirth",
        "departementCode",
        "phoneNumber",
        "postalCode",
        "resetPasswordToken",
        "validationToken",
    ]
    column_labels = dict(
        email="Email",
        isBeneficiary="Est bénéficiaire",
        firstName="Prénom",
        lastName="Nom",
        publicName="Nom d'utilisateur",
        dateOfBirth="Date de naissance",
        departementCode="Département",
        phoneNumber="Numéro de téléphone",
        postalCode="Code postal",
        resetPasswordToken="Jeton d'activation et réinitialisation de mot de passe",
        validationToken="Jeton de validation d'adresse email",
    )
    column_searchable_list = ["id", "publicName", "email", "firstName", "lastName"]
    column_filters = ["postalCode", "isBeneficiary"]
    form_columns = [
        "email",
        "firstName",
        "lastName",
        "publicName",
        "dateOfBirth",
        "departementCode",
        "postalCode",
    ]

    def get_query(self) -> query:
        return UserSQLEntity.query.join(UserOfferer).distinct(UserSQLEntity.id)

    def get_count_query(self) -> query:
        return self.session.query(func.count(distinct(UserSQLEntity.id))).select_from(UserSQLEntity).join(UserOfferer)
