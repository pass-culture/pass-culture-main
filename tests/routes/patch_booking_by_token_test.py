from datetime import datetime
from urllib.parse import urlencode

import pytest

from models import PcObject, EventType, ThingType, Deposit
from models.db import db
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_offer_with_thing_product, create_deposit, create_venue, create_offerer, \
    create_user, create_booking, create_offer_with_event_product, \
    create_event_occurrence, create_stock_from_event_occurrence, create_user_offerer
from tests.test_utils import create_stock_with_event_offer
from utils.human_ids import humanize


@pytest.mark.standalone
class PatchBookingAsAnonymousUserTest:
    @clean_database
    def test_with_token_and_valid_email_and_offer_id_returns_204_and_sets_booking_is_used(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.save(booking)
        url = API_URL + '/bookings/token/{}?email={}&offer_id={}'.format(booking.token, user.email,
                                                                         humanize(stock.resolvedOffer.id))

        # When
        response = TestClient().patch(url)

        # Then
        assert response.status_code == 204
        db.session.refresh(booking)
        assert booking.isUsed is True

    @clean_database
    def test_patch_booking_with_token_and_offer_id_without_email_returns_400(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.save(booking)
        url = API_URL + '/bookings/token/{}?&offer_id={}'.format(booking.token, humanize(stock.resolvedOffer.id))

        # When
        response = TestClient().patch(url)

        # Then
        assert response.status_code == 400
        assert response.json()['email'] == [
            "L'adresse email qui a servie à la réservation est obligatoire dans l'URL [?email=<email>]"]

    @clean_database
    def test_patch_booking_with_token_and_email_without_offer_id_returns_400(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.save(booking)
        url = API_URL + '/bookings/token/{}?email={}'.format(booking.token, user.email)

        # When
        response = TestClient().patch(url)

        # Then
        assert response.status_code == 400
        assert response.json()['offer_id'] == ["L'id de l'offre réservée est obligatoire dans l'URL [?offer_id=<id>]"]

    @clean_database
    def test_patch_booking_with_token_without_offer_id_and_without_email_returns_400_with_both_errors(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.save(booking)
        url = API_URL + '/bookings/token/{}'.format(booking.token, user.email)

        # When
        response = TestClient().patch(url)

        # Then
        assert response.status_code == 400
        assert response.json()['offer_id'] == ["L'id de l'offre réservée est obligatoire dans l'URL [?offer_id=<id>]"]
        assert response.json()['email'] == [
            "L'adresse email qui a servie à la réservation est obligatoire dans l'URL [?email=<email>]"]

    @clean_database
    def test_patch_booking_with_token_returns_404_if_booking_missing(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.save(booking)
        url = API_URL + '/bookings/token/{}?email={}&offer_id={}'.format(booking.token, 'wrong.email@test.com',
                                                                         humanize(stock.resolvedOffer.id))

        # When
        response = TestClient().patch(url)

        # Then
        assert response.status_code == 404
        assert response.json()['global'] == ["Cette contremarque n'a pas été trouvée"]


@pytest.mark.standalone
class PatchBookingByTokenAsLoggedInUserTest:
    @clean_database
    def test_when_has_rights_returns_204_and_is_used_is_true(self, app):
        # Given
        user = create_user()
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        user_offerer = create_user_offerer(admin_user, offerer)
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.save(booking, user_offerer)
        url = API_URL + '/bookings/token/{}'.format(booking.token)

        # When
        response = TestClient().with_auth('admin@email.fr').patch(url)

        # Then
        assert response.status_code == 204
        db.session.refresh(booking)
        assert booking.isUsed == True

    @clean_database
    def test_valid_request_with_non_standard_header_returns_204_and_is_used_is_true(self, app):
        # Given
        user = create_user()
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        user_offerer = create_user_offerer(admin_user, offerer)
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.save(booking, user_offerer)
        url = API_URL + '/bookings/token/{}'.format(booking.token)

        # When
        response = TestClient().with_auth('admin@email.fr', headers={'origin': 'http://random_header.fr'}).patch(url)

        # Then
        assert response.status_code == 204
        db.session.refresh(booking)
        assert booking.isUsed == True

    @clean_database
    def test_valid_request_and_email_with_special_character_url_encoded_returns_204(self, app):
        # Given
        user = create_user(email='user+plus@email.fr')
        user_admin = create_user(email='admin@email.fr')
        offerer = create_offerer()
        user_offerer = create_user_offerer(user_admin, offerer, is_admin=True)
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue, event_name='Event Name')
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)

        PcObject.save(user_offerer, booking)
        url_email = urlencode({'email': 'user+plus@email.fr'})
        url = API_URL + '/bookings/token/{}?{}'.format(booking.token, url_email)

        # When
        response = TestClient().with_auth('admin@email.fr').patch(url)
        # Then
        assert response.status_code == 204

    @clean_database
    def test_when_user_not_editor_and_valid_email_returns_403_global_in_error_and_is_used_is_false(self, app):
        # Given
        user = create_user()
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.save(booking, admin_user)
        url = API_URL + '/bookings/token/{}?email={}'.format(booking.token, user.email)

        # When
        response = TestClient().with_auth('admin@email.fr').patch(url)

        # Then
        assert response.status_code == 403
        assert response.json()['global'] == ["Cette structure n'est pas enregistr\u00e9e chez cet utilisateur."]
        db.session.refresh(booking)
        assert booking.isUsed == False

    @clean_database
    def test_when_user_not_editor_and_invalid_email_returns_404_and_is_used_is_false(self, app):
        # Given
        user = create_user()
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.save(booking, admin_user)
        url = API_URL + '/bookings/token/{}?email={}'.format(booking.token, 'wrong@email.fr')

        # When
        response = TestClient().with_auth('admin@email.fr').patch(url)

        # Then
        assert response.status_code == 404
        db.session.refresh(booking)
        assert booking.isUsed == False

    @clean_database
    def test_email_with_special_character_not_url_encoded_returns_404(self, app):
        # Given
        user = create_user(email='user+plus@email.fr')
        user_admin = create_user(email='admin@email.fr')
        offerer = create_offerer()
        user_offerer = create_user_offerer(user_admin, offerer, is_admin=True)
        venue = create_venue(offerer)
        offer = create_offer_with_event_product(venue, event_name='Event Name')
        event_occurrence = create_event_occurrence(offer)
        stock = create_stock_from_event_occurrence(event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)

        PcObject.save(user_offerer, booking)
        url = API_URL + '/bookings/token/{}?email={}'.format(booking.token, user.email)

        # When
        response = TestClient().with_auth('admin@email.fr').patch(url)
        # Then
        assert response.status_code == 404

    @clean_database
    def test_when_user_not_editor_and_valid_email_but_invalid_offer_id_returns_404_and_is_used_false(self, app):
        # Given
        user = create_user()
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.save(booking, admin_user)
        url = API_URL + '/bookings/token/{}?email={}&offer_id={}'.format(booking.token, user.email, humanize(123))

        # When
        response = TestClient().with_auth('admin@email.fr').patch(url)

        # Then
        assert response.status_code == 404
        db.session.refresh(booking)
        assert booking.isUsed == False

    @clean_database
    def test_valid_request_when_booking_is_cancelled_returns_410_and_booking_in_error_and_is_used_is_false(self, app):
        # Given
        user = create_user()
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        user_offerer = create_user_offerer(admin_user, offerer)
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        booking.isCancelled = True
        PcObject.save(booking, user_offerer)
        url = API_URL + '/bookings/token/{}'.format(booking.token)

        # When
        response = TestClient().with_auth('admin@email.fr').patch(url)

        # Then
        assert response.status_code == 410
        assert response.json()['booking'] == ['Cette réservation a été annulée']
        db.session.refresh(booking)
        assert booking.isUsed == False

    @clean_database
    def test_valid_request_when_booking_already_validated_returns_410_and_booking_in_error_and_is_used_is_false(self,
                                                                                                                app):
        # Given
        user = create_user()
        admin_user = create_user(email='admin@email.fr')
        offerer = create_offerer()
        user_offerer = create_user_offerer(admin_user, offerer)
        venue = create_venue(offerer)
        stock = create_stock_with_event_offer(offerer, venue, price=0)
        booking = create_booking(user, stock, venue=venue)
        booking.isUsed = True
        PcObject.save(booking, user_offerer)
        url = API_URL + '/bookings/token/{}'.format(booking.token)

        # When
        response = TestClient().with_auth('admin@email.fr').patch(url)

        # Then
        assert response.status_code == 410
        assert response.json()['booking'] == ['Cette réservation a déjà été validée']
        db.session.refresh(booking)
        assert booking.isUsed == True


@pytest.mark.standalone
class PatchBookingByTokenForActivationOffersTest:
    @clean_database
    def test_when_user_patching_admin_and_activation_event_returns_status_code_204_set_can_book_free_offers_true_for_booking_user(
            self, app):
        # Given
        user = create_user(can_book_free_offers=False, is_admin=False)
        pro_user = create_user(email='pro@email.fr', can_book_free_offers=False, is_admin=True)
        offerer = create_offerer()
        user_offerer = create_user_offerer(pro_user, offerer)
        venue = create_venue(offerer)
        activation_offer = create_offer_with_event_product(venue, event_type=EventType.ACTIVATION)
        activation_event_occurrence = create_event_occurrence(activation_offer)
        stock = create_stock_from_event_occurrence(activation_event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.save(booking, user_offerer)
        url = API_URL + '/bookings/token/{}'.format(booking.token)

        # When
        response = TestClient().with_auth('pro@email.fr').patch(url)

        # Then
        db.session.refresh(user)
        assert response.status_code == 204
        assert user.canBookFreeOffers == True

    @clean_database
    def test_when_user_patching_admin_and_activation_thing_set_can_book_free_offers_true_for_booking_user(self, app):
        # Given
        user = create_user(can_book_free_offers=False, is_admin=False)
        pro_user = create_user(email='pro@email.fr', can_book_free_offers=False, is_admin=True)
        offerer = create_offerer()
        user_offerer = create_user_offerer(pro_user, offerer)
        venue = create_venue(offerer)
        activation_offer = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        activation_event_occurrence = create_event_occurrence(activation_offer)
        stock = create_stock_from_event_occurrence(activation_event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.save(booking, user_offerer)
        url = API_URL + '/bookings/token/{}'.format(booking.token)

        # When
        response = TestClient().with_auth('pro@email.fr').patch(url)

        # Then
        db.session.refresh(user)
        assert response.status_code == 204
        assert user.canBookFreeOffers == True

    @clean_database
    def test_when_user_patching_admin_and_no_deposit_for_booking_user_add_500_eur_deposit(self, app):
        # Given
        user = create_user(can_book_free_offers=False, is_admin=False)
        pro_user = create_user(email='pro@email.fr', can_book_free_offers=False, is_admin=True)
        offerer = create_offerer()
        user_offerer = create_user_offerer(pro_user, offerer)
        venue = create_venue(offerer)
        activation_offer = create_offer_with_event_product(venue, event_type=EventType.ACTIVATION)
        activation_event_occurrence = create_event_occurrence(activation_offer)
        stock = create_stock_from_event_occurrence(activation_event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.save(booking, user_offerer)
        url = API_URL + '/bookings/token/{}'.format(booking.token)

        # When
        response = TestClient().with_auth('pro@email.fr').patch(url)

        # Then
        deposits_for_user = Deposit.query.filter_by(userId=user.id).all()
        assert response.status_code == 204
        assert len(deposits_for_user) == 1
        assert deposits_for_user[0].amount == 500
        assert user.canBookFreeOffers == True

    @clean_database
    def test_when_user_patching_admin_and_deposit_for_booking_do_not_add_new_deposit_and_return_status_code_405(self,
                                                                                                                app):
        # Given
        user = create_user(can_book_free_offers=False, is_admin=False)
        pro_user = create_user(email='pro@email.fr', can_book_free_offers=False, is_admin=True)
        offerer = create_offerer()
        user_offerer = create_user_offerer(pro_user, offerer)
        venue = create_venue(offerer)
        activation_offer = create_offer_with_event_product(venue, event_type=EventType.ACTIVATION)
        activation_event_occurrence = create_event_occurrence(activation_offer)
        stock = create_stock_from_event_occurrence(activation_event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)
        deposit = create_deposit(user, datetime.utcnow(), amount=500)
        PcObject.save(booking, user_offerer, deposit)
        url = API_URL + '/bookings/token/{}'.format(booking.token)

        # When
        response = TestClient().with_auth('pro@email.fr').patch(url)

        # Then
        deposits_for_user = Deposit.query.filter_by(userId=user.id).all()
        assert response.status_code == 405
        assert len(deposits_for_user) == 1
        assert deposits_for_user[0].amount == 500

    @clean_database
    def test_when_user_patching_not_admin_status_code_403(self, app):
        # Given
        user = create_user()
        pro_user = create_user(email='pro@email.fr', is_admin=False)
        offerer = create_offerer()
        user_offerer = create_user_offerer(pro_user, offerer)
        venue = create_venue(offerer)
        activation_offer = create_offer_with_event_product(venue, event_type=EventType.ACTIVATION)
        activation_event_occurrence = create_event_occurrence(activation_offer)
        stock = create_stock_from_event_occurrence(activation_event_occurrence, price=0)
        booking = create_booking(user, stock, venue=venue)
        PcObject.save(booking, user_offerer)
        url = API_URL + '/bookings/token/{}'.format(booking.token)

        # When
        response = TestClient().with_auth('pro@email.fr').patch(url)

        # Then
        assert response.status_code == 403
