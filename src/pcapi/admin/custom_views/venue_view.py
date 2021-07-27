from typing import Union

from flask import flash
from flask import request
from flask import url_for
from markupsafe import Markup
from markupsafe import escape
from sqlalchemy.orm import query
from wtforms import Form

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.core import search
from pcapi.core.bookings.exceptions import CannotDeleteVenueWithBookingsException
from pcapi.core.offerers.api import VENUE_ALGOLIA_INDEXED_FIELDS
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.api import update_offer_and_stock_id_at_providers
from pcapi.scripts.offerer.delete_cascade_venue_by_id import delete_cascade_venue_by_id


def _offers_link(view, context, model, name) -> Markup:
    url = url_for("offer_for_venue.index", id=model.id)
    return Markup('<a href="{}">Offres associées</a>').format(escape(url))


def _get_venue_provider_link(view, context, model, name) -> Union[Markup, None]:
    if not model.venueProviders:
        return None
    url = url_for("venue_providers.index_view", id=model.id)
    return Markup('<a href="{}">Voir</a>').format(url)


class VenueView(BaseAdminView):
    can_edit = True
    can_delete = True
    column_list = [
        "id",
        "name",
        "siret",
        "city",
        "postalCode",
        "address",
        "offres",
        "publicName",
        "latitude",
        "longitude",
        "isPermanent",
        "offer_import",
    ]
    column_labels = dict(
        name="Nom",
        siret="SIRET",
        city="Ville",
        postalCode="Code postal",
        address="Adresse",
        publicName="Nom d'usage",
        latitude="Latitude",
        longitude="Longitude",
        isPermanent="Lieu permanent",
        offer_import="Import d'offres",
    )
    column_searchable_list = ["name", "siret", "publicName"]
    column_filters = ["postalCode", "city", "publicName", "id"]
    form_columns = [
        "name",
        "siret",
        "city",
        "postalCode",
        "address",
        "publicName",
        "latitude",
        "longitude",
        "isPermanent",
    ]

    def get_query(self) -> query:
        return self._extend_query(super().get_query())

    def get_count_query(self) -> query:
        return self._extend_query(super().get_count_query())

    @staticmethod
    def _extend_query(query_to_override: query) -> query:
        venue_id = request.args.get("id")

        if venue_id:
            return query_to_override.filter(Venue.id == venue_id)

        return query_to_override

    @property
    def column_formatters(self):
        formatters = super().column_formatters
        formatters.update(offres=_offers_link)
        formatters.update(offer_import=_get_venue_provider_link)
        return formatters

    def delete_model(self, venue: Venue) -> bool:
        try:
            delete_cascade_venue_by_id(venue.id)
            return True
        except CannotDeleteVenueWithBookingsException:
            flash("Impossible d'effacer un lieu pour lequel il existe des reservations.", "error")
        return False

    def update_model(self, new_venue_form: Form, venue: Venue) -> bool:
        has_siret_changed = new_venue_form.siret.data != venue.siret
        old_siret = venue.siret

        has_indexed_attribute_changed = any(
            (
                hasattr(new_venue_form, field) and getattr(new_venue_form, field).data != getattr(venue, field)
                for field in VENUE_ALGOLIA_INDEXED_FIELDS
            )
        )

        super().update_model(new_venue_form, venue)

        if has_siret_changed and old_siret:
            update_offer_and_stock_id_at_providers(venue, old_siret)

        if has_indexed_attribute_changed:
            search.async_index_venue_ids([venue.id])

        return True
