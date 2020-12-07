from wtforms import Form

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.connectors import redis
from pcapi.flask_app import app
from pcapi.models import Offer


class OfferView(BaseAdminView):
    can_create = False
    can_edit = True
    can_delete = False
    column_list = ["id", "name", "type", "criteria"]
    column_searchable_list = ["name", "criteria.name"]
    column_sortable_list = ["name", "type", "criteria"]
    column_labels = {"name": "Nom", "type": "Type", "criteria": "Tag", "criteria.name": "Tag"}
    column_filters = ["type", "criteria.name"]
    form_columns = ["criteria"]

    def on_model_change(self, form: Form, offer: Offer, is_created: bool = False) -> None:
        redis.add_offer_id(client=app.redis_client, offer_id=offer.id)
