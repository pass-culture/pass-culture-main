import datetime
from decimal import Decimal
from unittest import mock

from freezegun.api import freeze_time
import pytest
import requests_mock
from sqlalchemy import create_engine
import sqlalchemy.exc
from sqlalchemy.sql import text

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational import api as educational_api
from pcapi.core.educational import exceptions
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.educational.models import EducationalBookingStatus
from pcapi.core.educational.models import EducationalRedactor
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import factories as offers_factories
from pcapi.core.testing import override_settings

from tests.conftest import clean_database


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


@freeze_time("2020-11-17 15:00:00")
@pytest.mark.usefixtures("db_session")
class BookEducationalOfferTest:
    def test_should_create_educational_booking_on_requested_educational_offer(self):
        # Given
        stock = offers_factories.EducationalStockFactory(beginningDatetime=datetime.datetime(2021, 5, 15))
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_year = educational_factories.EducationalYearFactory(
            beginningDate=datetime.datetime(2020, 9, 1), expirationDate=datetime.datetime(2021, 8, 31)
        )
        educational_factories.EducationalYearFactory(
            beginningDate=datetime.datetime(2021, 9, 1), expirationDate=datetime.datetime(2022, 8, 31)
        )
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")

        # When
        returned_booking = educational_api.book_educational_offer(
            redactor_email=educational_redactor.email,
            uai_code=educational_institution.institutionId,
            stock_id=stock.id,
        )

        # Then
        saved_educational_booking = EducationalBooking.query.join(Booking).filter(Booking.stockId == stock.id).first()

        assert saved_educational_booking.booking.id == returned_booking.id
        assert saved_educational_booking.booking.stock.id == stock.id
        assert saved_educational_booking.booking.stock.dnBookedQuantity == 1
        assert saved_educational_booking.educationalInstitution.institutionId == educational_institution.institutionId
        assert saved_educational_booking.educationalYear.adageId == educational_year.adageId
        assert saved_educational_booking.booking.status == BookingStatus.PENDING
        # Assert we do not create an extra educational redactor when exist
        assert EducationalRedactor.query.count() == 1

    @override_settings(ADAGE_API_URL="https://adage-api-url")
    @override_settings(ADAGE_API_KEY="adage-api-key")
    def test_should_create_educational_redactor_when_it_does_not_exist(self):
        # Given
        stock = offers_factories.EducationalStockFactory(beginningDatetime=datetime.datetime(2021, 5, 15))
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory(
            beginningDate=datetime.datetime(2020, 9, 1), expirationDate=datetime.datetime(2021, 8, 31)
        )
        educational_factories.EducationalYearFactory(
            beginningDate=datetime.datetime(2021, 9, 1), expirationDate=datetime.datetime(2022, 8, 31)
        )

        institutional_project_redactor_email = "turlupin@example.com"
        response = {
            "civilite": "Mme",
            "nom": "Redactor",
            "prenom": "Project",
            "mail": institutional_project_redactor_email,
            "etablissements": [{"uai": "XXXXXXXXX", "nom": "LYCÉE JEAN - SAINT-NAZAIRE"}],
        }

        # When
        with requests_mock.Mocker() as request_mock:
            request_mock.get(
                f"https://adage-api-url/v1/redacteur-projet/{institutional_project_redactor_email}",
                request_headers={
                    "X-omogen-api-key": "adage-api-key",
                },
                json=response,
            )
            educational_api.book_educational_offer(
                redactor_email=institutional_project_redactor_email,
                uai_code=educational_institution.institutionId,
                stock_id=stock.id,
            )

        # Then
        saved_educational_booking = EducationalBooking.query.join(Booking).filter(Booking.stockId == stock.id).first()
        assert saved_educational_booking.educationalRedactor.email == institutional_project_redactor_email
        educational_redactor: EducationalRedactor = EducationalRedactor.query.one()
        assert educational_redactor.email == institutional_project_redactor_email
        assert educational_redactor.firstName == "Project"
        assert educational_redactor.lastName == "Redactor"
        assert educational_redactor.civility == "Mme"

    def test_should_not_create_educational_booking_when_educational_institution_unknown(self):
        # Given
        stock = offers_factories.EducationalStockFactory(beginningDatetime=datetime.datetime(2021, 5, 15))
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")
        provided_institution_id = "AU3568Unknown"

        # When
        with pytest.raises(exceptions.EducationalInstitutionUnknown) as error:
            educational_api.book_educational_offer(
                redactor_email=educational_redactor.email,
                uai_code=provided_institution_id,
                stock_id=stock.id,
            )

        # Then
        assert error.value.errors == {"educationalInstitution": ["Cette institution est inconnue"]}

        saved_bookings = EducationalBooking.query.join(Booking).filter(Booking.stockId == stock.id).all()
        assert len(saved_bookings) == 0

    def test_should_not_create_educational_booking_when_stock_does_not_exist(self):
        # Given
        offers_factories.EducationalStockFactory(beginningDatetime=datetime.datetime(2021, 5, 15))
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")
        requested_stock_id = 4875

        # When
        with pytest.raises(offers_exceptions.StockDoesNotExist):
            educational_api.book_educational_offer(
                redactor_email=educational_redactor.email,
                uai_code=educational_institution.institutionId,
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

        # When
        with pytest.raises(exceptions.StockNotBookable) as error:
            educational_api.book_educational_offer(
                redactor_email=educational_redactor.email,
                uai_code=educational_institution.institutionId,
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
        stock = offers_factories.EducationalStockFactory(beginningDatetime=date_before_education_year_beginning)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory()
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")

        # When
        with pytest.raises(exceptions.EducationalYearNotFound) as error:
            educational_api.book_educational_offer(
                redactor_email=educational_redactor.email,
                uai_code=educational_institution.institutionId,
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

        # When
        with pytest.raises(exceptions.OfferIsNotEducational) as error:
            educational_api.book_educational_offer(
                redactor_email=educational_redactor.email,
                uai_code=educational_institution.institutionId,
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

        # When
        with pytest.raises(exceptions.OfferIsNotEvent) as error:
            educational_api.book_educational_offer(
                redactor_email=educational_redactor.email,
                uai_code=educational_institution.institutionId,
                stock_id=stock.id,
            )

        # Then
        assert error.value.errors == {"offer": [f"L'offre {stock.offer.id} n'est pas une offre évènementielle"]}

        saved_bookings = EducationalBooking.query.join(Booking).filter(Booking.stockId == stock.id).all()
        assert len(saved_bookings) == 0


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
        stock = offers_factories.EducationalStockFactory(quantity=200, dnBookedQuantity=0)
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
        stock = offers_factories.EducationalStockFactory(dnBookedQuantity=20)
        booking = bookings_factories.EducationalBookingFactory(
            educationalBooking__status=EducationalBookingStatus.REFUSED,
            quantity=1,
            stock=stock,
        )

        educational_api.refuse_educational_booking(booking.educationalBookingId)

        assert stock.dnBookedQuantity == 21
