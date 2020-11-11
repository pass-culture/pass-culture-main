from datetime import datetime
from datetime import timedelta
from decimal import Decimal

import pytest

from pcapi.core.bookings.models import ActivationUser
from pcapi.domain.user_activation import generate_activation_users_csv
from pcapi.domain.user_activation import is_activation_booking
from pcapi.domain.user_activation import is_import_status_change_allowed
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_product_with_event_type
from pcapi.models import EventType
from pcapi.models import ImportStatus
from pcapi.models import ThingType
from pcapi.models import UserSQLEntity
from pcapi.scripts.beneficiary.old_remote_import import create_beneficiary_from_application


class GenerateActivationUsersCsvTest:
    def test_generate_activation_users_csv(self):
        # Given
        user1 = create_user(
            email="email1@test.com", first_name="Pedro", last_name="Gutierrez", reset_password_token="AZERTY123"
        )
        user2 = create_user(
            email="email2+alias@test.com", first_name="Pablo", last_name="Rodriguez", reset_password_token="123AZERTY"
        )
        offerer = create_offerer()
        venue = create_venue(offerer, is_virtual=True, address=None, postal_code=None, departement_code=None)
        activation_offer = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        stock = create_stock(offer=activation_offer, price=0)
        booking1 = create_booking(user=user1, stock=stock, token="abc")
        booking2 = create_booking(user=user2, stock=stock, token="def")
        bookings = [booking1, booking2]
        activation_users = map(lambda b: ActivationUser(b), bookings)

        # When
        csv = generate_activation_users_csv(activation_users)

        # Then
        csv_list_format = [row.split(",") for row in csv.split("\r\n")]
        csv_list_format = [row_list for row_list in csv_list_format if row_list[0]]
        assert csv_list_format[0] == ['"Prénom"', '"Nom"', '"Email"', '"Contremarque d\'activation"']
        assert csv_list_format[1] == ['"Pedro"', '"Gutierrez"', '"email1@test.com"', '"abc"']
        assert csv_list_format[2] == ['"Pablo"', '"Rodriguez"', '"email2+alias@test.com"', '"def"']


class IsImportStatusChangeAllowedTest:
    @pytest.mark.parametrize(
        ["new_status", "allowed"],
        [
            (ImportStatus.REJECTED, True),
            (ImportStatus.RETRY, True),
            (ImportStatus.ERROR, False),
            (ImportStatus.CREATED, False),
        ],
    )
    def test_duplicate_can_be_rejected_or_retried(self, new_status, allowed):
        assert is_import_status_change_allowed(ImportStatus.DUPLICATE, new_status) is allowed

    @pytest.mark.parametrize(
        "new_status", [ImportStatus.DUPLICATE, ImportStatus.REJECTED, ImportStatus.CREATED, ImportStatus.RETRY]
    )
    def test_error_cannot_be_changed(self, new_status):
        assert is_import_status_change_allowed(ImportStatus.ERROR, new_status) is False

    @pytest.mark.parametrize(
        "new_status", [ImportStatus.DUPLICATE, ImportStatus.REJECTED, ImportStatus.ERROR, ImportStatus.RETRY]
    )
    def test_created_cannot_be_changed(self, new_status):
        assert is_import_status_change_allowed(ImportStatus.CREATED, new_status) is False

    @pytest.mark.parametrize(
        "new_status", [ImportStatus.DUPLICATE, ImportStatus.CREATED, ImportStatus.ERROR, ImportStatus.RETRY]
    )
    def test_rejected_cannot_be_changed(self, new_status):
        assert is_import_status_change_allowed(ImportStatus.REJECTED, new_status) is False

    @pytest.mark.parametrize(
        "new_status", [ImportStatus.DUPLICATE, ImportStatus.CREATED, ImportStatus.ERROR, ImportStatus.REJECTED]
    )
    def test_retry_cannot_be_changed(self, new_status):
        assert is_import_status_change_allowed(ImportStatus.RETRY, new_status) is False


class CreateBeneficiaryFromApplicationTest:
    def test_return_newly_created_user(self):
        # given
        THIRTY_DAYS_FROM_NOW = (datetime.utcnow() + timedelta(days=30)).date()
        beneficiary_information = {
            "department": "67",
            "last_name": "Doe",
            "first_name": "Jane",
            "activity": "Lycéen",
            "civility": "Mme",
            "birth_date": datetime(2000, 5, 1),
            "email": "jane.doe@test.com",
            "phone": "0612345678",
            "postal_code": "67200",
            "application_id": 123,
        }

        # when
        beneficiary = create_beneficiary_from_application(beneficiary_information)

        # then
        assert beneficiary.lastName == "Doe"
        assert beneficiary.firstName == "Jane"
        assert beneficiary.publicName == "Jane Doe"
        assert beneficiary.email == "jane.doe@test.com"
        assert beneficiary.phoneNumber == "0612345678"
        assert beneficiary.departementCode == "67"
        assert beneficiary.postalCode == "67200"
        assert beneficiary.dateOfBirth == datetime(2000, 5, 1)
        assert beneficiary.canBookFreeOffers == True
        assert beneficiary.isAdmin == False
        assert beneficiary.password is not None
        assert beneficiary.resetPasswordToken is not None
        assert beneficiary.resetPasswordTokenValidityLimit.date() == THIRTY_DAYS_FROM_NOW
        assert beneficiary.activity == "Lycéen"
        assert beneficiary.civility == "Mme"
        assert beneficiary.hasSeenTutorials == False

    def test_a_deposit_is_made_for_the_new_beneficiary(self):
        # given
        beneficiary_information = {
            "department": "67",
            "last_name": "Doe",
            "first_name": "Jane",
            "activity": "Lycéen",
            "civility": "Mme",
            "birth_date": datetime(2000, 5, 1),
            "email": "jane.doe@test.com",
            "phone": "0612345678",
            "postal_code": "67200",
            "application_id": 123,
        }
        # when
        beneficiary = create_beneficiary_from_application(beneficiary_information)

        # then
        assert len(beneficiary.deposits) == 1
        assert beneficiary.deposits[0].amount == Decimal(500)
        assert beneficiary.deposits[0].source == "démarches simplifiées dossier [123]"


class IsActivationBookingTest:
    def test_returns_true_when_offer_is_event_type_activation(self):
        # Given
        product = create_product_with_event_type(event_type=EventType.ACTIVATION)
        offer = create_offer_with_event_product(product=product)
        stock = create_stock(offer=offer)
        booking = create_booking(user=UserSQLEntity(), stock=stock)

        # Then
        assert is_activation_booking(booking)

    def test_returns_true_when_offer_is_thing_type_activation(self):
        # Given
        product = create_product_with_event_type(event_type=ThingType.ACTIVATION)
        offer = create_offer_with_event_product(product=product)
        stock = create_stock(offer=offer)
        booking = create_booking(user=UserSQLEntity(), stock=stock)

        # Then
        assert is_activation_booking(booking)

    def test_returns_false_with_type_of_offer_is_not_an_activation(self):
        # Given
        product = create_product_with_event_type(event_type=EventType.SPECTACLE_VIVANT)
        offer = create_offer_with_event_product(product=product)
        offer.type = "EventType.SPECTACLE_VIVANT"
        stock = create_stock(offer=offer)
        booking = create_booking(user=UserSQLEntity(), stock=stock)

        # Then
        assert is_activation_booking(booking) is False
