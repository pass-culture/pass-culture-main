from pcapi.admin.base_configuration import BaseAdminView
from pcapi.admin.custom_views.mixins.suspension_mixin import SuspensionMixin


class UserEmailHistoryView(SuspensionMixin, BaseAdminView):
    column_list = [
        "userId",
        "oldEmail",
        "newEmail",
        "creationDate",
        "eventType",
        "deviceId",
    ]
    column_labels = dict(
        userId="User ID",
        oldEmail="Ancienne adresse email",
        oldDomainEmail="Ancien nom de domaine d'adresse email",
        newEmail="Nouvelle adresse email",
        newDomainEmail="Nouveau nom de domaine d'adresse email",
        creationDate="Date de création",
        eventType="Type d'événement",
        deviceId="Device ID",
    )
    column_searchable_list = [
        "userId",
        "oldEmail",
        "newEmail",
        "deviceId",
    ]
    column_filters = [
        "userId",
        "oldEmail",
        "oldDomainEmail",
        "newEmail",
        "newDomainEmail",
        "eventType",
        "deviceId",
    ]
