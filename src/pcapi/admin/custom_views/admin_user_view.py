from flask_login import current_user
from sqlalchemy.orm import query
from sqlalchemy.sql.expression import distinct
from sqlalchemy.sql.functions import func
from wtforms import Form

from pcapi import settings
from pcapi.admin.base_configuration import BaseAdminView
from pcapi.domain.user_emails import send_admin_user_validation_email


class AdminUserView(BaseAdminView):
    can_edit = False

    @property
    def can_create(self) -> bool:
        if settings.IS_PROD:
            return current_user.email in settings.SUPER_ADMIN_EMAIL_ADDRESSES

        return True

    @property
    def can_delete(self) -> bool:
        if settings.IS_PROD:
            return current_user.email in settings.SUPER_ADMIN_EMAIL_ADDRESSES

        return True

    column_list = [
        "id",
        "firstName",
        "lastName",
        "email",
        "publicName",
        "isBeneficiary",
        "validationToken",
    ]
    column_labels = dict(
        email="Email",
        firstName="Prénom",
        lastName="Nom",
        publicName="Nom d'utilisateur",
    )
    column_searchable_list = ["id", "publicName", "email", "firstName", "lastName"]
    column_filters = ["email"]

    form_columns = [
        "email",
        "firstName",
        "lastName",
        "departementCode",
    ]

    def get_query(self) -> query:
        from pcapi.core.users.models import User

        return User.query.filter(User.isAdmin.is_(True)).from_self()

    def get_count_query(self) -> query:
        from pcapi.core.users.models import User

        return self.session.query(func.count(distinct(User.id))).select_from(User).filter(User.isAdmin.is_(True))

    def on_model_change(self, form: Form, model, is_created: bool) -> None:
        model.publicName = f"{model.firstName} {model.lastName}"
        model.isAdmin = True
        model.hasSeenProTutorials = True
        model.needsToFillCulturalSurvey = False
        model.generate_validation_token()

        if is_created:
            # This is to prevent a circulary import dependency
            from pcapi.core.users.api import fulfill_account_password

            fulfill_account_password(model)
            send_admin_user_validation_email(model)

        super().on_model_change(form, model, is_created)
