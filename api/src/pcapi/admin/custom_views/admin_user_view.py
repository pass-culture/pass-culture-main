from typing import Optional

from flask.helpers import flash
from sqlalchemy.orm import query
from sqlalchemy.sql.expression import distinct
from sqlalchemy.sql.functions import func
from wtforms import Form
from wtforms.validators import DataRequired
from wtforms.validators import Length

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.admin.custom_views.mixins.suspension_mixin import SuspensionMixin
from pcapi.core.users import api as users_api
from pcapi.core.users.constants import RESET_PASSWORD_TOKEN_LIFE_TIME_EXTENDED
from pcapi.core.users.utils import sanitize_email
from pcapi.domain.user_emails import send_admin_user_validation_email
from pcapi.utils.mailing import build_pc_webapp_reset_password_link


def filter_email(value: Optional[str]) -> Optional[str]:
    if not value:
        return value
    return sanitize_email(value)


class AdminUserView(SuspensionMixin, BaseAdminView):
    can_edit = False
    can_delete = False

    @property
    def can_create(self) -> bool:
        return self.check_super_admins()

    column_list = [
        "id",
        "isActive",
        "firstName",
        "lastName",
        "email",
        "publicName",
        "has_beneficiary_role",
        "has_underage_beneficiary_role",
        "isEmailValidated",
        "validationToken",
        "actions",
    ]
    column_labels = dict(
        isActive="Est activé",
        email="Email",
        firstName="Prénom",
        lastName="Nom",
        has_beneficiary_role="Bénéficiaire 18 ans ?",
        has_underage_beneficiary_role="Bénéficiaire 15-17 ?",
        isEmailValidated="Email validé ?",
        publicName="Nom d'utilisateur",
    )
    column_searchable_list = ["id", "publicName", "email", "firstName", "lastName"]
    column_filters = ["email", "isEmailValidated"]

    form_columns = ["email", "firstName", "lastName", "departementCode", "postalCode"]

    form_args = dict(
        departementCode=dict(
            label="Département",
            validators=[DataRequired(), Length(min=2, max=3, message="Mauvais format de département")],
        ),
        postalCode=dict(
            label="Code postal",
            validators=[DataRequired(), Length(min=5, max=5, message="Mauvais format de code postal")],
        ),
        email=dict(validators=[DataRequired()], filters=[filter_email]),
    )

    def get_query(self) -> query:
        from pcapi.core.users.models import User

        return User.query.filter(User.isAdmin.is_(True)).from_self()

    def get_count_query(self) -> query:
        from pcapi.core.users.models import User

        return self.session.query(func.count(distinct(User.id))).select_from(User).filter(User.isAdmin.is_(True))

    def on_model_change(self, form: Form, model, is_created: bool) -> None:
        # This is to prevent a circulary import dependency
        from pcapi.core.users.api import fulfill_account_password

        model.publicName = f"{model.firstName} {model.lastName}"
        model.add_admin_role()
        model.hasSeenProTutorials = True
        model.needsToFillCulturalSurvey = False

        fulfill_account_password(model)

        super().on_model_change(form, model, is_created)

    def after_model_change(self, form: Form, model, is_created: bool) -> None:
        if is_created:
            token = users_api.create_reset_password_token(
                model, token_life_time=RESET_PASSWORD_TOKEN_LIFE_TIME_EXTENDED
            )
            send_admin_user_validation_email(model, token)
            flash(f"Lien de réinitialisation du mot de passe : {build_pc_webapp_reset_password_link(token.value)}")

        super().after_model_change(form, model, is_created)
