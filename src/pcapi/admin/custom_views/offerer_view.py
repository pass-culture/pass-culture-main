from pcapi.admin.base_configuration import BaseAdminView


class OffererView(BaseAdminView):
    can_edit = True
    column_list = ["id", "name", "siren", "city", "postalCode", "address"]
    column_labels = dict(name="Nom", siren="SIREN", city="Ville", postalCode="Code postal", address="Adresse")
    column_searchable_list = ["name", "siren"]
    column_filters = ["postalCode", "city", "id", "name"]
    form_columns = ["name", "siren", "city", "postalCode", "address"]
