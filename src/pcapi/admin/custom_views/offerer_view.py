from flask import flash

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.core.bookings.exceptions import CannotDeleteOffererWithBookingsException
from pcapi.core.offerers.models import Offerer
from pcapi.scripts.offerer.delete_cascade_offerer_by_id import delete_cascade_offerer_by_id


class OffererView(BaseAdminView):
    can_edit = True
    can_delete = True
    column_list = ["id", "name", "siren", "city", "postalCode", "address"]
    column_labels = dict(name="Nom", siren="SIREN", city="Ville", postalCode="Code postal", address="Adresse")
    column_searchable_list = ["name", "siren"]
    column_filters = ["postalCode", "city", "id", "name"]
    form_columns = ["name", "siren", "city", "postalCode", "address"]

    def delete_model(self, offerer: Offerer) -> bool:
        try:
            delete_cascade_offerer_by_id(offerer.id)
            return True
        except CannotDeleteOffererWithBookingsException:
            flash("Impossible d'effacer une structure juridique pour lequel il existe des reservations.", "error")
        return False
