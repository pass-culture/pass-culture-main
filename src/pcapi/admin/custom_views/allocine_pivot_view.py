from typing import List

from pcapi.admin.base_configuration import BaseAdminView


class AllocinePivotView(BaseAdminView):
    can_create = True
    can_edit = True
    column_list = ["siret", "theaterId", "internalId"]
    column_searchable_list = ["siret", "theaterId", "internalId"]
    column_sortable_list: List[str] = []
    column_labels = {
        "theaterId": "Identifiant Allociné",
        "siret": "SIRET",
        "internalId": "Identifiant interne allociné",
    }
    column_filters: List[str] = []
    form_columns: List[str] = []
