import pytest

from tests.test_utils import create_recommendation, create_thing_offer, create_thing, create_venue, create_offerer, \
    create_mediation, create_user


# class TestRecommendationModel:
@pytest.mark.standalone
def test_model_should_have_thumbUrl_using_productId():
    # when
    product = create_thing(id='AKSA')
    offerer = create_offerer()
    venue = create_venue(offerer=offerer)
    offer = create_thing_offer(product=product, venue=venue)
    recommendation = create_recommendation(offer)

    # then
    assert recommendation.thumbUrl == "http://localhost/storage/thumbs/products/AKSA"


@pytest.mark.standalone
def test_model_should_use_mediation_first_as_thumbUrl():
    # given
    user = create_user(email='test@mail.com')
    product = create_thing(id='AKSA')
    offerer = create_offerer()
    venue = create_venue(offerer=offerer)
    offer = create_thing_offer(product=product, venue=venue)
    mediation = create_mediation(offer)

    # when
    recommendation = create_recommendation(offer, mediation, user)

    # then
    assert recommendation.thumbUrl == "http://localhost/storage/thumbs/mediations/AKSA"
