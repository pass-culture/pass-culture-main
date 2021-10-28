from datetime import date
from datetime import datetime

from freezegun import freeze_time
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.users import exceptions
from pcapi.core.users import factories as users_factories
from pcapi.core.users import repository
from pcapi.core.users.repository import get_user_with_validated_attachment_by_offerer
from pcapi.domain.favorite.favorite import FavoriteDomain


pytestmark = pytest.mark.usefixtures("db_session")


class CheckUserAndCredentialsTest:
    def test_unknown_user(self):
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(None, "doe")

    def test_user_with_invalid_password(self):
        user = users_factories.UserFactory.build(isActive=True)
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(user, "123")

    def test_inactive_user_with_invalid_password(self):
        user = users_factories.UserFactory.build(isActive=False)
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(user, "123")

    def test_user_pending_validation_wrong_password(self):
        user = users_factories.UserFactory.build(isActive=True, validationToken="123")
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(user, "doe")

    def test_user_pending_email_validation_wrong_password(self):
        user = users_factories.UserFactory.build(isActive=True, isEmailValidated=False)
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(user, "doe")

    def test_with_inactive_user(self):
        user = users_factories.UserFactory.build(isActive=False)
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(user, users_factories.DEFAULT_PASSWORD)

    def test_user_pending_validation(self):
        user = users_factories.UserFactory.build(isActive=True, validationToken="123")
        with pytest.raises(exceptions.UnvalidatedAccount):
            repository.check_user_and_credentials(user, users_factories.DEFAULT_PASSWORD)

    def test_user_pending_email_validation(self):
        user = users_factories.UserFactory.build(isActive=True, isEmailValidated=False)
        with pytest.raises(exceptions.UnvalidatedAccount):
            repository.check_user_and_credentials(user, users_factories.DEFAULT_PASSWORD)

    def test_user_with_valid_password(self):
        user = users_factories.UserFactory.build(isActive=True)
        repository.check_user_and_credentials(user, users_factories.DEFAULT_PASSWORD)


class GetNewlyEligibleUsersTest:
    @freeze_time("2018-01-01")
    def test_eligible_user(self):
        user_already_18 = users_factories.UserFactory(
            dateOfBirth=datetime(1999, 12, 31), dateCreated=datetime(2017, 12, 1)
        )
        user_just_18_in_eligible_area = users_factories.UserFactory(
            dateOfBirth=datetime(2000, 1, 1),
            dateCreated=datetime(2017, 12, 31),
            departementCode="93",
        )
        user_just_18_in_ineligible_area = users_factories.UserFactory(
            dateOfBirth=datetime(2000, 1, 1),
            dateCreated=datetime(2017, 12, 1),
            departementCode="92",
        )
        # Possible beneficiary that registered too late
        users_factories.UserFactory(dateOfBirth=datetime(2000, 1, 1), dateCreated=datetime(2018, 1, 1))
        # Admin
        users_factories.AdminFactory(dateOfBirth=datetime(2000, 1, 1), dateCreated=datetime(2018, 1, 1))
        # Pro
        pro_user = users_factories.ProFactory(dateOfBirth=datetime(2000, 1, 1), dateCreated=datetime(2018, 1, 1))
        offers_factories.UserOffererFactory(user=pro_user)
        # User not yet 18
        users_factories.UserFactory(dateOfBirth=datetime(2000, 1, 2), dateCreated=datetime(2017, 12, 1))

        # Users 18 on the day `since` should not appear, nor those that are not 18 yet
        users = repository.get_newly_eligible_users(since=date(2017, 12, 31))
        assert set(users) == {user_just_18_in_eligible_area, user_just_18_in_ineligible_area}
        users = repository.get_newly_eligible_users(since=date(2017, 12, 30))
        assert set(users) == {user_just_18_in_eligible_area, user_just_18_in_ineligible_area, user_already_18}


class FindByBeneficiaryTest:
    def test_returns_a_list_of_beneficiary_favorites(self, app):
        # given
        beneficiary = users_factories.UserFactory()
        venue = offers_factories.VenueFactory()
        offer_1 = offers_factories.ThingOfferFactory(venue=venue)
        mediation_1 = offers_factories.MediationFactory(offer=offer_1)
        users_factories.FavoriteFactory(mediation=mediation_1, offer=offer_1, user=beneficiary)
        offer_2 = offers_factories.ThingOfferFactory(venue=venue)
        users_factories.FavoriteFactory(offer=offer_2, user=beneficiary)

        # when
        favorites = repository.find_favorites_domain_by_beneficiary(beneficiary.id)

        # then
        assert len(favorites) == 2
        assert isinstance(favorites[0], FavoriteDomain)
        assert isinstance(favorites[1], FavoriteDomain)

    def test_should_not_return_favorites_of_other_beneficiary(self, app):
        # given
        beneficiary = users_factories.UserFactory()
        other_beneficiary = users_factories.UserFactory()
        offer = offers_factories.ThingOfferFactory()
        mediation = offers_factories.MediationFactory(offer=offer)
        users_factories.FavoriteFactory(mediation=mediation, offer=offer, user=other_beneficiary)

        # when
        favorites = repository.find_favorites_domain_by_beneficiary(beneficiary.id)

        # then
        assert len(favorites) == 0

    def test_should_return_booking_when_favorite_offer_is_booked(self, app):
        # given
        beneficiary = users_factories.UserFactory()
        venue = offers_factories.VenueFactory()
        offer = offers_factories.ThingOfferFactory(venue=venue)
        stock = offers_factories.StockFactory(offer=offer, price=0)
        booking = bookings_factories.BookingFactory(stock=stock, user=beneficiary)
        mediation = offers_factories.MediationFactory(offer=offer)
        favorite = users_factories.FavoriteFactory(mediation=mediation, offer=offer, user=beneficiary)

        # when
        favorites = repository.find_favorites_domain_by_beneficiary(beneficiary.id)

        # then
        assert len(favorites) == 1
        favorite = favorites[0]
        assert favorite.is_booked is True
        assert favorite.booking_identifier == booking.id
        assert favorite.booked_stock_identifier == stock.id
        assert favorite.booking_quantity == booking.quantity

    def test_should_not_return_booking_when_favorite_offer_booking_is_cancelled(self, app):
        # given
        beneficiary = users_factories.UserFactory()
        stock = offers_factories.StockFactory()
        bookings_factories.CancelledBookingFactory(
            stock=stock,
            user=beneficiary,
        )
        offer = stock.offer
        mediation = offers_factories.MediationFactory(offer=offer)
        favorite = users_factories.FavoriteFactory(mediation=mediation, offer=offer, user=beneficiary)

        # when
        favorites = repository.find_favorites_domain_by_beneficiary(beneficiary.id)

        # then
        assert len(favorites) == 1
        favorite = favorites[0]
        assert favorite.is_booked is False


class GetApplicantOfOffererUnderValidationTest:
    def test_return_user_with_validated_attachment(self):
        # Given
        applicant = users_factories.UserFactory()
        user_who_asked_for_attachment = users_factories.UserFactory()
        applied_offerer = offerers_factories.OffererFactory(validationToken="TOKEN")
        offers_factories.UserOffererFactory(offerer=applied_offerer, user=applicant)
        offers_factories.UserOffererFactory(
            offerer=applied_offerer, user=user_who_asked_for_attachment, validationToken="OTHER_TOKEN"
        )

        # When
        applicant_found = get_user_with_validated_attachment_by_offerer(applied_offerer)

        # Then
        assert applicant_found.id == applicant.id
