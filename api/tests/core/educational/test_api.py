from dataclasses import asdict
import datetime
from decimal import Decimal
from unittest import mock

import dateutil
from freezegun.api import freeze_time
import pytest
from sqlalchemy import create_engine
import sqlalchemy.exc
from sqlalchemy.sql import text

from pcapi.core import search
from pcapi.core.bookings import exceptions as bookings_exceptions
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational import api as educational_api
from pcapi.core.educational import exceptions
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.educational.models import EducationalBookingStatus
from pcapi.core.educational.models import EducationalRedactor
import pcapi.core.educational.testing as adage_api_testing
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import factories as offers_factories
import pcapi.core.search.testing as search_testing
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
from pcapi.models import api_errors
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.routes.adage.v1.serialization.prebooking import serialize_educational_booking
from pcapi.routes.adage_iframe.serialization.adage_authentication import AuthenticatedInformation
from pcapi.routes.adage_iframe.serialization.adage_authentication import RedactorInformation
from pcapi.routes.serialization import stock_serialize

from tests.conftest import clean_database


SIMPLE_OFFER_VALIDATION_CONFIG = """
        minimum_score: 0.6
        rules:
            - name: "check offer name"
              factor: 0
              conditions:
               - model: "Offer"
                 attribute: "name"
                 condition:
                    operator: "contains"
                    comparated:
                      - "suspicious"
            - name: "check CollectiveOffer name"
              factor: 0
              conditions:
               - model: "CollectiveOffer"
                 attribute: "name"
                 condition:
                    operator: "contains"
                    comparated:
                      - "suspicious"
            - name: "check CollectiveOfferTemplate name"
              factor: 0
              conditions:
               - model: "CollectiveOfferTemplate"
                 attribute: "name"
                 condition:
                    operator: "contains"
                    comparated:
                      - "suspicious"
        """


@freeze_time("2020-11-17 15:00:00")
class ConfirmEducationalBookingTest:
    @clean_database
    def test_confirm_educational_booking_lock(self, app):
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_year = educational_factories.EducationalYearFactory(adageId="1")
        deposit = educational_factories.EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(1400.00),
            isFinal=True,
        )
        bookings_factories.EducationalBookingFactory(
            amount=Decimal(20.00),
            quantity=20,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            status=BookingStatus.CONFIRMED,
        )

        booking = bookings_factories.EducationalBookingFactory(
            amount=Decimal(20.00),
            quantity=20,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            status=BookingStatus.PENDING,
        )

        # open a second connection on purpose and lock the deposit
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        with engine.connect() as connection:
            connection.execute(
                text("""SELECT * FROM educational_deposit WHERE id = :educational_deposit_id FOR UPDATE"""),
                educational_deposit_id=deposit.id,
            )

            with pytest.raises(sqlalchemy.exc.OperationalError):
                educational_api.confirm_educational_booking(booking.educationalBookingId)

        refreshed_booking = Booking.query.filter(Booking.id == booking.id).one()
        assert refreshed_booking.status == BookingStatus.PENDING

    def test_confirm_educational_booking(self, db_session):
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_year = educational_factories.EducationalYearFactory(adageId="1")
        educational_factories.EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(1400.00),
            isFinal=True,
        )
        booking = bookings_factories.EducationalBookingFactory(
            amount=Decimal(20.00),
            quantity=20,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            status=BookingStatus.PENDING,
        )
        educational_api.confirm_educational_booking(booking.educationalBookingId)

        assert booking.status == BookingStatus.CONFIRMED

    def test_confirm_educational_booking_sends_email(self, db_session):
        # Given
        educational_redactor = educational_factories.EducationalRedactorFactory(
            email="professeur@example.com", firstName="Georges", lastName="Moustaki"
        )
        educational_institution = educational_factories.EducationalInstitutionFactory(
            name="Lycée du pass", city="Paris", postalCode="75018"
        )
        educational_year = educational_factories.EducationalYearFactory(adageId="1")
        educational_factories.EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(1400.00),
            isFinal=True,
        )
        booking = bookings_factories.EducationalBookingFactory(
            amount=Decimal(20.00),
            quantity=1,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            educationalBooking__educationalRedactor=educational_redactor,
            status=BookingStatus.PENDING,
            stock__offer__bookingEmail="test@email.com",
            stock__beginningDatetime=datetime.datetime(2021, 5, 15),
        )

        # When
        educational_api.confirm_educational_booking(booking.educationalBookingId)

        # Then
        assert len(mails_testing.outbox) == 1
        sent_data = mails_testing.outbox[0].sent_data
        offer = booking.stock.offer
        assert sent_data["To"] == "test@email.com"
        assert sent_data["template"] == asdict(TransactionalEmail.EAC_NEW_BOOKING_TO_PRO.value)
        assert sent_data["params"] == {
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.name,
            "EVENT_DATE": "15-May-2021",
            "EVENT_HOUR": "2h",
            "QUANTITY": 1,
            "REDACTOR_FIRSTNAME": "Georges",
            "REDACTOR_LASTNAME": "Moustaki",
            "REDACTOR_EMAIL": "professeur@example.com",
            "EDUCATIONAL_INSTITUTION_NAME": "Lycée du pass",
            "EDUCATIONAL_INSTITUTION_CITY": "Paris",
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": "75018",
            "IS_EVENT": True,
        }

    def test_raises_if_no_educational_booking(self):
        with pytest.raises(exceptions.EducationalBookingNotFound):
            educational_api.confirm_educational_booking(100)

    def test_raises_if_no_educational_deposit(self, db_session):
        booking = bookings_factories.EducationalBookingFactory(status=BookingStatus.PENDING)
        with pytest.raises(exceptions.EducationalDepositNotFound):
            educational_api.confirm_educational_booking(booking.educationalBookingId)

    def test_raises_insufficient_fund(self, db_session) -> None:
        # When
        educational_year = educational_factories.EducationalYearFactory(adageId="1")
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalDepositFactory(
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
            amount=Decimal(400.00),
            isFinal=True,
        )
        booking = bookings_factories.EducationalBookingFactory(
            educationalBooking__educationalYear=educational_year,
            educationalBooking__educationalInstitution=educational_institution,
            amount=Decimal(500.00),
            quantity=1,
            status=BookingStatus.PENDING,
        )

        # Then
        with pytest.raises(exceptions.InsufficientFund):
            educational_api.confirm_educational_booking(booking.educationalBookingId)

    def test_raises_insufficient_temporary_fund(self, db_session) -> None:
        # When
        educational_year = educational_factories.EducationalYearFactory(adageId="1")
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalDepositFactory(
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
            amount=Decimal(1000.00),
            isFinal=False,
        )
        booking = bookings_factories.EducationalBookingFactory(
            educationalBooking__educationalYear=educational_year,
            educationalBooking__educationalInstitution=educational_institution,
            amount=Decimal(900.00),
            quantity=1,
            status=BookingStatus.PENDING,
        )

        # Then
        with pytest.raises(exceptions.InsufficientTemporaryFund):
            educational_api.confirm_educational_booking(booking.educationalBookingId)

    def test_raises_educational_booking_is_refused(self, db_session) -> None:
        # Given
        booking = bookings_factories.EducationalBookingFactory(
            educationalBooking__status=EducationalBookingStatus.REFUSED,
            status=BookingStatus.CANCELLED,
        )

        # Then
        with pytest.raises(exceptions.EducationalBookingIsRefused):
            educational_api.confirm_educational_booking(booking.educationalBookingId)

    def test_raises_booking_is_cancelled(self, db_session) -> None:
        # Given
        booking = bookings_factories.EducationalBookingFactory(status=BookingStatus.CANCELLED)

        # Then
        with pytest.raises(exceptions.BookingIsCancelled):
            educational_api.confirm_educational_booking(booking.educationalBookingId)

    @freeze_time("2021-08-05 15:00:00")
    def test_raises_confirmation_limit_date_has_passed(self, db_session) -> None:
        # Given
        booking: Booking = bookings_factories.EducationalBookingFactory(
            educationalBooking__confirmationLimitDate=datetime.datetime(2021, 8, 5, 14),
            status=BookingStatus.PENDING,
        )

        # Then
        with pytest.raises(bookings_exceptions.ConfirmationLimitDateHasPassed):
            educational_api.confirm_educational_booking(booking.educationalBookingId)


@freeze_time("2020-11-17 15:00:00")
@pytest.mark.usefixtures("db_session")
class BookEducationalOfferTest:
    def test_should_create_educational_booking_on_requested_educational_offer(self):
        # Given
        stock = offers_factories.EducationalEventStockFactory(beginningDatetime=datetime.datetime(2021, 5, 15))
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_year = educational_factories.EducationalYearFactory(
            beginningDate=datetime.datetime(2020, 9, 1), expirationDate=datetime.datetime(2021, 8, 31)
        )
        educational_factories.EducationalYearFactory(
            beginningDate=datetime.datetime(2021, 9, 1), expirationDate=datetime.datetime(2022, 8, 31)
        )
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")
        redactor_informations = AuthenticatedInformation(
            email=educational_redactor.email,
            civility=educational_redactor.civility,
            firstname=educational_redactor.firstName,
            lastname=educational_redactor.lastName,
            uai=educational_institution.institutionId,
        )

        # When
        returned_booking = educational_api.book_educational_offer(
            redactor_informations=redactor_informations,
            stock_id=stock.id,
        )

        # Then
        saved_educational_booking = EducationalBooking.query.join(Booking).filter(Booking.stockId == stock.id).first()

        assert saved_educational_booking.booking.id == returned_booking.id
        assert saved_educational_booking.booking.stock.id == stock.id
        assert saved_educational_booking.booking.stock.dnBookedQuantity == 1
        assert saved_educational_booking.confirmationLimitDate == stock.bookingLimitDatetime
        assert saved_educational_booking.booking.cancellationLimitDate == stock.beginningDatetime - datetime.timedelta(
            days=15
        )
        assert saved_educational_booking.educationalInstitution.institutionId == educational_institution.institutionId
        assert saved_educational_booking.educationalYear.adageId == educational_year.adageId
        assert saved_educational_booking.booking.status == BookingStatus.PENDING
        # Assert we do not create an extra educational redactor when exist
        assert EducationalRedactor.query.count() == 1

    def test_should_send_email_on_educational_booking_creation(self):
        # Given
        stock = offers_factories.EducationalEventStockFactory(
            beginningDatetime=datetime.datetime(2021, 5, 15),
            offer__bookingEmail="test@email.com",
        )
        educational_institution = educational_factories.EducationalInstitutionFactory(
            name="lycée du Pass", city="Paris", postalCode="75018"
        )
        educational_factories.EducationalYearFactory(
            beginningDate=datetime.datetime(2020, 9, 1), expirationDate=datetime.datetime(2021, 8, 31)
        )
        educational_factories.EducationalYearFactory(
            beginningDate=datetime.datetime(2021, 9, 1), expirationDate=datetime.datetime(2022, 8, 31)
        )
        educational_redactor = educational_factories.EducationalRedactorFactory(
            email="professeur@example.com",
            firstName="Georges",
            lastName="Moustaki",
        )
        redactor_informations = AuthenticatedInformation(
            email=educational_redactor.email,
            civility=educational_redactor.civility,
            firstname=educational_redactor.firstName,
            lastname=educational_redactor.lastName,
            uai=educational_institution.institutionId,
        )

        # When
        educational_api.book_educational_offer(
            redactor_informations=redactor_informations,
            stock_id=stock.id,
        )

        # Then
        assert len(mails_testing.outbox) == 1
        sent_data = mails_testing.outbox[0].sent_data
        offer = stock.offer

        assert sent_data["template"] == asdict(TransactionalEmail.EAC_NEW_PREBOOKING_TO_PRO.value)

        assert sent_data["params"] == {
            "OFFER_NAME": offer.name,
            "VENUE_NAME": offer.venue.name,
            "EVENT_DATE": "samedi 15 mai 2021",
            "EVENT_HOUR": "2h",
            "QUANTITY": 1,
            "PRICE": "10.00",
            "REDACTOR_FIRSTNAME": "Georges",
            "REDACTOR_LASTNAME": "Moustaki",
            "REDACTOR_EMAIL": "professeur@example.com",
            "EDUCATIONAL_INSTITUTION_CITY": "Paris",
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": "75018",
            "EDUCATIONAL_INSTITUTION_NAME": "lycée du Pass",
            "IS_EVENT": True,
        }

    @override_settings(ADAGE_API_URL="https://adage_base_url")
    @override_settings(ADAGE_API_KEY="adage-api-key")
    def test_should_notify_adage_on_educational_prebooking_creation(self):
        # Given
        stock = offers_factories.EducationalEventStockFactory(
            beginningDatetime=datetime.datetime(2021, 5, 15),
            offer__bookingEmail="test@email.com",
        )
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory(
            beginningDate=datetime.datetime(2020, 9, 1), expirationDate=datetime.datetime(2021, 8, 31)
        )
        educational_factories.EducationalYearFactory(
            beginningDate=datetime.datetime(2021, 9, 1), expirationDate=datetime.datetime(2022, 8, 31)
        )
        educational_redactor = educational_factories.EducationalRedactorFactory(
            email="professeur@example.com",
            firstName="Fabulous",
            lastName="Fab",
        )
        redactor_informations = RedactorInformation(
            email=educational_redactor.email,
            civility=educational_redactor.civility,
            firstname=educational_redactor.firstName,
            lastname=educational_redactor.lastName,
            uai=educational_institution.institutionId,
        )

        # When
        booking = educational_api.book_educational_offer(
            redactor_informations=redactor_informations,
            stock_id=stock.id,
        )

        # Then
        expected_payload = serialize_educational_booking(booking.educationalBooking)
        assert adage_api_testing.adage_requests[0]["sent_data"] == expected_payload
        assert adage_api_testing.adage_requests[0]["url"] == "https://adage_base_url/v1/prereservation"

    @override_settings(ADAGE_API_URL="https://adage_base_url")
    @override_settings(ADAGE_API_KEY="adage-api-key")
    def test_should_notify_adage_with_less_redactor_information(self):
        # Given
        stock = offers_factories.EducationalEventStockFactory(
            beginningDatetime=datetime.datetime(2021, 5, 15),
            offer__bookingEmail="test@email.com",
        )
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory(
            beginningDate=datetime.datetime(2020, 9, 1), expirationDate=datetime.datetime(2021, 8, 31)
        )
        educational_factories.EducationalYearFactory(
            beginningDate=datetime.datetime(2021, 9, 1), expirationDate=datetime.datetime(2022, 8, 31)
        )
        educational_redactor = educational_factories.EducationalRedactorFactory(
            email="professeur@example.com",
            firstName=None,
            lastName=None,
            civility=None,
        )
        redactor_informations = RedactorInformation(
            email=educational_redactor.email,
            civility=None,
            firstname=None,
            lastname=None,
            uai=educational_institution.institutionId,
        )

        # When
        booking = educational_api.book_educational_offer(
            redactor_informations=redactor_informations,
            stock_id=stock.id,
        )

        # Then
        expected_payload = serialize_educational_booking(booking.educationalBooking)
        assert adage_api_testing.adage_requests[0]["sent_data"] == expected_payload
        assert adage_api_testing.adage_requests[0]["url"] == "https://adage_base_url/v1/prereservation"

    def test_should_create_educational_redactor_when_it_does_not_exist(self):
        # Given
        stock = offers_factories.EducationalEventStockFactory(beginningDatetime=datetime.datetime(2021, 5, 15))
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory(
            beginningDate=datetime.datetime(2020, 9, 1), expirationDate=datetime.datetime(2021, 8, 31)
        )
        educational_factories.EducationalYearFactory(
            beginningDate=datetime.datetime(2021, 9, 1), expirationDate=datetime.datetime(2022, 8, 31)
        )
        redactor_informations = AuthenticatedInformation(
            email="turlupin@example.com",
            civility="Mme",
            firstname="Project",
            lastname="Redactor",
            uai=educational_institution.institutionId,
        )

        # When
        educational_api.book_educational_offer(
            redactor_informations=redactor_informations,
            stock_id=stock.id,
        )

        # Then
        saved_educational_booking = EducationalBooking.query.join(Booking).filter(Booking.stockId == stock.id).first()
        assert saved_educational_booking.educationalRedactor.email == redactor_informations.email
        educational_redactor: EducationalRedactor = EducationalRedactor.query.one()
        assert educational_redactor.email == redactor_informations.email
        assert educational_redactor.firstName == "Project"
        assert educational_redactor.lastName == "Redactor"
        assert educational_redactor.civility == "Mme"

    def test_should_not_create_educational_booking_when_educational_institution_unknown(self):
        # Given
        stock = offers_factories.EducationalEventStockFactory(beginningDatetime=datetime.datetime(2021, 5, 15))
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")
        provided_institution_id = "AU3568Unknown"
        redactor_informations = AuthenticatedInformation(
            email=educational_redactor.email,
            civility=educational_redactor.civility,
            firstname=educational_redactor.firstName,
            lastname=educational_redactor.lastName,
            uai=provided_institution_id,
        )

        # When
        with pytest.raises(exceptions.EducationalInstitutionUnknown) as error:
            educational_api.book_educational_offer(
                redactor_informations=redactor_informations,
                stock_id=stock.id,
            )

        # Then
        assert error.value.errors == {"educationalInstitution": ["Cette institution est inconnue"]}

        saved_bookings = EducationalBooking.query.join(Booking).filter(Booking.stockId == stock.id).all()
        assert len(saved_bookings) == 0

    def test_should_not_create_educational_booking_when_stock_does_not_exist(self):
        # Given
        offers_factories.EducationalEventStockFactory(beginningDatetime=datetime.datetime(2021, 5, 15))
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")
        requested_stock_id = 4875
        redactor_informations = AuthenticatedInformation(
            email=educational_redactor.email,
            civility=educational_redactor.civility,
            firstname=educational_redactor.firstName,
            lastname=educational_redactor.lastName,
            uai=educational_institution.institutionId,
        )

        # When
        with pytest.raises(offers_exceptions.StockDoesNotExist):
            educational_api.book_educational_offer(
                redactor_informations=redactor_informations,
                stock_id=requested_stock_id,
            )

        # Then
        saved_bookings = EducationalBooking.query.all()
        assert len(saved_bookings) == 0

    @mock.patch("pcapi.core.offers.repository.get_and_lock_stock")
    def test_should_not_create_educational_booking_when_stock_is_not_bookable(self, mocked_get_and_lock_stock):
        # Given
        stock = mock.MagicMock()
        stock.isBookable = False
        stock.id = 1
        mocked_get_and_lock_stock.return_value = stock
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")
        educational_institution = educational_factories.EducationalInstitutionFactory()
        redactor_informations = AuthenticatedInformation(
            email=educational_redactor.email,
            civility=educational_redactor.civility,
            firstname=educational_redactor.firstName,
            lastname=educational_redactor.lastName,
            uai=educational_institution.institutionId,
        )

        # When
        with pytest.raises(exceptions.StockNotBookable) as error:
            educational_api.book_educational_offer(
                redactor_informations=redactor_informations,
                stock_id=stock.id,
            )

        # Then
        assert error.value.errors == {"stock": [f"Le stock {stock.id} n'est pas réservable"]}
        saved_bookings = EducationalBooking.query.join(Booking).filter(Booking.stockId == stock.id).all()
        assert len(saved_bookings) == 0

    @freeze_time("2017-11-17 15:00:00")
    def test_should_not_create_educational_booking_when_educational_year_not_found(self):
        # Given
        date_before_education_year_beginning = datetime.datetime(2018, 9, 20)
        stock = offers_factories.EducationalEventStockFactory(beginningDatetime=date_before_education_year_beginning)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")
        redactor_informations = AuthenticatedInformation(
            email=educational_redactor.email,
            civility=educational_redactor.civility,
            firstname=educational_redactor.firstName,
            lastname=educational_redactor.lastName,
            uai=educational_institution.institutionId,
        )

        # When
        with pytest.raises(exceptions.EducationalYearNotFound) as error:
            educational_api.book_educational_offer(
                redactor_informations=redactor_informations,
                stock_id=stock.id,
            )

        # Then
        assert error.value.errors == {
            "educationalYear": ["Aucune année scolaire correspondant à la réservation demandée n'a été trouvée"]
        }

        saved_bookings = EducationalBooking.query.join(Booking).filter(Booking.stockId == stock.id).all()
        assert len(saved_bookings) == 0

    def test_should_not_create_educational_booking_when_requested_offer_is_not_educational(self):
        # Given
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")
        stock = offers_factories.EventStockFactory(
            offer__isEducational=False, beginningDatetime=datetime.datetime(2021, 5, 15)
        )
        redactor_informations = AuthenticatedInformation(
            email=educational_redactor.email,
            civility=educational_redactor.civility,
            firstname=educational_redactor.firstName,
            lastname=educational_redactor.lastName,
            uai=educational_institution.institutionId,
        )

        # When
        with pytest.raises(exceptions.OfferIsNotEducational) as error:
            educational_api.book_educational_offer(
                redactor_informations=redactor_informations,
                stock_id=stock.id,
            )

        # Then
        assert error.value.errors == {"offer": [f"L'offre {stock.offer.id} n'est pas une offre éducationnelle"]}

        saved_bookings = EducationalBooking.query.join(Booking).filter(Booking.stockId == stock.id).all()
        assert len(saved_bookings) == 0

    def test_should_not_create_educational_booking_when_offer_is_not_an_event(self):
        # Given
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")
        stock = offers_factories.ThingStockFactory(
            beginningDatetime=datetime.datetime(2021, 5, 15), offer__isEducational=True
        )
        redactor_informations = AuthenticatedInformation(
            email=educational_redactor.email,
            civility=educational_redactor.civility,
            firstname=educational_redactor.firstName,
            lastname=educational_redactor.lastName,
            uai=educational_institution.institutionId,
        )

        # When
        with pytest.raises(exceptions.OfferIsNotEvent) as error:
            educational_api.book_educational_offer(
                redactor_informations=redactor_informations,
                stock_id=stock.id,
            )

        # Then
        assert error.value.errors == {"offer": [f"L'offre {stock.offer.id} n'est pas une offre évènementielle"]}

        saved_bookings = EducationalBooking.query.join(Booking).filter(Booking.stockId == stock.id).all()
        assert len(saved_bookings) == 0

    def test_should_create_educational_booking_with_cancellation_limit_date_at_booking_date_when_less_than_15_days_to_event(
        self,
    ):
        # Given
        stock = offers_factories.EducationalEventStockFactory(beginningDatetime=datetime.datetime(2020, 11, 27))
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory(
            beginningDate=datetime.datetime(2020, 9, 1), expirationDate=datetime.datetime(2021, 8, 31)
        )
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")
        redactor_informations = AuthenticatedInformation(
            email=educational_redactor.email,
            civility=educational_redactor.civility,
            firstname=educational_redactor.firstName,
            lastname=educational_redactor.lastName,
            uai=educational_institution.institutionId,
        )

        # When
        returned_booking = educational_api.book_educational_offer(
            redactor_informations=redactor_informations,
            stock_id=stock.id,
        )

        # Then
        saved_educational_booking = EducationalBooking.query.join(Booking).filter(Booking.stockId == stock.id).first()

        assert saved_educational_booking.booking.id == returned_booking.id
        assert saved_educational_booking.booking.cancellationLimitDate == returned_booking.dateCreated


class RefuseEducationalBookingTest:
    @clean_database
    def test_refuse_educational_booking_stock_lock(self, app):
        booking = bookings_factories.EducationalBookingFactory(
            status=BookingStatus.CONFIRMED,
        )
        educational_booking = booking.educationalBooking

        # open a second connection on purpose and lock the deposit
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        with engine.connect() as connection:
            connection.execute(
                text("""SELECT * FROM stock WHERE id = :stock_id FOR UPDATE"""),
                stock_id=booking.stock.id,
            )

            with pytest.raises(sqlalchemy.exc.OperationalError):
                educational_api.refuse_educational_booking(educational_booking.id)

        refreshed_booking = Booking.query.filter(Booking.id == booking.id).one()
        assert refreshed_booking.status == BookingStatus.CONFIRMED

    def test_refuse_educational_booking(self, db_session):
        stock = offers_factories.EducationalEventStockFactory(quantity=200, dnBookedQuantity=0)
        booking = bookings_factories.EducationalBookingFactory(
            status=BookingStatus.CONFIRMED,
            stock=stock,
            quantity=20,
        )

        educational_api.refuse_educational_booking(booking.educationalBookingId)

        assert stock.dnBookedQuantity == 0
        assert booking.status == BookingStatus.CANCELLED
        assert booking.cancellationReason == BookingCancellationReasons.REFUSED_BY_INSTITUTE

    def test_raises_when_no_educational_booking_found(self):
        with pytest.raises(exceptions.EducationalBookingNotFound):
            educational_api.refuse_educational_booking(123)

    def test_no_op_when_educational_booking_already_refused(self, db_session):
        stock = offers_factories.EducationalEventStockFactory(dnBookedQuantity=20)
        booking = bookings_factories.EducationalBookingFactory(
            educationalBooking__status=EducationalBookingStatus.REFUSED,
            quantity=1,
            stock=stock,
        )

        educational_api.refuse_educational_booking(booking.educationalBookingId)

        assert stock.dnBookedQuantity == 21


# @freeze_time("2020-11-17 15:00:00")
@pytest.mark.usefixtures("db_session")
class EditCollectiveOfferStocksTest:
    def test_should_update_all_fields_when_all_changed(self):
        # Given
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        initial_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            beginningDatetime=initial_event_date,
            price=1200,
            numberOfTickets=30,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=7, hours=5),
            bookingLimitDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=5, hours=16),
            totalPrice=1500,
            numberOfTickets=35,
        )

        # When
        educational_api.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.beginningDatetime == new_stock_data.beginningDatetime
        assert stock.bookingLimitDatetime == new_stock_data.bookingLimitDatetime
        assert stock.price == 1500
        assert stock.numberOfTickets == 35

    def test_should_update_some_fields_and_keep_non_edited_ones(self):
        # Given
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        initial_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            beginningDatetime=initial_event_date,
            price=1200,
            numberOfTickets=30,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=7, hours=5),
            numberOfTickets=35,
        )

        # When
        educational_api.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.beginningDatetime == new_stock_data.beginningDatetime
        assert stock.bookingLimitDatetime == initial_booking_limit_date
        assert stock.price == 1200
        assert stock.numberOfTickets == 35

    def test_should_replace_bookingLimitDatetime_with_new_event_datetime_if_provided_but_none(self):
        # Given
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        initial_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            beginningDatetime=initial_event_date,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_event_datetime = datetime.datetime.utcnow() + datetime.timedelta(days=7, hours=5)
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            beginningDatetime=new_event_datetime,
            bookingLimitDatetime=None,
        )

        # When
        educational_api.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.bookingLimitDatetime == new_event_datetime

    def test_should_replace_bookingLimitDatetime_with_old_event_datetime_if_provided_but_none_and_event_date_unchanged(
        self,
    ):
        # Given
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        initial_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            beginningDatetime=initial_event_date,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            bookingLimitDatetime=None,
        )

        # When
        educational_api.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.bookingLimitDatetime == initial_event_date

    # FIXME (rpaoloni, 2022-03-09): Uncomment for when pc-13428 is merged
    # @mock.patch("pcapi.core.search.async_index_offer_ids")
    # def test_should_reindex_offer_on_algolia(self, mocked_async_index_offer_ids):
    #     # Given
    #     initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
    #     initial_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)
    #     stock_to_be_updated = educational_factories.CollectiveStockFactory(
    #         beginningDatetime=initial_event_date,
    #         price=1200,
    #         numberOfTickets=30,
    #         bookingLimitDatetime=initial_booking_limit_date,
    #     )
    #     new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
    #         beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=7, hours=5),
    #         numberOfTickets=35,
    #     )

    #     # When
    #     educational_api.edit_collective_stock(
    #         stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
    #     )

    #     # Then
    #     stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
    #     mocked_async_index_offer_ids.assert_called_once_with([stock.collectiveOfferId])

    def test_should_not_allow_stock_edition_when_booking_status_is_not_PENDING(self):
        # Given
        stock_to_be_updated = educational_factories.CollectiveStockFactory(price=1200)
        educational_factories.CollectiveBookingFactory(
            confirmationLimitDate=datetime.datetime.utcnow() + datetime.timedelta(days=1337),
            collectiveStock=stock_to_be_updated,
        )

        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            totalPrice=1500,
        )

        # When
        with pytest.raises(exceptions.CollectiveOfferStockBookedAndBookingNotPending):
            educational_api.edit_collective_stock(
                stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
            )

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).first()
        assert stock.price == 1200

    @freeze_time("2020-11-17 15:00:00")
    def should_update_bookings_cancellation_limit_date_if_event_postponed(self):
        # Given
        educational_year = educational_factories.EducationalYearFactory(
            beginningDate=datetime.datetime(2020, 9, 1), expirationDate=datetime.datetime(2021, 8, 31)
        )
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=20)
        cancellation_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(beginningDatetime=initial_event_date)
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_to_be_updated,
            status=CollectiveBookingStatus.PENDING,
            cancellationLimitDate=cancellation_limit_date,
            confirmationLimitDate=datetime.datetime.utcnow() + datetime.timedelta(days=30),
            educationalYear=educational_year,
        )

        new_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=25, hours=5)
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            beginningDatetime=new_event_date,
        )

        # When
        educational_api.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        # Then
        booking_updated = CollectiveBooking.query.filter_by(id=booking.id).one()
        assert booking_updated.cancellationLimitDate == new_event_date - datetime.timedelta(days=15)

    @freeze_time("2020-11-17 15:00:00")
    def should_update_bookings_cancellation_limit_date_if_beginningDatetime_earlier(self):
        # Given
        educational_year = educational_factories.EducationalYearFactory(
            beginningDate=datetime.datetime(2020, 9, 1), expirationDate=datetime.datetime(2021, 8, 31)
        )
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=20)
        cancellation_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(beginningDatetime=initial_event_date)
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_to_be_updated,
            status=CollectiveBookingStatus.PENDING,
            cancellationLimitDate=cancellation_limit_date,
            confirmationLimitDate=datetime.datetime.utcnow() + datetime.timedelta(days=30),
            educationalYear=educational_year,
        )

        new_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=5, hours=5)
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            beginningDatetime=new_event_date,
            bookingLimitDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=3, hours=5),
        )

        # When
        educational_api.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        # Then
        booking_updated = CollectiveBooking.query.filter_by(id=booking.id).one()
        assert booking_updated.cancellationLimitDate == datetime.datetime.utcnow()

    @freeze_time("2020-11-17 15:00:00")
    def test_should_allow_stock_edition_and_not_modify_cancellation_limit_date_when_booking_cancelled(self):
        # Given
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=20)
        cancellation_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            beginningDatetime=initial_event_date,
        )
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock=stock_to_be_updated,
            status=CollectiveBookingStatus.CANCELLED,
            cancellationLimitDate=cancellation_limit_date,
            confirmationLimitDate=datetime.datetime.utcnow() + datetime.timedelta(days=30),
        )

        new_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=25, hours=5)
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            beginningDatetime=new_event_date,
        )

        # When
        educational_api.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        # Then
        booking = CollectiveBooking.query.filter_by(id=booking.id).one()
        assert booking.cancellationLimitDate == cancellation_limit_date
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.beginningDatetime == new_event_date

    def test_does_not_allow_edition_of_an_expired_event_stock(self):
        # Given
        initial_event_date = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        initial_booking_limit_date = datetime.datetime.utcnow() - datetime.timedelta(days=10)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            beginningDatetime=initial_event_date,
            price=1200,
            numberOfTickets=30,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            beginningDatetime=datetime.datetime.utcnow() + datetime.timedelta(days=7, hours=5),
            numberOfTickets=35,
        )

        # When
        with pytest.raises(offers_exceptions.ApiErrors) as error:
            educational_api.edit_collective_stock(
                stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
            )

        # Then
        assert error.value.errors == {"global": ["Les événements passés ne sont pas modifiables"]}
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).first()
        assert stock.numberOfTickets == 30

    def test_edit_stock_of_non_approved_offer_fails(self):
        # Given
        offer = educational_factories.CollectiveOfferFactory(validation=OfferValidationStatus.PENDING)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
            price=1200,
            numberOfTickets=30,
        )
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            numberOfTickets=35,
        )

        # When
        with pytest.raises(offers_exceptions.ApiErrors) as error:
            educational_api.edit_collective_stock(
                stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
            )

        # Then
        assert error.value.errors == {
            "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
        }
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.numberOfTickets == 30

    @freeze_time("2020-11-17 15:00:00")
    def test_should_not_allow_stock_edition_when_beginningDatetime_not_provided_and_bookingLimitDatetime_set_after_existing_event_datetime(
        self,
    ):
        # Given
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime.datetime(2021, 12, 10), bookingLimitDatetime=datetime.datetime(2021, 12, 5)
        )
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            bookingLimitDatetime=datetime.datetime(2021, 12, 20)
        )

        # When
        with pytest.raises(offers_exceptions.BookingLimitDatetimeTooLate):
            educational_api.edit_collective_stock(
                stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
            )

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.bookingLimitDatetime == datetime.datetime(2021, 12, 5)

    @freeze_time("2020-11-17 15:00:00")
    def test_should_not_allow_stock_edition_when_bookingLimitDatetime_not_provided_and_beginningDatetime_set_before_existing_event_datetime(
        self,
    ):
        # Given
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime.datetime(2021, 12, 10), bookingLimitDatetime=datetime.datetime(2021, 12, 5)
        )
        new_stock_data = stock_serialize.EducationalStockEditionBodyModel(
            beginningDatetime=datetime.datetime(2021, 12, 4)
        )

        # When
        with pytest.raises(offers_exceptions.BookingLimitDatetimeTooLate):
            educational_api.edit_collective_stock(
                stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
            )

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.beginningDatetime == datetime.datetime(2021, 12, 10)


@freeze_time("2020-11-17 15:00:00")
@pytest.mark.usefixtures("db_session")
class CreateCollectiveOfferStocksTest:
    def should_create_one_stock_on_collective_offer_stock_creation(self):
        # Given
        user_pro = users_factories.ProFactory()
        offer = educational_factories.CollectiveOfferFactory()
        new_stock = stock_serialize.EducationalStockCreationBodyModel(
            offerId=offer.id,
            beginningDatetime=dateutil.parser.parse("2021-12-15T20:00:00Z"),
            bookingLimitDatetime=dateutil.parser.parse("2021-12-05T00:00:00Z"),
            totalPrice=1200,
            numberOfTickets=35,
        )

        # When
        stock_created = educational_api.create_collective_stock(stock_data=new_stock, user=user_pro)

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_created.id).one()
        assert stock.beginningDatetime == datetime.datetime.fromisoformat("2021-12-15T20:00:00")
        assert stock.bookingLimitDatetime == datetime.datetime.fromisoformat("2021-12-05T00:00:00")
        assert stock.price == 1200
        assert stock.numberOfTickets == 35
        assert stock.stockId == None

        search.index_collective_offers_in_queue()
        assert offer.id in search_testing.search_store["collective-offers"]

    def should_set_booking_limit_datetime_to_beginning_datetime_when_not_provided(self):
        # Given
        user_pro = users_factories.ProFactory()
        offer = educational_factories.CollectiveOfferFactory()
        new_stock = stock_serialize.EducationalStockCreationBodyModel(
            offerId=offer.id,
            beginningDatetime=dateutil.parser.parse("2021-12-15T20:00:00Z"),
            totalPrice=1200,
            numberOfTickets=35,
        )

        # When
        stock_created = educational_api.create_collective_stock(stock_data=new_stock, user=user_pro)

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_created.id).one()
        assert stock.bookingLimitDatetime == dateutil.parser.parse("2021-12-15T20:00:00")

    @override_features(ENABLE_NEW_COLLECTIVE_MODEL=True)
    def test_create_stock_triggers_draft_offer_validation(self):
        # Given
        offers_api.import_offer_validation_config(SIMPLE_OFFER_VALIDATION_CONFIG)
        user_pro = users_factories.ProFactory()
        draft_approvable_offer = educational_factories.CollectiveOfferFactory(
            name="a great offer", validation=OfferValidationStatus.DRAFT
        )
        draft_suspicious_offer = educational_factories.CollectiveOfferFactory(
            name="a suspicious offer", validation=OfferValidationStatus.DRAFT
        )
        common_created_stock_data = {
            "beginningDatetime": dateutil.parser.parse("2022-01-17T22:00:00Z"),
            "bookingLimitDatetime": dateutil.parser.parse("2021-12-31T20:00:00Z"),
            "totalPrice": 1500,
            "numberOfTickets": 38,
        }
        created_stock_data_approvable = stock_serialize.EducationalStockCreationBodyModel(
            offerId=draft_approvable_offer.id, **common_created_stock_data
        )
        created_stock_data_suspicious = stock_serialize.EducationalStockCreationBodyModel(
            offerId=draft_suspicious_offer.id, **common_created_stock_data
        )

        # When
        educational_api.create_collective_stock(stock_data=created_stock_data_approvable, user=user_pro)
        educational_api.create_collective_stock(stock_data=created_stock_data_suspicious, user=user_pro)

        # Then
        assert draft_approvable_offer.validation == OfferValidationStatus.APPROVED
        assert draft_approvable_offer.isActive
        assert draft_approvable_offer.lastValidationDate == datetime.datetime(2020, 11, 17, 15, 0)
        assert draft_suspicious_offer.validation == OfferValidationStatus.PENDING
        assert not draft_suspicious_offer.isActive
        assert draft_suspicious_offer.lastValidationDate == datetime.datetime(2020, 11, 17, 15, 0)

    def test_create_stock_for_non_approved_offer_fails(self):
        # Given
        user = users_factories.ProFactory()
        offer = educational_factories.CollectiveOfferFactory(validation=OfferValidationStatus.PENDING)
        created_stock_data = stock_serialize.EducationalStockCreationBodyModel(
            offerId=offer.id,
            beginningDatetime=dateutil.parser.parse("2022-01-17T22:00:00Z"),
            bookingLimitDatetime=dateutil.parser.parse("2021-12-31T20:00:00Z"),
            totalPrice=1500,
            numberOfTickets=38,
        )

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            educational_api.create_collective_stock(stock_data=created_stock_data, user=user)

        # Then
        assert error.value.errors == {
            "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
        }
        assert CollectiveStock.query.count() == 0

    @override_features(ENABLE_NEW_COLLECTIVE_MODEL=True)
    @mock.patch("pcapi.domain.admin_emails.send_offer_creation_notification_to_administration")
    @mock.patch("pcapi.core.offers.api.set_offer_status_based_on_fraud_criteria")
    def test_send_email_when_offer_automatically_approved_based_on_fraud_criteria(
        self, mocked_set_offer_status_based_on_fraud_criteria, mocked_offer_creation_notification_to_admin
    ):
        # Given
        user = users_factories.ProFactory()
        offer = educational_factories.CollectiveOfferFactory(validation=OfferValidationStatus.DRAFT)
        created_stock_data = stock_serialize.EducationalStockCreationBodyModel(
            offerId=offer.id,
            beginningDatetime=dateutil.parser.parse("2022-01-17T22:00:00Z"),
            bookingLimitDatetime=dateutil.parser.parse("2021-12-31T20:00:00Z"),
            totalPrice=1500,
            numberOfTickets=38,
        )
        mocked_set_offer_status_based_on_fraud_criteria.return_value = OfferValidationStatus.APPROVED

        # When
        educational_api.create_collective_stock(stock_data=created_stock_data, user=user)

        # Then
        mocked_offer_creation_notification_to_admin.assert_called_once_with(offer)

    @mock.patch("pcapi.domain.admin_emails.send_offer_creation_notification_to_administration")
    @mock.patch("pcapi.core.offers.api.set_offer_status_based_on_fraud_criteria")
    def test_not_send_email_when_offer_pass_to_pending_based_on_fraud_criteria(
        self, mocked_set_offer_status_based_on_fraud_criteria, mocked_offer_creation_notification_to_admin
    ):
        # Given
        user = users_factories.ProFactory()
        offer = educational_factories.CollectiveOfferFactory(validation=OfferValidationStatus.DRAFT)
        created_stock_data = stock_serialize.EducationalStockCreationBodyModel(
            offerId=offer.id,
            beginningDatetime=dateutil.parser.parse("2022-01-17T22:00:00Z"),
            bookingLimitDatetime=dateutil.parser.parse("2021-12-31T20:00:00Z"),
            totalPrice=1500,
            numberOfTickets=38,
        )
        mocked_set_offer_status_based_on_fraud_criteria.return_value = OfferValidationStatus.PENDING

        # When
        educational_api.create_collective_stock(stock_data=created_stock_data, user=user)

        # Then
        assert not mocked_offer_creation_notification_to_admin.called


@freeze_time("2020-01-05 10:00:00")
@pytest.mark.usefixtures("db_session")
class UnindexExpiredOffersTest:
    @override_settings(ALGOLIA_DELETING_COLLECTIVE_OFFERS_CHUNK_SIZE=2)
    @mock.patch("pcapi.core.search.unindex_collective_offer_ids")
    def test_default_run(self, mock_unindex_collective_offer_ids):
        # Given
        educational_factories.CollectiveStockFactory(bookingLimitDatetime=datetime.datetime(2020, 1, 2, 12, 0))
        collective_stock1 = educational_factories.CollectiveStockFactory(
            bookingLimitDatetime=datetime.datetime(2020, 1, 3, 12, 0)
        )
        collective_stock2 = educational_factories.CollectiveStockFactory(
            bookingLimitDatetime=datetime.datetime(2020, 1, 3, 12, 0)
        )
        collective_stock3 = educational_factories.CollectiveStockFactory(
            bookingLimitDatetime=datetime.datetime(2020, 1, 4, 12, 0)
        )
        educational_factories.CollectiveStockFactory(bookingLimitDatetime=datetime.datetime(2020, 1, 5, 12, 0))

        # When
        educational_api.unindex_expired_collective_offers()

        # Then
        assert mock_unindex_collective_offer_ids.mock_calls == [
            mock.call([collective_stock1.collectiveOfferId, collective_stock2.collectiveOfferId]),
            mock.call([collective_stock3.collectiveOfferId]),
        ]

    @mock.patch("pcapi.core.search.unindex_collective_offer_ids")
    def test_run_unlimited(self, mock_unindex_collective_offer_ids):
        # more than 2 days ago, must be processed
        collective_stock = educational_factories.CollectiveStockFactory(
            bookingLimitDatetime=datetime.datetime(2020, 1, 2, 12, 0)
        )
        # today, must be ignored
        educational_factories.CollectiveStockFactory(bookingLimitDatetime=datetime.datetime(2020, 1, 5, 12, 0))

        # When
        educational_api.unindex_expired_collective_offers(process_all_expired=True)

        # Then
        assert mock_unindex_collective_offer_ids.mock_calls == [
            mock.call([collective_stock.collectiveOfferId]),
        ]
