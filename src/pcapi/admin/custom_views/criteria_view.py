from typing import List

from pcapi.admin.base_configuration import BaseAdminView


class CriteriaView(BaseAdminView):
    can_create = True
    can_edit = True
    can_delete = True
    column_list = ["id", "name", "description", "scoreDelta"]
    column_labels = dict(name="Nom", description="Description", scoreDelta="Score")
    column_searchable_list = ["name", "description"]
    column_filters: List[str] = []
    form_columns = ["name", "description", "scoreDelta"]
