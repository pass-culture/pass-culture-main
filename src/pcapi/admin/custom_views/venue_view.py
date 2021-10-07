from typing import Union

from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from flask_admin.actions import action
from flask_admin.base import expose
from flask_admin.helpers import get_redirect_target
from markupsafe import Markup
from markupsafe import escape
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import query
from wtforms import Form
from wtforms.fields.core import BooleanField
from wtforms.fields.simple import HiddenField

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.core import search
from pcapi.core.bookings.exceptions import CannotDeleteVenueWithBookingsException
from pcapi.core.offerers.api import VENUE_ALGOLIA_INDEXED_FIELDS
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.api import update_offer_and_stock_id_at_providers
from pcapi.models import db
from pcapi.scripts.offerer.delete_cascade_venue_by_id import delete_cascade_venue_by_id


def _offers_link(view, context, model, name) -> Markup:
    url = url_for("offer_for_venue.index", id=model.id)
    return Markup('<a href="{}">Offres associées</a>').format(escape(url))


def _get_venue_provider_link(view, context, model, name) -> Union[Markup, None]:
    if not model.venueProviders:
        return None
    url = url_for("venue_providers.index_view", id=model.id)
    return Markup('<a href="{url}">{text}</a>').format(url=url, text=model.venueProviders[0].provider.name)


class VenueChangeForm(Form):
    ids = HiddenField()
    is_permanent = BooleanField(
        label="Lieu permanent",
    )


class VenueView(BaseAdminView):
    list_template = "admin/bulk_edit_components/custom_list_with_modal.html"
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
        "provider_name",
        "managingOfferer.name",
    ]
    column_labels = {
        "name": "Nom",
        "siret": "SIRET",
        "city": "Ville",
        "postalCode": "Code postal",
        "address": "Adresse",
        "publicName": "Nom d'usage",
        "latitude": "Latitude",
        "longitude": "Longitude",
        "isPermanent": "Lieu permanent",
        "provider_name": "Provider",
        "managingOfferer.name": "Structure",
    }
    column_searchable_list = ["name", "siret", "publicName"]
    column_filters = ["postalCode", "city", "publicName", "id", "managingOfferer.name"]
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
        return (
            self._extend_query(super().get_query())
            .options(joinedload(Venue.managingOfferer))
            .options(joinedload(Venue.venueProviders))
        )

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
        formatters.update(provider_name=_get_venue_provider_link)
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
        search.async_index_venue_ids([venue.id])

        if has_siret_changed and old_siret:
            update_offer_and_stock_id_at_providers(venue, old_siret)

        if has_indexed_attribute_changed:
            search.async_index_offers_of_venue_ids([venue.id])

        return True

    @action("bulk_edit", "Édition multiple")
    def action_bulk_edit(self, ids):
        url = get_redirect_target() or self.get_url(".index_view")
        return redirect(url, code=307)

    @expose("/", methods=["POST"])
    def index(self):
        url = get_redirect_target() or self.get_url(".index_view")
        ids = request.form.getlist("rowid")
        joined_ids = ",".join(ids)
        change_form = VenueChangeForm()
        change_form.ids.data = joined_ids
        change_form.is_permanent.data = True

        self._template_args["url"] = url
        self._template_args["change_form"] = change_form
        self._template_args["change_modal"] = True
        self._template_args["update_view"] = "venue.update_view"
        self._template_args["modal_title"] = f"Éditer des Lieux - {len(ids)} lieu(x) sélectionné(s)"

        return self.index_view()

    @expose("/update/", methods=["POST"])
    def update_view(self):
        url = get_redirect_target() or self.get_url(".index_view")
        change_form = VenueChangeForm(request.form)
        if change_form.validate():
            venue_ids: list[str] = change_form.ids.data.split(",")
            is_permanent: bool = change_form.is_permanent.data

            Venue.query.filter(Venue.id.in_(venue_ids)).update(
                values={"isPermanent": is_permanent}, synchronize_session=False
            )
            db.session.commit()
            return redirect(url)

        # Form didn't validate
        flash("Le formulaire est invalide: %s" % (change_form.errors), "error")
        return redirect(url, code=307)
