from pcapi.domain.beneficiary_bookings.thumb_url import ThumbUrl


class ProductThumbUrlTest:
    def should_return_url_specified_for_product(self):
        # Given
        product_thumb_url = ThumbUrl.for_product(identifier=12)

        # When / Then
        assert product_thumb_url.url() == "http://localhost/storage/thumbs/products/BQ"


class MediationThumbUrlTest:
    def should_return_url_specified_for_mediation(self):
        # Given
        mediation_thumb_url = ThumbUrl.for_mediation(identifier=12)

        # When / Then
        assert mediation_thumb_url.url() == "http://localhost/storage/thumbs/mediations/BQ"
