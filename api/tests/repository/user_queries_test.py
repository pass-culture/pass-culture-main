import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.repository import repository
from pcapi.repository.user_queries import find_pro_users_by_email_provider
from pcapi.repository.user_queries import get_all_users_wallet_balances


class GetAllUsersWalletBalancesTest:
    @pytest.mark.usefixtures("db_session")
    def test_users_are_sorted_by_user_id(self):
        # given
        user1 = users_factories.BeneficiaryGrant18Factory()
        user2 = users_factories.BeneficiaryGrant18Factory()

        # when
        balances = get_all_users_wallet_balances()

        # then
        assert balances.count() == 2
        assert [b.user_id for b in balances] == [user1.id, user2.id]

    @pytest.mark.usefixtures("db_session")
    def test_users_with_no_deposits_are_ignored(self):
        # given
        user1 = users_factories.BeneficiaryGrant18Factory()
        user2 = users_factories.BeneficiaryGrant18Factory()
        repository.delete(user2.deposit)

        # when
        balances = get_all_users_wallet_balances()

        # then
        assert balances.count() == 1
        assert balances[0].user_id == user1.id

    @pytest.mark.usefixtures("db_session")
    def test_returns_both_current_and_real_balances(self):
        # given
        offer = offers_factories.OfferFactory()
        stock1 = offers_factories.StockFactory(offer=offer, price=20)
        stock2 = offers_factories.StockFactory(offer=offer, price=30)
        stock3 = offers_factories.StockFactory(offer=offer, price=40)
        user = users_factories.BeneficiaryGrant18Factory(deposit__version=1)

        bookings_factories.IndividualBookingFactory(individualBooking__user=user, stock=stock1)
        bookings_factories.CancelledIndividualBookingFactory(individualBooking__user=user, stock=stock2)
        bookings_factories.UsedIndividualBookingFactory(individualBooking__user=user, stock=stock3, quantity=2)

        # when
        balances = get_all_users_wallet_balances()

        # then
        balance = balances[0]
        assert balance.current_balance == 500 - (20 + 40 * 2)
        assert balance.real_balance == 500 - (40 * 2)


class FindProUsersByEmailProviderTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_pro_users_with_matching_email_provider(self):
        pro_user_with_matching_email = users_factories.ProFactory(email="pro_user@suspect.com", isActive=True)
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro_user_with_matching_email, offerer=offerer)

        pro_user_with_not_matching_email = users_factories.ProFactory(email="pro_user@example.com", isActive=True)
        offerer2 = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro_user_with_not_matching_email, offerer=offerer2)

        users = find_pro_users_by_email_provider("suspect.com")

        assert len(users) == 1
        assert users[0] == pro_user_with_matching_email

    @pytest.mark.usefixtures("db_session")
    def test_returns_only_pro_users_with_matching_email_provider(self):
        pro_user_with_matching_email = users_factories.ProFactory(
            email="pro_user_with_matching_email@suspect.com", isActive=True
        )
        offerer = offers_factories.OffererFactory()
        offers_factories.UserOffererFactory(user=pro_user_with_matching_email, offerer=offerer)

        users_factories.UserFactory(email="not_pro_with_matching_email@suspect.com", isActive=True)

        users = find_pro_users_by_email_provider("suspect.com")

        assert len(users) == 1
        assert users[0] == pro_user_with_matching_email
