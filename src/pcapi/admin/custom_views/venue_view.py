from pcapi.admin.base_configuration import BaseAdminView


class VenueView(BaseAdminView):
    can_edit = True
    column_list = ["id", "name", "siret", "city", "postalCode", "address", "publicName", "latitude", "longitude"]
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
