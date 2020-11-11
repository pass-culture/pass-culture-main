from unittest.mock import patch

from pcapi.domain.beneficiary_bookings.thumb_url import ThumbUrl


class ProductThumbUrlTest:
    @patch("pcapi.domain.beneficiary_bookings.thumb_url.get_storage_base_url", return_value="http://example.com")
    def should_return_url_specified_for_product(self, mock_get_storage):
        # Given
        product_thumb_url = ThumbUrl.for_product(identifier=12)

        # When / Then
        assert product_thumb_url.url() == "http://example.com/thumbs/products/BQ"


class MediationThumbUrlTest:
    @patch("pcapi.domain.beneficiary_bookings.thumb_url.get_storage_base_url", return_value="http://example.com")
    def should_return_url_specified_for_mediation(self, mock_get_storage):
        # Given
        mediation_thumb_url = ThumbUrl.for_mediation(identifier=12)

        # When / Then
        assert mediation_thumb_url.url() == "http://example.com/thumbs/mediations/BQ"
