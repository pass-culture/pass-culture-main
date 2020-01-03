from datetime import datetime, timedelta

from models import PcObject, \
    EventType
from models.feature import FeatureToggle
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user, create_stock, create_offerer, create_venue, \
    create_recommendation, create_mediation
from tests.model_creators.specific_creators import create_stock_from_event_occurrence, create_stock_from_offer, \
    create_product_with_thing_type, create_offer_with_thing_product, create_offer_with_event_product, \
    create_event_occurrence
from tests.test_utils import deactivate_feature
from utils.date import strftime

TWENTY_DAYS_FROM_NOW = datetime.utcnow() + timedelta(days=20)

TEN_DAYS_FROM_NOW = datetime.utcnow() + timedelta(days=10)

RECOMMENDATION_URL = '/recommendations'



class Get:
    class Returns401:
        def when_no_user_is_logged_in(self, app):
            # when
            url = RECOMMENDATION_URL + '?keywords=Training'
            response = TestClient(app.test_client()).get(url, headers={'origin': 'http://localhost:3000'})

            # then
            assert response.status_code == 401

        @clean_database
        def when_searching_by_keywords_and_distance_without_latitude_and_longitude(self, app):
            # Given
            user = create_user(email='test@email.com')

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?distance=1&keywords=funky')

            # Then
            assert response.status_code == 401

        @clean_database
        def when_searching_by_keywords_and_distance_without_latitude(self, app):
            # Given
            user = create_user(email='test@email.com')

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?distance=1&keywords=funky&latitude=1.9333')

            # Then
            assert response.status_code == 401

        @clean_database
        def when_searching_by_keywords_and_distance_without_longitude(self, app):
            # Given
            user = create_user(email='test@email.com')

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?distance=1&keywords=funky&longitude=45.9333')

            # Then
            assert response.status_code == 401

    class Returns200:
        def setup_method(self, method):
            self.now = datetime.utcnow()
            self.in_one_hour = self.now + timedelta(hours=1)
            self.one_day_from_now = self.now + timedelta(days=1)
            self.three_days_from_now = self.now + timedelta(days=3)
            self.three_days_and_one_hour_from_now = self.three_days_from_now + timedelta(hours=1)
            self.five_days_from_now = self.now + timedelta(days=5)
            self.ten_days_from_now = self.now + timedelta(days=10)
            self.ten_days_and_three_hours_from_now = self.ten_days_from_now + timedelta(hours=3)
            self.thirty_days_from_now = self.now + timedelta(days=30)

            self.offerer = create_offerer()
            self.venue75 = create_venue(
                self.offerer,
                name='LE GRAND REX PARIS',
                address="1 BD POISSONNIERE",
                postal_code='75002',
                city="Paris",
                departement_code='75',
                is_virtual=False,
                longitude="2.4002701",
                latitude="48.8363788",
                siret="50763357600075"
            )
            self.venue13 = create_venue(
                self.offerer,
                name='Friche La Belle de Mai',
                city="Marseille",
                departement_code='13',
                is_virtual=False,
                longitude="5.3764073",
                latitude="43.303906",
                siret="50763357600013"
            )
            self.venue973 = create_venue(
                self.offerer,
                name='Théâtre de Macouria',
                city="Cayenne",
                departement_code='973',
                is_virtual=False,
                longitude="-52.423277",
                latitude="4.9780178",
                siret="50763357600973"
            )

        @clean_database
        def when_get_recommendations_and_returns_all_includes(self, app):
            # given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Training in Modern Jazz')
            mediation = create_mediation(offer)
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(
                offer, beginning_datetime=TEN_DAYS_FROM_NOW, end_datetime=TWENTY_DAYS_FROM_NOW
            )
            PcObject.save(stock, recommendation)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(user.email) \
                .get(RECOMMENDATION_URL)

            # then
            assert response.status_code == 200
            recommendations = response.json
            recommendation = recommendations[0]
            assert 'productOrTutoIdentifier' in recommendation
            assert 'mediation' in recommendation
            assert 'thumbUrl' in recommendation['mediation']
            assert 'offer' in recommendation
            assert 'dateRange' in recommendation['offer']
            assert 'isEvent' in recommendation['offer']
            assert 'isNotBookable' in recommendation['offer']
            assert 'isFullyBooked' in recommendation['offer']
            assert 'isThing' in recommendation['offer']
            assert 'offerType' in recommendation['offer']
            assert 'product' in recommendation['offer']
            assert 'thumbUrl' in recommendation['offer']['product']
            assert 'stocks' in recommendation['offer']
            assert 'isBookable' in recommendation['offer']['stocks'][0]
            assert 'venue' in recommendation['offer']
            assert 'validationToken' not in recommendation['offer']['venue']
            assert 'managingOfferer' in recommendation['offer']['venue']
            assert 'validationToken' not in recommendation['offer']['venue']['managingOfferer']
            assert 'thumbUrl' in recommendation

        @clean_database
        def when_searching_by_keywords_with_matching_case(self, app):
            # given
            keywords_string = "Training"
            search = "keywords_string={}".format(keywords_string)
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Training in Modern Jazz')
            recommendation = create_recommendation(offer, user, search=search)
            stock = create_stock_from_offer(
                offer, beginning_datetime=TEN_DAYS_FROM_NOW, end_datetime=TWENTY_DAYS_FROM_NOW
            )
            PcObject.save(stock, recommendation)

            # when
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?keywords={}'.format(keywords_string))

            # then
            assert response.status_code == 200
            recommendations = response.json
            assert 'Training' in recommendations[0]['offer']['product']['name']
            assert recommendations[0]['search'] == search

        @clean_database
        def when_searching_by_keywords_on_unvalidated_offerer(self, app):
            # given
            keywords_string = "Training"
            search = "keywords_string={}".format(keywords_string)
            user = create_user(email='test@email.com')
            offerer = create_offerer(validation_token='ABC123')
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Training in Modern Jazz')
            recommendation = create_recommendation(offer, user, search=search)
            stock = create_stock_from_offer(offer)
            PcObject.save(stock, recommendation)

            # when
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?keywords={}'.format(keywords_string))

            # then
            assert response.status_code == 200
            assert len(response.json) == 0

        @clean_database
        def when_keywords_contains_special_char(self, app):
            # given
            user = create_user(email='test@email.com')
            offerer = create_offerer(validation_token='ABC123')
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='www.test.fr event')
            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_offer(offer)
            PcObject.save(stock, recommendation)

            # when
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?keywords=https%3A%2F%2Fwww.test.fr%2F')

            # then
            assert response.status_code == 200
            assert len(response.json) == 0

        @clean_database
        def when_searching_by_keywords_on_inactive_offerer(self, app):
            # given
            keywords_string = "Training"
            search = "keywords_string={}".format(keywords_string)
            user = create_user(email='test@email.com')
            offerer = create_offerer(is_active=False)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Training in Modern Jazz')
            recommendation = create_recommendation(offer, user, search=search)
            stock = create_stock_from_offer(offer)
            PcObject.save(stock, recommendation)

            # when
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?keywords={}'.format(keywords_string))

            # then
            assert response.status_code == 200
            assert len(response.json) == 0

        @clean_database
        def when_searching_by_keywords_containing_an_apostrophe(self, app):
            # given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name="L'histoire sans fin")
            stock = create_stock_from_offer(offer,
                                            beginning_datetime=TEN_DAYS_FROM_NOW, end_datetime=TWENTY_DAYS_FROM_NOW)
            PcObject.save(stock, user)

            # when
            response = TestClient(app.test_client()).with_auth(user.email) \
                .get(RECOMMENDATION_URL + '?keywords=l%27histoire')

            # then
            assert response.status_code == 200
            recommendations = response.json
            assert recommendations[0]['offer']['product']['name'] == "L'histoire sans fin"
            assert len(recommendations) == 1

        @clean_database
        def when_keywords_contain_single_quote(self, app):
            # given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name="Vortek's")
            stock = create_stock_from_offer(offer, beginning_datetime=TEN_DAYS_FROM_NOW,
                                            end_datetime=TWENTY_DAYS_FROM_NOW)
            PcObject.save(stock, user)

            # when
            response = TestClient(app.test_client()).with_auth(user.email) \
                .get(RECOMMENDATION_URL + '?keywords=vortek%27s')

            # then
            assert response.status_code == 200
            recommendations = response.json
            assert recommendations[0]['offer']['product']['name'] == "Vortek's"
            assert len(recommendations) == 1

        @clean_database
        def when_searching_by_keywords_with_non_matching_case(self, app):
            # given
            search = "keywords_string={}".format("rencontres")
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Rencontres avec des auteurs')
            # NOTE: we need to create event occurrence and stock because
            # GET recommendations filter offer without stock
            recommendation = create_recommendation(offer, user, search=search)
            stock = create_stock_from_offer(offer, beginning_datetime=TEN_DAYS_FROM_NOW,
                                            end_datetime=TWENTY_DAYS_FROM_NOW)
            PcObject.save(stock, recommendation)

            # when
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?keywords={}'.format("rencontres"))

            # then
            assert response.status_code == 200
            recommendations = response.json
            assert 'Rencontres' in recommendations[0]['offer']['product']['name']
            assert recommendations[0]['search'] == search

        @clean_database
        def when_searching_by_keywords_with_trailing_whitespaces(self, app):
            # given
            search = "keywords_string={}".format(" rencontres avec auteurs ")
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Rencontres avec des auteurs')
            recommendation = create_recommendation(offer, user, search=search)
            stock = create_stock_from_offer(offer, beginning_datetime=TEN_DAYS_FROM_NOW,
                                            end_datetime=TWENTY_DAYS_FROM_NOW)
            PcObject.save(stock, recommendation)

            # when
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?keywords={}'.format(" rencontres avec auteurs "))

            # then
            assert response.status_code == 200
            recommendations = response.json
            assert 'Rencontres' in recommendations[0]['offer']['product']['name']

        @clean_database
        def when_searching_by_keywords_with_partial_keyword(self, app):
            # given
            search = "keywords_string={}".format("rencon")
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Rencontres avec des auteurs')
            recommendation = create_recommendation(offer, user, search=search)
            stock = create_stock_from_offer(offer, beginning_datetime=TEN_DAYS_FROM_NOW,
                                            end_datetime=TWENTY_DAYS_FROM_NOW)
            PcObject.save(stock, recommendation)

            # when
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?keywords={}'.format("rencon"))

            # then
            assert response.status_code == 200
            recommendations = response.json
            assert 'Rencontres' in recommendations[0]['offer']['product']['name']
            assert recommendations[0]['search'] == search

        @clean_database
        def when_searching_by_keywords_ignores_soft_deleted_stocks(self, app):
            # given
            search = 'keywords={}'.format('rencontres')
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer1 = create_offer_with_event_product(venue, event_name='Rencontres avec des peintres')
            offer2 = create_offer_with_event_product(venue, event_name='Rencontres avec des auteurs')
            recommendation1 = create_recommendation(offer1, user, search=search)
            recommendation2 = create_recommendation(offer2, user, search=search)

            # NOTE: we need to create event occurrence and stock because
            # GET recommendations filter offer without stock
            event_occurrence1 = create_event_occurrence(offer1)
            event_occurrence2 = create_event_occurrence(offer1)
            event_occurrence3 = create_event_occurrence(offer2)

            stock1 = create_stock_from_event_occurrence(event_occurrence1, price=10, soft_deleted=False)
            stock2 = create_stock_from_event_occurrence(event_occurrence2, price=20, soft_deleted=True)
            stock3 = create_stock_from_event_occurrence(event_occurrence3, price=30, soft_deleted=True)

            PcObject.save(stock1, stock2, stock3, recommendation1, recommendation2)

            # when
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?keywords={}'.format('rencontres'))

            # then
            assert response.status_code == 200
            assert len(response.json) == 1

        @clean_database
        def when_searching_by_type_with_two_types(self, app):
            # given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer1 = create_offer_with_event_product(venue, event_name='Training in Modern Jazz')
            offer2 = create_offer_with_event_product(venue, event_name='Training in Modern Jazz',
                                                     event_type=EventType.CINEMA)
            recommendation = create_recommendation(offer1, user)
            recommendation2 = create_recommendation(offer2, user)
            stock = create_stock_from_offer(offer1, beginning_datetime=TEN_DAYS_FROM_NOW,
                                            end_datetime=TWENTY_DAYS_FROM_NOW)
            stock2 = create_stock_from_offer(offer2, beginning_datetime=TEN_DAYS_FROM_NOW,
                                             end_datetime=TWENTY_DAYS_FROM_NOW)
            PcObject.save(stock, recommendation, stock2, recommendation2)

            # when
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?categories=Applaudir%2CRegarder')

            # then
            assert response.status_code == 200
            assert len(response.json) == 2

        @clean_database
        def when_searching_by_type_with_all_types(self, app):
            # given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer1 = create_offer_with_event_product(venue, event_name='Training in Modern Jazz')
            offer2 = create_offer_with_event_product(venue, event_name='Training in Modern Jazz',
                                                     event_type=EventType.CINEMA)
            offer3 = create_offer_with_event_product(venue, event_name='Training in Modern Jazz',
                                                     event_type=EventType.SPECTACLE_VIVANT)
            recommendation = create_recommendation(offer1, user)
            recommendation2 = create_recommendation(offer2, user)
            recommendation3 = create_recommendation(offer3, user)
            stock = create_stock_from_offer(offer1,
                                            beginning_datetime=TEN_DAYS_FROM_NOW, end_datetime=TWENTY_DAYS_FROM_NOW)
            stock2 = create_stock_from_offer(offer2,
                                             beginning_datetime=TEN_DAYS_FROM_NOW, end_datetime=TWENTY_DAYS_FROM_NOW)
            stock3 = create_stock_from_offer(offer3,
                                             beginning_datetime=TEN_DAYS_FROM_NOW, end_datetime=TWENTY_DAYS_FROM_NOW)
            PcObject.save(stock, recommendation, stock2, recommendation2, stock3, recommendation3)

            # when
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?categories=%25C3%2589couter%2CApplaudir%2CJouer%2CLire%2CPratiquer%2CRegarder%2CRencontrer'
            )

            # then
            assert response.status_code == 200
            assert len(response.json) == 3

        @clean_database
        def when_searching_by_date_and_date_range(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Training in Modern Jazz')

            event_occurrence = create_event_occurrence(
                offer, beginning_datetime=self.three_days_from_now, end_datetime=self.three_days_and_one_hour_from_now
            )

            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_event_occurrence(event_occurrence)
            PcObject.save(stock, recommendation)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?date=%s&days=1-5' % strftime(self.now))

            # Then
            recommendations = response.json
            assert response.status_code == 200
            assert recommendations[0]['offer']['dateRange'] == [
                strftime(self.three_days_from_now), strftime(self.three_days_and_one_hour_from_now)
            ]
            assert len(response.json) == 1

        @clean_database
        def when_searching_by_date_and_date_range_and_type(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='The new film', event_type=EventType.CINEMA)
            offer2 = create_offer_with_event_product(venue, event_name='Spectacle',
                                                     event_type=EventType.SPECTACLE_VIVANT)
            thing_product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)

            thing_offer = create_offer_with_thing_product(venue, thing_product)

            event_occurrence = create_event_occurrence(offer, beginning_datetime=self.three_days_from_now,
                                                       end_datetime=self.three_days_and_one_hour_from_now)

            recommendation = create_recommendation(offer, user)
            recommendation2 = create_recommendation(thing_offer, user)
            recommendation3 = create_recommendation(offer2, user)
            stock = create_stock_from_event_occurrence(event_occurrence)
            stock1 = create_stock_from_offer(offer2)
            thing_stock = create_stock(price=12, available=5, offer=thing_offer)
            PcObject.save(stock, recommendation, recommendation2, recommendation3, thing_stock, stock1)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?categories=Lire%2CRegarder' + '&date=%s&days=1-5' % strftime(self.now)
            )

            # Then
            assert response.status_code == 200
            recommendations = response.json
            assert len(recommendations) == 2

            recommendation_names = [recommendation['offer']['product']['name']
                                    for recommendation in recommendations]
            assert 'The new film' in recommendation_names
            assert 'Lire un livre' in recommendation_names

            assert 'Spectacle' not in recommendation_names

        @clean_database
        def when_searching_by_keywords_and_date(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Training in Modern Jazz',
                                                    event_type=EventType.CINEMA)

            event_occurrence = create_event_occurrence(offer, beginning_datetime=self.ten_days_from_now,
                                                       end_datetime=self.ten_days_and_three_hours_from_now)

            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_event_occurrence(event_occurrence)
            PcObject.save(stock, recommendation)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?date=%s&keywords=Jazz' % strftime(self.ten_days_from_now)
            )

            # Then
            assert response.status_code == 200
            assert len(response.json) == 1

        @clean_database
        def when_searching_by_keywords_and_distance_and_latitude_longitude(self, app):
            # Given
            user = create_user(email='test@email.com')

            concert_offer13 = create_offer_with_event_product(self.venue13, event_name='Funky Concert de Gael Faye',
                                                              event_type=EventType.MUSIQUE)
            concert_offer75 = create_offer_with_event_product(self.venue75, event_name='Funky Concert de Gael Faye',
                                                              event_type=EventType.MUSIQUE)
            concert_offer973 = create_offer_with_event_product(self.venue973, event_name='Kiwi',
                                                               event_type=EventType.MUSIQUE)

            event_occurrence13 = create_event_occurrence(concert_offer13, beginning_datetime=self.in_one_hour,
                                                         end_datetime=self.ten_days_from_now)
            event_occurrence75 = create_event_occurrence(concert_offer75, beginning_datetime=self.in_one_hour,
                                                         end_datetime=self.ten_days_from_now)
            event_occurrence973 = create_event_occurrence(concert_offer973, beginning_datetime=self.in_one_hour,
                                                          end_datetime=self.ten_days_from_now)

            recommendation13 = create_recommendation(concert_offer13, user)
            recommendation75 = create_recommendation(concert_offer75, user)
            recommendation973 = create_recommendation(concert_offer973, user)

            stock13 = create_stock_from_event_occurrence(event_occurrence13)
            stock75 = create_stock_from_event_occurrence(event_occurrence75)
            stock973 = create_stock_from_event_occurrence(event_occurrence973)

            PcObject.save(stock13, recommendation13, stock75, recommendation75, stock973, recommendation973)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?distance=20000&keywords=Macouria&latitude=48.8363788&longitude=2.4002701')

            # Then
            assert response.status_code == 200
            offers = response.json
            assert len(offers) == 1
            assert 'Kiwi' in offers[0]['offer']['product']['name']

        @clean_database
        def when_searching_by_non_matching_date_range(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Training in Modern Jazz')

            event_occurrence = create_event_occurrence(offer, beginning_datetime=self.three_days_from_now,
                                                       end_datetime=self.three_days_and_one_hour_from_now)

            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_event_occurrence(event_occurrence)
            PcObject.save(stock, recommendation)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?date=%s&days=1-5' % strftime(self.ten_days_from_now))

            # Then
            assert response.status_code == 200
            assert len(response.json) == 0

        @clean_database
        def when_searching_by_type_including_activation_type(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='The new film', event_type=EventType.CINEMA)
            offer1 = create_offer_with_event_product(venue, event_name='Activation de votre Pass Culture',
                                                     event_type=EventType.ACTIVATION)
            event_occurrence = create_event_occurrence(offer, beginning_datetime=self.in_one_hour,
                                                       end_datetime=self.one_day_from_now)

            recommendation = create_recommendation(offer, user)
            recommendation1 = create_recommendation(offer1, user)
            stock = create_stock_from_event_occurrence(event_occurrence)
            stock1 = create_stock_from_offer(offer1, beginning_datetime=TEN_DAYS_FROM_NOW,
                                             end_datetime=TWENTY_DAYS_FROM_NOW)
            PcObject.save(stock, stock1, recommendation, recommendation1)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?categories=Activation%2CLire%2CRegarder')

            # Then
            assert response.status_code == 200
            assert len(response.json) == 2
            recommendations = response.json
            assert set([r['offer']['product']['name'] for r in recommendations]) == \
                   {'The new film', 'Activation de votre Pass Culture'}

        @clean_database
        def when_searching_by_date_and_type_activation(
                self, app):
            # Given
            category_and_date_search = "categories=Lire%2CRegarder%2CActivation&date=" + strftime(
                self.now) + "&days=1-5"
            user = create_user(email='test@email.com')

            offerer = create_offerer()
            venue = create_venue(offerer)

            cinema_event_offer = create_offer_with_event_product(venue, event_name='The new film',
                                                                 event_type=EventType.CINEMA)

            activation_event_offer = create_offer_with_event_product(venue,
                                                                     event_name='Activation de votre Pass Culture',
                                                                     event_type=EventType.ACTIVATION)

            book_thing = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)
            book_thing_offer = create_offer_with_thing_product(venue, book_thing)
            cinema_event_occurrence = create_event_occurrence(cinema_event_offer,
                                                              beginning_datetime=self.three_days_from_now,
                                                              end_datetime=self.three_days_and_one_hour_from_now)
            activation_event_occurrence = create_event_occurrence(activation_event_offer,
                                                                  beginning_datetime=self.three_days_from_now,
                                                                  end_datetime=self.three_days_and_one_hour_from_now)

            cinema_recommendation = create_recommendation(cinema_event_offer, user)
            book_recommendation = create_recommendation(book_thing_offer, user)
            activation_recommendation = create_recommendation(activation_event_offer, user)

            cinema_event_occurence_stock = create_stock_from_event_occurrence(cinema_event_occurrence)
            activation_event_occurence_stock = create_stock_from_event_occurrence(activation_event_occurrence)
            book_thing_stock = create_stock(price=12, available=5, offer=book_thing_offer)

            PcObject.save(cinema_recommendation, book_recommendation, activation_recommendation,
                          cinema_event_occurence_stock, activation_event_occurence_stock, book_thing_stock)

            # When

            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?%s' % category_and_date_search)

            # Then
            assert response.status_code == 200
            assert len(response.json) == 3
            recommendations = response.json
            recommendation_names = [recommendation['offer']['product']['name'] for recommendation in
                                    recommendations]
            assert 'Activation de votre Pass Culture' in recommendation_names

        @clean_database
        def when_searching_by_non_matching_date_and_matching_keywords(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Training in Modern Jazz',
                                                    event_type=EventType.CINEMA)

            event_occurrence = create_event_occurrence(offer, beginning_datetime=self.in_one_hour,
                                                       end_datetime=self.ten_days_from_now)

            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_event_occurrence(event_occurrence)
            PcObject.save(stock, recommendation)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?date=%s&keywords=Jazz' % strftime(self.thirty_days_from_now)
            )

            # Then
            assert response.status_code == 200
            assert len(response.json) == 0

        @clean_database
        def when_searching_by_date_and_type_and_pagination_not_in_range(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='The new film', event_type=EventType.CINEMA)
            thing_product = create_product_with_thing_type(thing_name='Lire un livre', is_national=True)

            thingOffer = create_offer_with_thing_product(venue, thing_product)

            event_occurrence = create_event_occurrence(offer, beginning_datetime=self.three_days_from_now,
                                                       end_datetime=self.three_days_and_one_hour_from_now)

            recommendation = create_recommendation(offer, user)
            recommendation2 = create_recommendation(thingOffer, user)
            stock = create_stock_from_event_occurrence(event_occurrence)
            thing_stock = create_stock(price=12, available=5, offer=thingOffer)
            PcObject.save(stock, recommendation, recommendation2, thing_stock)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?categories=Lire%2CRegarder&days=1-5&page=2' + '&date=%s' % strftime(self.now)
            )

            # Then
            assert response.status_code == 200
            assert len(response.json) == 0

        @clean_database
        def when_searching_by_not_exact_match_for_keywords_and_distance(self, app):
            # Given
            user = create_user(email='test@email.com')

            concert_offer13 = create_offer_with_event_product(self.venue13, event_name='Funky Concert de Gael Faye',
                                                              event_type=EventType.MUSIQUE)
            concert_offer75 = create_offer_with_event_product(self.venue75, event_name='Soulfull Concert de Gael Faye',
                                                              event_type=EventType.MUSIQUE)
            concert_offer973 = create_offer_with_event_product(self.venue973, event_name='Kiwi',
                                                               event_type=EventType.MUSIQUE)

            event_occurrence13 = create_event_occurrence(concert_offer13, beginning_datetime=self.in_one_hour,
                                                         end_datetime=self.ten_days_from_now)
            event_occurrence75 = create_event_occurrence(concert_offer75, beginning_datetime=self.in_one_hour,
                                                         end_datetime=self.ten_days_from_now)
            event_occurrence973 = create_event_occurrence(concert_offer973, beginning_datetime=self.in_one_hour,
                                                          end_datetime=self.ten_days_from_now)

            recommendation13 = create_recommendation(concert_offer13, user)
            recommendation75 = create_recommendation(concert_offer75, user)
            recommendation973 = create_recommendation(concert_offer973, user)

            stock13 = create_stock_from_event_occurrence(event_occurrence13)
            stock75 = create_stock_from_event_occurrence(event_occurrence75)
            stock973 = create_stock_from_event_occurrence(event_occurrence973)

            PcObject.save(stock13, recommendation13, stock75, recommendation75, stock973, recommendation973)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?distance=1&latitude=48.8363788&longitude=2.4002701&keywords=Funky'
            )

            # Then
            assert response.status_code == 200
            assert len(response.json) == 0

        @clean_database
        def when_searching_by_matching_date_and_non_matching_keywords(self, app):
            # Given
            user = create_user(email='test@email.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue, event_name='Training in Modern Jazz')

            event_occurrence = create_event_occurrence(offer, beginning_datetime=self.in_one_hour,
                                                       end_datetime=self.ten_days_from_now)

            recommendation = create_recommendation(offer, user)
            stock = create_stock_from_event_occurrence(event_occurrence)
            PcObject.save(stock, recommendation)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?date=%s&keywords=nekfeu' % strftime(self.ten_days_from_now)
            )

            # Then
            assert response.status_code == 200
            assert len(response.json) == 0

        @clean_database
        def when_searching_by_keywords_offer_with_matching_pattern_in_name_return_firsts(self, app):
            user = create_user(email='test@email.com')
            offerer = create_offerer(name='modern')
            venue1 = create_venue(offerer)
            venue2 = create_venue(offerer, name='modern', siret="12345678912365")
            offer1 = create_offer_with_event_product(venue1, event_name='Modern Tango')
            offer2 = create_offer_with_event_product(venue1, event_name='Training in Modern Jazz')
            offer3 = create_offer_with_event_product(venue1, event_name='Training',
                                                     description='Modern modern Jazz, Salsa & Co')
            offer4 = create_offer_with_event_product(venue2, event_name='modern Plus')
            offer5 = create_offer_with_event_product(venue1, event_name='Tango Plus')

            event_occurrence1 = create_event_occurrence(offer1, beginning_datetime=self.in_one_hour,
                                                        end_datetime=self.ten_days_from_now)
            event_occurrence2 = create_event_occurrence(offer2, beginning_datetime=self.in_one_hour,
                                                        end_datetime=self.ten_days_from_now)
            event_occurrence3 = create_event_occurrence(offer3, beginning_datetime=self.in_one_hour,
                                                        end_datetime=self.ten_days_from_now)
            event_occurrence4 = create_event_occurrence(offer4, beginning_datetime=self.in_one_hour,
                                                        end_datetime=self.ten_days_from_now)
            event_occurrence5 = create_event_occurrence(offer5, beginning_datetime=self.in_one_hour,
                                                        end_datetime=self.ten_days_from_now)

            stock1 = create_stock_from_event_occurrence(event_occurrence1)
            stock2 = create_stock_from_event_occurrence(event_occurrence2)
            stock3 = create_stock_from_event_occurrence(event_occurrence3)
            stock4 = create_stock_from_event_occurrence(event_occurrence4)
            stock5 = create_stock_from_event_occurrence(event_occurrence5)
            PcObject.save(stock1, stock2, stock3, stock4, stock5, user)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?keywords=modern'
            )

            # Then
            assert response.status_code == 200
            assert len(response.json) == 5
            assert response.json[0]['offer']['name'] == 'Training in Modern Jazz'
            assert response.json[1]['offer']['name'] == 'modern Plus'
            assert response.json[2]['offer']['name'] == 'Modern Tango'
            assert response.json[3]['offer']['name'] == 'Training'
            assert response.json[4]['offer']['name'] == 'Tango Plus'

        @clean_database
        def when_searching_by_keywords_offer_with_search_feature_deactivated(self, app):
            deactivate_feature(FeatureToggle.FULL_OFFERS_SEARCH_WITH_OFFERER_AND_VENUE)
            user = create_user(email='test@email.com')
            offerer = create_offerer(name='modern')
            venue1 = create_venue(offerer)
            venue2 = create_venue(offerer, name='modern', siret="12345678912365")
            offer1 = create_offer_with_event_product(venue1, event_name='modern Tango')
            offer2 = create_offer_with_event_product(venue1, event_name='Training in Modern Jazz')
            offer3 = create_offer_with_event_product(venue1, event_name='Training',
                                                     description='Modern modern Jazz, Salsa & Co')
            offer4 = create_offer_with_event_product(venue2, event_name='Salsa Plus')
            offer5 = create_offer_with_event_product(venue1, event_name='Tango Plus')

            event_occurrence1 = create_event_occurrence(offer1, beginning_datetime=self.in_one_hour,
                                                        end_datetime=self.ten_days_from_now)
            event_occurrence2 = create_event_occurrence(offer2, beginning_datetime=self.in_one_hour,
                                                        end_datetime=self.ten_days_from_now)
            event_occurrence3 = create_event_occurrence(offer3, beginning_datetime=self.in_one_hour,
                                                        end_datetime=self.ten_days_from_now)
            event_occurrence4 = create_event_occurrence(offer4, beginning_datetime=self.in_one_hour,
                                                        end_datetime=self.ten_days_from_now)
            event_occurrence5 = create_event_occurrence(offer5, beginning_datetime=self.in_one_hour,
                                                        end_datetime=self.ten_days_from_now)

            stock1 = create_stock_from_event_occurrence(event_occurrence1)
            stock2 = create_stock_from_event_occurrence(event_occurrence2)
            stock3 = create_stock_from_event_occurrence(event_occurrence3)
            stock4 = create_stock_from_event_occurrence(event_occurrence4)
            stock5 = create_stock_from_event_occurrence(event_occurrence5)
            PcObject.save(stock1, stock2, stock3, stock4, stock5, user)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).get(
                RECOMMENDATION_URL + '?keywords=modern'
            )

            # Then
            assert response.status_code == 200
            assert len(response.json) == 3
