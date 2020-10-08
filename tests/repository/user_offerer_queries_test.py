import pytest
from sqlalchemy.orm.exc import MultipleResultsFound

from models import OfferSQLEntity, Offerer, UserOfferer, VenueSQLEntity
from repository import repository
from repository.user_offerer_queries import find_one_or_none_by_user_id, \
    find_user_offerer_email, \
    filter_query_where_user_is_user_offerer_and_is_validated
from tests.conftest import clean_database
from model_creators.generic_creators import create_user, create_offerer, create_venue, create_user_offerer
from model_creators.specific_creators import create_product_with_thing_type, create_product_with_event_type, \
    create_offer_with_thing_product, create_offer_with_event_product


@clean_database
def test_find_user_offerer_email(app):
    # Given
    user = create_user(email='offerer@email.com')
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer)
    repository.save(user_offerer)

    # When
    email = find_user_offerer_email(user_offerer.id)

    # Then
    assert email == 'offerer@email.com'


@clean_database
def test_find_one_or_none_by_user_id_should_return_one_user_offerer_with_same_user_id(app):
    # Given
    user = create_user(email='offerer@email.com')
    offerer = create_offerer(siren='123456789')
    user_offerer = create_user_offerer(user, offerer)
    repository.save(user_offerer)

    # When
    first_user_offerer = find_one_or_none_by_user_id(user.id)

    # Then
    assert type(first_user_offerer) == UserOfferer
    assert first_user_offerer.id == user_offerer.id


@clean_database
def test_find_one_or_none_by_user_id_raises_exception_when_several_are_found(app):
    # Given
    user = create_user(email='offerer@email.com')
    offerer1 = create_offerer(siren='123456789')
    offerer2 = create_offerer(siren='987654321')
    user_offerer1 = create_user_offerer(user, offerer1)
    user_offerer2 = create_user_offerer(user, offerer2)
    repository.save(user_offerer1, user_offerer2)

    # When
    with pytest.raises(MultipleResultsFound) as error:
        first_user_offerer = find_one_or_none_by_user_id(user.id)



@clean_database
def test_find_one_or_none_by_user_id_should_return_none_user_offerer_when_none_are_found(app):
    # Given
    user = create_user(email='offerer@email.com')
    offerer = create_offerer(siren='123456789')
    repository.save(user, offerer)

    # When
    first_user_offerer = find_one_or_none_by_user_id(user.id)

    # Then
    assert first_user_offerer is None



@clean_database
def test_filter_query_where_user_is_user_offerer_and_is_validated(app):
    # Given
    user = create_user(email='offerer@email.com')
    offerer1 = create_offerer(siren='123456789')
    offerer2 = create_offerer(siren='987654321')
    offerer3 = create_offerer(siren='123456780')
    user_offerer1 = create_user_offerer(user, offerer1)
    user_offerer2 = create_user_offerer(user, offerer2)

    event1 = create_product_with_event_type(event_name='Rencontre avec Jacques Martin')
    event2 = create_product_with_event_type(event_name='Concert de contrebasse')
    thing1 = create_product_with_thing_type(thing_name='Jacques la fripouille')
    thing2 = create_product_with_thing_type(thing_name='Belle du Seigneur')
    venue1 = create_venue(offerer1, name='Bataclan', city='Paris', siret=offerer1.siren + '12345')
    venue2 = create_venue(offerer2, name='Librairie la Rencontre', city='Saint Denis', siret=offerer2.siren + '54321')
    venue3 = create_venue(offerer3, name='Une librairie du méchant concurrent gripsou', city='Saint Denis',
                          siret=offerer3.siren + '54321')
    offer1 = create_offer_with_event_product(venue=venue1, product=event1)
    offer2 = create_offer_with_event_product(venue=venue1, product=event2)
    offer3 = create_offer_with_thing_product(venue=venue2, product=thing1)
    offer4 = create_offer_with_thing_product(venue=venue3, product=thing2)

    repository.save(
        user_offerer1, user_offerer2, offerer3,
        offer1, offer2, offer3, offer4
    )

    # When
    offers = filter_query_where_user_is_user_offerer_and_is_validated(
        OfferSQLEntity.query.join(VenueSQLEntity).join(Offerer),
        user
    ).all()

    # Then
    offer_ids = [offer.id for offer in offers]
    assert offer1.id in offer_ids
    assert offer2.id in offer_ids
    assert offer3.id in offer_ids
    assert offer4.id not in offer_ids
