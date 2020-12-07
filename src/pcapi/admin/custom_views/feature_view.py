from pcapi.admin.base_configuration import BaseAdminView


class FeatureView(BaseAdminView):
    can_edit = True
    column_list = ["name", "description", "isActive"]
    column_labels = dict(name="Nom", description="Description", isActive="Activé")
    form_columns = ["isActive"]
