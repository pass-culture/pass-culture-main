from typing import List

from pcapi.admin.base_configuration import BaseAdminView


class CriteriaView(BaseAdminView):
    can_create = True
    can_edit = True
    can_delete = True
    column_list = ["id", "name", "description", "scoreDelta", "startDateTime", "endDateTime"]
    column_labels = dict(
        name="Nom",
        description="Description",
        scoreDelta="Score",
        startDateTime="Date de début",
        endDateTime="Date de fin",
    )
    column_searchable_list = ["name", "description", "startDateTime", "endDateTime"]
    column_filters: List[str] = []
    form_columns = ["name", "description", "scoreDelta", "startDateTime", "endDateTime"]
