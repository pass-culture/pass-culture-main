from flask import abort
from flask import request
from flask_admin.base import expose
from sqlalchemy.orm import query
from wtforms import Form

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.connectors import redis
from pcapi.core.offerers.models import Venue
from pcapi.flask_app import app
from pcapi.models import Offer


class OfferView(BaseAdminView):
    can_create = False
    can_edit = True
    can_delete = False
    column_list = ["id", "name", "type", "criteria"]
    column_sortable_list = ["name", "type", "criteria"]
    column_labels = {
        "name": "Nom",
        "type": "Type",
        "criteria": "Tag",
        "criteria.name": "Tag",
    }
    # Do not add searchable column on offer view for performance reasons
    # use the filters feature instead
    column_filters = ["type", "criteria.name", "name"]
    form_columns = ["criteria"]
    simple_list_pager = True

    def on_model_change(self, form: Form, offer: Offer, is_created: bool = False) -> None:
        redis.add_offer_id(client=app.redis_client, offer_id=offer.id)


class OfferForVenueSubview(OfferView):
    column_searchable_list = ["name", "criteria.name"]
    list_template = "admin/venue_offers_list.html"

    @expose("/", methods=(["GET"]))
    def index(self):
        self._template_args["venue_name"] = self._get_venue_name()
        return super().index_view()

    def is_visible(self) -> bool:
        return False

    def get_query(self) -> query:
        return self._extend_query(super().get_query())

    def get_count_query(self) -> query:
        return self._extend_query(super().get_count_query())

    def _extend_query(self, query_to_override: query) -> query:
        venue_id = request.args.get("id")

        if venue_id is None:
            abort(400, "Venue id required")

        return query_to_override.filter(Offer.venueId == venue_id)

    def _get_venue_name(self) -> str:
        venue_id = request.args.get("id")

        if venue_id is None:
            abort(400, "Venue id required")

        venue = Venue.query.filter(Venue.id == venue_id).one()
        if not venue:
            abort(404, "Ce lieu n'existe pas ou plus")

        return venue.name
