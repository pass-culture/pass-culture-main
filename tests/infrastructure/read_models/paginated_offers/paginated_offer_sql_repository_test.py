from collections import namedtuple
from unittest.mock import patch, MagicMock

from domain.pro_offers.paginated_offers import PaginatedOffers
from infrastructure.repository.pro_offers.paginated_offer_sql_repository import PaginatedOffersSQLRepository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user


class PaginatedOfferSQLRepositoryTest:
    @clean_database
    @patch(
        'infrastructure.repository.pro_offers.paginated_offer_sql_repository.build_find_offers_with_filter_parameters')
    def test_should_call_build_find_offers_with_filter_parameters(self, mock_build_query, app):
        # Given
        user = create_user()
        fake_query = MagicMock()
        paginate_query_mock = namedtuple("PaginateQueryMock", ["items", "total"])
        paginate_query_mock.items = []
        paginate_query_mock.total = 12
        fake_query.paginate.return_value = paginate_query_mock
        mock_build_query.return_value = fake_query

        # When
        paginated_offers = PaginatedOffersSQLRepository().get_paginated_offers_for_offerer_venue_and_keywords(
            user_id=user.id,
            user_is_admin=user.isAdmin,
            offerer_id=None,
            pagination_limit=10,
            venue_id=14,
            keywords='Keywords',
            page=1
        )

        # Then
        mock_build_query.assert_called_once_with(
            user_id=user.id,
            user_is_admin=user.isAdmin,
            offerer_id=None,
            venue_id=14,
            keywords_string='Keywords',
        )
        assert isinstance(paginated_offers, PaginatedOffers)
        assert paginated_offers.total == 12
        assert len(paginated_offers.offers) == 0
