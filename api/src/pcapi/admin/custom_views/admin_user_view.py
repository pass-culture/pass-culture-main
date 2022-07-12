import datetime

from flask.helpers import flash
from flask_sqlalchemy import BaseQuery
from sqlalchemy.sql.expression import distinct
from sqlalchemy.sql.functions import func
from wtforms import Form
from wtforms.validators import DataRequired
from wtforms.validators import Length

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.admin.custom_views.mixins.suspension_mixin import SuspensionMixin
from pcapi.core.mails.transactional.pro.email_validation import send_email_validation_to_admin_email
from pcapi.core.users import api as users_api
from pcapi.core.users.constants import RESET_PASSWORD_TOKEN_LIFE_TIME_EXTENDED
from pcapi.core.users.utils import sanitize_email
from pcapi.utils.mailing import build_pc_webapp_reset_password_link


def filter_email(value: str | None) -> str | None:
    if not value:
        return value
    return sanitize_email(value)


class AdminUserView(SuspensionMixin, BaseAdminView):
    can_edit = False
    can_delete = False
    can_view_details = True

    @property
    def can_create(self) -> bool:  # type: ignore [override]
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
        comment="Commentaire",
        isActive="Est activé",
        email="Email",
        firstName="Prénom",
        lastName="Nom",
        has_beneficiary_role="Bénéficiaire 18 ans ?",
        has_underage_beneficiary_role="Bénéficiaire 15-17 ?",
        isEmailValidated="Email validé ?",
        publicName="Nom d'utilisateur",
        suspension_history="Historique de suspension",
    )
    column_searchable_list = ["id", "publicName", "email", "firstName", "lastName"]
    column_filters = ["email", "isEmailValidated"]
    column_details_list = ["suspension_history", "comment"]

    @property
    def form_columns(self):  # type: ignore [no-untyped-def]
        fields = ("email", "firstName", "lastName", "departementCode", "postalCode")
        if self.check_super_admins():
            fields += ("comment",)
        return fields

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

    def get_query(self) -> BaseQuery:
        from pcapi.core.users.models import User

        return User.query.filter(User.has_admin_role.is_(True)).from_self()  # type: ignore [attr-defined]

    def get_count_query(self) -> BaseQuery:
        from pcapi.core.users.models import User

        return self.session.query(func.count(distinct(User.id))).select_from(User).filter(User.has_admin_role.is_(True))  # type: ignore [attr-defined]

    def on_model_change(self, form: Form, model, is_created: bool) -> None:  # type: ignore [no-untyped-def]
        model.publicName = f"{model.firstName} {model.lastName}"
        model.add_admin_role()
        model.hasSeenProTutorials = True
        model.hasSeenProRgs = True
        model.needsToFillCulturalSurvey = False

        users_api.fulfill_account_password(model)

        super().on_model_change(form, model, is_created)

    def after_model_change(self, form: Form, model, is_created: bool) -> None:  # type: ignore [no-untyped-def]
        if is_created:
            token = users_api.create_reset_password_token(
                model,
                expiration=datetime.datetime.utcnow() + RESET_PASSWORD_TOKEN_LIFE_TIME_EXTENDED,
            )
            send_email_validation_to_admin_email(model, token)
            flash(f"Lien de réinitialisation du mot de passe : {build_pc_webapp_reset_password_link(token.value)}")

        super().after_model_change(form, model, is_created)
