from pcapi import settings
from pcapi.admin import base_configuration


class MessageView(base_configuration.BaseAdminView):
    page_size = 100
    can_edit = not settings.IS_PROD
    can_create = not settings.IS_PROD
    can_view_details = True

    column_searchable_list = ["id", "user.email"]
    column_list = []
    column_labels = {
        "user": "Utilisateur",
        "dateCreated": "Date de création",
        "userMessage": "Message Utilisateur",
        "callToActionTitle": "Titre du CTA",
        "callToActionLink": "Lien du CTA",
        "callToActionIcon": "Icône du CTA",
        "popOverIcon": "Icône popover",
    }

    column_filters = []
    column_sortable_list = [
        "dateCreated",
    ]
