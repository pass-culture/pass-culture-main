from unittest.mock import patch

from tests.domain_creators.generic_creators import create_domain_favorite
from pcapi.model_creators.generic_creators import create_offerer, create_venue, create_mediation
from pcapi.model_creators.specific_creators import create_offer_with_thing_product


class ThumbUrlTest:
    @patch.dict('os.environ', {'OBJECT_STORAGE_URL': 'http://localhost/storage'})
    def should_return_mediation_thumb_url_for_a_mediation_favorite(self):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(venue=venue)
        mediation = create_mediation(idx=123, offer=offer, thumb_count=1)
        favorite = create_domain_favorite(identifier=1, offer=offer, mediation=mediation)

        # When
        thumb_url = favorite.thumb_url

        # Then
        assert thumb_url == 'http://localhost/storage/thumbs/mediations/PM'

    @patch.dict('os.environ', {'OBJECT_STORAGE_URL': 'http://localhost/storage'})
    def should_return_offer_thumb_url_for_a_non_mediation_favorite(self):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer=offerer)
        offer = create_offer_with_thing_product(product_idx=321, thumb_count=1, venue=venue)
        favorite = create_domain_favorite(identifier=1, offer=offer)

        # When
        thumb_url = favorite.thumb_url

        # Then
        assert thumb_url == 'http://localhost/storage/thumbs/products/AFAQ'
