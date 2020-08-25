from unittest.mock import patch

from tests.model_creators.generic_creators import create_mediation, create_offerer, create_recommendation, create_user, create_venue
from tests.model_creators.specific_creators import create_offer_with_event_product, create_offer_with_thing_product, create_product_with_event_type, create_product_with_thing_type


@patch('models.has_thumb_mixin.get_storage_base_url', return_value='http://localhost/storage')
def test_model_thumb_url_should_use_mediation_first_as_thumb_url(get_storage_base_url):
    # given
    user = create_user(email='user@example.com')
    offerer = create_offerer()
    venue = create_venue(offerer)
    product = create_product_with_event_type()
    offer = create_offer_with_event_product(product=product, venue=venue)
    mediation = create_mediation(offer, idx=1, thumb_count=1)

    # when
    recommendation = create_recommendation(offer, user, mediation=mediation)
    recommendation.mediationId = 1

    # then
    assert recommendation.thumbUrl == "http://localhost/storage/thumbs/mediations/AE"


@patch('models.has_thumb_mixin.get_storage_base_url', return_value='http://localhost/storage')
def test_model_thumb_url_should_have_thumb_url_using_product_id_when_no_mediation(get_storage_base_url):
    # given
    product = create_product_with_thing_type(thumb_count=1)
    product.id = 2
    offerer = create_offerer()
    venue = create_venue(offerer=offerer)
    offer = create_offer_with_thing_product(product=product, venue=venue)

    # when
    recommendation = create_recommendation(offer)

    # then
    assert recommendation.thumbUrl == "http://localhost/storage/thumbs/products/A9"


@patch('models.has_thumb_mixin.get_storage_base_url', return_value='https://passculture.app/storage/v2')
def test_model_should_use_environment_variable(get_storage_base_url):
    # given
    user = create_user(email='user@example.com')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue)
    mediation = create_mediation(offer, idx=1, thumb_count=1)

    # when
    recommendation = create_recommendation(offer, user, mediation=mediation)
    recommendation.mediationId = 1

    # then
    assert recommendation.thumbUrl == "https://passculture.app/storage/v2/thumbs/mediations/AE"
