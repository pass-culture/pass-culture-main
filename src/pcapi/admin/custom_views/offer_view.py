from flask import abort
from flask import request
from flask import url_for
from flask_admin.base import expose
from markupsafe import Markup
from sqlalchemy import func
from sqlalchemy.orm import query
from wtforms import Form

from pcapi import settings
from pcapi.admin.base_configuration import BaseAdminView
from pcapi.connectors import redis
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.flask_app import app
from pcapi.models import Offer
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.settings import IS_PROD
from pcapi.utils.human_ids import humanize


class OfferView(BaseAdminView):
    can_create = False
    can_edit = True
    can_delete = False
    column_list = ["id", "name", "type", "criteria", "validation"]
    column_sortable_list = ["name", "type", "criteria", "validation"]
    column_labels = {
        "name": "Nom",
        "type": "Type",
        "criteria": "Tag",
        "criteria.name": "Tag",
    }
    # Do not add searchable column on offer view for performance reasons
    # use the filters feature instead
    column_filters = ["type", "criteria.name", "name", "validation"]
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


def _offer_pc_links(view, context, model, name) -> Markup:
    url = settings.PRO_URL + f"/offres/{humanize(model.id)}/edition"
    text = "Offre PC"

    return Markup(f'<a href="{url}" target="_blank" rel="noopener noreferrer">{text}</a>')


def _related_offers_links(view, context, model, name) -> Markup:
    url = url_for("offer_for_venue.index", id=model.venue.id)
    text = "Offres associées"

    return Markup(f'<a href="{url}">{text}</a>')


def _metabase_offers_links(view, context, model, name) -> Markup:
    url = f"https://data-analytics.internal-passculture.app/question/901?offerid={model.id}"
    text = "Offre"

    return Markup(f'<a href="{url}" target="_blank" rel="noopener noreferrer">{text}</a>')


class ValidationView(BaseAdminView):
    can_create = False
    can_edit = True
    can_delete = False
    column_list = ["id", "name", "validation", "venue.name", "score", "offer", "offers"]
    if IS_PROD:
        column_list.append("metabase")
    column_sortable_list = ["id", "name", "validation"]
    column_labels = {
        "name": "Nom",
        "type": "Type",
        "validation": "Validation",
        "venue.name": "Lieu",
        "offer": "Offre",
        "offers": "Offres",
        "score": "Score",
        "metabase": "Metabase",
    }
    column_filters = ["type"]
    form_columns = ["validation"]
    simple_list_pager = True

    @property
    def column_formatters(self):
        formatters = super().column_formatters
        formatters.update(offer=_offer_pc_links)
        formatters.update(offers=_related_offers_links)
        formatters.update(metabase=_metabase_offers_links)
        return formatters

    def on_model_change(self, form: Form, offer: Offer, is_created: bool = False) -> None:
        if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
            redis.add_offer_id(client=app.redis_client, offer_id=offer.id)

    def get_query(self):
        return self.session.query(self.model).filter(self.model.validation == OfferValidationStatus.AWAITING)

    def get_count_query(self):
        return self.session.query(func.count("*")).filter(self.model.validation == OfferValidationStatus.AWAITING)
