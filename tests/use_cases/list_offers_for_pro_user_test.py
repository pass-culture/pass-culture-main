from unittest.mock import MagicMock

from pcapi.domain.identifier.identifier import Identifier
from pcapi.domain.pro_offers.offers_status_filters import OffersStatusFilters
from pcapi.infrastructure.repository.pro_offers.paginated_offers_recap_sql_repository import PaginatedOffersSQLRepository
from pcapi.models import ThingType
from pcapi.use_cases.list_offers_for_pro_user import ListOffersForProUser, OffersRequestParameters


class OffersRequestParametersTest:
    def should_create_object_with_default_values(self):
        # When
        offers_request_parameters = OffersRequestParameters(
                user_id=12,
                user_is_admin=True,
                offerer_id=None,
                venue_id=None,
                type_id=None,
                page=None,
                offers_per_page=None
        )

        # Then
        assert offers_request_parameters.name_keywords is None
        assert offers_request_parameters.page == OffersRequestParameters.DEFAULT_PAGE
        assert offers_request_parameters.offers_per_page == OffersRequestParameters.DEFAULT_OFFERS_PER_PAGE
        assert isinstance(offers_request_parameters.status_filters, OffersStatusFilters)

    def should_create_object_with_expected_values(self):
        # Given
        status_filters = OffersStatusFilters(exclude_inactive=True)

        # When
        offers_request_parameters = OffersRequestParameters(
                user_id=12,
                user_is_admin=False,
                offerer_id=Identifier(12),
                venue_id=None,
                type_id=None,
                name_keywords='Toto bateau',
                page=12,
                offers_per_page=3,
                status_filters=status_filters
        )

        # Then
        assert offers_request_parameters.name_keywords == 'Toto bateau'
        assert offers_request_parameters.offerer_id == Identifier(12)
        assert offers_request_parameters.page == 12
        assert offers_request_parameters.offers_per_page == 3
        assert offers_request_parameters.user_id == 12
        assert offers_request_parameters.user_is_admin is False
        assert offers_request_parameters.venue_id is None
        assert offers_request_parameters.status_filters == status_filters


class ListOffersForProUserTest:
    def setup_method(self):
        self.paginated_offers_repository = PaginatedOffersSQLRepository()
        self.paginated_offers_repository.get_paginated_offers_for_offerer_venue_and_keywords = MagicMock()
        self.list_offers_for_pro_user = ListOffersForProUser(paginated_offer_repository=self.paginated_offers_repository)

    def should_call_get_paginated_offers_repository(self):
        # Given
        status_filters = OffersStatusFilters(exclude_inactive=True)
        offers_request_parameters = OffersRequestParameters(
                user_id=12,
                user_is_admin=False,
                offerer_id=Identifier(43),
                venue_id=Identifier(36),
                type_id=str(ThingType.AUDIOVISUEL),
                offers_per_page=12,
                name_keywords='Offre Label',
                page=12,
                status_filters=status_filters
        )

        # When
        self.list_offers_for_pro_user.execute(offers_request_parameters)

        # Then
        self.paginated_offers_repository.get_paginated_offers_for_offerer_venue_and_keywords.assert_called_once_with(
                name_keywords='Offre Label',
                offerer_id=Identifier(43),
                page=12,
                offers_per_page=12,
                user_id=12,
                user_is_admin=False,
                venue_id=Identifier(36),
                type_id=str(ThingType.AUDIOVISUEL),
                status_filters=status_filters
        )
