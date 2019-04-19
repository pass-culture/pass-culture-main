from datetime import datetime
from decimal import Decimal

import pytest

from models import ApiErrors, PcObject, RightsType
from tests.conftest import clean_database
from tests.test_utils import create_user, create_offerer, create_user_offerer, create_deposit, create_booking, \
    create_stock, create_venue, create_offer_with_thing_product


@clean_database
@pytest.mark.standalone
def test_cannot_create_admin_that_can_book(app):
    # Given
    user = create_user(can_book_free_offers=True, is_admin=True)

    # When
    with pytest.raises(ApiErrors):
        PcObject.check_and_save(user)


@pytest.mark.standalone
class HasRightsTest:
    @clean_database
    def test_user_has_no_editor_right_on_offerer_if_he_is_not_attached(self, app):
        # given
        offerer = create_offerer()
        user = create_user(is_admin=False)
        PcObject.check_and_save(offerer, user)

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
        PcObject.check_and_save(user_offerer)

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
        PcObject.check_and_save(user_offerer)

        # when
        has_rights = user.hasRights(RightsType.editor, offerer.id)

        # then
        assert has_rights is False

    @clean_database
    def test_user_has_editor_right_on_offerer_if_he_is_not_attached_but_is_admin(self, app):
        # given
        offerer = create_offerer()
        user = create_user(can_book_free_offers=False, is_admin=True)
        PcObject.check_and_save(offerer, user)

        # when
        has_rights = user.hasRights(RightsType.editor, offerer.id)

        # then
        assert has_rights is True


@pytest.mark.standalone
class WalletBalanceTest:
    @clean_database
    def test_wallet_balance_is_0_with_no_deposits_and_no_bookings(self, app):
        # given
        user = create_user()
        PcObject.check_and_save(user)

        # when
        balance = user.wallet_balance

        # then
        assert balance == Decimal(0)

    @clean_database
    def test_wallet_balance_is_the_sum_of_deposits_if_no_bookings(self, app):
        # given
        user = create_user()
        deposit1 = create_deposit(user, datetime.utcnow(), amount=100)
        deposit2 = create_deposit(user, datetime.utcnow(), amount=50)
        PcObject.check_and_save(deposit1, deposit2)

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

        deposit1 = create_deposit(user, datetime.utcnow(), amount=100)
        deposit2 = create_deposit(user, datetime.utcnow(), amount=50)
        stock1 = create_stock(price=20, offer=offer)
        stock2 = create_stock(price=30, offer=offer)
        booking1 = create_booking(user, venue=venue, stock=stock1, quantity=1)
        booking2 = create_booking(user, venue=venue, stock=stock2, quantity=2)

        PcObject.check_and_save(deposit1, deposit2, booking1, booking2)

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

        deposit1 = create_deposit(user, datetime.utcnow(), amount=100)
        deposit2 = create_deposit(user, datetime.utcnow(), amount=50)
        stock1 = create_stock(price=20, offer=offer)
        stock2 = create_stock(price=30, offer=offer)
        booking1 = create_booking(user, venue=venue, stock=stock1, quantity=1, is_cancelled=False)
        booking2 = create_booking(user, venue=venue, stock=stock2, quantity=2, is_cancelled=True)

        PcObject.check_and_save(deposit1, deposit2, booking1, booking2)

        # when
        balance = user.wallet_balance

        # then
        assert balance == Decimal(130)


@pytest.mark.standalone
class RealWalletBalanceTest:
    @clean_database
    def test_real_wallet_balance_is_0_with_no_deposits_and_no_bookings(self, app):
        # given
        user = create_user()
        PcObject.check_and_save(user)

        # when
        balance = user.real_wallet_balance

        # then
        assert balance == Decimal(0)

    @clean_database
    def test_real_wallet_balance_is_the_sum_of_deposits_if_no_bookings(self, app):
        # given
        user = create_user()
        deposit1 = create_deposit(user, datetime.utcnow(), amount=100)
        deposit2 = create_deposit(user, datetime.utcnow(), amount=50)
        PcObject.check_and_save(deposit1, deposit2)

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

        deposit1 = create_deposit(user, datetime.utcnow(), amount=100)
        deposit2 = create_deposit(user, datetime.utcnow(), amount=50)
        stock1 = create_stock(price=20, offer=offer)
        stock2 = create_stock(price=30, offer=offer)
        stock3 = create_stock(price=40, offer=offer)
        booking1 = create_booking(user, venue=venue, stock=stock1, quantity=1, is_used=True)
        booking2 = create_booking(user, venue=venue, stock=stock2, quantity=2, is_used=True)
        booking3 = create_booking(user, venue=venue, stock=stock3, quantity=1, is_used=False)

        PcObject.check_and_save(deposit1, deposit2, booking1, booking2, booking3)

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

        deposit1 = create_deposit(user, datetime.utcnow(), amount=100)
        deposit2 = create_deposit(user, datetime.utcnow(), amount=50)
        stock1 = create_stock(price=20, offer=offer)
        stock2 = create_stock(price=30, offer=offer)
        stock3 = create_stock(price=40, offer=offer)
        booking1 = create_booking(user, venue=venue, stock=stock1, quantity=1, is_cancelled=True, is_used=True)
        booking2 = create_booking(user, venue=venue, stock=stock2, quantity=2, is_cancelled=False, is_used=True)
        booking3 = create_booking(user, venue=venue, stock=stock3, quantity=1, is_cancelled=False, is_used=True)

        PcObject.check_and_save(deposit1, deposit2, booking1, booking2, booking3)

        # when
        balance = user.real_wallet_balance

        # then
        assert balance == Decimal(50)
