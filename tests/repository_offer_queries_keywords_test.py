import pytest

from models import PcObject, Offer
from repository.offer_queries import filter_offers_with_keywords_string
from tests.conftest import clean_database
from utils.test_utils import create_event, create_thing, create_offerer, create_venue, create_event_offer, \
    create_thing_offer


@pytest.mark.standalone
@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_one_keyword_at_event_or_thing_level(app):
    # given
    ok_event1 = create_event(event_name='Rencontre avec Jacques Martin')
    ko_event2 = create_event(event_name='Concert de contrebasse')
    ok_thing = create_thing(thing_name='Rencontre avec Belle du Seigneur')
    offerer = create_offerer()
    venue = create_venue(offerer)
    ok_offer1 = create_event_offer(venue, ok_event1)
    ko_offer2 = create_event_offer(venue, ko_event2)
    ok_offer3 = create_thing_offer(venue, ok_thing)
    PcObject.check_and_save(ok_offer1, ko_offer2, ok_offer3)

    # when
    query = filter_offers_with_keywords_string(Offer.query, 'Rencontre')

    # then
    found_offers = query.all()
    assert len(found_offers) == 2
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id

@pytest.mark.standalone
@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_one_partial_keyword_at_event_or_thing_level(app):
    # given
    ok_event1 = create_event(event_name='Rencontre avec Jacques Martin')
    ko_event2 = create_event(event_name='Concert de contrebasse')
    ok_thing = create_thing(thing_name='Rencontre avec Belle du Seigneur')
    offerer = create_offerer()
    venue = create_venue(offerer)
    ok_offer1 = create_event_offer(venue, ok_event1)
    ko_offer2 = create_event_offer(venue, ko_event2)
    ok_offer3 = create_thing_offer(venue, ok_thing)
    PcObject.check_and_save(ok_offer1, ko_offer2, ok_offer3)

    # when
    query = filter_offers_with_keywords_string(Offer.query, 'Renc')

    # then
    found_offers = query.all()
    assert len(found_offers) == 2
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id

@pytest.mark.standalone
@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_several_keywords_at_event_or_thing_level(app):
    # given
    ok_event1 = create_event(event_name='Rencontre avec Jacques Martin')
    ko_event2 = create_event(event_name='Concert de contrebasse')
    ko_thing = create_thing(thing_name='Rencontre avec Belle du Seigneur')
    offerer = create_offerer()
    venue = create_venue(offerer)
    ok_offer1 = create_event_offer(venue, ok_event1)
    ko_offer2 = create_event_offer(venue, ko_event2)
    ko_offer3 = create_thing_offer(venue, ko_thing)
    PcObject.check_and_save(ok_offer1, ko_offer2, ko_offer3)

    # when
    query = filter_offers_with_keywords_string(Offer.query, 'Rencontre Jacques')

    # then
    found_offers = query.all()
    assert len(found_offers) == 1
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ko_offer3.id not in found_offers_id

@pytest.mark.standalone
@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_several_partial_keywords_at_event_or_thing_level(app):
    # given
    ok_event1 = create_event(event_name='Rencontre avec Jacques Martin')
    ko_event2 = create_event(event_name='Concert de contrebasse')
    ko_thing = create_thing(thing_name='Rencontre avec Belle du Seigneur')
    offerer = create_offerer()
    venue = create_venue(offerer)
    ok_offer1 = create_event_offer(venue, ok_event1)
    ko_offer2 = create_event_offer(venue, ko_event2)
    ko_offer3 = create_thing_offer(venue, ko_thing)
    PcObject.check_and_save(ok_offer1, ko_offer2, ko_offer3)

    # when
    query = filter_offers_with_keywords_string(Offer.query, 'Renc Jacqu')

    # then
    found_offers = query.all()
    assert len(found_offers) == 1
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ko_offer3.id not in found_offers_id


@pytest.mark.standalone
@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_one_keyword_at_venue_or_offerer_level(app):
    # given
    ko_event = create_event()
    ko_thing = create_thing()
    ok_offerer1 = create_offerer(name="La Rencontre")
    ko_offerer2 = create_offerer(siren='123456788')
    ko_offerer3 = create_offerer(siren='123456787')
    ko_offerer4 = create_offerer(siren='123456786')
    ok_venue1 = create_venue(ok_offerer1, siret=ok_offerer1.siren + '54321')
    ko_venue2 = create_venue(ko_offerer2, siret=ko_offerer2.siren + '12345')
    ok_venue3 = create_venue(ko_offerer3, name='Librairie la Rencontre', city='Saint Denis', siret=ko_offerer3.siren + '54321')
    ko_venue4 = create_venue(ko_offerer4, name='Bataclan', city='Paris', siret=ko_offerer4.siren + '12345')
    ok_offer1 = create_event_offer(ok_venue1, ko_event)
    ko_offer2 = create_event_offer(ko_venue2, ko_event)
    ok_offer3 = create_thing_offer(ok_venue1, ko_thing)
    ko_offer4 = create_thing_offer(ko_venue2, ko_thing)
    ok_offer5 = create_event_offer(ok_venue3, ko_event)
    ko_offer6 = create_event_offer(ko_venue4, ko_event)
    ok_offer7 = create_thing_offer(ok_venue3, ko_thing)
    ko_offer8 = create_thing_offer(ko_venue4, ko_thing)
    PcObject.check_and_save(
        ok_offer1, ko_offer2, ok_offer3, ko_offer4,
        ok_offer5, ko_offer6, ok_offer7, ko_offer8
    )

    # when
    query = filter_offers_with_keywords_string(Offer.query, 'Rencontre')

    # then
    found_offers = query.all()
    assert len(found_offers) == 4
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id
    assert ko_offer4.id not in found_offers_id
    assert ok_offer5.id in found_offers_id
    assert ko_offer6.id not in found_offers_id
    assert ok_offer7.id in found_offers_id
    assert ko_offer8.id not in found_offers_id

@pytest.mark.standalone
@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_one_partial_keyword_at_venue_or_offerer_level(app):
    # given
    ko_event = create_event()
    ko_thing = create_thing()
    ok_offerer1 = create_offerer(name="La Rencontre")
    ko_offerer2 = create_offerer(siren='123456788')
    ko_offerer3 = create_offerer(siren='123456787')
    ko_offerer4 = create_offerer(siren='123456786')
    ok_venue1 = create_venue(ok_offerer1, siret=ok_offerer1.siren + '54321')
    ko_venue2 = create_venue(ko_offerer2, siret=ko_offerer2.siren + '12345')
    ok_venue3 = create_venue(ko_offerer3, name='Librairie la Rencontre', city='Saint Denis', siret=ko_offerer3.siren + '54321')
    ko_venue4 = create_venue(ko_offerer4, name='Bataclan', city='Paris', siret=ko_offerer4.siren + '12345')
    ok_offer1 = create_event_offer(ok_venue1, ko_event)
    ko_offer2 = create_event_offer(ko_venue2, ko_event)
    ok_offer3 = create_thing_offer(ok_venue1, ko_thing)
    ko_offer4 = create_thing_offer(ko_venue2, ko_thing)
    ok_offer5 = create_event_offer(ok_venue3, ko_event)
    ko_offer6 = create_event_offer(ko_venue4, ko_event)
    ok_offer7 = create_thing_offer(ok_venue3, ko_thing)
    ko_offer8 = create_thing_offer(ko_venue4, ko_thing)
    PcObject.check_and_save(
        ok_offer1, ko_offer2, ok_offer3, ko_offer4,
        ok_offer5, ko_offer6, ok_offer7, ko_offer8
    )

    # when
    query = filter_offers_with_keywords_string(Offer.query, 'Renc')

    # then
    found_offers = query.all()
    assert len(found_offers) == 4
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id
    assert ko_offer4.id not in found_offers_id
    assert ok_offer5.id in found_offers_id
    assert ko_offer6.id not in found_offers_id
    assert ok_offer7.id in found_offers_id
    assert ko_offer8.id not in found_offers_id

@pytest.mark.standalone
@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_several_keywords_at_venue_or_offerer_level(app):
    # given
    ko_event = create_event()
    ko_thing = create_thing()
    ok_offerer1 = create_offerer(name="Librairie La Rencontre")
    ko_offerer2 = create_offerer(siren='123456788')
    ko_offerer3 = create_offerer(siren='123456787')
    ko_offerer4 = create_offerer(siren='123456786')
    ok_venue1 = create_venue(ok_offerer1, siret=ok_offerer1.siren + '54321')
    ko_venue2 = create_venue(ko_offerer2, siret=ko_offerer2.siren + '12345')
    ok_venue3 = create_venue(ko_offerer3, name='Librairie la Rencontre', city='Saint Denis', siret=ko_offerer3.siren + '54321')
    ko_venue4 = create_venue(ko_offerer4, name='Bataclan', city='Paris', siret=ko_offerer4.siren + '12345')
    ok_offer1 = create_event_offer(ok_venue1, ko_event)
    ko_offer2 = create_event_offer(ko_venue2, ko_event)
    ok_offer3 = create_thing_offer(ok_venue1, ko_thing)
    ko_offer4 = create_thing_offer(ko_venue2, ko_thing)
    ok_offer5 = create_event_offer(ok_venue3, ko_event)
    ko_offer6 = create_event_offer(ko_venue4, ko_event)
    ok_offer7 = create_thing_offer(ok_venue3, ko_thing)
    ko_offer8 = create_thing_offer(ko_venue4, ko_thing)
    PcObject.check_and_save(
        ok_offer1, ko_offer2, ok_offer3, ko_offer4,
        ok_offer5, ko_offer6, ok_offer7, ko_offer8
    )

    # when
    query = filter_offers_with_keywords_string(Offer.query, 'Librairie Rencontre')

    # then
    found_offers = query.all()
    assert len(found_offers) == 4
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id
    assert ko_offer4.id not in found_offers_id
    assert ok_offer5.id in found_offers_id
    assert ko_offer6.id not in found_offers_id
    assert ok_offer7.id in found_offers_id
    assert ko_offer8.id not in found_offers_id

@pytest.mark.standalone
@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_several_partial_keywords_at_venue_or_offerer_level(app):
    # given
    ko_event = create_event()
    ko_thing = create_thing()
    ok_offerer1 = create_offerer(name="Librairie La Rencontre")
    ko_offerer2 = create_offerer(siren='123456788')
    ko_offerer3 = create_offerer(siren='123456787')
    ko_offerer4 = create_offerer(siren='123456786')
    ok_venue1 = create_venue(ok_offerer1, siret=ok_offerer1.siren + '54321')
    ko_venue2 = create_venue(ko_offerer2, siret=ko_offerer2.siren + '12345')
    ok_venue3 = create_venue(ko_offerer3, name='Librairie la Rencontre', city='Saint Denis', siret=ko_offerer3.siren + '54321')
    ko_venue4 = create_venue(ko_offerer4, name='Bataclan', city='Paris', siret=ko_offerer4.siren + '12345')
    ok_offer1 = create_event_offer(ok_venue1, ko_event)
    ko_offer2 = create_event_offer(ko_venue2, ko_event)
    ok_offer3 = create_thing_offer(ok_venue1, ko_thing)
    ko_offer4 = create_thing_offer(ko_venue2, ko_thing)
    ok_offer5 = create_event_offer(ok_venue3, ko_event)
    ko_offer6 = create_event_offer(ko_venue4, ko_event)
    ok_offer7 = create_thing_offer(ok_venue3, ko_thing)
    ko_offer8 = create_thing_offer(ko_venue4, ko_thing)
    PcObject.check_and_save(
        ok_offer1, ko_offer2, ok_offer3, ko_offer4,
        ok_offer5, ko_offer6, ok_offer7, ko_offer8
    )

    # when
    query = filter_offers_with_keywords_string(Offer.query, 'Lib Renc')

    # then
    found_offers = query.all()
    assert len(found_offers) == 4
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id
    assert ko_offer4.id not in found_offers_id
    assert ok_offer5.id in found_offers_id
    assert ko_offer6.id not in found_offers_id
    assert ok_offer7.id in found_offers_id
    assert ko_offer8.id not in found_offers_id


@pytest.mark.standalone
@clean_database
def test_create_filter_matching_all_keywords_with_one_keyword_at_event_or_thing_or_venue_or_offerer_level(app):
    # given
    ok_event1 = create_event(event_name='Rencontre avec Jacques Martin')
    ko_event2 = create_event(event_name='Concert de contrebasse')
    ko_thing = create_thing(thing_name='Belle du Seigneur')
    offerer = create_offerer()
    ko_venue1 = create_venue(offerer, name='Bataclan', city='Paris', siret=offerer.siren + '12345')
    ok_venue2 = create_venue(offerer, name='Librairie la Rencontre', city='Saint Denis', siret=offerer.siren + '54321')
    ok_offer1 = create_event_offer(ko_venue1, ok_event1)
    ko_offer2 = create_event_offer(ko_venue1, ko_event2)
    ok_offer3 = create_thing_offer(ok_venue2, ko_thing)
    PcObject.check_and_save(ok_offer1, ko_offer2, ok_offer3)

    # when
    query = filter_offers_with_keywords_string(Offer.query, 'Rencontre')

    # then
    found_offers = query.all()
    assert len(found_offers) == 2
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id


@pytest.mark.standalone
@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_one_partial_keyword_at_event_or_thing_or_venue_or_offerer_level(
        app):
    # given
    ok_event1 = create_event(event_name='Rencontre avec Jacques Martin')
    ko_event2 = create_event(event_name='Concert de contrebasse')
    ko_thing = create_thing(thing_name='Belle du Seigneur')
    offerer = create_offerer()
    ko_venue1 = create_venue(offerer, name='Bataclan', city='Paris', siret=offerer.siren + '12345')
    ok_venue2 = create_venue(offerer, name='Librairie la Rencontre', city='Saint Denis', siret=offerer.siren + '54321')
    ok_offer1 = create_event_offer(ko_venue1, ok_event1)
    ko_offer2 = create_event_offer(ko_venue1, ko_event2)
    ok_offer3 = create_thing_offer(ok_venue2, ko_thing)
    PcObject.check_and_save(ok_offer1, ko_offer2, ok_offer3)

    # when
    query = filter_offers_with_keywords_string(Offer.query, 'Rencon')

    # then
    found_offers = query.all()
    assert len(found_offers) == 2
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id



@pytest.mark.standalone
@clean_database
@pytest.mark.skip
def test_create_filter_matching_all_keywords_in_any_models_with_several_keywords_at_event_or_thing_or_venue_or_offerer_level(
        app):
    # given
    ok_event1 = create_event(event_name='Rencontre avec Jacques Martin')
    ko_event2 = create_event(event_name='Claquettes avec Jacques Martin')
    ko_event3 = create_event(event_name='Concert de contrebasse')
    ok_thing = create_thing(thing_name='Rencontre avec Belle du Seigneur')
    offerer = create_offerer()
    ko_venue1 = create_venue(offerer, name='Stade de France', city='Saint Denis', siret=offerer.siren + '54321')
    ok_venue2 = create_venue(offerer, name='Bataclan', city='Paris', siret=offerer.siren + '12345')

    ok_offer1 = create_event_offer(ko_venue1, ok_event1)
    ko_offer2 = create_event_offer(ko_venue1, ko_event2)
    ok_offer3 = create_event_offer(ok_venue2, ko_event3)
    ok_offer4 = create_thing_offer(ok_venue2, ok_thing)
    PcObject.check_and_save(ok_offer1, ko_offer2, ok_offer3, ok_offer4)

    # when
    query = filter_offers_with_keywords_string(Offer.query, 'Rencontre Bataclan')

    # then
    found_offer_ids = [offer.id for offer in query.all()]
    assert len(found_offer_ids) == 3
    assert ok_offer1.id in found_offer_ids
    assert ko_offer2.id not in found_offer_ids
    assert ok_offer3.id in found_offer_ids
    assert ok_offer4.id in found_offer_ids


@pytest.mark.standalone
@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_several_partial_keywords_at_event_or_thing_or_venue_or_offerer_level(
        app):
    # given
    ok_event1 = create_event(event_name='Rencontre avec Jacques Martin')
    ko_event2 = create_event(event_name='Concert de contrebasse')
    ko_thing = create_thing(thing_name='Belle du Seigneur')
    offerer = create_offerer()
    ko_venue1 = create_venue(offerer, name='Bataclan', city='Paris', siret=offerer.siren + '12345')
    ok_venue2 = create_venue(offerer, name='Librairie la Rencontre', city='Saint Denis', siret=offerer.siren + '54321')
    ok_offer1 = create_event_offer(ko_venue1, ok_event1)
    ko_offer2 = create_event_offer(ko_venue1, ko_event2)
    ok_offer3 = create_thing_offer(ok_venue2, ko_thing)
    PcObject.check_and_save(ok_offer1, ko_offer2, ok_offer3)

    # when
    query = filter_offers_with_keywords_string(Offer.query, 'Jacques Rencontre')

    # then
    found_offers = query.all()
    assert len(found_offers) == 2
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id
