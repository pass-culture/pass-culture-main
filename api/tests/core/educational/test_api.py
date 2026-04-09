import datetime
import decimal
import logging
from unittest import mock

import dateutil
import pytest
import time_machine

from pcapi.core.educational import exceptions
from pcapi.core.educational import factories
from pcapi.core.educational import models
from pcapi.core.educational.api import booking as educational_api_booking
from pcapi.core.educational.api import institution as institution_api
from pcapi.core.educational.api import offer as educational_api_offer
from pcapi.core.educational.api import stock as educational_api_stock
from pcapi.core.mails import testing as mails_testing
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.routes.serialization import collective_stock_serialize
from pcapi.utils import date as date_utils
from pcapi.utils import db as db_utils


@pytest.mark.usefixtures("db_session")
class CreateCollectiveOfferStocksTest:
    @time_machine.travel("2020-11-17 15:00:00")
    def should_create_one_stock_on_collective_offer_stock_creation(self) -> None:
        start_date = dateutil.parser.parse("2021-12-15T20:00:00Z")
        factories.EducationalYearFactory(
            beginningDate=start_date - datetime.timedelta(days=100),
            expirationDate=start_date + datetime.timedelta(days=100),
        )
        offer = factories.CollectiveOfferFactory()
        new_stock = collective_stock_serialize.CollectiveStockCreationBodyModel(
            offerId=offer.id,
            startDatetime=start_date,
            endDatetime=start_date,
            bookingLimitDatetime=dateutil.parser.parse("2021-12-05T00:00:00Z"),
            totalPrice=1200,
            numberOfTickets=35,
            educationalPriceDetail="hello",
        )

        stock_created = educational_api_stock.create_collective_stock(stock_data=new_stock)

        stock = db.session.query(models.CollectiveStock).filter_by(id=stock_created.id).one()
        assert stock.startDatetime == datetime.datetime.fromisoformat("2021-12-15T20:00:00")
        assert stock.bookingLimitDatetime == datetime.datetime.fromisoformat("2021-12-05T00:00:00")
        assert stock.price == 1200
        assert stock.numberOfTickets == 35

    @time_machine.travel("2020-11-17 15:00:00")
    def should_set_booking_limit_datetime_to_beginning_datetime_when_not_provided(self) -> None:
        start_date = dateutil.parser.parse("2021-12-15T20:00:00Z")
        factories.EducationalYearFactory(
            beginningDate=start_date - datetime.timedelta(days=100),
            expirationDate=start_date + datetime.timedelta(days=100),
        )
        offer = factories.CollectiveOfferFactory()
        new_stock = collective_stock_serialize.CollectiveStockCreationBodyModel(
            offerId=offer.id,
            startDatetime=start_date,
            endDatetime=start_date,
            bookingLimitDatetime=start_date,
            totalPrice=1200,
            numberOfTickets=35,
            educationalPriceDetail="hello",
        )

        stock_created = educational_api_stock.create_collective_stock(stock_data=new_stock)

        stock = db.session.query(models.CollectiveStock).filter_by(id=stock_created.id).one()
        assert stock.bookingLimitDatetime == dateutil.parser.parse("2021-12-15T20:00:00")

    @time_machine.travel("2020-11-17 15:00:00")
    @pytest.mark.parametrize("status", [OfferValidationStatus.REJECTED, OfferValidationStatus.PENDING])
    def test_create_stock_for_rejected_or_pending_offer_fails(self, status) -> None:
        start_date = dateutil.parser.parse("2022-01-17T22:00:00Z")
        factories.EducationalYearFactory(
            beginningDate=start_date - datetime.timedelta(days=100),
            expirationDate=start_date + datetime.timedelta(days=100),
        )
        offer = factories.CollectiveOfferFactory(validation=status)
        created_stock_data = collective_stock_serialize.CollectiveStockCreationBodyModel(
            offerId=offer.id,
            startDatetime=start_date,
            endDatetime=start_date,
            bookingLimitDatetime=dateutil.parser.parse("2021-12-31T20:00:00Z"),
            totalPrice=1500,
            numberOfTickets=38,
            educationalPriceDetail="hello",
        )

        with pytest.raises(exceptions.EducationalException) as error:
            educational_api_stock.create_collective_stock(stock_data=created_stock_data)

        assert error.value.errors == {
            "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
        }
        assert db.session.query(models.CollectiveStock).count() == 0


@pytest.mark.usefixtures("db_session")
class UnindexExpiredOffersTest:
    @pytest.mark.settings(ALGOLIA_DELETING_COLLECTIVE_OFFERS_CHUNK_SIZE=3)
    @mock.patch("pcapi.core.search.unindex_collective_offer_template_ids")
    def test_default_run_template(self, mock_unindex_collective_offer_template_ids) -> None:
        # Expired template offer
        collective_offer_template_1 = factories.CollectiveOfferTemplateFactory(
            dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=9),
            dateRange=db_utils.make_timerange(
                start=date_utils.get_naive_utc_now() - datetime.timedelta(days=7),
                end=date_utils.get_naive_utc_now() - datetime.timedelta(days=3),
            ),
        )
        # Non expired template offer
        factories.CollectiveOfferTemplateFactory()
        # Expired template offer
        collective_offer_template_2 = factories.CollectiveOfferTemplateFactory(
            dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=9),
            dateRange=db_utils.make_timerange(
                start=date_utils.get_naive_utc_now() - datetime.timedelta(days=7),
                end=date_utils.get_naive_utc_now() - datetime.timedelta(hours=1),
            ),
        )
        # Archived template offer
        collective_offer_template_3 = factories.CollectiveOfferTemplateFactory(
            dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=9),
            dateRange=db_utils.make_timerange(
                start=date_utils.get_naive_utc_now() - datetime.timedelta(days=3),
                end=date_utils.get_naive_utc_now() + datetime.timedelta(days=3),
            ),
            dateArchived=date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
            isActive=False,
        )
        # Non expired template offer with dateRange overlapping today
        factories.CollectiveOfferTemplateFactory(
            dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=9),
            dateRange=db_utils.make_timerange(
                start=date_utils.get_naive_utc_now() - datetime.timedelta(days=3),
                end=date_utils.get_naive_utc_now() + datetime.timedelta(days=3),
            ),
        )

        educational_api_offer.unindex_expired_or_archived_collective_offers_template()

        assert mock_unindex_collective_offer_template_ids.mock_calls == [
            mock.call([collective_offer_template_1.id, collective_offer_template_2.id, collective_offer_template_3.id]),
        ]


@pytest.mark.usefixtures("db_session")
class EACPendingBookingWithConfirmationLimitDate3DaysTest:
    @time_machine.travel("2022-11-26 18:29")
    def test_with_pending_booking_limit_date_in_3_days(self) -> None:
        booking = factories.PendingCollectiveBookingFactory(
            confirmationLimitDate="2022-11-29 18:29",
            collectiveStock__collectiveOffer__bookingEmails=["pouet@example.com", "plouf@example.com"],
            collectiveStock__collectiveOffer__locationType=models.CollectiveLocationType.SCHOOL,
        )

        educational_api_booking.notify_pro_pending_booking_confirmation_limit_in_3_days()

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["params"] == {
            "OFFER_NAME": booking.collectiveStock.collectiveOffer.name,
            "VENUE_NAME": booking.collectiveStock.collectiveOffer.venue.name,
            "EVENT_DATE": "dimanche 27 novembre 2022",
            "START_DATE": "dimanche 27 novembre 2022",
            "START_HOUR": "19h29",
            "END_DATE": "dimanche 27 novembre 2022",
            "END_HOUR": "19h29",
            "USER_FIRSTNAME": booking.educationalRedactor.firstName,
            "USER_LASTNAME": booking.educationalRedactor.lastName,
            "USER_EMAIL": booking.educationalRedactor.email,
            "EDUCATIONAL_INSTITUTION_NAME": booking.educationalInstitution.name,
            "BOOKING_ID": booking.id,
            "COLLECTIVE_OFFER_ID": booking.collectiveStock.collectiveOffer.id,
            "COLLECTIVE_OFFER_ADDRESS": "En établissement scolaire",
        }

    def test_with_pending_booking_limit_date_in_less_or_more_than_3_days(self) -> None:
        factories.PendingCollectiveBookingFactory(
            confirmationLimitDate="2022-11-28 18:29",
            collectiveStock__collectiveOffer__bookingEmails=["pouet@example.com", "plouf@example.com"],
        )

        factories.PendingCollectiveBookingFactory(
            confirmationLimitDate="2022-12-01 18:29",
            collectiveStock__collectiveOffer__bookingEmails=["pouet@example.com", "plouf@example.com"],
        )

        educational_api_booking.notify_pro_pending_booking_confirmation_limit_in_3_days()

        assert len(mails_testing.outbox) == 0

    def test_with_confirmed_booking_confirmation_limit_date_in_3_days(self) -> None:

        factories.CollectiveBookingFactory(
            confirmationLimitDate="2022-11-29 18:29",
            collectiveStock__collectiveOffer__bookingEmails=["pouet@example.com", "plouf@example.com"],
        )

        educational_api_booking.notify_pro_pending_booking_confirmation_limit_in_3_days()

        assert len(mails_testing.outbox) == 0


@pytest.mark.usefixtures("db_session")
class NotifyProUserOneDayTest:
    @time_machine.travel("2020-01-05 10:00:00")
    def test_notify_pro_users_one_day_before(self) -> None:
        # should send email
        booking1 = factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking1",
            collectiveStock__collectiveOffer__bookingEmails=["booking1@example.com", "booking1-2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            status=models.CollectiveBookingStatus.CONFIRMED,
        )
        # cancelled should not send email
        factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking2",
            collectiveStock__collectiveOffer__bookingEmails=["booking2+1@example.com", "booking2+2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            status=models.CollectiveBookingStatus.CANCELLED,
        )
        # should send email (linked to a cancelled one)
        booking3 = factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking3",
            collectiveStock__collectiveOffer__bookingEmails=["booking3+2@example.com", "booking3+1@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            status=models.CollectiveBookingStatus.CONFIRMED,
        )
        # cancelled should not send email (linked to a good one)
        factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking4",
            collectiveStock__collectiveOffer__bookingEmails=["booking4+1@example.com", "booking4+2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            collectiveStock=booking3.collectiveStock,
            status=models.CollectiveBookingStatus.CANCELLED,
        )
        # no emails registered, should not send email
        factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking5",
            collectiveStock__collectiveOffer__bookingEmails=[],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            status=models.CollectiveBookingStatus.CONFIRMED,
        )
        # old booking should not be selected
        factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking6",
            collectiveStock__collectiveOffer__bookingEmails=["booking6+1@example.com", "booking6+2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2019, 1, 6),
            status=models.CollectiveBookingStatus.CONFIRMED,
        )
        # too far in the future to be selected
        factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking7",
            collectiveStock__collectiveOffer__bookingEmails=["booking7+1@example.com", "booking7+2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2021, 1, 6),
            status=models.CollectiveBookingStatus.CONFIRMED,
        )
        educational_api_booking.notify_pro_users_one_day_before()
        assert len(mails_testing.outbox) == 2

        for mail in mails_testing.outbox:
            params = mail["params"]
            assert params["OFFER_NAME"] in ("booking1", "booking3")
            if params["OFFER_NAME"] == booking1.collectiveStock.collectiveOffer.name:
                assert params == {
                    "OFFER_NAME": booking1.collectiveStock.collectiveOffer.name,
                    "VENUE_NAME": booking1.collectiveStock.collectiveOffer.venue.name,
                    "EVENT_HOUR": "01h00",
                    "START_DATE": "lundi 6 janvier 2020",
                    "START_HOUR": "01h00",
                    "END_DATE": "lundi 6 janvier 2020",
                    "END_HOUR": "01h00",
                    "QUANTITY": 1,
                    "PRICE": str(booking1.collectiveStock.price),
                    "FORMATTED_PRICE": "100 €",
                    "REDACTOR_FIRSTNAME": booking1.educationalRedactor.firstName,
                    "REDACTOR_LASTNAME": booking1.educationalRedactor.lastName,
                    "REDACTOR_EMAIL": booking1.educationalRedactor.email,
                    "EDUCATIONAL_INSTITUTION_NAME": booking1.educationalInstitution.name,
                    "COLLECTIVE_OFFER_ADDRESS": "À déterminer avec l'enseignant",
                }
                assert mail["To"] == booking1.collectiveStock.collectiveOffer.bookingEmails[0]
                assert mail["Bcc"] == booking1.collectiveStock.collectiveOffer.bookingEmails[1]

            elif params["OFFER_NAME"] == booking3.collectiveStock.collectiveOffer.name:
                assert params == {
                    "OFFER_NAME": booking3.collectiveStock.collectiveOffer.name,
                    "VENUE_NAME": booking3.collectiveStock.collectiveOffer.venue.name,
                    "EVENT_HOUR": "01h00",
                    "START_DATE": "lundi 6 janvier 2020",
                    "START_HOUR": "01h00",
                    "END_DATE": "lundi 6 janvier 2020",
                    "END_HOUR": "01h00",
                    "QUANTITY": 1,
                    "PRICE": str(booking3.collectiveStock.price),
                    "FORMATTED_PRICE": "100 €",
                    "REDACTOR_FIRSTNAME": booking3.educationalRedactor.firstName,
                    "REDACTOR_LASTNAME": booking3.educationalRedactor.lastName,
                    "REDACTOR_EMAIL": booking3.educationalRedactor.email,
                    "EDUCATIONAL_INSTITUTION_NAME": booking3.educationalInstitution.name,
                    "COLLECTIVE_OFFER_ADDRESS": "À déterminer avec l'enseignant",
                }
                assert mail["To"] == booking3.collectiveStock.collectiveOffer.bookingEmails[0]
                assert mail["Bcc"] == booking3.collectiveStock.collectiveOffer.bookingEmails[1]


@pytest.mark.usefixtures("db_session")
class NotifyProUserOneDayAfterTest:
    @time_machine.travel("2020-01-07 10:00:00")
    def test_notify_pro_users_one_day_after(self) -> None:
        # should send email
        booking1 = factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking1",
            collectiveStock__collectiveOffer__bookingEmails=["booking1@example.com", "booking1-2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            status=models.CollectiveBookingStatus.CONFIRMED,
        )
        # cancelled should not send email
        factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking2",
            collectiveStock__collectiveOffer__bookingEmails=["booking2+1@example.com", "booking2+2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            status=models.CollectiveBookingStatus.CANCELLED,
        )
        # should send email (linked to a cancelled one)
        booking3 = factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking3",
            collectiveStock__collectiveOffer__bookingEmails=["booking3+2@example.com", "booking3+1@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            status=models.CollectiveBookingStatus.CONFIRMED,
        )
        # cancelled should not send email (linked to a good one)
        factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking4",
            collectiveStock__collectiveOffer__bookingEmails=["booking4+1@example.com", "booking4+2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            collectiveStock=booking3.collectiveStock,
            status=models.CollectiveBookingStatus.CANCELLED,
        )
        # no emails registered, should not send email
        factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking5",
            collectiveStock__collectiveOffer__bookingEmails=[],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            status=models.CollectiveBookingStatus.CONFIRMED,
        )
        # old booking should not be selected
        factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking6",
            collectiveStock__collectiveOffer__bookingEmails=["booking6+1@example.com", "booking6+2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2019, 1, 6),
            status=models.CollectiveBookingStatus.CONFIRMED,
        )
        # too far in the future to be selected
        factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking7",
            collectiveStock__collectiveOffer__bookingEmails=["booking7+1@example.com", "booking7+2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2021, 1, 6),
            status=models.CollectiveBookingStatus.CONFIRMED,
        )
        # should not send email only the endDate should be taken into account
        factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking8",
            collectiveStock__collectiveOffer__bookingEmails=["booking8+1@example.com", "booking8+2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            collectiveStock__endDatetime=datetime.datetime(2020, 1, 9),  # -> a different endDatetime
            status=models.CollectiveBookingStatus.CONFIRMED,
        )
        # should not send email: start date is passed but booking is pending
        factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking9",
            collectiveStock__collectiveOffer__bookingEmails=["booking9+1@example.com", "booking9+2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            collectiveStock__endDatetime=datetime.datetime(2020, 1, 6),
            status=models.CollectiveBookingStatus.PENDING,
        )

        educational_api_booking.notify_pro_users_one_day_after()
        assert len(mails_testing.outbox) == 2

        for mail in mails_testing.outbox:
            params = mail["params"]
            assert params["OFFER_NAME"] in ("booking1", "booking3")
            if params["OFFER_NAME"] == booking1.collectiveStock.collectiveOffer.name:
                assert params == {
                    "OFFER_NAME": booking1.collectiveStock.collectiveOffer.name,
                    "VENUE_NAME": booking1.collectiveStock.collectiveOffer.venue.name,
                    "EVENT_HOUR": "01h00",
                    "EVENT_DATE": "lundi 6 janvier 2020",
                    "START_DATE": "lundi 6 janvier 2020",
                    "START_HOUR": "01h00",
                    "END_DATE": "lundi 6 janvier 2020",
                    "END_HOUR": "01h00",
                    "EDUCATIONAL_INSTITUTION_NAME": booking1.educationalInstitution.name,
                    "COLLECTIVE_OFFER_ADDRESS": "À déterminer avec l'enseignant",
                }
                assert mail["To"] == booking1.collectiveStock.collectiveOffer.bookingEmails[0]
                assert mail["Bcc"] == booking1.collectiveStock.collectiveOffer.bookingEmails[1]

            elif params["OFFER_NAME"] == booking3.collectiveStock.collectiveOffer.name:
                assert params == {
                    "OFFER_NAME": booking3.collectiveStock.collectiveOffer.name,
                    "VENUE_NAME": booking3.collectiveStock.collectiveOffer.venue.name,
                    "EVENT_HOUR": "01h00",
                    "EVENT_DATE": "lundi 6 janvier 2020",
                    "START_DATE": "lundi 6 janvier 2020",
                    "START_HOUR": "01h00",
                    "END_DATE": "lundi 6 janvier 2020",
                    "END_HOUR": "01h00",
                    "EDUCATIONAL_INSTITUTION_NAME": booking3.educationalInstitution.name,
                    "COLLECTIVE_OFFER_ADDRESS": "À déterminer avec l'enseignant",
                }
                assert mail["To"] == booking3.collectiveStock.collectiveOffer.bookingEmails[0]
                assert mail["Bcc"] == booking3.collectiveStock.collectiveOffer.bookingEmails[1]


@pytest.mark.usefixtures("db_session")
class SynchroniseRuralityLevelTest:
    def test_should_update_rurality_level(self):
        et1 = factories.EducationalInstitutionFactory(ruralLevel=None)
        et2 = factories.EducationalInstitutionFactory(ruralLevel=models.InstitutionRuralLevel.RURAL_A_HABITAT_DISPERSE)
        et3 = factories.EducationalInstitutionFactory(ruralLevel=models.InstitutionRuralLevel.RURAL_A_HABITAT_DISPERSE)
        et4 = factories.EducationalInstitutionFactory(ruralLevel=models.InstitutionRuralLevel.RURAL_A_HABITAT_DISPERSE)

        mock_path = "pcapi.connectors.big_query.TestingBackend.run_query"
        with mock.patch(mock_path) as mock_run_query:
            mock_run_query.return_value = [
                {
                    "institution_id": str(et1.id),
                    "institution_rural_level": models.InstitutionRuralLevel.RURAL_A_HABITAT_DISPERSE.value,
                },
                {
                    "institution_id": str(et2.id),
                    "institution_rural_level": models.InstitutionRuralLevel.RURAL_A_HABITAT_DISPERSE.value,
                },
                {
                    "institution_id": str(et3.id),
                    "institution_rural_level": models.InstitutionRuralLevel.GRANDS_CENTRES_URBAINS.value,
                },
                {
                    "institution_id": str(et4.id),
                    "institution_rural_level": None,
                },
            ]
            institution_api.synchronise_rurality_level()

        institutions = db.session.query(models.EducationalInstitution).order_by(models.EducationalInstitution.id).all()
        assert [i.id for i in institutions] == [et1.id, et2.id, et3.id, et4.id]
        assert institutions[0].ruralLevel == models.InstitutionRuralLevel.RURAL_A_HABITAT_DISPERSE
        assert institutions[1].ruralLevel == models.InstitutionRuralLevel.RURAL_A_HABITAT_DISPERSE
        assert institutions[2].ruralLevel == models.InstitutionRuralLevel.GRANDS_CENTRES_URBAINS
        assert institutions[3].ruralLevel == None


@pytest.mark.usefixtures("db_session")
class SynchroniseInstitutionsGeolocationTest:
    def test_synchronise_institutions_geolocation(self):
        factories.EducationalCurrentYearFactory()

        institution = factories.EducationalInstitutionFactory(institutionId="0470009E", latitude=None, longitude=None)
        institution_with_values = factories.EducationalInstitutionFactory(
            institutionId="0470010E", latitude=42, longitude=2
        )

        # The backend for test is in AdageSpyClient#get_adage_educational_institutions
        institution_not_present = factories.EducationalInstitutionFactory(
            institutionId="0111111E", latitude=None, longitude=None
        )

        institution_api.synchronise_institutions_geolocation()

        assert institution.latitude == decimal.Decimal("48.8534100")
        assert institution.longitude == decimal.Decimal("2.3488000")
        assert institution_with_values.latitude == decimal.Decimal("48.8534100")
        assert institution_with_values.longitude == decimal.Decimal("2.3488000")
        assert institution_not_present.latitude is None
        assert institution_not_present.longitude is None


@pytest.mark.usefixtures("db_session")
class UpdateInstitutionsEducationalProgramTest:
    def test_update_program(self, caplog):
        program = factories.EducationalInstitutionProgramFactory(name="The Program")
        now = datetime.datetime.now()
        past = now - datetime.timedelta(days=100)
        past_timespan = db_utils.make_timerange(past, now - datetime.timedelta(days=2))
        current_timespan = db_utils.make_timerange(past, None)

        uai_1 = "11111111"
        uai_2 = "11111112"
        uai_3 = "11111113"
        uai_4 = "11111114"
        uai_5 = "11111115"
        uai_6 = "11111116"
        uais = [uai_1, uai_3, uai_5]

        # institution not associated to the program, added to the program
        # expected: link institution to the program, log an info
        institution_1 = factories.EducationalInstitutionFactory(institutionId=uai_1)
        assert len(institution_1.programAssociations) == 0
        # institution not associated to the program, not added to the program
        # expected: no change
        institution_2 = factories.EducationalInstitutionFactory(institutionId=uai_2)
        assert len(institution_2.programAssociations) == 0

        # institution previously associated to the program, added to the program
        # expected: no change, log an error
        institution_3 = factories.EducationalInstitutionFactory(institutionId=uai_3)
        association_3 = factories.EducationalInstitutionProgramAssociationFactory(
            institution=institution_3, program=program, timespan=past_timespan
        )
        association_3_timespan = association_3.timespan
        # institution previously associated to the program, not added to the program
        # expected: no change
        institution_4 = factories.EducationalInstitutionFactory(institutionId=uai_4)
        association_4 = factories.EducationalInstitutionProgramAssociationFactory(
            institution=institution_4, program=program, timespan=past_timespan
        )
        association_4_timespan = association_4.timespan

        # institution currently associated to the program, added to the program
        # expected: no change
        institution_5 = factories.EducationalInstitutionFactory(institutionId=uai_5)
        association_5 = factories.EducationalInstitutionProgramAssociationFactory(
            institution=institution_5, program=program, timespan=current_timespan
        )
        association_5_timespan = association_5.timespan
        # institution currently associated to the program, not added to the program
        # expected: no change, log an error
        institution_6 = factories.EducationalInstitutionFactory(institutionId=uai_6)
        association_6 = factories.EducationalInstitutionProgramAssociationFactory(
            institution=institution_6, program=program, timespan=current_timespan
        )
        association_6_timespan = association_6.timespan

        with caplog.at_level(logging.INFO):
            institution_api._update_institutions_educational_program(educational_program=program, uais=uais, start=now)

        [association_1] = institution_1.programAssociations
        assert association_1.programId == program.id
        assert association_1.timespan == db_utils.make_timerange(now, None)

        # check that associations (and their timespan) have not changed
        assert len(institution_2.programAssociations) == 0
        assert institution_3.programAssociations == [association_3]
        assert association_3.timespan == association_3_timespan
        assert institution_4.programAssociations == [association_4]
        assert association_4.timespan == association_4_timespan
        assert institution_5.programAssociations == [association_5]
        assert association_5.timespan == association_5_timespan
        assert institution_6.programAssociations == [association_6]
        assert association_6.timespan == association_6_timespan

        logs = [(log_record.message, log_record.extra, log_record.levelname) for log_record in caplog.records]
        assert logs == [
            (
                "UAIs in DB are associated with program but not present in data",
                {"program_name": "The Program", "uais": {"11111116"}},
                "WARNING",
            ),
            ("Linking UAI 11111111 to program The Program", {}, "INFO"),
            (
                "UAI was previously associated with program, cannot add it back",
                {"program_name": "The Program", "uai": "11111113"},
                "WARNING",
            ),
        ]


class CheckAllowedActionTest:
    def test_patch_details_fields_public(self):
        # if the public api schema PatchCollectiveOfferBodyModel is updated, we need to check PATCH_DETAILS_FIELDS_PUBLIC
        # which is computed from the list of fields of the schema
        # e.g if we add a new field, we need to make sure that the field coresponds to the allowed action CAN_EDIT_DETAILS
        # if not, it must be manually removed from PATCH_DETAILS_FIELDS_PUBLIC (and checked separately)

        expected = {
            "name",
            "description",
            "venueId",
            "formats",
            "bookingEmails",
            "contactEmail",
            "contactPhone",
            "domains",
            "students",
            "location",
            "interventionArea",
            "durationMinutes",
            "audioDisabilityCompliant",
            "mentalDisabilityCompliant",
            "motorDisabilityCompliant",
            "visualDisabilityCompliant",
            "imageCredit",
            "imageFile",
            "nationalProgramId",
        }
        assert len(educational_api_offer.PATCH_DETAILS_FIELDS_PUBLIC) == len(expected)
        assert set(educational_api_offer.PATCH_DETAILS_FIELDS_PUBLIC) == expected
