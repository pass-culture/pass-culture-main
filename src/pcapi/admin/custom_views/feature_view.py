import logging

from pcapi.admin.base_configuration import BaseAdminView


logger = logging.getLogger(__name__)


class FeatureView(BaseAdminView):
    can_edit = True
    column_default_sort = ("name", False)
    column_filters = ["isActive"]
    column_list = ["name", "description", "isActive"]
    column_labels = {"name": "Nom", "description": "Description", "isActive": "Activé"}

    column_searchable_list = ["name"]
    form_columns = ["isActive"]

    page_size = 100

    def on_model_change(self, form, model, is_created):
        logger.info("Activated or deactivated feature flag", extra={"feature": model.name, "active": model.isActive})
        return super().on_model_change(form=form, model=model, is_created=is_created)
