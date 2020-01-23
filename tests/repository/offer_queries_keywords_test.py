from datetime import datetime, timedelta

from repository import repository
from repository.offer_queries import filter_offers_with_keywords_string, build_offer_search_base_query, \
    get_offers_for_recommendations_search
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_booking, create_user, create_stock, create_offerer, \
    create_venue
from tests.model_creators.specific_creators import create_stock_from_event_occurrence, create_product_with_thing_type, \
    create_product_with_event_type, create_offer_with_thing_product, create_offer_with_event_product, \
    create_event_occurrence


@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_one_keyword_at_event_or_thing_level(app):
    # given
    ok_event1 = create_product_with_event_type(event_name='Rencontre avec Jacques Martin')
    event2 = create_product_with_event_type(event_name='Concert de contrebasse')
    ok_thing = create_product_with_thing_type(thing_name='Rencontre avec Belle du Seigneur')
    offerer = create_offerer()
    venue = create_venue(offerer)
    ok_offer1 = create_offer_with_event_product(venue, ok_event1)
    ko_offer2 = create_offer_with_event_product(venue, event2)
    ok_offer3 = create_offer_with_thing_product(venue, ok_thing)
    repository.save(ok_offer1, ko_offer2, ok_offer3)

    # when
    query = filter_offers_with_keywords_string(build_offer_search_base_query(), 'rencontre')

    # then
    found_offers = query.all()
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id


@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_one_partial_keyword_at_event_or_thing_level(app):
    # given
    ok_event1 = create_product_with_event_type(event_name='Rencontre avec Jacques Martin')
    event2 = create_product_with_event_type(event_name='Concert de contrebasse')
    ok_thing = create_product_with_thing_type(thing_name='Rencontre avec Belle du Seigneur')
    offerer = create_offerer()
    venue = create_venue(offerer)
    ok_offer1 = create_offer_with_event_product(venue, ok_event1)
    ko_offer2 = create_offer_with_event_product(venue, event2)
    ok_offer3 = create_offer_with_thing_product(venue, ok_thing)
    repository.save(ok_offer1, ko_offer2, ok_offer3)

    # when
    query = filter_offers_with_keywords_string(build_offer_search_base_query(), 'Renc')

    # then
    found_offers = query.all()
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id


@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_several_keywords_at_just_event_or_just_thing_level(app):
    # given
    ok_event1 = create_product_with_event_type(event_name='Rencontre avec Jacques Martin')
    event2 = create_product_with_event_type(event_name='Concert de contrebasse')
    ok_thing1 = create_product_with_thing_type(thing_name='Rencontre avec vous savez qui',
                                               description='Il s\'agit de Jacques')
    thing2 = create_product_with_thing_type(thing_name='Rencontre avec Belle du Seigneur')
    offerer = create_offerer()
    venue = create_venue(offerer)
    ok_offer1 = create_offer_with_event_product(venue, ok_event1)
    ko_offer2 = create_offer_with_event_product(venue, event2)
    ok_offer3 = create_offer_with_thing_product(venue, ok_thing1)
    ko_offer4 = create_offer_with_thing_product(venue, thing2)
    repository.save(ok_offer1, ko_offer2, ok_offer3, ko_offer4)

    # when
    query = filter_offers_with_keywords_string(build_offer_search_base_query(), 'Rencontre Jacques')

    # then
    found_offers = query.all()
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id
    assert ko_offer4.id not in found_offers_id


@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_several_partial_keywords_at_just_event_or_just_thing_level(
        app):
    # given
    ok_event1 = create_product_with_event_type(event_name='Rencontre avec Jacques Martin')
    event2 = create_product_with_event_type(event_name='Concert de contrebasse')
    ok_thing1 = create_product_with_thing_type(thing_name='Rencontre avec vous savez qui',
                                               description='Il s\'agit de Jacques')
    thing2 = create_product_with_thing_type(thing_name='Rencontre avec Belle du Seigneur')
    offerer = create_offerer()
    venue = create_venue(offerer)
    ok_offer1 = create_offer_with_event_product(venue, ok_event1)
    ko_offer2 = create_offer_with_event_product(venue, event2)
    ok_offer3 = create_offer_with_thing_product(venue, ok_thing1)
    ko_offer4 = create_offer_with_thing_product(venue, thing2)
    repository.save(ok_offer1, ko_offer2, ok_offer3, ko_offer4)

    # when
    query = filter_offers_with_keywords_string(build_offer_search_base_query(), 'Renc Jacqu')

    # then
    found_offers = query.all()
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id
    assert ko_offer4.id not in found_offers_id


@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_one_keyword_at_venue_or_offerer_level(app):
    # given
    event_product = create_product_with_event_type()
    thing_product = create_product_with_thing_type()
    ok_offerer1 = create_offerer(name='La Rencontre', siren='123456789')
    offerer2 = create_offerer(siren='123456788')
    offerer3 = create_offerer(siren='123456787')
    offerer4 = create_offerer(siren='123456786')
    ok_venue1 = create_venue(ok_offerer1, siret=ok_offerer1.siren + '54321')
    venue2 = create_venue(offerer2, siret=offerer2.siren + '12345')
    ok_venue3 = create_venue(offerer3, name='Librairie la Rencontre', city='Saint Denis',
                             siret=offerer3.siren + '54321')
    venue4 = create_venue(offerer4, name='Bataclan', city='Paris', siret=offerer4.siren + '12345')
    ok_offer1 = create_offer_with_event_product(ok_venue1, event_product)
    ko_offer2 = create_offer_with_event_product(venue2, event_product)
    ok_offer3 = create_offer_with_thing_product(ok_venue1, thing_product)
    ko_offer4 = create_offer_with_thing_product(venue2, thing_product)
    ok_offer5 = create_offer_with_event_product(ok_venue3, event_product)
    ko_offer6 = create_offer_with_event_product(venue4, event_product)
    ok_offer7 = create_offer_with_thing_product(ok_venue3, thing_product)
    ko_offer8 = create_offer_with_thing_product(venue4, thing_product)
    repository.save(
        ok_offer1, ko_offer2, ok_offer3, ko_offer4,
        ok_offer5, ko_offer6, ok_offer7, ko_offer8
    )

    # when
    query = filter_offers_with_keywords_string(build_offer_search_base_query(), 'Rencontre')

    # then
    found_offers = query.all()
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id
    assert ko_offer4.id not in found_offers_id
    assert ok_offer5.id in found_offers_id
    assert ko_offer6.id not in found_offers_id
    assert ok_offer7.id in found_offers_id
    assert ko_offer8.id not in found_offers_id


@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_one_keyword_at_venue_public_name_level(app):
    # given
    event = create_product_with_event_type()
    thing = create_product_with_thing_type()
    ok_offerer1 = create_offerer(name='La Rencontre', siren='123456789')
    offerer2 = create_offerer(siren='123456788')
    offerer3 = create_offerer(siren='123456787')
    offerer4 = create_offerer(siren='123456786')
    ok_venue1 = create_venue(offerer=ok_offerer1, siret=ok_offerer1.siren + '54321', public_name='Un lieu trop chouette de ouf')
    venue2 = create_venue(offerer=offerer2, siret=offerer2.siren + '12345')
    ok_venue3 = create_venue(offerer=offerer3, name='Librairie la Rencontre', city='Saint Denis', siret=offerer3.siren + '54321', public_name='chouette endroit de ouf')
    venue4 = create_venue(offerer=offerer4, name='Bataclan', city='Paris', siret=offerer4.siren + '12345')
    ok_offer1 = create_offer_with_event_product(ok_venue1, event)
    ko_offer2 = create_offer_with_event_product(venue2, event)
    ok_offer3 = create_offer_with_thing_product(ok_venue1, thing)
    ko_offer4 = create_offer_with_thing_product(venue2, thing)
    ok_offer5 = create_offer_with_event_product(ok_venue3, event)
    ko_offer6 = create_offer_with_event_product(venue4, event)
    ok_offer7 = create_offer_with_thing_product(ok_venue3, thing)
    ko_offer8 = create_offer_with_thing_product(venue4, thing)
    repository.save(
        ok_offer1, ko_offer2, ok_offer3, ko_offer4,
        ok_offer5, ko_offer6, ok_offer7, ko_offer8
    )

    # when
    query = filter_offers_with_keywords_string(build_offer_search_base_query(), 'chouette')

    # then
    found_offers = query.all()
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id
    assert ko_offer4.id not in found_offers_id
    assert ok_offer5.id in found_offers_id
    assert ko_offer6.id not in found_offers_id
    assert ok_offer7.id in found_offers_id
    assert ko_offer8.id not in found_offers_id


@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_one_partial_keyword_at_venue_public_name_level(app):
    # given
    event = create_product_with_event_type()
    thing = create_product_with_thing_type()
    ok_offerer1 = create_offerer(name='La Rencontre', siren='123456789')
    offerer2 = create_offerer(siren='123456788')
    offerer3 = create_offerer(siren='123456787')
    offerer4 = create_offerer(siren='123456786')
    ok_venue1 = create_venue(ok_offerer1, siret=ok_offerer1.siren + '54321', public_name='Un lieu trop chouette de ouf')
    venue2 = create_venue(offerer2, siret=offerer2.siren + '12345')
    ok_venue3 = create_venue(offerer3, name='Librairie la Rencontre', city='Saint Denis',
                             siret=offerer3.siren + '54321', public_name='chouette endroit de ouf')
    venue4 = create_venue(offerer4, name='Bataclan', city='Paris', siret=offerer4.siren + '12345')
    ok_offer1 = create_offer_with_event_product(ok_venue1, event)
    ko_offer2 = create_offer_with_event_product(venue2, event)
    ok_offer3 = create_offer_with_thing_product(ok_venue1, thing)
    ko_offer4 = create_offer_with_thing_product(venue2, thing)
    ok_offer5 = create_offer_with_event_product(ok_venue3, event)
    ko_offer6 = create_offer_with_event_product(venue4, event)
    ok_offer7 = create_offer_with_thing_product(ok_venue3, thing)
    ko_offer8 = create_offer_with_thing_product(venue4, thing)
    repository.save(
        ok_offer1, ko_offer2, ok_offer3, ko_offer4,
        ok_offer5, ko_offer6, ok_offer7, ko_offer8
    )

    # when
    query = filter_offers_with_keywords_string(build_offer_search_base_query(), 'chou')

    # then
    found_offers = query.all()
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id
    assert ko_offer4.id not in found_offers_id
    assert ok_offer5.id in found_offers_id
    assert ko_offer6.id not in found_offers_id
    assert ok_offer7.id in found_offers_id
    assert ko_offer8.id not in found_offers_id


@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_several_keywords_at_venue_public_name_level(app):
    # given
    event = create_product_with_event_type()
    thing = create_product_with_thing_type()
    ok_offerer1 = create_offerer(name='La Rencontre', siren='123456789')
    offerer2 = create_offerer(siren='123456788')
    offerer3 = create_offerer(siren='123456787')
    offerer4 = create_offerer(siren='123456786')
    ok_venue1 = create_venue(ok_offerer1, siret=ok_offerer1.siren + '54321', public_name='Un lieu trop chouette de ouf')
    venue2 = create_venue(offerer2, siret=offerer2.siren + '12345')
    ok_venue3 = create_venue(offerer3, name='Librairie la Rencontre', city='Saint Denis',
                             siret=offerer3.siren + '54321', public_name='chouette endroit de ouf')
    venue4 = create_venue(offerer4, name='Bataclan', city='Paris', siret=offerer4.siren + '12345')
    ok_offer1 = create_offer_with_event_product(ok_venue1, event)
    ko_offer2 = create_offer_with_event_product(venue2, event)
    ok_offer3 = create_offer_with_thing_product(ok_venue1, thing)
    ko_offer4 = create_offer_with_thing_product(venue2, thing)
    ok_offer5 = create_offer_with_event_product(ok_venue3, event)
    ko_offer6 = create_offer_with_event_product(venue4, event)
    ok_offer7 = create_offer_with_thing_product(ok_venue3, thing)
    ko_offer8 = create_offer_with_thing_product(venue4, thing)
    repository.save(
        ok_offer1, ko_offer2, ok_offer3, ko_offer4,
        ok_offer5, ko_offer6, ok_offer7, ko_offer8
    )

    # when
    query = filter_offers_with_keywords_string(build_offer_search_base_query(), 'chouette ouf')

    # then
    found_offers = query.all()
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id
    assert ko_offer4.id not in found_offers_id
    assert ok_offer5.id in found_offers_id
    assert ko_offer6.id not in found_offers_id
    assert ok_offer7.id in found_offers_id
    assert ko_offer8.id not in found_offers_id


@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_several_partial_keywords_at_venue_public_name_level(
        app):
    # given
    event = create_product_with_event_type()
    thing = create_product_with_thing_type()
    ok_offerer1 = create_offerer(name='La Rencontre', siren='123456789')
    offerer2 = create_offerer(siren='123456788')
    offerer3 = create_offerer(siren='123456787')
    offerer4 = create_offerer(siren='123456786')
    ok_venue1 = create_venue(ok_offerer1, siret=ok_offerer1.siren + '54321', public_name='Un lieu trop chouette de ouf')
    venue2 = create_venue(offerer2, siret=offerer2.siren + '12345')
    ok_venue3 = create_venue(offerer3, name='Librairie la Rencontre', city='Saint Denis',
                             siret=offerer3.siren + '54321', public_name='chouette endroit de ouf')
    venue4 = create_venue(offerer4, name='Bataclan', city='Paris', siret=offerer4.siren + '12345')
    ok_offer1 = create_offer_with_event_product(ok_venue1, event)
    ko_offer2 = create_offer_with_event_product(venue2, event)
    ok_offer3 = create_offer_with_thing_product(ok_venue1, thing)
    ko_offer4 = create_offer_with_thing_product(venue2, thing)
    ok_offer5 = create_offer_with_event_product(ok_venue3, event)
    ko_offer6 = create_offer_with_event_product(venue4, event)
    ok_offer7 = create_offer_with_thing_product(ok_venue3, thing)
    ko_offer8 = create_offer_with_thing_product(venue4, thing)
    repository.save(
        ok_offer1, ko_offer2, ok_offer3, ko_offer4,
        ok_offer5, ko_offer6, ok_offer7, ko_offer8
    )

    # when
    query = filter_offers_with_keywords_string(build_offer_search_base_query(), 'chou ou')

    # then
    found_offers = query.all()
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id
    assert ko_offer4.id not in found_offers_id
    assert ok_offer5.id in found_offers_id
    assert ko_offer6.id not in found_offers_id
    assert ok_offer7.id in found_offers_id
    assert ko_offer8.id not in found_offers_id


@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_one_keyword_at_venue_city_level(app):
    # given
    event = create_product_with_event_type()
    thing = create_product_with_thing_type()
    ok_offerer1 = create_offerer(name='La Rencontre', siren='123456789')
    offerer2 = create_offerer(siren='123456788')
    offerer3 = create_offerer(siren='123456787')
    offerer4 = create_offerer(siren='123456786')
    ok_venue1 = create_venue(ok_offerer1,
                             siret=ok_offerer1.siren + '54321',
                             public_name='Un lieu trop chouette de ouf',
                             city='Saint-Denis')
    venue2 = create_venue(offerer2, siret=offerer2.siren + '12345')
    ok_venue3 = create_venue(offerer3, name='Librairie la Rencontre', city='Saint-Denis',
                             siret=offerer3.siren + '54321', public_name='chouette endroit de ouf')
    venue4 = create_venue(offerer4, name='Bataclan', city='Paris', siret=offerer4.siren + '12345')
    ok_offer1 = create_offer_with_event_product(ok_venue1, event)
    ko_offer2 = create_offer_with_event_product(venue2, event)
    ok_offer3 = create_offer_with_thing_product(ok_venue1, thing)
    ko_offer4 = create_offer_with_thing_product(venue2, thing)
    ok_offer5 = create_offer_with_event_product(ok_venue3, event)
    ko_offer6 = create_offer_with_event_product(venue4, event)
    ok_offer7 = create_offer_with_thing_product(ok_venue3, thing)
    ko_offer8 = create_offer_with_thing_product(venue4, thing)
    repository.save(
        ok_offer1, ko_offer2, ok_offer3, ko_offer4,
        ok_offer5, ko_offer6, ok_offer7, ko_offer8
    )

    # when
    query = filter_offers_with_keywords_string(build_offer_search_base_query(), 'Saint-Denis')

    # then
    found_offers = query.all()
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id
    assert ko_offer4.id not in found_offers_id
    assert ok_offer5.id in found_offers_id
    assert ko_offer6.id not in found_offers_id
    assert ok_offer7.id in found_offers_id
    assert ko_offer8.id not in found_offers_id


@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_one_partial_keyword_at_venue_or_offerer_level(app):
    # given
    event_product = create_product_with_event_type()
    thing_product = create_product_with_thing_type()
    ok_offerer1 = create_offerer(name='La Rencontre', siren='123456789')
    offerer2 = create_offerer(siren='123456788')
    offerer3 = create_offerer(siren='123456787')
    offerer4 = create_offerer(siren='123456786')
    ok_venue1 = create_venue(ok_offerer1, siret=ok_offerer1.siren + '54321')
    venue2 = create_venue(offerer2, siret=offerer2.siren + '12345')
    ok_venue3 = create_venue(offerer3, name='Librairie la Rencontre', city='Saint Denis',
                             siret=offerer3.siren + '54321')
    venue4 = create_venue(offerer4, name='Bataclan', city='Paris', siret=offerer4.siren + '12345')
    ok_offer1 = create_offer_with_event_product(ok_venue1, event_product)
    ko_offer2 = create_offer_with_event_product(venue2, event_product)
    ok_offer3 = create_offer_with_thing_product(ok_venue1, thing_product)
    ko_offer4 = create_offer_with_thing_product(venue2, thing_product)
    ok_offer5 = create_offer_with_event_product(ok_venue3, event_product)
    ko_offer6 = create_offer_with_event_product(venue4, event_product)
    ok_offer7 = create_offer_with_thing_product(ok_venue3, thing_product)
    ko_offer8 = create_offer_with_thing_product(venue4, thing_product)
    repository.save(
        ok_offer1, ko_offer2, ok_offer3, ko_offer4,
        ok_offer5, ko_offer6, ok_offer7, ko_offer8
    )

    # when
    query = filter_offers_with_keywords_string(build_offer_search_base_query(), 'Renc')

    # then
    found_offers = query.all()
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id
    assert ko_offer4.id not in found_offers_id
    assert ok_offer5.id in found_offers_id
    assert ko_offer6.id not in found_offers_id
    assert ok_offer7.id in found_offers_id
    assert ko_offer8.id not in found_offers_id


@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_several_keywords_at_just_venue_or_just_offerer_level(
        app):
    # given
    event_product = create_product_with_event_type()
    thing_product = create_product_with_thing_type()
    ok_offerer1 = create_offerer(name='Librairie La Rencontre', siren='123456789')
    offerer2 = create_offerer(siren='123456788')
    offerer3 = create_offerer(siren='123456787')
    offerer4 = create_offerer(siren='123456786')
    ok_venue1 = create_venue(ok_offerer1, siret=ok_offerer1.siren + '54321')
    venue2 = create_venue(offerer2, siret=offerer2.siren + '12345')
    ok_venue3 = create_venue(offerer3, name='Librairie la Rencontre', city='Saint Denis',
                             siret=offerer3.siren + '54321')
    venue4 = create_venue(offerer4, name='Bataclan', city='Paris', siret=offerer4.siren + '12345')
    ok_offer1 = create_offer_with_event_product(ok_venue1, event_product)
    ko_offer2 = create_offer_with_event_product(venue2, event_product)
    ok_offer3 = create_offer_with_thing_product(ok_venue1, thing_product)
    ko_offer4 = create_offer_with_thing_product(venue2, thing_product)
    ok_offer5 = create_offer_with_event_product(ok_venue3, event_product)
    ko_offer6 = create_offer_with_event_product(venue4, event_product)
    ok_offer7 = create_offer_with_thing_product(ok_venue3, thing_product)
    ko_offer8 = create_offer_with_thing_product(venue4, thing_product)
    repository.save(
        ok_offer1, ko_offer2, ok_offer3, ko_offer4,
        ok_offer5, ko_offer6, ok_offer7, ko_offer8
    )

    # when
    query = filter_offers_with_keywords_string(build_offer_search_base_query(), 'Librairie Rencontre')

    # then
    found_offers = query.all()
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id
    assert ko_offer4.id not in found_offers_id
    assert ok_offer5.id in found_offers_id
    assert ko_offer6.id not in found_offers_id
    assert ok_offer7.id in found_offers_id
    assert ko_offer8.id not in found_offers_id


@clean_database
def test_create_filter_matching_all_keywords_with_one_keyword_at_mixed_event_or_thing_or_venue_or_offerer_level(app):
    # given
    ok_event1 = create_product_with_event_type(event_name='Rencontre avec Jacques Martin')
    event2 = create_product_with_event_type(event_name='Concert de contrebasse')
    thing_product = create_product_with_thing_type(thing_name='Belle du Seigneur')
    offerer = create_offerer(siren='123456789')
    venue1 = create_venue(offerer, name='Bataclan', city='Paris', siret=offerer.siren + '12345')
    ok_venue2 = create_venue(offerer, name='Librairie la Rencontre', city='Saint Denis', siret=offerer.siren + '54321')
    ok_offer1 = create_offer_with_event_product(venue1, ok_event1)
    ko_offer2 = create_offer_with_event_product(venue1, event2)
    ok_offer3 = create_offer_with_thing_product(ok_venue2, thing_product)
    repository.save(ok_offer1, ko_offer2, ok_offer3)

    # when
    query = filter_offers_with_keywords_string(build_offer_search_base_query(), 'Rencontre')

    # then
    found_offers = query.all()
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id


@clean_database
def test_create_filter_matching_all_keywords_in_any_models_with_one_partial_keyword_at_mixed_event_or_thing_or_venue_or_offerer_level(
        app):
    # given
    ok_event1 = create_product_with_event_type(event_name='Rencontre avec Jacques Martin')
    event2 = create_product_with_event_type(event_name='Concert de contrebasse')
    thing_product = create_product_with_thing_type(thing_name='Belle du Seigneur')
    offerer = create_offerer(siren='123456789')
    venue1 = create_venue(offerer, name='Bataclan', city='Paris', siret=offerer.siren + '12345')
    ok_venue2 = create_venue(offerer, name='Librairie la Rencontre', city='Saint Denis', siret=offerer.siren + '54321')
    ok_offer1 = create_offer_with_event_product(venue1, ok_event1)
    ko_offer2 = create_offer_with_event_product(venue1, event2)
    ok_offer3 = create_offer_with_thing_product(ok_venue2, thing_product)
    repository.save(ok_offer1, ko_offer2, ok_offer3)

    # when
    query = filter_offers_with_keywords_string(build_offer_search_base_query(), 'Rencon')

    # then
    found_offers = query.all()
    found_offers_id = [found_offer.id for found_offer in found_offers]
    assert ok_offer1.id in found_offers_id
    assert ko_offer2.id not in found_offers_id
    assert ok_offer3.id in found_offers_id


@clean_database
def test_get_offers_for_recommendations_search_only_return_available_offers(app):
    # Given
    in_one_hour = datetime.utcnow() + timedelta(hours=1)
    in_two_hours = datetime.utcnow() + timedelta(hours=2)

    offerer = create_offerer()
    venue = create_venue(offerer)
    thing_product = create_product_with_thing_type(thing_name='Lire un livre de Jazz')
    offer_available = create_offer_with_thing_product(venue, thing_product)
    stock_available = create_stock(price=12, available=5, offer=offer_available)

    offer_not_available = create_offer_with_event_product(venue, event_name='Training in Modern Jazz')
    event_occurrence = create_event_occurrence(offer_not_available, beginning_datetime=in_one_hour,
                                               end_datetime=in_two_hours)
    stock_with_no_available = create_stock_from_event_occurrence(event_occurrence, available=0)
    stock_with_one_available = create_stock_from_event_occurrence(event_occurrence, available=1, price=0)
    user = create_user()
    booking = create_booking(user=user, stock=stock_with_one_available, quantity=1, venue=venue)

    repository.save(stock_with_no_available, stock_available, booking)

    # When
    offers = get_offers_for_recommendations_search(keywords_string='Jazz')

    # Then
    assert len(offers) == 1
    assert offer_available in offers
