import pytest
from datetime import datetime, timedelta

from models import PcObject, \
    EventType
from tests.conftest import clean_database
from utils.date import strftime
from utils.test_utils import API_URL, \
    create_event_occurrence, \
    create_stock_from_event_occurrence, \
    create_event_offer, \
    create_offerer, \
    create_recommendation, \
    create_stock, \
    create_stock_from_offer, \
    create_thing, \
    create_thing_offer, \
    create_user, \
    create_venue, \
    req, \
    req_with_auth

RECOMMENDATION_URL = API_URL + '/recommendations'


@pytest.mark.standalone
class GetRecommendationsSearchTest:
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

    def test_get_recommendations_works_only_when_logged_in(self):
        # when
        url = RECOMMENDATION_URL + '?keywords=Training'
        response = req.get(url, headers={'origin': 'http://localhost:3000'})

        # then
        assert response.status_code == 401

    @clean_database
    def test_get_recommendations_returns_one_recommendation_found_from_search_with_matching_case(self, app):
        # given
        keywords_string = "Training"
        keyword_search = "keywords={}".format(keywords_string)
        search = "keywords_string={}".format(keywords_string)
        user = create_user(email='test@email.com', password='P@55w0rd')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='Training in Modern Jazz')
        recommendation = create_recommendation(offer, user, search=search)
        stock = create_stock_from_offer(offer)
        PcObject.check_and_save(stock, recommendation)
        auth_request = req_with_auth(user.email, user.clearTextPassword)

        # when
        response = auth_request.get(RECOMMENDATION_URL + '?%s' % keyword_search)

        # then
        assert response.status_code == 200
        recommendations = response.json()
        assert 'Training' in recommendations[0]['offer']['eventOrThing']['name']
        assert recommendations[0]['search'] == search

    @clean_database
    def test_get_recommendations_returns_one_recommendation_from_search_by_type(self, app):
        # given
        category_search = "categories=Applaudir"
        user = create_user(email='test@email.com', password='P@55w0rd')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='Training in Modern Jazz')
        recommendation = create_recommendation(offer, user)
        stock = create_stock_from_offer(offer)
        PcObject.check_and_save(stock, recommendation)
        auth_request = req_with_auth(user.email, user.clearTextPassword)

        # when
        response = auth_request.get(RECOMMENDATION_URL + '?%s' % category_search)

        # then
        assert response.status_code == 200
        assert len(response.json()) == 1

    @clean_database
    def test_get_recommendations_returns_one_recommendation_found_from_search_ignoring_case(self, app):
        # given
        keywords_string = "rencontres"
        keyword_search = "keywords={}".format(keywords_string)
        search = "keywords_string={}".format(keywords_string)
        user = create_user(email='test@email.com', password='P@55w0rd')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='Rencontres avec des auteurs')
        # NOTE: we need to create event occurrence and stock because
        # GET recommendations filter offer without stock
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence)
        recommendation = create_recommendation(offer, user, search=search)
        stock = create_stock_from_offer(offer)
        PcObject.check_and_save(stock, recommendation)
        auth_request = req_with_auth(user.email, user.clearTextPassword)

        # when
        response = auth_request.get(RECOMMENDATION_URL + '?%s' % keyword_search)

        # then
        assert response.status_code == 200
        recommendations = response.json()
        assert 'Rencontres' in recommendations[0]['offer']['eventOrThing']['name']
        assert recommendations[0]['search'] == search

    @clean_database
    def test_get_recommendations_with_double_and_trailing_whitespaces_returns_one_recommendation(self, app):
        # given
        keywords_string = " rencontres avec auteurs "
        keyword_search = "keywords={}".format(keywords_string)
        search = "keywords_string={}".format(keywords_string)
        user = create_user(email='test@email.com', password='P@55w0rd')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='Rencontres avec des auteurs')
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence)
        recommendation = create_recommendation(offer, user, search=search)
        stock = create_stock_from_offer(offer)
        PcObject.check_and_save(stock, recommendation)
        auth_request = req_with_auth(user.email, user.clearTextPassword)

        # when
        response = auth_request.get(RECOMMENDATION_URL + '?%s' % keyword_search)

        # then
        assert response.status_code == 200
        recommendations = response.json()
        assert 'Rencontres' in recommendations[0]['offer']['eventOrThing']['name']

    @clean_database
    def test_get_recommendations_returns_one_recommendation_found_from_partial_search(self, app):
        # given
        keywords_string = "rencon"
        keyword_search = "keywords={}".format(keywords_string)
        search = "keywords_string={}".format(keywords_string)
        user = create_user(email='test@email.com', password='P@55w0rd')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='Rencontres avec des auteurs')
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence)
        recommendation = create_recommendation(offer, user, search=search)
        stock = create_stock_from_offer(offer)
        PcObject.check_and_save(stock, recommendation)
        auth_request = req_with_auth(user.email, user.clearTextPassword)

        # when
        response = auth_request.get(RECOMMENDATION_URL + '?%s' % keyword_search)

        # then
        assert response.status_code == 200
        recommendations = response.json()
        assert 'Rencontres' in recommendations[0]['offer']['eventOrThing']['name']
        assert recommendations[0]['search'] == search

    @clean_database
    def test_get_recommendations_does_not_return_recommendations_of_offers_with_soft_deleted_stocks(self, app):
        # given
        keywords_string = 'rencontres'
        keyword_search = 'keywords={}'.format(keywords_string)
        search = 'keywords={}'.format(keywords_string)
        user = create_user(email='test@email.com', password='P@55w0rd')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_event_offer(venue, event_name='Rencontres avec des peintres')
        offer2 = create_event_offer(venue, event_name='Rencontres avec des auteurs')
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

        PcObject.check_and_save(stock1, stock2, stock3, recommendation1, recommendation2)
        auth_request = req_with_auth(user.email, user.clearTextPassword)

        # when
        response = auth_request.get(RECOMMENDATION_URL + '?%s' % keyword_search)

        # then
        assert response.status_code == 200
        assert len(response.json()) == 1

    @clean_database
    def test_get_recommendations_returns_two_recommendation_from_filter_by_two_types(self, app):
        # given
        category_search = "categories=Applaudir%2CRegarder"
        user = create_user(email='test@email.com', password='P@55w0rd')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_event_offer(venue, event_name='Training in Modern Jazz')
        offer2 = create_event_offer(venue, event_name='Training in Modern Jazz', event_type=EventType.CINEMA)
        recommendation = create_recommendation(offer1, user)
        recommendation2 = create_recommendation(offer2, user)
        stock = create_stock_from_offer(offer1)
        stock2 = create_stock_from_offer(offer2)
        PcObject.check_and_save(stock, recommendation, stock2, recommendation2)
        auth_request = req_with_auth(user.email, user.clearTextPassword)

        # when
        response = auth_request.get(RECOMMENDATION_URL + '?%s' % category_search)

        # then
        assert response.status_code == 200
        assert len(response.json()) == 2

    @clean_database
    def test_get_recommendations_returns_all_recommendations_from_filter_by_all_types(self, app):
        # given
        category_search = "categories=%25C3%2589couter%2CApplaudir%2CJouer%2CLire%2CPratiquer%2CRegarder%2CRencontrer"
        user = create_user(email='test@email.com', password='P@55w0rd')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_event_offer(venue, event_name='Training in Modern Jazz')
        offer2 = create_event_offer(venue, event_name='Training in Modern Jazz', event_type=EventType.CINEMA)
        offer3 = create_event_offer(venue, event_name='Training in Modern Jazz', event_type=EventType.SPECTACLE_VIVANT)
        recommendation = create_recommendation(offer1, user)
        recommendation2 = create_recommendation(offer2, user)
        recommendation3 = create_recommendation(offer3, user)
        stock = create_stock_from_offer(offer1)
        stock2 = create_stock_from_offer(offer2)
        stock3 = create_stock_from_offer(offer3)
        PcObject.check_and_save(stock, recommendation, stock2, recommendation2, stock3, recommendation3)
        auth_request = req_with_auth(user.email, user.clearTextPassword)

        # when
        response = auth_request.get(RECOMMENDATION_URL + '?%s' % category_search)

        # then
        assert response.status_code == 200
        assert len(response.json()) == 3

    @clean_database
    def test_get_recommendations_returns_recommendations_in_date_range_from_search_by_date(self, app):
        # Given
        date_search = "date=" + strftime(self.now) + "&days=1-5"
        user = create_user(email='test@email.com', password='P@55w0rd')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='Training in Modern Jazz')

        event_occurrence = create_event_occurrence(offer, beginning_datetime=self.three_days_from_now,
                                                   end_datetime=self.three_days_and_one_hour_from_now)

        recommendation = create_recommendation(offer, user)
        stock = create_stock_from_event_occurrence(event_occurrence)
        PcObject.check_and_save(stock, recommendation)
        auth_request = req_with_auth(user.email, user.clearTextPassword)

        # When
        response = auth_request.get(RECOMMENDATION_URL + '?%s' % date_search)

        # Then
        recommendations = response.json()
        assert response.status_code == 200
        assert recommendations[0]['offer']['dateRange'] == [strftime(self.three_days_from_now),
                                                            strftime(self.three_days_and_one_hour_from_now)]
        assert len(response.json()) == 1

    @clean_database
    def test_get_recommendations_returns_no_recommendation_when_no_stock_in_date_range(self, app):
        # Given
        date_search = "date=" + strftime(self.ten_days_from_now) + "&days=1-5"
        user = create_user(email='test@email.com', password='P@55w0rd')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='Training in Modern Jazz')

        event_occurrence = create_event_occurrence(offer, beginning_datetime=self.three_days_from_now,
                                                   end_datetime=self.three_days_and_one_hour_from_now)

        recommendation = create_recommendation(offer, user)
        stock = create_stock_from_event_occurrence(event_occurrence)
        PcObject.check_and_save(stock, recommendation)
        auth_request = req_with_auth(user.email, user.clearTextPassword)

        # When
        response = auth_request.get(RECOMMENDATION_URL + '?%s' % date_search)

        # Then
        assert response.status_code == 200
        assert len(response.json()) == 0

    @clean_database
    def test_get_recommendations_returns_two_recommendations_from_search_by_date_and_type(self, app):
        # Given
        date_and_category_search = "categories=Lire%2CRegarder&date=" + strftime(self.now) + "&days=1-5"
        user = create_user(email='test@email.com', password='P@55w0rd')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='The new film', event_type=EventType.CINEMA)
        offer2 = create_event_offer(venue, event_name='Spectacle', event_type=EventType.SPECTACLE_VIVANT)
        thing = create_thing(thing_name='Lire un livre', is_national=True)

        thingOffer = create_thing_offer(venue, thing)

        event_occurrence = create_event_occurrence(offer, beginning_datetime=self.three_days_from_now,
                                                   end_datetime=self.three_days_and_one_hour_from_now)

        recommendation = create_recommendation(offer, user)
        recommendation2 = create_recommendation(thingOffer, user)
        recommendation3 = create_recommendation(offer2, user)
        stock = create_stock_from_event_occurrence(event_occurrence)
        stock1 = create_stock_from_offer(offer2)
        thingStock = create_stock(price=12, available=5, offer=thingOffer)
        PcObject.check_and_save(stock, recommendation, recommendation2, recommendation3, thingStock, stock1)
        auth_request = req_with_auth(user.email, user.clearTextPassword)

        # When
        response = auth_request.get(RECOMMENDATION_URL + '?%s' % date_and_category_search)

        # Then
        assert response.status_code == 200
        assert len(response.json()) == 2
        recommendations = response.json()
        assert recommendations[0]['offer']['eventOrThing']['name'] == 'The new film'
        assert recommendations[1]['offer']['eventOrThing']['name'] == 'Lire un livre'

    @clean_database
    def test_get_recommendations_returns_recommendations_from_search_by_date_and_type_except_if_it_is_activation_type(
            self, app):
        # Given
        category_and_date_search = "categories=Lire%2CRegarder%2CActivation&date=" + strftime(self.now) + "&days=1-5"
        user = create_user(email='test@email.com', password='P@55w0rd')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='The new film', event_type=EventType.CINEMA)
        offer2 = create_event_offer(venue, event_name='Activation de votre Pass Culture',
                                    event_type=EventType.ACTIVATION)
        thing = create_thing(thing_name='Lire un livre', is_national=True)

        thingOffer = create_thing_offer(venue, thing)

        event_occurrence = create_event_occurrence(offer, beginning_datetime=self.three_days_from_now,
                                                   end_datetime=self.three_days_and_one_hour_from_now)

        recommendation = create_recommendation(offer, user)
        recommendation2 = create_recommendation(thingOffer, user)
        recommendation3 = create_recommendation(offer2, user)
        stock = create_stock_from_event_occurrence(event_occurrence)
        stock1 = create_stock_from_offer(offer2)
        thingStock = create_stock(price=12, available=5, offer=thingOffer)
        PcObject.check_and_save(stock, recommendation, recommendation2, recommendation3, thingStock, stock1)
        auth_request = req_with_auth(user.email, user.clearTextPassword)

        # When
        response = auth_request.get(RECOMMENDATION_URL + '?%s' % category_and_date_search)

        # Then
        assert response.status_code == 200
        assert len(response.json()) == 2
        recommendations = response.json()
        assert recommendations[0]['offer']['eventOrThing']['name'] == 'The new film'
        assert recommendations[1]['offer']['eventOrThing']['name'] == 'Lire un livre'

    @clean_database
    def test_get_recommendations_returns_recommendation_from_search_by_type_including_activation_type(self, app):
        # Given
        category_search = "categories=Activation%2CLire%2CRegarder"
        user = create_user(email='test@email.com', password='P@55w0rd')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='The new film', event_type=EventType.CINEMA)
        offer1 = create_event_offer(venue, event_name='Activation de votre Pass Culture',
                                    event_type=EventType.ACTIVATION)
        event_occurrence = create_event_occurrence(offer, beginning_datetime=self.in_one_hour,
                                                   end_datetime=self.one_day_from_now)

        recommendation = create_recommendation(offer, user)
        recommendation1 = create_recommendation(offer1, user)
        stock = create_stock_from_event_occurrence(event_occurrence)
        stock1 = create_stock_from_offer(offer1)
        PcObject.check_and_save(stock, stock1, recommendation, recommendation1)
        auth_request = req_with_auth(user.email, user.clearTextPassword)

        # When
        response = auth_request.get(RECOMMENDATION_URL + '?%s' % category_search)

        # Then
        assert response.status_code == 200
        assert len(response.json()) == 2
        recommendations = response.json()
        assert set([r['offer']['eventOrThing']['name'] for r in recommendations]) == \
               set(['The new film', 'Activation de votre Pass Culture'])

    @clean_database
    def test_get_recommendations_returns_no_recommendations_from_search_by_date_and_type_and_pagination_not_in_range(
            self, app):
        # Given
        category_and_date_search = "categories=Lire%2CRegarder&date=" + strftime(self.now) + "&days=1-5&page=2"
        user = create_user(email='test@email.com', password='P@55w0rd')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='The new film', event_type=EventType.CINEMA)
        thing = create_thing(thing_name='Lire un livre', is_national=True)

        thingOffer = create_thing_offer(venue, thing)

        event_occurrence = create_event_occurrence(offer, beginning_datetime=self.three_days_from_now,
                                                   end_datetime=self.three_days_and_one_hour_from_now)

        recommendation = create_recommendation(offer, user)
        recommendation2 = create_recommendation(thingOffer, user)
        stock = create_stock_from_event_occurrence(event_occurrence)
        thingStock = create_stock(price=12, available=5, offer=thingOffer)
        PcObject.check_and_save(stock, recommendation, recommendation2, thingStock)
        auth_request = req_with_auth(user.email, user.clearTextPassword)

        # When
        response = auth_request.get(RECOMMENDATION_URL + '?%s' % category_and_date_search)

        # Then
        assert response.status_code == 200
        assert len(response.json()) == 0

    @clean_database
    def test_get_recommendations_returns_no_recommendation_from_search_by_date_that_match_but_the_keyword_not(self,
                                                                                                              app):
        # Given
        date_and_keyword_search = "date=" + strftime(self.ten_days_from_now) + "&keywords=nekfeu"
        user = create_user(email='test@email.com', password='P@55w0rd')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='Training in Modern Jazz')

        event_occurrence = create_event_occurrence(offer, beginning_datetime=self.in_one_hour,
                                                   end_datetime=self.ten_days_from_now)

        recommendation = create_recommendation(offer, user)
        stock = create_stock_from_event_occurrence(event_occurrence)
        PcObject.check_and_save(stock, recommendation)
        auth_request = req_with_auth(user.email, user.clearTextPassword)

        # When
        response = auth_request.get(RECOMMENDATION_URL + '?%s' % date_and_keyword_search)

        # Then
        assert response.status_code == 200
        assert len(response.json()) == 0

    @clean_database
    def test_get_recommendations_returns_one_recommendation_from_search_by_date_and_keyword_that_match(self, app):
        # Given
        date_and_keyword_search = "date=" + strftime(self.ten_days_from_now) + "&keywords=Jazz"
        user = create_user(email='test@email.com', password='P@55w0rd')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='Training in Modern Jazz', event_type=EventType.CINEMA)

        event_occurrence = create_event_occurrence(offer, beginning_datetime=self.ten_days_from_now,
                                                   end_datetime=self.ten_days_and_three_hours_from_now)

        recommendation = create_recommendation(offer, user)
        stock = create_stock_from_event_occurrence(event_occurrence)
        PcObject.check_and_save(stock, recommendation)
        auth_request = req_with_auth(user.email, user.clearTextPassword)

        # When
        response = auth_request.get(RECOMMENDATION_URL + '?%s' % date_and_keyword_search)

        # Then
        assert response.status_code == 200
        assert len(response.json()) == 1

    @clean_database
    def test_get_recommendations_returns_no_recommendation_from_search_by_date_that_does_not_match_and_keyword_that_match(
            self, app):
        # Given
        date_and_keyword_search = "date=" + strftime(self.thirty_days_from_now) + "&keywords=Jazz"
        user = create_user(email='test@email.com', password='P@55w0rd')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_event_offer(venue, event_name='Training in Modern Jazz', event_type=EventType.CINEMA)

        event_occurrence = create_event_occurrence(offer, beginning_datetime=self.in_one_hour,
                                                   end_datetime=self.ten_days_from_now)

        recommendation = create_recommendation(offer, user)
        stock = create_stock_from_event_occurrence(event_occurrence)
        PcObject.check_and_save(stock, recommendation)
        auth_request = req_with_auth(user.email, user.clearTextPassword)

        # When
        response = auth_request.get(RECOMMENDATION_URL + '?%s' % date_and_keyword_search)

        # Then
        assert response.status_code == 200
        assert len(response.json()) == 0

    @clean_database
    def test_get_recommendations_returns_no_recommendation_if_not_exact_match_for_keywords_and_distance(self, app):
        # Given
        location_search = "distance=1&latitude=48.8363788&longitude=2.4002701&keywords=Funky"
        user = create_user(email='test@email.com', password='P@55w0rd')

        concert_offer13 = create_event_offer(self.venue13, event_name='Funky Concert de Gael Faye',
                                             event_type=EventType.MUSIQUE)
        concert_offer75 = create_event_offer(self.venue75, event_name='Soulfull Concert de Gael Faye',
                                             event_type=EventType.MUSIQUE)
        concert_offer973 = create_event_offer(self.venue973, event_name='Kiwi', event_type=EventType.MUSIQUE)

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

        PcObject.check_and_save(stock13, recommendation13, stock75, recommendation75, stock973, recommendation973)

        auth_request = req_with_auth(user.email, user.clearTextPassword)

        # When
        response = auth_request.get(RECOMMENDATION_URL + '?%s' % location_search)

        # Then
        assert len(response.json()) == 0

    @clean_database
    def test_get_recommendations_returns_one_recommandation_that_matches_both_keywords_and_all_distances(self, app):
        # Given
        location_search = "distance=20000&latitude=48.8363788&longitude=2.4002701&keywords=Macouria"
        user = create_user(email='test@email.com', password='P@55w0rd')

        concert_offer13 = create_event_offer(self.venue13, event_name='Funky Concert de Gael Faye',
                                             event_type=EventType.MUSIQUE)
        concert_offer75 = create_event_offer(self.venue75, event_name='Funky Concert de Gael Faye',
                                             event_type=EventType.MUSIQUE)
        concert_offer973 = create_event_offer(self.venue973, event_name='Kiwi', event_type=EventType.MUSIQUE)

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

        PcObject.check_and_save(stock13, recommendation13, stock75, recommendation75, stock973, recommendation973)

        auth_request = req_with_auth(user.email, user.clearTextPassword)

        # When
        response = auth_request.get(RECOMMENDATION_URL + '?%s' % location_search)

        # Then
        offers = response.json()
        assert len(offers) == 1
        assert 'Kiwi' in offers[0]['offer']['eventOrThing']['name']

    @clean_database
    def test_get_recommendations_returns_all_recommendations_matching_keywords_if_keywords_and_distance_are_given_but_no_latitude_and_longitude(
            self, app):
        # Given
        location_search = "distance=1&keywords=funky"
        user = create_user(email='test@email.com', password='P@55w0rd')

        concert_offer13 = create_event_offer(self.venue13, event_name='Funky Concert de Gael Faye',
                                             event_type=EventType.MUSIQUE)
        concert_offer75 = create_event_offer(self.venue75, event_name='Funky Concert de Gael Faye',
                                             event_type=EventType.MUSIQUE)
        concert_offer973 = create_event_offer(self.venue973, event_name='Kiwi', event_type=EventType.MUSIQUE)

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
        print(stock13.bookingLimitDatetime > self.now)
        print(stock75.bookingLimitDatetime > self.now)
        print(stock973.bookingLimitDatetime > self.now)

        PcObject.check_and_save(stock13, recommendation13, stock75, recommendation75, stock973, recommendation973)

        auth_request = req_with_auth(user.email, user.clearTextPassword)

        # When
        response = auth_request.get(RECOMMENDATION_URL + '?%s' % location_search)

        # Then
        assert len(response.json()) == 2
