from datetime import date
from datetime import datetime

from freezegun import freeze_time
import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.offers import factories as offers_factories
from pcapi.core.testing import override_features
from pcapi.core.users import exceptions
from pcapi.core.users import factories
from pcapi.core.users import repository
from pcapi.domain.favorite.favorite import FavoriteDomain
from pcapi.models import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import ImportStatus


class CheckUserAndCredentialsTest:
    def test_unknown_user(self):
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(None, "doe")

    def test_user_with_invalid_password(self):
        user = factories.UserFactory.build(isActive=True)
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(user, "123")

    def test_inactive_user_with_invalid_password(self):
        user = factories.UserFactory.build(isActive=False)
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(user, "123")

    def test_user_pending_validation_wrong_password(self):
        user = factories.UserFactory.build(isActive=True, validationToken="123")
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(user, "doe")

    def test_user_pending_email_validation_wrong_password(self):
        user = factories.UserFactory.build(isActive=True, isEmailValidated=False)
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(user, "doe")

    def test_with_inactive_user(self):
        user = factories.UserFactory.build(isActive=False)
        with pytest.raises(exceptions.InvalidIdentifier):
            repository.check_user_and_credentials(user, factories.DEFAULT_PASSWORD)

    def test_user_pending_validation(self):
        user = factories.UserFactory.build(isActive=True, validationToken="123")
        with pytest.raises(exceptions.UnvalidatedAccount):
            repository.check_user_and_credentials(user, factories.DEFAULT_PASSWORD)

    def test_user_pending_email_validation(self):
        user = factories.UserFactory.build(isActive=True, isEmailValidated=False)
        with pytest.raises(exceptions.UnvalidatedAccount):
            repository.check_user_and_credentials(user, factories.DEFAULT_PASSWORD)

    def test_user_with_valid_password(self):
        user = factories.UserFactory.build(isActive=True)
        repository.check_user_and_credentials(user, factories.DEFAULT_PASSWORD)


@pytest.mark.usefixtures("db_session")
class GetNewlyEligibleUsersTest:
    @override_features(WHOLE_FRANCE_OPENING=False)
    @freeze_time("2018-01-01 ")
    def test_eligible_user_before_opening(self):
        user_already_18 = factories.UserFactory(
            isBeneficiary=False,
            dateOfBirth=datetime(1999, 12, 31),
            dateCreated=datetime(2017, 12, 1),
            departementCode="93",
        )
        user_just_18_in_eligible_area = factories.UserFactory(
            isBeneficiary=False,
            dateOfBirth=datetime(2000, 1, 1),
            dateCreated=datetime(2017, 12, 31),
            departementCode="93",
        )
        # Same as above in a non eligible area
        factories.UserFactory(
            isBeneficiary=False,
            dateOfBirth=datetime(2000, 1, 1),
            dateCreated=datetime(2017, 12, 1),
            departementCode="92",
        )
        # Possible beneficiary that registered too late
        factories.UserFactory(
            isBeneficiary=False,
            dateOfBirth=datetime(2000, 1, 1),
            dateCreated=datetime(2018, 1, 1),
            departementCode="93",
        )
        # Admin
        factories.UserFactory(
            isBeneficiary=False,
            dateOfBirth=datetime(2000, 1, 1),
            dateCreated=datetime(2018, 1, 1),
            isAdmin=True,
            departementCode="93",
        )
        # Pro
        pro_user = factories.UserFactory(
            isBeneficiary=False,
            dateOfBirth=datetime(2000, 1, 1),
            dateCreated=datetime(2018, 1, 1),
            departementCode="93",
        )
        offers_factories.UserOffererFactory(user=pro_user)
        # User not yet 18
        factories.UserFactory(
            isBeneficiary=False,
            dateOfBirth=datetime(2000, 1, 2),
            dateCreated=datetime(2017, 12, 1),
            departementCode="93",
        )

        # Users 18 on the day `since` should not appear, nor those that are not 18 yet
        users = repository.get_newly_eligible_users(since=date(2017, 12, 31))
        assert set(users) == {user_just_18_in_eligible_area}
        users = repository.get_newly_eligible_users(since=date(2017, 12, 30))
        assert set(users) == {user_just_18_in_eligible_area, user_already_18}

    @override_features(WHOLE_FRANCE_OPENING=True)
    @freeze_time("2018-01-01 ")
    def test_eligible_user_after_opening(self):
        user_already_18 = factories.UserFactory(
            isBeneficiary=False, dateOfBirth=datetime(1999, 12, 31), dateCreated=datetime(2017, 12, 1)
        )
        user_just_18_in_eligible_area = factories.UserFactory(
            isBeneficiary=False,
            dateOfBirth=datetime(2000, 1, 1),
            dateCreated=datetime(2017, 12, 31),
            departementCode="93",
        )
        user_just_18_in_ineligible_area = factories.UserFactory(
            isBeneficiary=False,
            dateOfBirth=datetime(2000, 1, 1),
            dateCreated=datetime(2017, 12, 1),
            departementCode="92",
        )
        # Possible beneficiary that registered too late
        factories.UserFactory(isBeneficiary=False, dateOfBirth=datetime(2000, 1, 1), dateCreated=datetime(2018, 1, 1))
        # Admin
        factories.UserFactory(
            isBeneficiary=False, dateOfBirth=datetime(2000, 1, 1), dateCreated=datetime(2018, 1, 1), isAdmin=True
        )
        # Pro
        pro_user = factories.UserFactory(
            isBeneficiary=False, dateOfBirth=datetime(2000, 1, 1), dateCreated=datetime(2018, 1, 1)
        )
        offers_factories.UserOffererFactory(user=pro_user)
        # User not yet 18
        factories.UserFactory(isBeneficiary=False, dateOfBirth=datetime(2000, 1, 2), dateCreated=datetime(2017, 12, 1))

        # Users 18 on the day `since` should not appear, nor those that are not 18 yet
        users = repository.get_newly_eligible_users(since=date(2017, 12, 31))
        assert set(users) == {user_just_18_in_eligible_area, user_just_18_in_ineligible_area}
        users = repository.get_newly_eligible_users(since=date(2017, 12, 30))
        assert set(users) == {user_just_18_in_eligible_area, user_just_18_in_ineligible_area, user_already_18}


class FindByBeneficiaryTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_a_list_of_beneficiary_favorites(self, app):
        # given
        beneficiary = factories.UserFactory()
        venue = offers_factories.VenueFactory()
        offer_1 = offers_factories.ThingOfferFactory(venue=venue)
        mediation_1 = offers_factories.MediationFactory(offer=offer_1)
        factories.FavoriteFactory(mediation=mediation_1, offer=offer_1, user=beneficiary)
        offer_2 = offers_factories.ThingOfferFactory(venue=venue)
        factories.FavoriteFactory(offer=offer_2, user=beneficiary)

        # when
        favorites = repository.find_favorites_domain_by_beneficiary(beneficiary.id)

        # then
        assert len(favorites) == 2
        assert isinstance(favorites[0], FavoriteDomain)
        assert isinstance(favorites[1], FavoriteDomain)

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_favorites_of_other_beneficiary(self, app):
        # given
        beneficiary = factories.UserFactory()
        other_beneficiary = factories.UserFactory()
        offer = offers_factories.ThingOfferFactory()
        mediation = offers_factories.MediationFactory(offer=offer)
        factories.FavoriteFactory(mediation=mediation, offer=offer, user=other_beneficiary)

        # when
        favorites = repository.find_favorites_domain_by_beneficiary(beneficiary.id)

        # then
        assert len(favorites) == 0

    @pytest.mark.usefixtures("db_session")
    def test_should_return_booking_when_favorite_offer_is_booked(self, app):
        # given
        beneficiary = factories.UserFactory()
        venue = offers_factories.VenueFactory()
        offer = offers_factories.ThingOfferFactory(venue=venue)
        stock = offers_factories.StockFactory(offer=offer, price=0)
        booking = bookings_factories.BookingFactory(stock=stock, user=beneficiary)
        mediation = offers_factories.MediationFactory(offer=offer)
        favorite = factories.FavoriteFactory(mediation=mediation, offer=offer, user=beneficiary)

        # when
        favorites = repository.find_favorites_domain_by_beneficiary(beneficiary.id)

        # then
        assert len(favorites) == 1
        favorite = favorites[0]
        assert favorite.is_booked is True
        assert favorite.booking_identifier == booking.id
        assert favorite.booked_stock_identifier == stock.id
        assert favorite.booking_quantity == booking.quantity

    @pytest.mark.usefixtures("db_session")
    def test_should_not_return_booking_when_favorite_offer_booking_is_cancelled(self, app):
        # given
        beneficiary = factories.UserFactory()
        venue = offers_factories.VenueFactory()
        offer = offers_factories.ThingOfferFactory(venue=venue)
        stock = offers_factories.StockFactory(offer=offer, price=0)
        bookings_factories.BookingFactory(
            stock=stock,
            user=beneficiary,
            isCancelled=True,
            status=BookingStatus.CANCELLED,
            cancellationDate=datetime.now(),
        )
        mediation = offers_factories.MediationFactory(offer=offer)
        favorite = factories.FavoriteFactory(mediation=mediation, offer=offer, user=beneficiary)

        # when
        favorites = repository.find_favorites_domain_by_beneficiary(beneficiary.id)

        # then
        assert len(favorites) == 1
        favorite = favorites[0]
        assert favorite.is_booked is False


@pytest.mark.usefixtures("db_session")
class UserBeneficiaryImportTest:
    def test_get_beneficiary_import_for_beneficiary(self):
        """Create 'BeneficiaryImport's with different statuses and check that
        the last one created is the one returned.
        """
        user = factories.UserFactory()

        source = BeneficiaryImportSources.demarches_simplifiees.value
        for rejected_import in factories.BeneficiaryImportFactory.create_batch(3, beneficiary=user, source=source):
            factories.BeneficiaryImportStatusFactory(beneficiaryImport=rejected_import, status=ImportStatus.REJECTED)

        # The created status is set to a random datetime in the past (yesterday at most)
        created_import = factories.BeneficiaryImportFactory(beneficiary=user)
        factories.BeneficiaryImportStatusFactory(beneficiaryImport=created_import, status=ImportStatus.CREATED)

        latest_created_import = factories.BeneficiaryImportFactory(beneficiary=user)
        latest_created_import.setStatus(ImportStatus.CREATED)

        beneficiary_import = repository.get_beneficiary_import_for_beneficiary(user)
        assert beneficiary_import.id == latest_created_import.id
