import pytest
from unittest.mock import patch

from tests.test_utils import create_recommendation, create_thing_offer, create_thing, create_venue, create_offerer, \
    create_mediation, create_user, create_event_offer


@pytest.mark.standalone
@patch('models.recommendation.get_storage_base_url', return_value='http://localhost/storage/thumbs')
def test_model_should_have_thumbUrl_using_productId(get_storage_base_url):
    # given
    product = create_thing()
    product.id = 2
    offerer = create_offerer()
    venue = create_venue(offerer=offerer)
    offer = create_thing_offer(product=product, venue=venue)

    # when
    recommendation = create_recommendation(offer)

    # then
    assert recommendation.thumbUrl == "http://localhost/storage/thumbs/products/A9"


@pytest.mark.standalone
@patch('models.recommendation.get_storage_base_url', return_value='http://localhost/storage/thumbs')
def test_model_should_have_thumbUrl_using_productId(get_storage_base_url):
    # given
    product = create_thing()
    product.id = 2
    offerer = create_offerer()
    venue = create_venue(offerer=offerer)
    offer = create_thing_offer(product=product, venue=venue)

    # when
    recommendation = create_recommendation(offer)

    # then
    assert recommendation.thumbUrl == "http://localhost/storage/thumbs/products/A9"


@pytest.mark.standalone
@patch('models.recommendation.get_storage_base_url', return_value='http://localhost/storage/thumbs')
def test_model_should_use_mediation_first_as_thumbUrl(get_storage_base_url):
    # given
    user = create_user(email='user@test.com')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    mediation = create_mediation(offer)
    mediation.id = 1

    # when
    recommendation = create_recommendation(offer, user, mediation=mediation)
    recommendation.mediationId = 1

    # then
    assert recommendation.thumbUrl == "http://localhost/storage/thumbs/mediations/AE"


@pytest.mark.standalone
@patch('models.recommendation.get_storage_base_url', return_value='https://passculture.app/storage/v2')
def test_model_should_use_environment_variable(get_storage_base_url):
    # given
    user = create_user(email='user@test.com')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    mediation = create_mediation(offer)
    mediation.id = 1

    # when
    recommendation = create_recommendation(offer, user, mediation=mediation)
    recommendation.mediationId = 1

    # then
    assert recommendation.thumbUrl == "https://passculture.app/storage/v2/mediations/AE"
