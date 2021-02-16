from markupsafe import Markup

from pcapi.admin.base_configuration import BaseAdminView


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

    def _offers_links(self, view, context, model, name):
        url = self.get_url("offer_for_venue.index", id=model.id)
        text = "Offres associées"

        return Markup(f'<a href="{url}">{text}</a>')

    @property
    def column_formatters(self):
        formatters = super().column_formatters
        formatters.update(offres=self._offers_links)
        return formatters
