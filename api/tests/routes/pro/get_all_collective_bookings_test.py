from datetime import datetime
from datetime import timedelta
from datetime import timezone

from freezegun import freeze_time
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")

BOOKING_PERIOD_PARAMS = "bookingPeriodBeginningDate=2022-03-10&bookingPeriodEndingDate=2022-03-12"

BOOKING_PERIOD = (datetime(2022, 3, 10, tzinfo=timezone.utc).date(), datetime(2022, 3, 12, tzinfo=timezone.utc).date())


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    @freeze_time("2022-05-01 15:00:00")
    def test_when_user_is_admin(self, client):
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserOffererFactory()
        educational_factories.CollectiveBookingFactory(
            dateCreated=datetime(2022, 3, 11, 12, 0, 0),
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
        )

        client = client.with_session_auth(admin.email)
        response = client.get(f"collective/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=booked")

        assert response.status_code == 200
        assert len(response.json["bookingsRecap"]) == 1

    @freeze_time("2022-05-01 15:00:00")
    def test_when_regular_pro_user_and_booking_confirmed_by_ce(self, client):
        # Given
        booking_date = datetime(2022, 3, 11, 10, 15, 0)
        pro_user = users_factories.ProFactory()
        user_offerer = offerers_factories.UserOffererFactory(user=pro_user)
        redactor = educational_factories.EducationalRedactorFactory(
            email="reda.ktheur@example.com", firstName="Reda", lastName="Khteur", civility="M."
        )
        collective_stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name="Le chant des cigales",
            collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            beginningDatetime=datetime(2022, 5, 15, 10, 15, 0),
            price=1200,
        )
        booking = educational_factories.CollectiveBookingFactory(
            educationalRedactor=redactor,
            collectiveStock=collective_stock,
            dateCreated=booking_date,
            status=CollectiveBookingStatus.CONFIRMED,
            confirmationDate=booking_date + timedelta(days=1),
        )

        # When
        client = client.with_session_auth(pro_user.email)
        response = client.get(f"collective/bookings/pro?{BOOKING_PERIOD_PARAMS}")

        # Then
        expected_bookings_recap = [
            {
                "stock": {
                    "offer_name": "Le chant des cigales",
                    "offer_identifier": humanize(collective_stock.collectiveOfferId),
                    "offer_is_educational": True,
                    "event_beginning_datetime": "2022-05-15T12:15:00+02:00",
                    "offer_isbn": None,
                    "number_of_tickets": collective_stock.numberOfTickets,
                },
                "beneficiary": {
                    "email": redactor.email,
                    "firstname": redactor.firstName,
                    "lastname": redactor.lastName,
                    "phonenumber": None,
                },
                "booking_identifier": humanize(booking.id),
                "booking_date": "2022-03-11T11:15:00+01:00",
                "booking_amount": 1200.00,
                "booking_token": None,
                "booking_status": "confirmed",
                "booking_is_duo": False,
                "booking_status_history": [
                    {
                        "status": "booked",
                        "date": "2022-03-12T11:15:00+01:00",
                    },
                    {
                        "status": "confirmed",
                        "date": "2022-04-30T12:15:00+02:00",
                    },
                ],
            }
        ]

        assert response.status_code == 200
        assert response.json["page"] == 1
        assert response.json["pages"] == 1
        assert response.json["total"] == 1
        assert response.json["bookingsRecap"] == expected_bookings_recap

    @freeze_time("2022-05-01 15:00:00")
    def test_when_no_results(self, client):
        # Given
        booking_date = datetime(2022, 3, 15, 10, 15, 0)
        pro_user = users_factories.ProFactory()
        user_offerer = offerers_factories.UserOffererFactory(user=pro_user)
        redactor = educational_factories.EducationalRedactorFactory(
            email="reda.ktheur@example.com", firstName="Reda", lastName="Khteur", civility="M."
        )
        collective_stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name="Le chant des cigales",
            collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            beginningDatetime=datetime(2022, 5, 15, 10, 15, 0),
        )
        educational_factories.CollectiveBookingFactory(
            educationalRedactor=redactor,
            collectiveStock=collective_stock,
            dateCreated=booking_date,
        )

        # When
        client = client.with_session_auth(pro_user.email)
        response = client.get(f"collective/bookings/pro?{BOOKING_PERIOD_PARAMS}")
        # response = client.get(f"collective/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=used")

        # Then
        assert response.status_code == 200
        assert response.json["page"] == 1
        assert response.json["pages"] == 0
        assert response.json["total"] == 0
        assert response.json["bookingsRecap"] == []

    @freeze_time("2022-05-01 15:00:00")
    def test_when_collective_booking_pending_should_show_prereserve_in_history(self, client):
        # Given
        booking_date = datetime(2022, 3, 11, 10, 15, 0)
        pro_user = users_factories.ProFactory()
        user_offerer = offerers_factories.UserOffererFactory(user=pro_user)
        redactor = educational_factories.EducationalRedactorFactory(
            email="reda.ktheur@example.com", firstName="Reda", lastName="Khteur", civility="M."
        )
        collective_stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name="Le chant des cigales",
            collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            beginningDatetime=datetime(2022, 5, 15, 10, 15, 0),
            price=1200,
        )
        educational_factories.PendingCollectiveBookingFactory(
            educationalRedactor=redactor,
            collectiveStock=collective_stock,
            dateCreated=booking_date,
        )

        # When
        client = client.with_session_auth(pro_user.email)
        response = client.get(f"collective/bookings/pro?{BOOKING_PERIOD_PARAMS}")

        # Then
        assert response.status_code == 200
        booking_recap = response.json["bookingsRecap"][0]
        assert booking_recap["booking_status"] == "pending"
        assert booking_recap["booking_status_history"] == [
            {
                "status": "pending",
                "date": "2022-03-11T11:15:00+01:00",
            },
        ]

    @freeze_time("2022-05-01 15:00:00")
    def test_when_collective_booking_used_should_show_valide_and_previous_in_history_but_not_prereserve(self, client):
        # Given
        booking_date = datetime(2022, 3, 11, 10, 15, 0)
        event_date = datetime(2022, 5, 15, 20, 00, 0)
        pro_user = users_factories.ProFactory()
        user_offerer = offerers_factories.UserOffererFactory(user=pro_user)
        redactor = educational_factories.EducationalRedactorFactory(
            email="reda.ktheur@example.com", firstName="Reda", lastName="Khteur", civility="M."
        )
        collective_stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name="Le chant des cigales",
            collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            beginningDatetime=event_date,
            price=1200,
        )
        educational_factories.UsedCollectiveBookingFactory(
            educationalRedactor=redactor,
            collectiveStock=collective_stock,
            dateCreated=booking_date,
            confirmationDate=booking_date + timedelta(days=1, hours=2),
            dateUsed=event_date + timedelta(days=1),
        )

        # When
        client = client.with_session_auth(pro_user.email)
        response = client.get(f"collective/bookings/pro?{BOOKING_PERIOD_PARAMS}")

        # Then
        assert response.status_code == 200
        booking_recap = response.json["bookingsRecap"][0]
        assert booking_recap["booking_status"] == "validated"
        assert booking_recap["booking_status_history"] == [
            {
                "status": "booked",
                "date": "2022-03-12T13:15:00+01:00",
            },
            {
                "status": "confirmed",
                "date": "2022-04-30T22:00:00+02:00",
            },
            {
                "status": "validated",
                "date": "2022-05-16T22:00:00+02:00",
            },
        ]

    @freeze_time("2022-05-01 15:00:00")
    def test_when_collective_booking_cancelled_after_confirmed_should_show_annule_and_previous_in_history_but_not_prereserve(
        self, client
    ):
        # Given
        booking_date = datetime(2022, 3, 11, 10, 15, 0)
        event_date = datetime(2022, 5, 15, 20, 00, 0)
        pro_user = users_factories.ProFactory()
        user_offerer = offerers_factories.UserOffererFactory(user=pro_user)
        redactor = educational_factories.EducationalRedactorFactory(
            email="reda.ktheur@example.com", firstName="Reda", lastName="Khteur", civility="M."
        )
        collective_stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name="Le chant des cigales",
            collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            beginningDatetime=event_date,
            price=1200,
        )
        educational_factories.CancelledCollectiveBookingFactory(
            educationalRedactor=redactor,
            collectiveStock=collective_stock,
            dateCreated=booking_date,
            confirmationDate=booking_date + timedelta(days=1, hours=2),
            cancellationDate=booking_date + timedelta(days=5, minutes=32),
        )

        # When
        client = client.with_session_auth(pro_user.email)
        response = client.get(f"collective/bookings/pro?{BOOKING_PERIOD_PARAMS}")

        # Then
        assert response.status_code == 200
        booking_recap = response.json["bookingsRecap"][0]
        assert booking_recap["booking_status"] == "cancelled"
        assert booking_recap["booking_status_history"] == [
            {
                "status": "booked",
                "date": "2022-03-12T13:15:00+01:00",
            },
            {
                "status": "confirmed",
                "date": "2022-04-30T22:00:00+02:00",
            },
            {
                "status": "cancelled",
                "date": "2022-03-16T11:47:00+01:00",
            },
        ]

    @freeze_time("2022-05-01 15:00:00")
    def test_when_collective_booking_cancelled_while_pending_should_show_annule_and_reserve_in_history_but_not_prereserve(
        self, client
    ):
        # Given
        booking_date = datetime(2022, 3, 11, 10, 15, 0)
        event_date = datetime(2022, 5, 15, 20, 00, 0)
        pro_user = users_factories.ProFactory()
        user_offerer = offerers_factories.UserOffererFactory(user=pro_user)
        redactor = educational_factories.EducationalRedactorFactory(
            email="reda.ktheur@example.com", firstName="Reda", lastName="Khteur", civility="M."
        )
        collective_stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name="Le chant des cigales",
            collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            beginningDatetime=event_date,
            price=1200,
        )
        educational_factories.CancelledCollectiveBookingFactory(
            educationalRedactor=redactor,
            collectiveStock=collective_stock,
            dateCreated=booking_date,
            confirmationDate=None,
            cancellationDate=booking_date + timedelta(days=5, minutes=32),
        )

        # When
        client = client.with_session_auth(pro_user.email)
        response = client.get(f"collective/bookings/pro?{BOOKING_PERIOD_PARAMS}")

        # Then
        assert response.status_code == 200
        booking_recap = response.json["bookingsRecap"][0]
        assert booking_recap["booking_status"] == "cancelled"
        assert booking_recap["booking_status_history"] == [
            {
                "status": "booked",
                "date": "2022-03-11T11:15:00+01:00",
            },
            {
                "status": "cancelled",
                "date": "2022-03-16T11:47:00+01:00",
            },
        ]

    @freeze_time("2022-06-30 15:00:00")
    def test_when_collective_booking_reimbursed_should_show_rembourse_and_previous_in_history_but_not_prereserve(
        self, client
    ):
        # Given
        booking_date = datetime(2022, 3, 11, 10, 15, 0)
        event_date = datetime(2022, 5, 15, 20, 00, 0)
        pro_user = users_factories.ProFactory()
        user_offerer = offerers_factories.UserOffererFactory(user=pro_user)
        redactor = educational_factories.EducationalRedactorFactory(
            email="reda.ktheur@example.com", firstName="Reda", lastName="Khteur", civility="M."
        )
        collective_stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name="Le chant des cigales",
            collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            beginningDatetime=event_date,
            price=1200,
        )
        educational_factories.ReimbursedCollectiveBookingFactory(
            educationalRedactor=redactor,
            collectiveStock=collective_stock,
            dateCreated=booking_date,
            cancellationLimitDate=event_date - timedelta(days=15),
            confirmationDate=booking_date + timedelta(days=1, hours=2),
            dateUsed=event_date + timedelta(days=1),
            reimbursementDate=event_date + timedelta(days=15),
        )

        # When
        client = client.with_session_auth(pro_user.email)
        response = client.get(f"collective/bookings/pro?{BOOKING_PERIOD_PARAMS}")

        # Then
        assert response.status_code == 200
        booking_recap = response.json["bookingsRecap"][0]
        assert booking_recap["booking_status"] == "reimbursed"
        assert booking_recap["booking_status_history"] == [
            {
                "status": "booked",
                "date": "2022-03-12T13:15:00+01:00",
            },
            {
                "status": "confirmed",
                "date": "2022-04-30T22:00:00+02:00",
            },
            {
                "status": "validated",
                "date": "2022-05-16T22:00:00+02:00",
            },
            {
                "status": "reimbursed",
                "date": "2022-05-30T22:00:00+02:00",
            },
        ]

    @freeze_time("2022-05-10 15:00:00")
    def test_when_collective_booking_pending_and_cancellationLimitDate_has_passed_should_show_prereserve_only(
        self, client
    ):
        # Given
        booking_date = datetime(2022, 3, 11, 10, 15, 0)
        event_date = datetime(2022, 5, 15, 20, 00, 0)
        pro_user = users_factories.ProFactory()
        user_offerer = offerers_factories.UserOffererFactory(user=pro_user)
        redactor = educational_factories.EducationalRedactorFactory(
            email="reda.ktheur@example.com", firstName="Reda", lastName="Khteur", civility="M."
        )
        collective_stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name="Le chant des cigales",
            collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            beginningDatetime=event_date,
            price=1200,
        )
        educational_factories.PendingCollectiveBookingFactory(
            educationalRedactor=redactor,
            collectiveStock=collective_stock,
            dateCreated=booking_date,
            cancellationLimitDate=event_date - timedelta(days=15),
        )

        # When
        client = client.with_session_auth(pro_user.email)
        response = client.get(f"collective/bookings/pro?{BOOKING_PERIOD_PARAMS}")

        # Then
        assert response.status_code == 200
        booking_recap = response.json["bookingsRecap"][0]
        assert booking_recap["booking_status"] == "pending"
        assert booking_recap["booking_status_history"] == [
            {
                "status": "pending",
                "date": "2022-03-11T11:15:00+01:00",
            },
        ]

    @freeze_time("2022-05-01 15:00:00")
    def test_when_filter_venue_id(self, client):
        # Given
        booking_date = datetime(2022, 3, 11, 10, 15, 0)
        pro_user = users_factories.ProFactory()
        user_offerer = offerers_factories.UserOffererFactory(user=pro_user)
        redactor = educational_factories.EducationalRedactorFactory(
            email="reda.ktheur@example.com", firstName="Reda", lastName="Khteur", civility="M."
        )
        collective_stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name="Le chant des cigales",
            collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            beginningDatetime=datetime(2022, 5, 15, 10, 15, 0),
            price=1200,
        )
        booking = educational_factories.CollectiveBookingFactory(
            educationalRedactor=redactor,
            collectiveStock=collective_stock,
            dateCreated=booking_date,
            status=CollectiveBookingStatus.CONFIRMED,
            confirmationDate=booking_date + timedelta(days=1),
        )
        educational_factories.CollectiveBookingFactory(
            educationalRedactor=redactor,
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            dateCreated=booking_date,
            status=CollectiveBookingStatus.CONFIRMED,
            confirmationDate=booking_date + timedelta(days=1),
        )

        # When
        venue_id = humanize(collective_stock.collectiveOffer.venueId)
        client = client.with_session_auth(pro_user.email)
        response = client.get(f"collective/bookings/pro?{BOOKING_PERIOD_PARAMS}&venueId={venue_id}")

        # Then
        expected_bookings_recap = [
            {
                "stock": {
                    "offer_name": "Le chant des cigales",
                    "offer_identifier": humanize(collective_stock.collectiveOfferId),
                    "offer_is_educational": True,
                    "event_beginning_datetime": "2022-05-15T12:15:00+02:00",
                    "offer_isbn": None,
                    "number_of_tickets": collective_stock.numberOfTickets,
                },
                "beneficiary": {
                    "email": redactor.email,
                    "firstname": redactor.firstName,
                    "lastname": redactor.lastName,
                    "phonenumber": None,
                },
                "booking_identifier": humanize(booking.id),
                "booking_date": "2022-03-11T11:15:00+01:00",
                "booking_amount": 1200.00,
                "booking_token": None,
                "booking_status": "confirmed",
                "booking_is_duo": False,
                "booking_status_history": [
                    {
                        "status": "booked",
                        "date": "2022-03-12T11:15:00+01:00",
                    },
                    {
                        "status": "confirmed",
                        "date": "2022-04-30T12:15:00+02:00",
                    },
                ],
            }
        ]

        assert response.status_code == 200
        assert response.json["page"] == 1
        assert response.json["pages"] == 1
        assert response.json["total"] == 1
        assert response.json["bookingsRecap"] == expected_bookings_recap

    @freeze_time("2022-05-01 15:00:00")
    def test_when_filter_event_date(self, client):
        # Given
        booking_date = datetime(2022, 3, 11, 10, 15, 0)
        pro_user = users_factories.ProFactory()
        user_offerer = offerers_factories.UserOffererFactory(user=pro_user)
        redactor = educational_factories.EducationalRedactorFactory(
            email="reda.ktheur@example.com", firstName="Reda", lastName="Khteur", civility="M."
        )
        collective_stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name="Le chant des cigales",
            collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            beginningDatetime=datetime(2022, 5, 15, 10, 15, 0),
            price=1200,
        )
        booking = educational_factories.CollectiveBookingFactory(
            educationalRedactor=redactor,
            collectiveStock=collective_stock,
            dateCreated=booking_date,
            status=CollectiveBookingStatus.CONFIRMED,
            confirmationDate=booking_date + timedelta(days=1),
        )
        educational_factories.CollectiveBookingFactory(
            educationalRedactor=redactor,
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            collectiveStock__beginningDatetime=datetime(2022, 5, 16, 10, 15, 0),
            dateCreated=booking_date,
            status=CollectiveBookingStatus.CONFIRMED,
            confirmationDate=booking_date + timedelta(days=1),
        )

        # When
        client = client.with_session_auth(pro_user.email)
        response = client.get(f"collective/bookings/pro?{BOOKING_PERIOD_PARAMS}&eventDate=2022-05-15T00:00:00Z")

        # Then
        expected_bookings_recap = [
            {
                "stock": {
                    "offer_name": "Le chant des cigales",
                    "offer_identifier": humanize(collective_stock.collectiveOfferId),
                    "offer_is_educational": True,
                    "event_beginning_datetime": "2022-05-15T12:15:00+02:00",
                    "offer_isbn": None,
                    "number_of_tickets": collective_stock.numberOfTickets,
                },
                "beneficiary": {
                    "email": redactor.email,
                    "firstname": redactor.firstName,
                    "lastname": redactor.lastName,
                    "phonenumber": None,
                },
                "booking_identifier": humanize(booking.id),
                "booking_date": "2022-03-11T11:15:00+01:00",
                "booking_amount": 1200.00,
                "booking_token": None,
                "booking_status": "confirmed",
                "booking_is_duo": False,
                "booking_status_history": [
                    {
                        "status": "booked",
                        "date": "2022-03-12T11:15:00+01:00",
                    },
                    {
                        "status": "confirmed",
                        "date": "2022-04-30T12:15:00+02:00",
                    },
                ],
            }
        ]

        assert response.status_code == 200
        assert response.json["page"] == 1
        assert response.json["pages"] == 1
        assert response.json["total"] == 1
        assert response.json["bookingsRecap"] == expected_bookings_recap

    @freeze_time("2022-05-20 15:00:00")
    def test_when_filter_booking_status(self, client):
        # Given
        booking_date = datetime(2022, 2, 11, 10, 15, 0)
        event_date = datetime(2022, 3, 10, 10, 15, 0)
        pro_user = users_factories.ProFactory()
        user_offerer = offerers_factories.UserOffererFactory(user=pro_user)
        redactor = educational_factories.EducationalRedactorFactory(
            email="reda.ktheur@example.com", firstName="Reda", lastName="Khteur", civility="M."
        )
        collective_stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__name="Le chant des cigales",
            collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            beginningDatetime=event_date,
            price=1200,
        )
        booking = educational_factories.UsedCollectiveBookingFactory(
            educationalRedactor=redactor,
            collectiveStock=collective_stock,
            dateCreated=booking_date,
            confirmationDate=booking_date + timedelta(days=1),
            dateUsed=event_date + timedelta(days=1),
        )
        educational_factories.CollectiveBookingFactory(
            educationalRedactor=redactor,
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            collectiveStock__beginningDatetime=datetime(2022, 5, 16, 10, 15, 0),
            dateCreated=datetime(2022, 3, 11, 10, 15, 0),
            status=CollectiveBookingStatus.CONFIRMED,
            confirmationDate=booking_date + timedelta(days=1),
        )

        # When
        client = client.with_session_auth(pro_user.email)
        response = client.get(f"collective/bookings/pro?{BOOKING_PERIOD_PARAMS}&bookingStatusFilter=validated")

        # Then
        # FIXME (gvanneste) : voir pour pouvoir fixer la date limtie d'annulation qu'on souhaite (ici event - 1 jour)
        expected_bookings_recap = [
            {
                "stock": {
                    "offer_name": "Le chant des cigales",
                    "offer_identifier": humanize(collective_stock.collectiveOfferId),
                    "offer_is_educational": True,
                    "event_beginning_datetime": "2022-03-10T11:15:00+01:00",
                    "offer_isbn": None,
                    "number_of_tickets": collective_stock.numberOfTickets,
                },
                "beneficiary": {
                    "email": redactor.email,
                    "firstname": redactor.firstName,
                    "lastname": redactor.lastName,
                    "phonenumber": None,
                },
                "booking_identifier": humanize(booking.id),
                "booking_date": "2022-02-11T11:15:00+01:00",
                "booking_amount": 1200.00,
                "booking_token": None,
                "booking_status": "validated",
                "booking_is_duo": False,
                "booking_status_history": [
                    {
                        "status": "booked",
                        "date": "2022-02-12T11:15:00+01:00",
                    },
                    {
                        "status": "confirmed",
                        "date": "2022-02-23T11:15:00+01:00",  # la date limite d'annulation est automatiquement calculée en db et écrase celle fournie. Dans notre cas : 15 jours avant date evènement.
                    },
                    {
                        "status": "validated",
                        "date": "2022-03-11T11:15:00+01:00",
                    },
                ],
            }
        ]

        assert response.status_code == 200
        assert response.json["page"] == 1
        assert response.json["pages"] == 1
        assert response.json["total"] == 1
        assert response.json["bookingsRecap"] == expected_bookings_recap


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def when_page_number_is_not_a_number(self, client):
        pro = users_factories.ProFactory()

        client = client.with_session_auth(pro.email)
        response = client.get(f"collective/bookings/pro?{BOOKING_PERIOD_PARAMS}&page=not-a-number")

        assert response.status_code == 400
        assert response.json["page"] == ["Saisissez un nombre valide"]

    def when_booking_period_and_event_date_is_not_given(self, client):
        pro = users_factories.ProFactory()

        client = client.with_session_auth(pro.email)
        response = client.get("collective/bookings/pro")

        assert response.status_code == 400
        assert response.json["eventDate"] == ["Ce champ est obligatoire si aucune période n'est renseignée."]
        assert response.json["bookingPeriodBeginningDate"] == [
            "Ce champ est obligatoire si la date d'évènement n'est renseignée"
        ]
        assert response.json["bookingPeriodEndingDate"] == [
            "Ce champ est obligatoire si la date d'évènement n'est renseignée"
        ]
