from unittest.mock import MagicMock

from infrastructure.repository.pro_offerers.paginated_offerers_sql_repository import PaginatedOfferersSQLRepository
from use_cases.list_offerers_for_pro_user import OfferersRequestParameters, ListOfferersForProUser


class OfferersRequestParametersTest:
    def should_create_object_with_expected_values(self):
        # When
        offerers_request_parameters = OfferersRequestParameters(
            user_id=12,
            user_is_admin=False,
            is_filtered_by_offerer_status=False,
            only_validated_offerers=False,
            pagination_limit='15',
            keywords='some keywords',
            page='2',
        )

        # Then
        assert offerers_request_parameters.user_id == 12
        assert offerers_request_parameters.user_is_admin is False
        assert offerers_request_parameters.is_filtered_by_offerer_status is False
        assert offerers_request_parameters.only_validated_offerers is False
        assert offerers_request_parameters.keywords == 'some keywords'
        assert offerers_request_parameters.page == 2
        assert offerers_request_parameters.pagination_limit == 15


class ListOfferersForProUserTest:
    def setup_method(self):
        self.paginated_offerers_repository = PaginatedOfferersSQLRepository()
        self.paginated_offerers_repository.with_status_and_keywords = MagicMock()
        self.list_offerers_for_pro_user = ListOfferersForProUser(
            paginated_offerers_repository=self.paginated_offerers_repository)

    def should_call_get_paginated_offerers_repository(self):
        # Given
        offerers_request_parameters = OfferersRequestParameters(
            user_id=12,
            user_is_admin=False,
            is_filtered_by_offerer_status=False,
            only_validated_offerers=False,
            pagination_limit='10',
            keywords='Offerer or venue name',
            page='2',
        )

        # When
        self.list_offerers_for_pro_user.execute(offerers_request_parameters)

        # Then
        self.paginated_offerers_repository.with_status_and_keywords.assert_called_once_with(
            user_id=12,
            user_is_admin=False,
            is_filtered_by_offerer_status=False,
            only_validated_offerers=False,
            pagination_limit=10,
            keywords='Offerer or venue name',
            page=2,
        )
