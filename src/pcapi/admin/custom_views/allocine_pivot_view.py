from wtforms import Form
from wtforms import validators

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.models import AllocinePivot
from pcapi.repository.venue_queries import find_by_siret


class AllocinePivotView(BaseAdminView):
    can_create = True
    can_edit = True
    can_delete = False
    column_list = ["siret", "theaterId"]
    column_searchable_list = ["siret", "theaterId"]
    column_sortable_list = []
    column_labels = {"theaterId": "Identifiant Allociné", "siret": "SIRET"}
    column_filters = []
    form_columns = []

    def on_model_change(self, form: Form, model: AllocinePivot, is_created=False):
        venue = find_by_siret(model.siret)

        if venue is None:
            raise validators.ValidationError(f"Le SIRET ({model.siret}) n'est associé à aucun lieu")
