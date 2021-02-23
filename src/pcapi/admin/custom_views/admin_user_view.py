from sqlalchemy.orm import query
from sqlalchemy.sql.expression import distinct
from sqlalchemy.sql.functions import func

from pcapi.admin.base_configuration import BaseAdminView


class AdminUserView(BaseAdminView):
    can_edit = False
    can_create = False
    column_list = [
        "id",
        "firstName",
        "lastName",
        "email",
        "publicName",
    ]
    column_labels = dict(
        email="Email",
        firstName="Prénom",
        lastName="Nom",
        publicName="Nom d'utilisateur",
    )
    column_searchable_list = ["id", "publicName", "email", "firstName", "lastName"]
    column_filters = ["email"]

    def get_query(self) -> query:
        from pcapi.core.users.models import User

        return User.query.filter(User.isAdmin.is_(True)).from_self()

    def get_count_query(self) -> query:
        from pcapi.core.users.models import User

        return self.session.query(func.count(distinct(User.id))).select_from(User).filter(User.isAdmin.is_(True))
