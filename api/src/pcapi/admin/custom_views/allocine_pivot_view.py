from pcapi.admin.base_configuration import BaseAdminView


class AllocinePivotView(BaseAdminView):
    can_create = True
    can_edit = True
    column_list = ["venue.name", "venue.siret", "theaterId", "internalId"]
    column_searchable_list = ["venue.name", "venue.siret", "theaterId", "internalId"]
    column_sortable_list: list[str] = []
    column_labels = {
        "theaterId": "Identifiant Allociné",
        "venue.id": "Lieu",
        "venueId": "Identifiant lieu",
        "internalId": "Identifiant interne allociné",
        "venue.name": "Lieu",
        "venue.siret": "Siret du lieu",
    }
    column_filters: list[str] = []
    form_columns = ["venueId", "theaterId", "internalId"]
