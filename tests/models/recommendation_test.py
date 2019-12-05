from unittest.mock import patch

from models import PcObject
from tests.conftest import clean_database
from tests.test_utils import create_recommendation, create_offer_with_thing_product, create_product_with_thing_type, \
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
    mediation = create_mediation(offer, idx=1)

    # when
    recommendation = create_recommendation(offer, user, mediation=mediation)
    recommendation.mediationId = 1

    # then
    assert recommendation.thumbUrl == "http://localhost/storage/thumbs/mediations/AE"


@patch('models.has_thumb_mixin.get_storage_base_url', return_value='http://localhost/storage')
def test_model_thumbUrl_should_have_thumbUrl_using_productId_when_no_mediation(get_storage_base_url):
    # given
    product = create_product_with_thing_type(thumb_count=0)
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
    user = create_user(email='user@test.com')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue)
    mediation = create_mediation(offer, idx=1)

    # when
    recommendation = create_recommendation(offer, user, mediation=mediation)
    recommendation.mediationId = 1

    # then
    assert recommendation.thumbUrl == "https://passculture.app/storage/v2/thumbs/mediations/AE"


@clean_database
def test_model_should_return_false_if_no_favorite_exists_for_offer_mediation_and_user(app):
    # given
    user = create_user(email='user@test.com')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue)
    mediation = create_mediation(offer)

    # when
    recommendation = create_recommendation(offer, user, mediation=mediation)
    PcObject.save(recommendation)

    # then
    assert recommendation.isFavorite is False


@clean_database
def test_model_should_return_true_if_favorite_exists_for_offer_mediation_and_user(app):
    # given
    user = create_user(email='user@test.com')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue)
    mediation = create_mediation(offer)
    favorite = create_favorite(mediation, offer, user)
    PcObject.save(favorite)

    # when
    recommendation = create_recommendation(offer, user, mediation=mediation)
    PcObject.save(recommendation)

    # then
    assert recommendation.isFavorite is True


@clean_database
def test_model_should_return_true_if_favorite_exists_for_offer_without_mediation_and_user(app):
    # given
    user = create_user(email='user@test.com')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue)
    mediation = None
    favorite = create_favorite(mediation, offer, user)
    PcObject.save(favorite)

    # when
    recommendation = create_recommendation(offer, user, mediation=mediation)
    PcObject.save(recommendation)

    # then
    assert recommendation.isFavorite is True
