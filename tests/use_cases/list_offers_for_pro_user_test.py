from unittest.mock import MagicMock

from domain.identifier.identifier import Identifier

from infrastructure.repository.pro_offers.paginated_offers_recap_sql_repository import PaginatedOffersSQLRepository
from use_cases.list_offers_for_pro_user import ListOffersForProUser, OffersRequestParameters, DEFAULT_PAGE, DEFAULT_OFFERS_PER_PAGE


class OffersRequestParametersTest:
    def should_create_object_with_default_values(self):
        # When
        offers_request_parameters = OffersRequestParameters(
                user_id=12,
                user_is_admin=True,
                venue_id=None,
                page=None,
                offers_per_page=None
        )

        # Then
        assert offers_request_parameters.name_keywords is None
        assert offers_request_parameters.page == DEFAULT_PAGE
        assert offers_request_parameters.offers_per_page == DEFAULT_OFFERS_PER_PAGE

    def should_create_object_with_expected_values(self):
        # When
        offers_request_parameters = OffersRequestParameters(
                user_id=12,
                user_is_admin=False,
                venue_id=None,
                name_keywords='Toto bateau',
                page=12,
                offers_per_page=3,
        )

        # Then
        assert offers_request_parameters.name_keywords == 'Toto bateau'
        assert offers_request_parameters.page == 12
        assert offers_request_parameters.offers_per_page == 3
        assert offers_request_parameters.user_id == 12
        assert offers_request_parameters.user_is_admin is False
        assert offers_request_parameters.venue_id is None


class ListOffersForProUserTest:
    def setup_method(self):
        self.paginated_offers_repository = PaginatedOffersSQLRepository()
        self.paginated_offers_repository.get_paginated_offers_for_offerer_venue_and_keywords = MagicMock()
        self.list_offers_for_pro_user = ListOffersForProUser(
                paginated_offer_repository=self.paginated_offers_repository)

    def should_call_get_paginated_offers_repository(self):
        # Given
        offers_request_parameters = OffersRequestParameters(
                user_id=12,
                user_is_admin=False,
                venue_id=Identifier(36),
                offers_per_page=12,
                name_keywords='Offre Label',
                page=12,
        )

        # When
        self.list_offers_for_pro_user.execute(offers_request_parameters)

        # Then
        self.paginated_offers_repository.get_paginated_offers_for_offerer_venue_and_keywords.assert_called_once_with(
                name_keywords='Offre Label',
                page=12,
                offers_per_page=12,
                user_id=12,
                user_is_admin=False,
                venue_id=Identifier(36)
        )
