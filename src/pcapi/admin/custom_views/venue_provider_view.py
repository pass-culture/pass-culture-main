from flask import request
from sqlalchemy.orm import query

from pcapi.admin.base_configuration import BaseAdminView
from pcapi.models import VenueProvider


class VenueProviderView(BaseAdminView):
    can_edit = True
    can_create = False

    column_list = ["provider.name", "venueIdAtOfferProvider", "isActive", "provider.isActive"]
    column_labels = {
        "provider.name": "Source de données",
        "venueIdAtOfferProvider": "Identifiant pivot (SIRET, ID Allociné …)",
        "isActive": "Import des offres et stocks activé",
        "provider.isActive": "Source de données disponible",
    }
    form_columns = ["isActive", "venueIdAtOfferProvider"]

    def is_accessible(self) -> bool:
        venue_id = request.args.get("id")

        if not venue_id:
            return False

        return super().is_accessible()

    def is_visible(self) -> bool:
        return False

    def get_query(self) -> query:
        return self._extend_query(super().get_query())

    def get_count_query(self) -> query:
        return self._extend_query(super().get_count_query())

    @staticmethod
    def _extend_query(query_to_override: query) -> query:
        venue_id = request.args.get("id")
        return query_to_override.filter(VenueProvider.venueId == venue_id)
