from flask import flash
from wtforms import Form

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.core.bookings.exceptions import CannotDeleteOffererWithBookingsException
from pcapi.core.offerers.models import Offerer
from pcapi.core.users.external import update_external_pro
from pcapi.repository import user_offerer_queries
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
        # Get users to update before association info is deleted
        users_offerer = user_offerer_queries.find_all_by_offerer_id(offerer.id)

        try:
            delete_cascade_offerer_by_id(offerer.id)
        except CannotDeleteOffererWithBookingsException:
            flash("Impossible d'effacer une structure juridique pour lequel il existe des reservations.", "error")
            return False

        for user_offerer in users_offerer:
            update_external_pro(user_offerer.user.email)

        return True

    def update_model(self, form: Form, offerer: Offerer) -> bool:
        result = super().update_model(form, offerer)

        if result:
            for user_offerer in user_offerer_queries.find_all_by_offerer_id(offerer.id):
                update_external_pro(user_offerer.user.email)

        return result
