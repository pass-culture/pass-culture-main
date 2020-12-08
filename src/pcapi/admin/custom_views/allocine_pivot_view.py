from pcapi.admin.base_configuration import BaseAdminView


class AllocinePivotView(BaseAdminView):
    can_create = True
    can_edit = True
    column_list = ["siret", "theaterId"]
    column_searchable_list = ["siret", "theaterId"]
    column_sortable_list = []
    column_labels = {"theaterId": "Identifiant Allociné", "siret": "SIRET"}
    column_filters = []
    form_columns = []
