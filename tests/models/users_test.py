from decimal import Decimal

import pytest

from models import ApiErrors, RightsType, ThingType
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_booking, create_user, create_stock, create_offerer, \
    create_venue, \
    create_deposit, create_user_offerer
from tests.model_creators.specific_creators import create_offer_with_thing_product


@clean_database
def test_cannot_create_admin_that_can_book(app):
    # Given
    user = create_user(can_book_free_offers=True, is_admin=True)

    # When
    with pytest.raises(ApiErrors):
        Repository.save(user)


class HasRightsTest:
    @clean_database
    def test_user_has_no_editor_right_on_offerer_if_he_is_not_attached(self, app):
        # given
        offerer = create_offerer()
        user = create_user(is_admin=False)
        Repository.save(offerer, user)

        # when
        has_rights = user.hasRights(RightsType.editor, offerer.id)

        # then
        assert has_rights is False

    @clean_database
    def test_user_has_editor_right_on_offerer_if_he_is_attached(self, app):
        # given
        offerer = create_offerer()
        user = create_user(is_admin=False)
        user_offerer = create_user_offerer(user, offerer)
        Repository.save(user_offerer)

        # when
        has_rights = user.hasRights(RightsType.editor, offerer.id)

        # then
        assert has_rights is True

    @clean_database
    def test_user_has_no_editor_right_on_offerer_if_he_is_attached_but_not_validated_yet(self, app):
        # given
        offerer = create_offerer()
        user = create_user(email='bobby@test.com', is_admin=False)
        user_offerer = create_user_offerer(user, offerer, validation_token='AZEFRGTHRQFQ')
        Repository.save(user_offerer)

        # when
        has_rights = user.hasRights(RightsType.editor, offerer.id)

        # then
        assert has_rights is False

    @clean_database
    def test_user_has_editor_right_on_offerer_if_he_is_not_attached_but_is_admin(self, app):
        # given
        offerer = create_offerer()
        user = create_user(can_book_free_offers=False, is_admin=True)
        Repository.save(offerer, user)

        # when
        has_rights = user.hasRights(RightsType.editor, offerer.id)

        # then
        assert has_rights is True


class WalletBalanceTest:
    @clean_database
    def test_wallet_balance_is_0_with_no_deposits_and_no_bookings(self, app):
        # given
        user = create_user()
        Repository.save(user)

        # when
        balance = user.wallet_balance

        # then
        assert balance == Decimal(0)

    @clean_database
    def test_wallet_balance_is_the_sum_of_deposits_if_no_bookings(self, app):
        # given
        user = create_user()
        deposit1 = create_deposit(user, amount=100)
        deposit2 = create_deposit(user, amount=50)
        Repository.save(deposit1, deposit2)

        # when
        balance = user.wallet_balance

        # then
        assert balance == Decimal(150)

    @clean_database
    def test_wallet_balance_is_the_sum_of_deposits_minus_the_sum_of_bookings(self, app):
        # given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)

        deposit1 = create_deposit(user, amount=100)
        deposit2 = create_deposit(user, amount=50)
        stock1 = create_stock(price=20, offer=offer)
        stock2 = create_stock(price=30, offer=offer)
        booking1 = create_booking(user=user, quantity=1, stock=stock1, venue=venue)
        booking2 = create_booking(user=user, quantity=2, stock=stock2, venue=venue)

        Repository.save(deposit1, deposit2, booking1, booking2)

        # when
        balance = user.wallet_balance

        # then
        assert balance == Decimal(70)

    @clean_database
    def test_wallet_balance_does_not_count_cancelled_bookings(self, app):
        # given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)

        deposit1 = create_deposit(user, amount=100)
        deposit2 = create_deposit(user, amount=50)
        stock1 = create_stock(price=20, offer=offer)
        stock2 = create_stock(price=30, offer=offer)
        booking1 = create_booking(user=user, is_cancelled=False, quantity=1, stock=stock1, venue=venue)
        booking2 = create_booking(user=user, is_cancelled=True, quantity=2, stock=stock2, venue=venue)

        Repository.save(deposit1, deposit2, booking1, booking2)

        # when
        balance = user.wallet_balance

        # then
        assert balance == Decimal(130)


class RealWalletBalanceTest:
    @clean_database
    def test_real_wallet_balance_is_0_with_no_deposits_and_no_bookings(self, app):
        # given
        user = create_user()
        Repository.save(user)

        # when
        balance = user.real_wallet_balance

        # then
        assert balance == Decimal(0)

    @clean_database
    def test_real_wallet_balance_is_the_sum_of_deposits_if_no_bookings(self, app):
        # given
        user = create_user()
        deposit1 = create_deposit(user, amount=100)
        deposit2 = create_deposit(user, amount=50)
        Repository.save(deposit1, deposit2)

        # when
        balance = user.real_wallet_balance

        # then
        assert balance == Decimal(150)

    @clean_database
    def test_real_wallet_balance_is_the_sum_of_deposits_minus_the_sum_of_used_bookings(self, app):
        # given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)

        deposit1 = create_deposit(user, amount=100)
        deposit2 = create_deposit(user, amount=50)
        stock1 = create_stock(price=20, offer=offer)
        stock2 = create_stock(price=30, offer=offer)
        stock3 = create_stock(price=40, offer=offer)
        booking1 = create_booking(user=user, is_used=True, quantity=1, stock=stock1, venue=venue)
        booking2 = create_booking(user=user, is_used=True, quantity=2, stock=stock2, venue=venue)
        booking3 = create_booking(user=user, is_used=False, quantity=1, stock=stock3, venue=venue)

        Repository.save(deposit1, deposit2, booking1, booking2, booking3)

        # when
        balance = user.real_wallet_balance

        # then
        assert balance == Decimal(70)

    @clean_database
    def test_real_wallet_balance_does_not_count_cancelled_bookings(self, app):
        # given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)

        deposit1 = create_deposit(user, amount=100)
        deposit2 = create_deposit(user, amount=50)
        stock1 = create_stock(price=20, offer=offer)
        stock2 = create_stock(price=30, offer=offer)
        stock3 = create_stock(price=40, offer=offer)
        booking1 = create_booking(user=user, is_cancelled=True, is_used=True, quantity=1, stock=stock1, venue=venue)
        booking2 = create_booking(user=user, is_cancelled=False, is_used=True, quantity=2, stock=stock2, venue=venue)
        booking3 = create_booking(user=user, is_cancelled=False, is_used=True, quantity=1, stock=stock3, venue=venue)

        Repository.save(deposit1, deposit2, booking1, booking2, booking3)

        # when
        balance = user.real_wallet_balance

        # then
        assert balance == Decimal(50)


class HasPhysicalVenuesTest:
    @clean_database
    def test_webapp_user_has_no_venue(self, app):
        # given
        user = create_user()

        # when
        Repository.save(user)

        # then
        assert user.hasPhysicalVenues is False

    @clean_database
    def test_pro_user_has_one_digital_venue_by_default(self, app):
        # given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        offerer_venue = create_venue(offerer, is_virtual=True, siret=None)

        # when
        Repository.save(offerer_venue, user_offerer)

        # then
        assert user.hasPhysicalVenues is False

    @clean_database
    def test_pro_user_has_one_digital_venue_and_a_physical_venue(self, app):
        # given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        offerer_virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
        offerer_physical_venue = create_venue(offerer)
        Repository.save(offerer_virtual_venue, offerer_physical_venue, user_offerer)

        # then
        assert user.hasPhysicalVenues is True

    @clean_database
    def test_pro_user_has_one_digital_venue_and_a_physical_venue(self, app):
        # given
        user = create_user()
        offerer = create_offerer()
        offerer2 = create_offerer(siren='123456788')
        user_offerer = create_user_offerer(user, offerer)
        user_offerer2 = create_user_offerer(user, offerer2)
        offerer_virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
        offerer2_physical_venue = create_venue(offerer2, siret='12345678856734')
        offerer2_virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
        Repository.save(offerer_virtual_venue, offerer2_physical_venue, user_offerer, user_offerer2)

        # then
        assert user.hasPhysicalVenues is True


class nOffersTest:
    @clean_database
    def test_webapp_user_has_no_offerers(self, app):
        # given
        user = create_user()

        Repository.save(user)

        # then
        assert user.hasOffers is False

    @clean_database
    def test_pro_user_with_offers_from_many_offerers(self, app):
        # given
        user = create_user()
        offerer = create_offerer()
        offerer2 = create_offerer(siren='123456788')
        user_offerer = create_user_offerer(user, offerer)
        user_offerer2 = create_user_offerer(user, offerer2)
        offerer_virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
        offerer2_physical_venue = create_venue(offerer2, siret='12345678856734')
        offerer2_virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
        offer = create_offer_with_thing_product(offerer_virtual_venue, thing_type=ThingType.JEUX_VIDEO_ABO, url='http://fake.url')
        offer2 = create_offer_with_thing_product(offerer2_physical_venue)

        Repository.save(offer, offer2, user_offerer, user_offerer2)

        # then
        assert user.hasOffers is True
