import pytest

from models import Offer, Offerer, PcObject, UserOfferer, Venue
from repository.user_offerer_queries import find_first_by_user_id, \
                                            find_user_offerer_email, \
                                            filter_query_where_user_is_user_offerer_and_is_validated
from tests.conftest import clean_database
from tests.test_utils import create_product_with_Event_type, \
                             create_offer_with_event_product, \
                             create_product_with_Thing_type, \
                             create_offer_with_thing_product, \
                             create_offerer, \
                             create_user, \
                             create_user_offerer, \
                             create_venue


@clean_database
def test_find_user_offerer_email(app):
    # Given
    user = create_user(email='offerer@email.com')
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer)
    PcObject.save(user_offerer)

    # When
    email = find_user_offerer_email(user_offerer.id)

    # Then
    assert email == 'offerer@email.com'


@clean_database
def test_find_first_by_user_id_should_return_one_user_offerers_with_user_id(app):
    # Given
    user = create_user(email='offerer@email.com')
    offerer1 = create_offerer(siren='123456789')
    offerer2 = create_offerer(siren='987654321')
    offerer3 = create_offerer(siren='123456780')
    user_offerer1 = create_user_offerer(user, offerer1)
    user_offerer2 = create_user_offerer(user, offerer2)
    PcObject.save(user_offerer1, user_offerer2, offerer3)

    # When
    first_user_offerer = find_first_by_user_id(user.id)

    # Then
    assert type(first_user_offerer) == UserOfferer
    assert first_user_offerer.id == user_offerer1.id

@clean_database
def test_filter_query_where_user_is_user_offerer_and_is_validated(app):
    # Given
    user = create_user(email='offerer@email.com')
    offerer1 = create_offerer(siren='123456789')
    offerer2 = create_offerer(siren='987654321')
    offerer3 = create_offerer(siren='123456780')
    user_offerer1 = create_user_offerer(user, offerer1)
    user_offerer2 = create_user_offerer(user, offerer2)

    event1 = create_product_with_Event_type(event_name='Rencontre avec Jacques Martin')
    event2 = create_product_with_Event_type(event_name='Concert de contrebasse')
    thing1 = create_product_with_Thing_type(thing_name='Jacques la fripouille')
    thing2 = create_product_with_Thing_type(thing_name='Belle du Seigneur')
    venue1 = create_venue(offerer1, name='Bataclan', city='Paris', siret=offerer1.siren + '12345')
    venue2 = create_venue(offerer2, name='Librairie la Rencontre', city='Saint Denis', siret=offerer2.siren + '54321')
    venue3 = create_venue(offerer3, name='Une librairie du méchant concurrent gripsou', city='Saint Denis', siret=offerer3.siren + '54321')
    offer1 = create_offer_with_event_product(venue1, event1)
    offer2 = create_offer_with_event_product(venue1, event2)
    offer3 = create_offer_with_thing_product(venue2, thing1)
    offer4 = create_offer_with_thing_product(venue3, thing2)

    PcObject.save(
        user_offerer1, user_offerer2, offerer3,
        offer1, offer2, offer3, offer4
    )

    # When
    offers = filter_query_where_user_is_user_offerer_and_is_validated(
        Offer.query.join(Venue).join(Offerer),
        user
    ).all()

    # Then
    offer_ids = [offer.id for offer in offers]
    assert offer1.id in offer_ids
    assert offer2.id in offer_ids
    assert offer3.id in offer_ids
    assert offer4.id not in offer_ids
