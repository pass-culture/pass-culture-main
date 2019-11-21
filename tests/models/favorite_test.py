from unittest.mock import patch

from tests.test_utils import create_offer_with_thing_product, create_product_with_thing_type, \
    create_venue, create_offerer, \
    create_mediation, create_user, create_offer_with_event_product, create_favorite, create_product_with_event_type


@patch('models.has_thumb_mixin.get_storage_base_url', return_value='http://localhost/storage')
def test_model_thumbUrl_should_use_mediation_first_as_thumbUrl(get_storage_base_url):
    # given
    user = create_user(email='user@test.com')
    offerer = create_offerer()
    venue = create_venue(offerer)
    product = create_product_with_event_type(thumb_count=1)
    offer = create_offer_with_event_product(product=product, venue=venue)
    mediation = create_mediation(offer)
    mediation.id = 1

    # when
    favorite = create_favorite(mediation=mediation, offer=offer, user=user)
    favorite.mediationId = 1

    # then
    assert favorite.thumbUrl == "http://localhost/storage/thumbs/mediations/AE"


@patch('models.has_thumb_mixin.get_storage_base_url', return_value='http://localhost/storage')
def test_model_thumbUrl_should_have_thumbUrl_using_productId_when_no_mediation(get_storage_base_url):
    # given
    user = create_user(email='user@booking.com')
    product = create_product_with_thing_type(thumb_count=0)
    product.id = 1
    offerer = create_offerer()
    venue = create_venue(offerer=offerer)
    offer = create_offer_with_thing_product(product=product, venue=venue)

    # when
    favorite = create_favorite(mediation=None, offer=offer, user=user)

    # then
    assert favorite.thumbUrl == "http://localhost/storage/thumbs/products/AE"
