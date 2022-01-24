from pcapi.admin.base_configuration import BaseAdminView


class ProviderView(BaseAdminView):
    can_edit = True
    can_create = True
    can_delete = False

    column_list = ["name", "apiUrl", "enabledForPro", "isActive"]

    column_labels = {
        "name": "Nom",
        "apiUrl": "URL Api",
        "enabledForPro": "Activé pour les pros",
        "isActive": "Actif ?",
    }

    column_default_sort = ("id", True)
    column_searchable_list = ["name", "apiUrl"]
    column_filters = ["enabledForPro", "isActive"]
    form_columns = ["name", "apiUrl", "enabledForPro", "isActive"]
