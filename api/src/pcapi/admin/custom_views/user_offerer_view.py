from jinja2.runtime import Context
import markupsafe
import sqlalchemy.orm as sqla_orm

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.core.offerers.models import UserOfferer
from pcapi.core.users.external import update_external_pro
from pcapi.utils.urls import build_pc_pro_offerer_link


def _format_offerer_name(view: BaseAdminView, context: Context, model: UserOfferer, name: str) -> markupsafe.Markup:
    offerer = model.offerer
    url = build_pc_pro_offerer_link(offerer)
    return markupsafe.Markup('<a href="{url}">{offerer.name}</a>').format(
        url=url,
        offerer=offerer,
    )


class UserOffererView(BaseAdminView):
    can_delete = True
    column_list = [
        "user.email",
        "user.firstName",
        "user.lastName",
        "user.id",
        "offerer.siren",
        "offerer.address",
        "offerer.name",
        "offerer.id",
        "isValidated",
    ]
    column_labels = {
        "user.email": "Email utilisateur",
        "user.firstName": "Prénom de l'utilisateur",
        "user.lastName": "Nom de l'utilisateur",
        "user.id": "Identifiant de l'utilisateur",
        "offerer.siren": "SIREN de la structure",
        "offerer.address": "Adresse de la structure",
        "offerer.name": "Nom de la structure",
        "offerer.id": "Identifiant de la structure",
        "isValidated": "Validé",
    }
    column_sortable_list: list[str] = []
    column_searchable_list = [
        "user.email",
        "user.firstName",
        "user.lastName",
        "user.id",
        "offerer.siren",
        "offerer.address",
        "offerer.name",
        "offerer.id",
    ]
    column_filters = [
        "user.email",
        "user.firstName",
        "user.lastName",
        "offerer.siren",
        "offerer.address",
        "offerer.name",
    ]
    column_formatters = {
        "offerer.name": _format_offerer_name,
    }

    def delete_model(self, user_offerer: UserOfferer) -> bool:
        # user_offerer.user is not available in this call, get email before deletion
        # joined user is no longer available after delete_model()
        user_offerer = (
            UserOfferer.query.filter_by(id=user_offerer.id).options(sqla_orm.joinedload(UserOfferer.user)).one_or_none()
        )
        email = user_offerer.user.email if user_offerer else None

        result = super().delete_model(user_offerer)

        if result and email:
            update_external_pro(email)

        return result
