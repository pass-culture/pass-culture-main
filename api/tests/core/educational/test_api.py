import datetime
import json
from unittest import mock

import dateutil
from flask import current_app
from freezegun.api import freeze_time
import pytest

from pcapi.core import search
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.api import adage as educational_api_adage
from pcapi.core.educational.api import booking as educational_api_booking
from pcapi.core.educational.api import stock as educational_api_stock
from pcapi.core.educational.api.offer import unindex_expired_collective_offers
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveStock
import pcapi.core.search.testing as search_testing
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
from pcapi.models import api_errors
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.routes.serialization import collective_stock_serialize


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
@pytest.mark.usefixtures("db_session")
class CreateCollectiveOfferStocksTest:
    def should_create_one_stock_on_collective_offer_stock_creation(self) -> None:
        # Given
        user_pro = users_factories.ProFactory()
        offer = educational_factories.CollectiveOfferFactory()
        new_stock = collective_stock_serialize.CollectiveStockCreationBodyModel(
            offerId=offer.id,
            beginningDatetime=dateutil.parser.parse("2021-12-15T20:00:00Z"),
            bookingLimitDatetime=dateutil.parser.parse("2021-12-05T00:00:00Z"),
            totalPrice=1200,
            numberOfTickets=35,
        )

        # When
        stock_created = educational_api_stock.create_collective_stock(stock_data=new_stock, user=user_pro)

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_created.id).one()
        assert stock.beginningDatetime == datetime.datetime.fromisoformat("2021-12-15T20:00:00")
        assert stock.bookingLimitDatetime == datetime.datetime.fromisoformat("2021-12-05T00:00:00")
        assert stock.price == 1200
        assert stock.numberOfTickets == 35
        assert stock.stockId == None

        search.index_collective_offers_in_queue()
        assert offer.id in search_testing.search_store["collective-offers"]

    def should_set_booking_limit_datetime_to_beginning_datetime_when_not_provided(self) -> None:
        # Given
        user_pro = users_factories.ProFactory()
        offer = educational_factories.CollectiveOfferFactory()
        new_stock = collective_stock_serialize.CollectiveStockCreationBodyModel(
            offerId=offer.id,
            beginningDatetime=dateutil.parser.parse("2021-12-15T20:00:00Z"),
            totalPrice=1200,
            numberOfTickets=35,
        )

        # When
        stock_created = educational_api_stock.create_collective_stock(stock_data=new_stock, user=user_pro)

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_created.id).one()
        assert stock.bookingLimitDatetime == dateutil.parser.parse("2021-12-15T20:00:00")

    def test_create_stock_for_non_approved_offer_fails(self) -> None:
        # Given
        user = users_factories.ProFactory()
        offer = educational_factories.CollectiveOfferFactory(validation=OfferValidationStatus.PENDING)
        created_stock_data = collective_stock_serialize.CollectiveStockCreationBodyModel(
            offerId=offer.id,
            beginningDatetime=dateutil.parser.parse("2022-01-17T22:00:00Z"),
            bookingLimitDatetime=dateutil.parser.parse("2021-12-31T20:00:00Z"),
            totalPrice=1500,
            numberOfTickets=38,
        )

        # When
        with pytest.raises(api_errors.ApiErrors) as error:
            educational_api_stock.create_collective_stock(stock_data=created_stock_data, user=user)

        # Then
        assert error.value.errors == {
            "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
        }
        assert CollectiveStock.query.count() == 0

    @mock.patch("pcapi.domain.admin_emails.send_offer_creation_notification_to_administration")
    @mock.patch("pcapi.core.offers.api.set_offer_status_based_on_fraud_criteria")
    def test_not_send_email_when_offer_pass_to_pending_based_on_fraud_criteria(
        self, mocked_set_offer_status_based_on_fraud_criteria, mocked_offer_creation_notification_to_admin
    ) -> None:
        # Given
        user = users_factories.ProFactory()
        offer = educational_factories.CollectiveOfferFactory(validation=OfferValidationStatus.DRAFT)
        created_stock_data = collective_stock_serialize.CollectiveStockCreationBodyModel(
            offerId=offer.id,
            beginningDatetime=dateutil.parser.parse("2022-01-17T22:00:00Z"),
            bookingLimitDatetime=dateutil.parser.parse("2021-12-31T20:00:00Z"),
            totalPrice=1500,
            numberOfTickets=38,
        )
        mocked_set_offer_status_based_on_fraud_criteria.return_value = OfferValidationStatus.PENDING

        # When
        educational_api_stock.create_collective_stock(stock_data=created_stock_data, user=user)

        # Then
        assert not mocked_offer_creation_notification_to_admin.called


@freeze_time("2020-01-05 10:00:00")
@pytest.mark.usefixtures("db_session")
class UnindexExpiredOffersTest:
    @override_settings(ALGOLIA_DELETING_COLLECTIVE_OFFERS_CHUNK_SIZE=2)
    @mock.patch("pcapi.core.search.unindex_collective_offer_ids")
    def test_default_run(self, mock_unindex_collective_offer_ids) -> None:
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
        unindex_expired_collective_offers()

        # Then
        assert mock_unindex_collective_offer_ids.mock_calls == [
            mock.call([collective_stock1.collectiveOfferId, collective_stock2.collectiveOfferId]),
            mock.call([collective_stock3.collectiveOfferId]),
        ]

    @mock.patch("pcapi.core.search.unindex_collective_offer_ids")
    def test_run_unlimited(self, mock_unindex_collective_offer_ids) -> None:
        # more than 2 days ago, must be processed
        collective_stock = educational_factories.CollectiveStockFactory(
            bookingLimitDatetime=datetime.datetime(2020, 1, 2, 12, 0)
        )
        # today, must be ignored
        educational_factories.CollectiveStockFactory(bookingLimitDatetime=datetime.datetime(2020, 1, 5, 12, 0))

        # When
        unindex_expired_collective_offers(process_all_expired=True)

        # Then
        assert mock_unindex_collective_offer_ids.mock_calls == [
            mock.call([collective_stock.collectiveOfferId]),
        ]


class GetCulturalPartnersTest:
    def test_cultural_partners_no_cache(self) -> None:
        # given
        redis_client = current_app.redis_client  # type: ignore [attr-defined]
        redis_client.delete("api:adage_cultural_partner:cache")

        # when
        result = educational_api_adage.get_cultural_partners()

        # then
        assert json.loads(result.json()) == {
            "partners": [
                {
                    "id": 128029,
                    "venueId": None,
                    "siret": "21260324500011",
                    "regionId": None,
                    "academieId": None,
                    "statutId": None,
                    "labelId": 4,
                    "typeId": 4,
                    "communeId": "26324",
                    "libelle": "Musée de St Paul Les trois Châteaux : Le musat Musée d'Archéologie Tricastine",
                    "adresse": "Place de Castellane",
                    "siteWeb": "http://www.musat.fr/",
                    "latitude": 44.349098,
                    "longitude": 4.768178,
                    "actif": 1,
                    "dateModification": "2021-09-01T00:00:00",
                    "statutLibelle": None,
                    "labelLibelle": "Musée de France",
                    "typeIcone": "museum",
                    "typeLibelle": "Musée, domaine ou monument",
                    "communeLibelle": "SAINT-PAUL-TROIS-CHATEAUX",
                    "communeDepartement": "026",
                    "academieLibelle": "GRENOBLE",
                    "regionLibelle": "AUVERGNE-RHÔNE-ALPES",
                    "domaines": "Patrimoine, mémoire, archéologie",
                    "domaineIds": "13",
                    "synchroPass": 0,
                },
                {
                    "id": 128028,
                    "venueId": None,
                    "siret": "",
                    "regionId": None,
                    "academieId": None,
                    "statutId": None,
                    "labelId": None,
                    "typeId": 8,
                    "communeId": "26324",
                    "libelle": "Fête du livre jeunesse de St Paul les trois Châteaux",
                    "adresse": "Place Charles Chausy",
                    "siteWeb": "http://www.fetedulivrejeunesse.fr/",
                    "latitude": 44.350457,
                    "longitude": 4.765918,
                    "actif": 1,
                    "dateModification": "2021-09-01T00:00:00",
                    "statutLibelle": None,
                    "labelLibelle": None,
                    "typeIcone": "town",
                    "typeLibelle": "Association ou fondation pour la promotion, le développement et la diffusion d\u0027oeuvres",
                    "communeLibelle": "SAINT-PAUL-TROIS-CHATEAUX",
                    "communeDepartement": "026",
                    "academieLibelle": "GRENOBLE",
                    "regionLibelle": "AUVERGNE-RHÔNE-ALPES",
                    "domaines": "Univers du livre, de la lecture et des écritures",
                    "domaineIds": "11",
                    "synchroPass": 0,
                },
            ]
        }

    def test_cultural_partners_get_cache(self) -> None:
        # given
        redis_client = current_app.redis_client  # type: ignore [attr-defined]
        data = [
            {
                "id": 23,
                "venueId": None,
                "siret": "21260324500011",
                "regionId": None,
                "academieId": None,
                "statutId": None,
                "labelId": 4,
                "typeId": 4,
                "communeId": "26324",
                "libelle": "Musée de St Paul Les trois Châteaux : Le musat Musée d'Archéologie Tricastine",
                "adresse": "Place de Castellane",
                "siteWeb": "http://www.musat.fr/",
                "latitude": 44.349098,
                "longitude": 4.768178,
                "actif": 1,
                "dateModification": "2021-09-01T00:00:00",
                "statutLibelle": None,
                "labelLibelle": "Musée de France",
                "typeIcone": "museum",
                "typeLibelle": "Musée, domaine ou monument",
                "communeLibelle": "SAINT-PAUL-TROIS-CHATEAUX",
                "communeDepartement": "026",
                "academieLibelle": "GRENOBLE",
                "regionLibelle": "AUVERGNE-RHÔNE-ALPES",
                "domaines": "Patrimoine, mémoire, archéologie",
                "domaineIds": "13",
                "synchroPass": 0,
            },
        ]
        redis_client.set("api:adage_cultural_partner:cache", json.dumps(data).encode("utf-8"))

        # when
        result = educational_api_adage.get_cultural_partners()

        # then
        assert json.loads(result.json()) == {
            "partners": [
                {
                    "id": 23,
                    "venueId": None,
                    "siret": "21260324500011",
                    "regionId": None,
                    "academieId": None,
                    "statutId": None,
                    "labelId": 4,
                    "typeId": 4,
                    "communeId": "26324",
                    "libelle": "Musée de St Paul Les trois Châteaux : Le musat Musée d'Archéologie Tricastine",
                    "adresse": "Place de Castellane",
                    "siteWeb": "http://www.musat.fr/",
                    "latitude": 44.349098,
                    "longitude": 4.768178,
                    "actif": 1,
                    "dateModification": "2021-09-01T00:00:00",
                    "statutLibelle": None,
                    "labelLibelle": "Musée de France",
                    "typeIcone": "museum",
                    "typeLibelle": "Musée, domaine ou monument",
                    "communeLibelle": "SAINT-PAUL-TROIS-CHATEAUX",
                    "communeDepartement": "026",
                    "academieLibelle": "GRENOBLE",
                    "regionLibelle": "AUVERGNE-RHÔNE-ALPES",
                    "domaines": "Patrimoine, mémoire, archéologie",
                    "domaineIds": "13",
                    "synchroPass": 0,
                },
            ]
        }

    def test_cultural_partners_force_update(self) -> None:
        # given
        redis_client = current_app.redis_client  # type: ignore [attr-defined]
        data = [
            {
                "id": 23,
                "venueId": None,
                "siret": "21260324500011",
                "regionId": None,
                "academieId": None,
                "statutId": None,
                "labelId": 4,
                "typeId": 4,
                "communeId": "26324",
                "libelle": "Musée de St Paul Les trois Châteaux : Le musat Musée d'Archéologie Tricastine",
                "adresse": "Place de Castellane",
                "siteWeb": "http://www.musat.fr/",
                "latitude": 44.349098,
                "longitude": 4.768178,
                "actif": 1,
                "dateModification": "2021-09-01T00:00:00",
                "statutLibelle": None,
                "labelLibelle": "Musée de France",
                "typeIcone": "museum",
                "typeLibelle": "Musée, domaine ou monument",
                "communeLibelle": "SAINT-PAUL-TROIS-CHATEAUX",
                "communeDepartement": "026",
                "academieLibelle": "GRENOBLE",
                "regionLibelle": "AUVERGNE-RHÔNE-ALPES",
                "domaines": "Patrimoine, mémoire, archéologie",
                "domaineIds": "13",
                "synchroPass": 1,
            },
        ]
        redis_client.set("api:adage_cultural_partner:cache", json.dumps(data).encode("utf-8"))

        # when
        result = educational_api_adage.get_cultural_partners(force_update=True)

        # then
        # then
        assert json.loads(result.json()) == {
            "partners": [
                {
                    "id": 128029,
                    "venueId": None,
                    "siret": "21260324500011",
                    "regionId": None,
                    "academieId": None,
                    "statutId": None,
                    "labelId": 4,
                    "typeId": 4,
                    "communeId": "26324",
                    "libelle": "Musée de St Paul Les trois Châteaux : Le musat Musée d'Archéologie Tricastine",
                    "adresse": "Place de Castellane",
                    "siteWeb": "http://www.musat.fr/",
                    "latitude": 44.349098,
                    "longitude": 4.768178,
                    "actif": 1,
                    "dateModification": "2021-09-01T00:00:00",
                    "statutLibelle": None,
                    "labelLibelle": "Musée de France",
                    "typeIcone": "museum",
                    "typeLibelle": "Musée, domaine ou monument",
                    "communeLibelle": "SAINT-PAUL-TROIS-CHATEAUX",
                    "communeDepartement": "026",
                    "academieLibelle": "GRENOBLE",
                    "regionLibelle": "AUVERGNE-RHÔNE-ALPES",
                    "domaines": "Patrimoine, mémoire, archéologie",
                    "domaineIds": "13",
                    "synchroPass": 0,
                },
                {
                    "id": 128028,
                    "venueId": None,
                    "siret": "",
                    "regionId": None,
                    "academieId": None,
                    "statutId": None,
                    "labelId": None,
                    "typeId": 8,
                    "communeId": "26324",
                    "libelle": "Fête du livre jeunesse de St Paul les trois Châteaux",
                    "adresse": "Place Charles Chausy",
                    "siteWeb": "http://www.fetedulivrejeunesse.fr/",
                    "latitude": 44.350457,
                    "longitude": 4.765918,
                    "actif": 1,
                    "dateModification": "2021-09-01T00:00:00",
                    "statutLibelle": None,
                    "labelLibelle": None,
                    "typeIcone": "town",
                    "typeLibelle": "Association ou fondation pour la promotion, le développement et la diffusion d\u0027oeuvres",
                    "communeLibelle": "SAINT-PAUL-TROIS-CHATEAUX",
                    "communeDepartement": "026",
                    "academieLibelle": "GRENOBLE",
                    "regionLibelle": "AUVERGNE-RHÔNE-ALPES",
                    "domaines": "Univers du livre, de la lecture et des écritures",
                    "domaineIds": "11",
                    "synchroPass": 0,
                },
            ]
        }


@freeze_time("2022-11-26 18:29:20.891028")
@pytest.mark.usefixtures("db_session")
class EACPendingBookingWithConfirmationLimitDate3DaysTest:
    @mock.patch(
        "pcapi.core.mails.transactional.educational.eac_pending_booking_confirmation_limit_date_in_3_days.mails.send"
    )
    def test_with_pending_booking_limit_date_in_3_days(self, mock_mail_sender) -> None:
        # given
        booking = educational_factories.PendingCollectiveBookingFactory(
            confirmationLimitDate="2022-11-29 18:29:20.891028",
            collectiveStock__collectiveOffer__bookingEmails=["pouet@example.com", "plouf@example.com"],
        )

        # when
        educational_api_booking.notify_pro_pending_booking_confirmation_limit_in_3_days()

        # then
        mock_mail_sender.assert_called_once()
        assert mock_mail_sender.call_args.kwargs["data"].params == {
            "OFFER_NAME": booking.collectiveStock.collectiveOffer.name,
            "VENUE_NAME": booking.collectiveStock.collectiveOffer.venue.name,
            "EVENT_DATE": "dimanche 27 novembre 2022",
            "USER_FIRSTNAME": booking.educationalRedactor.firstName,
            "USER_LASTNAME": booking.educationalRedactor.lastName,
            "USER_EMAIL": booking.educationalRedactor.email,
            "EDUCATIONAL_INSTITUTION_NAME": booking.educationalInstitution.name,
            "BOOKING_ID": booking.id,
        }

    @mock.patch(
        "pcapi.core.mails.transactional.educational.eac_pending_booking_confirmation_limit_date_in_3_days.mails.send"
    )
    def test_with_pending_booking_limit_date_in_less_or_more_than_3_days(self, mock_mail_sender) -> None:
        # given
        educational_factories.PendingCollectiveBookingFactory(
            confirmationLimitDate="2022-11-28 18:29:20.891028",
            collectiveStock__collectiveOffer__bookingEmails=["pouet@example.com", "plouf@example.com"],
        )

        educational_factories.PendingCollectiveBookingFactory(
            confirmationLimitDate="2022-12-01 18:29:20.891028",
            collectiveStock__collectiveOffer__bookingEmails=["pouet@example.com", "plouf@example.com"],
        )

        # when
        educational_api_booking.notify_pro_pending_booking_confirmation_limit_in_3_days()

        # then
        mock_mail_sender.assert_not_called()

    @mock.patch(
        "pcapi.core.mails.transactional.educational.eac_pending_booking_confirmation_limit_date_in_3_days.mails.send"
    )
    def test_with_confirmed_booking_confirmation_limit_date_in_3_days(self, mock_mail_sender) -> None:
        # given
        educational_factories.CollectiveBookingFactory(
            confirmationLimitDate="2022-11-29 18:29:20.891028",
            collectiveStock__collectiveOffer__bookingEmails=["pouet@example.com", "plouf@example.com"],
        )

        # when
        educational_api_booking.notify_pro_pending_booking_confirmation_limit_in_3_days()

        # then
        mock_mail_sender.assert_not_called()


@freeze_time("2020-01-05 10:00:00")
@pytest.mark.usefixtures("db_session")
class NotifyProUserOneDayTest:
    @mock.patch("pcapi.core.mails.transactional.educational.eac_one_day_before_event.mails.send")
    def test_notify_pro_users_one_day(self, mock_mail_sender) -> None:
        # sould send email
        booking1 = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking1",
            collectiveStock__collectiveOffer__bookingEmails=["booking1@example.com", "booking1-2@example.com"],
            collectiveStock__beginningDatetime=datetime.datetime(2020, 1, 6),
            status=CollectiveBookingStatus.CONFIRMED,
        )
        # cancelled should not send email
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking2",
            collectiveStock__collectiveOffer__bookingEmails=["booking2+1@example.com", "booking2+2@example.com"],
            collectiveStock__beginningDatetime=datetime.datetime(2020, 1, 6),
            status=CollectiveBookingStatus.CANCELLED,
        )
        # sould send email (linked to a cancelled one)
        booking3 = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking3",
            collectiveStock__collectiveOffer__bookingEmails=["booking3+2@example.com", "booking3+1@example.com"],
            collectiveStock__beginningDatetime=datetime.datetime(2020, 1, 6),
            status=CollectiveBookingStatus.CONFIRMED,
        )
        # cancelled should not send email (linked to a good one)
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking4",
            collectiveStock__collectiveOffer__bookingEmails=["booking4+1@example.com", "booking4+2@example.com"],
            collectiveStock__beginningDatetime=datetime.datetime(2020, 1, 6),
            collectiveStock=booking3.collectiveStock,
            status=CollectiveBookingStatus.CANCELLED,
        )
        # no emails register, should not send email
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking5",
            collectiveStock__collectiveOffer__bookingEmails=[],
            collectiveStock__beginningDatetime=datetime.datetime(2020, 1, 6),
            status=CollectiveBookingStatus.CONFIRMED,
        )
        # old booking should not be selected
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking6",
            collectiveStock__collectiveOffer__bookingEmails=["booking6+1@example.com", "booking6+2@example.com"],
            collectiveStock__beginningDatetime=datetime.datetime(2019, 1, 6),
            status=CollectiveBookingStatus.CONFIRMED,
        )
        # too far in the future to be selected
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking7",
            collectiveStock__collectiveOffer__bookingEmails=["booking7+1@example.com", "booking7+2@example.com"],
            collectiveStock__beginningDatetime=datetime.datetime(2021, 1, 6),
            status=CollectiveBookingStatus.CONFIRMED,
        )
        educational_api_booking.notify_pro_users_one_day()
        assert mock_mail_sender.call_count == 2
        for args in mock_mail_sender.call_args_list:
            data = args.kwargs["data"]
            assert data.params["OFFER_NAME"] in ("booking1", "booking3")
            if data.params["OFFER_NAME"] == booking1.collectiveStock.collectiveOffer.name:
                assert data.params == {
                    "OFFER_NAME": booking1.collectiveStock.collectiveOffer.name,
                    "VENUE_NAME": booking1.collectiveStock.collectiveOffer.venue.name,
                    "EVENT_HOUR": "1h",
                    "QUANTITY": 1,
                    "PRICE": str(booking1.collectiveStock.price),
                    "REDACTOR_FIRSTNAME": booking1.educationalRedactor.firstName,
                    "REDACTOR_LASTNAME": booking1.educationalRedactor.lastName,
                    "REDACTOR_EMAIL": booking1.educationalRedactor.email,
                    "EDUCATIONAL_INSTITUTION_NAME": booking1.educationalInstitution.name,
                }
                assert args.kwargs["recipients"] == [booking1.collectiveStock.collectiveOffer.bookingEmails[0]]
                assert args.kwargs["bcc_recipients"] == booking1.collectiveStock.collectiveOffer.bookingEmails[1:]
            elif data.params["OFFER_NAME"] == booking3.collectiveStock.collectiveOffer.name:
                assert data.params == {
                    "OFFER_NAME": booking3.collectiveStock.collectiveOffer.name,
                    "VENUE_NAME": booking3.collectiveStock.collectiveOffer.venue.name,
                    "EVENT_HOUR": "1h",
                    "QUANTITY": 1,
                    "PRICE": str(booking3.collectiveStock.price),
                    "REDACTOR_FIRSTNAME": booking3.educationalRedactor.firstName,
                    "REDACTOR_LASTNAME": booking3.educationalRedactor.lastName,
                    "REDACTOR_EMAIL": booking3.educationalRedactor.email,
                    "EDUCATIONAL_INSTITUTION_NAME": booking3.educationalInstitution.name,
                }
                assert args.kwargs["recipients"] == [booking3.collectiveStock.collectiveOffer.bookingEmails[0]]
                assert args.kwargs["bcc_recipients"] == booking3.collectiveStock.collectiveOffer.bookingEmails[1:]
