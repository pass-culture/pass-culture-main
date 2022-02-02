import markupsafe

from pcapi import settings
from pcapi.admin.base_configuration import BaseAdminView
from pcapi.core.users.external import update_external_pro
from pcapi.models.user_offerer import UserOfferer
from pcapi.repository.user_offerer_queries import find_one_or_none_by_id
from pcapi.utils import human_ids


def format_offerer_name(view, context, model, name):
    offerer = model.offerer
    humanized_id = human_ids.humanize(offerer.id)
    url = f"{settings.PRO_URL}/accueil?structure={humanized_id}"
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
        "offerer.name": format_offerer_name,
    }

    def delete_model(self, user_offerer: UserOfferer) -> bool:
        # user_offerer.user is not available in this call, get email before deletion
        user_offerer_with_join = find_one_or_none_by_id(user_offerer.id)

        result = super().delete_model(user_offerer)

        if result and user_offerer_with_join:
            update_external_pro(user_offerer_with_join.user.email)

        return result
