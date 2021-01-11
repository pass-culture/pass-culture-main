from datetime import datetime
from unittest.mock import patch

from freezegun import freeze_time
import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.payments.factories as payments_factories
from pcapi.core.users import factories
from pcapi.core.users.factories import UserFactory
from pcapi.core.users.models import check_password
from pcapi.core.users.models import hash_password
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import ApiErrors
from pcapi.models import RightsType
from pcapi.models import ThingType
from pcapi.repository import repository


@pytest.mark.usefixtures("db_session")
def test_cannot_create_admin_that_can_book(app):
    # Given
    user = create_user(is_beneficiary=True, is_admin=True)

    # When
    with pytest.raises(ApiErrors):
        repository.save(user)


class HasRightsTest:
    @pytest.mark.usefixtures("db_session")
    def test_user_has_no_editor_right_on_offerer_if_he_is_not_attached(self, app):
        # given
        offerer = create_offerer()
        user = create_user(is_admin=False)
        repository.save(offerer, user)

        # when
        has_rights = user.hasRights(RightsType.editor, offerer.id)

        # then
        assert has_rights is False

    @pytest.mark.usefixtures("db_session")
    def test_user_has_editor_right_on_offerer_if_he_is_attached(self, app):
        # given
        offerer = create_offerer()
        user = create_user(is_admin=False)
        user_offerer = create_user_offerer(user, offerer)
        repository.save(user_offerer)

        # when
        has_rights = user.hasRights(RightsType.editor, offerer.id)

        # then
        assert has_rights is True

    @pytest.mark.usefixtures("db_session")
    def test_user_has_no_editor_right_on_offerer_if_he_is_attached_but_not_validated_yet(self, app):
        # given
        offerer = create_offerer()
        user = create_user(email="bobby@test.com", is_admin=False)
        user_offerer = create_user_offerer(user, offerer, validation_token="AZEFRGTHRQFQ")
        repository.save(user_offerer)

        # when
        has_rights = user.hasRights(RightsType.editor, offerer.id)

        # then
        assert has_rights is False

    @pytest.mark.usefixtures("db_session")
    def test_user_has_editor_right_on_offerer_if_he_is_not_attached_but_is_admin(self, app):
        # given
        offerer = create_offerer()
        user = create_user(is_beneficiary=False, is_admin=True)
        repository.save(offerer, user)

        # when
        has_rights = user.hasRights(RightsType.editor, offerer.id)

        # then
        assert has_rights is True


class WalletBalanceTest:
    @pytest.mark.usefixtures("db_session")
    def test_balance_is_0_with_no_deposits_and_no_bookings(self):
        # given
        user = factories.UserFactory()
        repository.delete(user.deposits[0])

        # then
        assert user.wallet_balance == 0
        assert user.real_wallet_balance == 0

    @pytest.mark.usefixtures("db_session")
    def test_balance_is_the_sum_of_deposits_if_no_bookings(self):
        # given
        user = factories.UserFactory(deposit__version=1)
        payments_factories.DepositFactory(user=user, version=1)

        # then
        assert user.wallet_balance == 500 + 500
        assert user.real_wallet_balance == 500 + 500

    @pytest.mark.usefixtures("db_session")
    def test_balance(self):
        # given
        user = factories.UserFactory(deposit__version=1)
        bookings_factories.BookingFactory(user=user, isUsed=True, quantity=1, amount=10)
        bookings_factories.BookingFactory(user=user, isUsed=True, quantity=2, amount=20)
        bookings_factories.BookingFactory(user=user, isUsed=False, quantity=3, amount=30)
        bookings_factories.BookingFactory(user=user, isCancelled=True, quantity=4, amount=40)

        # then
        assert user.wallet_balance == 500 - (10 + 2 * 20 + 3 * 30)
        assert user.real_wallet_balance == 500 - (10 + 2 * 20)


class HasPhysicalVenuesTest:
    @pytest.mark.usefixtures("db_session")
    def test_webapp_user_has_no_venue(self, app):
        # given
        user = create_user()

        # when
        repository.save(user)

        # then
        assert user.hasPhysicalVenues is False

    @pytest.mark.usefixtures("db_session")
    def test_pro_user_has_one_digital_venue_by_default(self, app):
        # given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        offerer_venue = create_venue(offerer, is_virtual=True, siret=None)

        # when
        repository.save(offerer_venue, user_offerer)

        # then
        assert user.hasPhysicalVenues is False

    @pytest.mark.usefixtures("db_session")
    def test_pro_user_has_one_digital_venue_and_a_physical_venue(self, app):
        # given
        user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user, offerer)
        offerer_virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
        offerer_physical_venue = create_venue(offerer)
        repository.save(offerer_virtual_venue, offerer_physical_venue, user_offerer)

        # then
        assert user.hasPhysicalVenues is True


class nOffersTest:
    @pytest.mark.usefixtures("db_session")
    def test_webapp_user_has_no_offerers(self, app):
        # given
        user = create_user()

        repository.save(user)

        # then
        assert user.hasOffers is False

    @pytest.mark.usefixtures("db_session")
    def test_pro_user_with_offers_from_many_offerers(self, app):
        # given
        user = create_user()
        offerer = create_offerer()
        offerer2 = create_offerer(siren="123456788")
        user_offerer = create_user_offerer(user, offerer)
        user_offerer2 = create_user_offerer(user, offerer2)
        offerer_virtual_venue = create_venue(offerer, is_virtual=True, siret=None)
        offerer2_physical_venue = create_venue(offerer2, siret="12345678856734")
        create_venue(offerer, is_virtual=True, siret=None)
        offer = create_offer_with_thing_product(
            offerer_virtual_venue, thing_type=ThingType.JEUX_VIDEO_ABO, url="http://fake.url"
        )
        offer2 = create_offer_with_thing_product(offerer2_physical_venue)

        repository.save(offer, offer2, user_offerer, user_offerer2)

        # then
        assert user.hasOffers is True


class needsToSeeTutorialsTest:
    @pytest.mark.usefixtures("db_session")
    def test_beneficiary_has_to_see_tutorials_when_not_already_seen(self, app):
        # given
        user = create_user(is_beneficiary=True, has_seen_tutorials=False)
        # when
        repository.save(user)
        # then
        assert user.needsToSeeTutorials is True

    @pytest.mark.usefixtures("db_session")
    def test_beneficiary_has_not_to_see_tutorials_when_already_seen(self, app):
        # given
        user = create_user(is_beneficiary=True, has_seen_tutorials=True)
        # when
        repository.save(user)
        # then
        assert user.needsToSeeTutorials is False

    @pytest.mark.usefixtures("db_session")
    def test_pro_user_has_not_to_see_tutorials_when_already_seen(self, app):
        # given
        user = create_user(is_beneficiary=False)
        # when
        repository.save(user)
        # then
        assert user.needsToSeeTutorials is False


class DevEnvironmentPasswordHasherTest:
    def test_hash_password_uses_md5(self):
        hashed = hash_password("secret")
        assert hashed == b"5ebe2294ecd0e0f08eab7690d2a6ee69"

    def test_check_password(self):
        hashed = hash_password("secret")
        assert not check_password("wrong", hashed)
        assert check_password("secret", hashed)


@patch("pcapi.settings.IS_DEV", False)
class ProdEnvironmentPasswordHasherTest:
    def test_hash_password_uses_bcrypt(self):
        hashed = hash_password("secret")
        assert hashed != "secret"
        assert hashed.startswith(b"$2b$")  # bcrypt prefix

    def test_check_password(self):
        hashed = hash_password("secret")
        assert not check_password("wrong", hashed)
        assert check_password("secret", hashed)


class CalculateAgeTest:
    @freeze_time("2018-06-01")
    def test_calculate_age(self):
        assert create_user(date_of_birth=None).calculate_age() is None
        assert create_user(date_of_birth=datetime(2000, 6, 1)).calculate_age() == 18  # happy birthday
        assert create_user(date_of_birth=datetime(1999, 7, 1)).calculate_age() == 18
        assert create_user(date_of_birth=datetime(2000, 7, 1)).calculate_age() == 17
        assert create_user(date_of_birth=datetime(1999, 5, 1)).calculate_age() == 19


@pytest.mark.usefixtures("db_session")
class DepositVersionTest:
    def test_return_the_deposit(self):
        # given
        user = UserFactory(deposit__version=1)

        # then
        assert user.deposit_version == 1

    def test_when_no_deposit(self):
        # given
        user = UserFactory()
        repository.delete(*user.deposits)

        # then
        assert user.deposit_version == None
