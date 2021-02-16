from flask import url_for
from markupsafe import Markup

from pcapi.admin.base_configuration import BaseAdminView


def _offers_links(view, context, model, name) -> Markup:
    url = url_for("offer_for_venue.index", id=model.id)
    text = "Offres associées"

    return Markup(f'<a href="{url}">{text}</a>')


class VenueView(BaseAdminView):
    can_edit = True
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
    )
    column_searchable_list = ["name", "siret", "publicName"]
    column_filters = ["postalCode", "city", "publicName"]
    form_columns = ["name", "siret", "city", "postalCode", "address", "publicName", "latitude", "longitude"]

    @property
    def column_formatters(self):
        formatters = super().column_formatters
        formatters.update(offres=_offers_links)
        return formatters
