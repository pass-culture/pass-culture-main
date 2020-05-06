from models.offer_type import EventType, ThingType
from repository import repository, discovery_view_queries
from repository.offer_queries import get_offers_for_recommendation
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_booking, create_criterion, \
    create_user, create_offerer, create_venue, \
    create_favorite, create_mediation
from tests.model_creators.specific_creators import create_stock_from_offer, \
    create_stock_with_thing_offer, create_product_with_thing_type, \
    create_offer_with_thing_product, create_offer_with_event_product

REFERENCE_DATE = '2017-10-15 09:21:34'


class GetOfferForRecommendationsTest:
    class FiltersTest:
        @clean_database
        def test_when_department_code_00_should_return_offers_of_all_departements(self, app):
            # Given
            offerer = create_offerer(siren='123456789')
            user = create_user()
            venue_34 = create_venue(offerer, postal_code='34000',
                                    departement_code='34', siret=offerer.siren + '11111')
            venue_93 = create_venue(offerer, postal_code='93000',
                                    departement_code='93', siret=offerer.siren + '22222')
            venue_75 = create_venue(offerer, postal_code='75000',
                                    departement_code='75', siret=offerer.siren + '33333')
            offer_34 = create_offer_with_thing_product(venue_34)
            offer_93 = create_offer_with_thing_product(venue_93)
            offer_75 = create_offer_with_thing_product(venue_75)
            stock_34 = create_stock_from_offer(offer_34)
            stock_93 = create_stock_from_offer(offer_93)
            stock_75 = create_stock_from_offer(offer_75)
            create_mediation(stock_34.offer)
            create_mediation(stock_93.offer)
            create_mediation(stock_75.offer)

            repository.save(user, stock_34, stock_93, stock_75)

            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(departement_codes=['00'],
                                                   user=user)

            # Then
            assert offer_34 in offers
            assert offer_93 in offers
            assert offer_75 in offers

        @clean_database
        def test_should_return_offer_when_offer_is_national(self, app):
            # Given
            offerer = create_offerer(siren='123456789')
            user = create_user()
            venue_34 = create_venue(offerer, postal_code='34000',
                                    departement_code='34', siret=offerer.siren + '11111')
            offer_34 = create_offer_with_thing_product(venue_34)
            offer_national = create_offer_with_thing_product(
                venue_34, is_national=True)
            stock_34 = create_stock_from_offer(offer_34)
            stock_national = create_stock_from_offer(offer_national)
            create_mediation(stock_34.offer)
            create_mediation(stock_national.offer)

            repository.save(user, stock_34, stock_national)

            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(departement_codes=['93'],
                                                   user=user)

            # Then
            assert offer_34 not in offers
            assert offer_national in offers

        @clean_database
        def test_should_not_return_activation_event(self, app):
            # Given
            offerer = create_offerer(siren='123456789')
            user = create_user()
            venue_93 = create_venue(offerer, postal_code='93000',
                                    departement_code='93', siret=offerer.siren + '33333')
            offer_93 = create_offer_with_event_product(venue_93, thumb_count=1)
            offer_activation_93 = create_offer_with_event_product(venue_93, event_type=EventType.ACTIVATION,
                                                                  thumb_count=1)
            stock_93 = create_stock_from_offer(offer_93)
            stock_activation_93 = create_stock_from_offer(offer_activation_93)
            mediation1 = create_mediation(stock_93.offer)
            mediation2 = create_mediation(stock_activation_93.offer)

            repository.save(user, stock_93, stock_activation_93,
                            mediation1, mediation2)

            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(departement_codes=['00'],
                                                   user=user)

            # Then
            assert offer_93 in offers
            assert offer_activation_93 not in offers

        @clean_database
        def test_should_not_return_activation_thing(self, app):
            # Given
            offerer = create_offerer(siren='123456789')
            user = create_user()
            venue_93 = create_venue(offerer, postal_code='93000',
                                    departement_code='93', siret=offerer.siren + '33333')
            offer_93 = create_offer_with_thing_product(venue_93, thumb_count=1)
            offer_activation_93 = create_offer_with_thing_product(venue_93, thing_type=ThingType.ACTIVATION,
                                                                  thumb_count=1)
            stock_93 = create_stock_from_offer(offer_93)
            stock_activation_93 = create_stock_from_offer(offer_activation_93)
            create_mediation(stock_93.offer)
            create_mediation(stock_activation_93.offer)

            repository.save(user, stock_93, stock_activation_93)

            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(departement_codes=['00'],
                                                   user=user)

            # Then
            assert offer_93 in offers
            assert offer_activation_93 not in offers

        @clean_database
        def test_should_return_offers_with_stock(self, app):
            # Given
            product = create_product_with_thing_type(
                thing_name='Lire un livre', is_national=True)
            offerer = create_offerer()
            user = create_user()
            venue = create_venue(offerer, postal_code='34000',
                                 departement_code='34')
            offer = create_offer_with_thing_product(venue=venue, product=product)
            stock = create_stock_from_offer(offer, quantity=2)
            create_mediation(stock.offer)
            repository.save(user, stock)

            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(departement_codes=['00'],
                                                   user=user)

            # Then
            assert len(offers) == 1

        @clean_database
        def test_should_return_offers_with_mediation_only(self, app):
            # Given
            offerer = create_offerer()
            user = create_user()
            venue = create_venue(offerer, postal_code='34000',
                                 departement_code='34')
            stock1 = create_stock_with_thing_offer(offerer, venue, name='thing_with_mediation')
            stock2 = create_stock_with_thing_offer(offerer, venue, name='thing_without_mediation')
            create_mediation(stock1.offer)
            repository.save(user, stock1, stock2)

            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(departement_codes=['00'],
                                                   user=user)

            # Then
            assert len(offers) == 1
            assert offers[0].name == 'thing_with_mediation'

        @clean_database
        def test_should_not_return_offers_with_no_stock(self, app):
            # Given
            product = create_product_with_thing_type(
                thing_name='Lire un livre', is_national=True)
            offerer = create_offerer()
            user = create_user()
            venue = create_venue(offerer, postal_code='34000',
                                 departement_code='34')
            offer = create_offer_with_thing_product(venue=venue, product=product)
            stock = create_stock_from_offer(offer, price=0, quantity=2)
            booking1 = create_booking(
                user=user, stock=stock, is_cancelled=True, quantity=2, venue=venue)
            booking2 = create_booking(
                user=user, stock=stock, quantity=2, venue=venue)
            create_mediation(stock.offer)
            repository.save(user, booking1, booking2)
            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(departement_codes=['00'],
                                                   user=user)

            # Then
            assert len(offers) == 0

        @clean_database
        def test_should_not_return_booked_offers(self, app):
            # Given
            offerer = create_offerer()
            venue = create_venue(offerer, postal_code='34000',
                                 departement_code='34')
            offer = create_offer_with_thing_product(
                venue, thing_type=ThingType.CINEMA_ABO)
            stock = create_stock_from_offer(offer, price=0)
            user = create_user()
            booking = create_booking(user=user, stock=stock)
            create_mediation(stock.offer)
            repository.save(user, booking)
            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(departement_codes=['00'],
                                                   user=user)

            # Then
            assert offers == []

        @clean_database
        def test_should_not_return_favorite_offers(self, app):
            # Given
            offerer = create_offerer()
            user = create_user()
            venue = create_venue(offerer, postal_code='34000',
                                 departement_code='34')

            offer = create_offer_with_thing_product(
                venue, thing_type=ThingType.CINEMA_ABO)
            stock = create_stock_from_offer(offer, price=0)
            mediation = create_mediation(stock.offer)
            favorite = create_favorite(mediation=mediation, offer=offer, user=user)

            repository.save(user, favorite)
            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(departement_codes=['00'],
                                                   user=user)

            # Then
            assert offers == []

    class OrderTest:
        @clean_database
        def test_should_return_digital_offers_first_when_offers_have_same_criterion_score(self, app):
            # Given
            offerer = create_offerer()
            user = create_user()
            venue = create_venue(offerer, postal_code='34000',
                                 departement_code='34')
            digital_offer = create_offer_with_thing_product(venue=venue, is_national=True,
                                                            thing_type=ThingType.LIVRE_EDITION, url='https://url.com')
            physical_offer = create_offer_with_thing_product(venue=venue, is_national=True,
                                                             thing_type=ThingType.LIVRE_EDITION, url=None)
            stock_digital_offer = create_stock_from_offer(digital_offer, quantity=2)
            stock_physical_offer = create_stock_from_offer(physical_offer, quantity=2)
            create_mediation(physical_offer)
            create_mediation(digital_offer)
            repository.save(user, stock_digital_offer, stock_physical_offer)

            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(departement_codes=['00'],
                                                   user=user)

            # Then
            assert offers == [digital_offer, physical_offer]

        @clean_database
        def test_should_order_offers_by_criterion_score_first(self, app):
            # Given
            offerer = create_offerer()
            user = create_user()
            venue = create_venue(offerer, postal_code='34000',
                                 departement_code='34')
            digital_offer = create_offer_with_thing_product(venue=venue, is_national=True,
                                                            thing_type=ThingType.LIVRE_EDITION, url='https://url.com')
            physical_offer = create_offer_with_thing_product(venue=venue, is_national=True,
                                                             thing_type=ThingType.LIVRE_EDITION, url=None)
            stock_digital_offer = create_stock_from_offer(digital_offer, quantity=2)
            stock_physical_offer = create_stock_from_offer(physical_offer, quantity=2)
            create_mediation(physical_offer)
            create_mediation(digital_offer)
            digital_offer.criteria = [create_criterion(name='negative', score_delta=-1)]
            physical_offer.criteria = [create_criterion(name='negative', score_delta=-1),
                                       create_criterion(name='positive', score_delta=1)]

            repository.save(user, stock_digital_offer, stock_physical_offer)

            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(departement_codes=['00'],
                                                   user=user)

            # Then
            assert offers == [physical_offer, digital_offer]

        @clean_database
        def test_putting_a_super_bonus_to_a_physical_offer_puts_it_on_top_of_recommended_offers(self, app):
            # Given
            offerer = create_offerer()
            user = create_user()
            venue = create_venue(offerer, postal_code='34000',
                                 departement_code='34')
            digital_offer_with_bonus = create_offer_with_thing_product(venue=venue, is_national=True,
                                                                       thing_type=ThingType.LIVRE_EDITION,
                                                                       url='https://url.com')
            digital_offer_with_bonus.criteria = [create_criterion(name='negative', score_delta=1)]

            digital_offer = create_offer_with_thing_product(venue=venue, is_national=True,
                                                            thing_type=ThingType.LIVRE_EDITION, url='https://url.com')
            digital_offer_with_malus = create_offer_with_thing_product(venue=venue, is_national=True,
                                                                       thing_type=ThingType.LIVRE_EDITION,
                                                                       url='https://url.com')
            digital_offer_with_malus.criteria = [create_criterion(name='negative', score_delta=-1)]
            physical_offer = create_offer_with_thing_product(venue=venue, is_national=True,
                                                             thing_type=ThingType.LIVRE_EDITION, url=None)
            physical_offer_with_super_bonus = create_offer_with_thing_product(venue=venue, is_national=True,
                                                                              thing_type=ThingType.LIVRE_EDITION,
                                                                              url=None)
            physical_offer_with_super_bonus.criteria = [create_criterion(name='negative', score_delta=2)]

            stock_digital_offer_with_bonus = create_stock_from_offer(digital_offer_with_bonus, quantity=2)
            stock_digital_offer = create_stock_from_offer(digital_offer, quantity=2)
            stock_digital_offer_with_malus = create_stock_from_offer(digital_offer_with_malus, quantity=2)
            stock_physical_offer = create_stock_from_offer(physical_offer, quantity=2)
            stock_physical_offer_with_super_bonus = create_stock_from_offer(physical_offer_with_super_bonus, quantity=2)

            create_mediation(digital_offer_with_bonus)
            create_mediation(digital_offer)
            create_mediation(digital_offer_with_malus)
            create_mediation(physical_offer)
            create_mediation(physical_offer_with_super_bonus)

            repository.save(user, stock_digital_offer_with_bonus, stock_digital_offer, stock_digital_offer_with_malus,
                            stock_physical_offer, stock_physical_offer_with_super_bonus)

            discovery_view_queries.refresh(concurrently=False)

            # When
            offers = get_offers_for_recommendation(departement_codes=['00'],
                                                   user=user)

            # Then
            assert offers == [physical_offer_with_super_bonus, digital_offer_with_bonus, digital_offer, physical_offer,
                              digital_offer_with_malus]
