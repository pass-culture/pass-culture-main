from pcapi.admin.base_configuration import BaseAdminView


class AllocinePivotView(BaseAdminView):
    can_create = True
    can_edit = True
    column_list = ["siret", "theaterId", "internalId"]
    column_searchable_list = ["siret", "theaterId", "internalId"]
    column_sortable_list: list[str] = []
    column_labels = {
        "theaterId": "Identifiant Allociné",
        "siret": "SIRET",
        "internalId": "Identifiant interne allociné",
    }
    column_filters: list[str] = []
    form_columns: list[str] = []
