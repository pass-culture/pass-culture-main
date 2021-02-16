from pcapi.admin.custom_views.offer_view import OfferView
from pcapi.models import Offer


class BeneficiaryUserViewTest:
    def test_max_one_searchable_on_offer_view(self, db_session):
        # Given
        offer_view = OfferView(Offer, db_session)

        # Then
        assert offer_view.column_searchable_list is None or len(offer_view.column_searchable_list) == 0
