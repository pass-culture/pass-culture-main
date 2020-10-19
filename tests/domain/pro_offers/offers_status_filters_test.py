from pcapi.domain.pro_offers.offers_status_filters import OffersStatusFilters


class OffersStatusFiltersTest:
    def should_include_everything_by_default(self):
        # When
        status_filters = OffersStatusFilters()

        # Then
        assert status_filters.exclude_active is False
        assert status_filters.exclude_inactive is False

    def should_set_filters_at_init(self):
        # When
        status_filters = OffersStatusFilters(exclude_active=True, exclude_inactive=True)

        # Then
        assert status_filters.exclude_active is True
        assert status_filters.exclude_inactive is True
