from unittest.mock import patch

from domain.beneficiary_bookings.thumb_url import ProductThumbUrl, MediationThumbUrl


class ProductThumbUrlTest:
    @patch('domain.beneficiary_bookings.thumb_url.get_storage_base_url', return_value='http://example.com')
    def should_return_url_specified_for_product(self, mock_get_storage):
        # Given
        thumb_url = ProductThumbUrl(
            identifier=12,
        )

        # When / Then
        assert thumb_url.url() == 'http://example.com/thumbs/products/BQ'


class MediationThumbUrlTest:
    @patch('domain.beneficiary_bookings.thumb_url.get_storage_base_url', return_value='http://example.com')
    def should_return_url_specified_for_mediation(self, mock_get_storage):
        # Given
        thumb_url = MediationThumbUrl(
            identifier=12,
        )

        # When / Then
        assert thumb_url.url() == 'http://example.com/thumbs/mediations/BQ'
