import datetime
import decimal
import json
import logging
from unittest import mock

import dateutil
import pytest
import time_machine
from flask import current_app

import pcapi.core.educational.api.institution as institution_api
import pcapi.core.educational.exceptions as educational_exceptions
import pcapi.core.educational.factories as educational_factories
import pcapi.core.educational.models as educational_models
from pcapi.core.educational.api import adage as educational_api_adage
from pcapi.core.educational.api import booking as educational_api_booking
from pcapi.core.educational.api import offer as educational_api_offer
from pcapi.core.educational.api import stock as educational_api_stock
from pcapi.core.offerers import factories as offerers_factories
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.routes.serialization import collective_stock_serialize
from pcapi.utils import db as db_utils


@pytest.mark.usefixtures("db_session")
class CreateCollectiveOfferStocksTest:
    @time_machine.travel("2020-11-17 15:00:00")
    def should_create_one_stock_on_collective_offer_stock_creation(self) -> None:
        start_date = dateutil.parser.parse("2021-12-15T20:00:00Z")
        educational_factories.EducationalYearFactory(
            beginningDate=start_date - datetime.timedelta(days=100),
            expirationDate=start_date + datetime.timedelta(days=100),
        )
        offer = educational_factories.CollectiveOfferFactory()
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

        stock = db.session.query(educational_models.CollectiveStock).filter_by(id=stock_created.id).one()
        assert stock.startDatetime == datetime.datetime.fromisoformat("2021-12-15T20:00:00")
        assert stock.bookingLimitDatetime == datetime.datetime.fromisoformat("2021-12-05T00:00:00")
        assert stock.price == 1200
        assert stock.numberOfTickets == 35

    @time_machine.travel("2020-11-17 15:00:00")
    def should_set_booking_limit_datetime_to_beginning_datetime_when_not_provided(self) -> None:
        start_date = dateutil.parser.parse("2021-12-15T20:00:00Z")
        educational_factories.EducationalYearFactory(
            beginningDate=start_date - datetime.timedelta(days=100),
            expirationDate=start_date + datetime.timedelta(days=100),
        )
        offer = educational_factories.CollectiveOfferFactory()
        new_stock = collective_stock_serialize.CollectiveStockCreationBodyModel(
            offerId=offer.id,
            startDatetime=start_date,
            endDatetime=start_date,
            totalPrice=1200,
            numberOfTickets=35,
            educationalPriceDetail="hello",
        )

        stock_created = educational_api_stock.create_collective_stock(stock_data=new_stock)

        stock = db.session.query(educational_models.CollectiveStock).filter_by(id=stock_created.id).one()
        assert stock.bookingLimitDatetime == dateutil.parser.parse("2021-12-15T20:00:00")

    @time_machine.travel("2020-11-17 15:00:00")
    @pytest.mark.parametrize("status", [OfferValidationStatus.REJECTED, OfferValidationStatus.PENDING])
    def test_create_stock_for_rejected_or_pending_offer_fails(self, status) -> None:
        start_date = dateutil.parser.parse("2022-01-17T22:00:00Z")
        educational_factories.EducationalYearFactory(
            beginningDate=start_date - datetime.timedelta(days=100),
            expirationDate=start_date + datetime.timedelta(days=100),
        )
        offer = educational_factories.CollectiveOfferFactory(validation=status)
        created_stock_data = collective_stock_serialize.CollectiveStockCreationBodyModel(
            offerId=offer.id,
            startDatetime=start_date,
            endDatetime=start_date,
            bookingLimitDatetime=dateutil.parser.parse("2021-12-31T20:00:00Z"),
            totalPrice=1500,
            numberOfTickets=38,
            educationalPriceDetail="hello",
        )

        with pytest.raises(educational_exceptions.EducationalException) as error:
            educational_api_stock.create_collective_stock(stock_data=created_stock_data)

        assert error.value.errors == {
            "global": ["Les offres refusées ou en attente de validation ne sont pas modifiables"]
        }
        assert db.session.query(educational_models.CollectiveStock).count() == 0


@pytest.mark.usefixtures("db_session")
class UnindexExpiredOffersTest:
    @pytest.mark.settings(ALGOLIA_DELETING_COLLECTIVE_OFFERS_CHUNK_SIZE=3)
    @mock.patch("pcapi.core.search.unindex_collective_offer_template_ids")
    def test_default_run_template(self, mock_unindex_collective_offer_template_ids) -> None:
        # Given
        # Expired template offer
        collective_offer_template_1 = educational_factories.CollectiveOfferTemplateFactory(
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=9),
            dateRange=db_utils.make_timerange(
                start=datetime.datetime.utcnow() - datetime.timedelta(days=7),
                end=datetime.datetime.utcnow() - datetime.timedelta(days=3),
            ),
        )
        # Non expired template offer
        educational_factories.CollectiveOfferTemplateFactory()
        # Expired template offer
        collective_offer_template_2 = educational_factories.CollectiveOfferTemplateFactory(
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=9),
            dateRange=db_utils.make_timerange(
                start=datetime.datetime.utcnow() - datetime.timedelta(days=7),
                end=datetime.datetime.utcnow() - datetime.timedelta(hours=1),
            ),
        )
        # Archived template offer
        collective_offer_template_3 = educational_factories.CollectiveOfferTemplateFactory(
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=9),
            dateRange=db_utils.make_timerange(
                start=datetime.datetime.utcnow() - datetime.timedelta(days=3),
                end=datetime.datetime.utcnow() + datetime.timedelta(days=3),
            ),
            dateArchived=datetime.datetime.utcnow() - datetime.timedelta(days=1),
            isActive=False,
        )
        # Non expired template offer with dateRange overlapping today
        educational_factories.CollectiveOfferTemplateFactory(
            dateCreated=datetime.datetime.utcnow() - datetime.timedelta(days=9),
            dateRange=db_utils.make_timerange(
                start=datetime.datetime.utcnow() - datetime.timedelta(days=3),
                end=datetime.datetime.utcnow() + datetime.timedelta(days=3),
            ),
        )
        # When
        educational_api_offer.unindex_expired_or_archived_collective_offers_template()

        # Then
        assert mock_unindex_collective_offer_template_ids.mock_calls == [
            mock.call([collective_offer_template_1.id, collective_offer_template_2.id, collective_offer_template_3.id]),
        ]


class GetCulturalPartnersTest:
    def test_cultural_partners_no_cache(self) -> None:
        # given
        redis_client = current_app.redis_client  # type: ignore[attr-defined]
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
        redis_client = current_app.redis_client  # type: ignore[attr-defined]
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
        redis_client = current_app.redis_client  # type: ignore[attr-defined]
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


@pytest.mark.usefixtures("db_session")
class EACPendingBookingWithConfirmationLimitDate3DaysTest:
    @time_machine.travel("2022-11-26 18:29")
    @mock.patch(
        "pcapi.core.mails.transactional.educational.eac_pending_booking_confirmation_limit_date_in_3_days.mails.send"
    )
    def test_with_pending_booking_limit_date_in_3_days(self, mock_mail_sender) -> None:
        booking = educational_factories.PendingCollectiveBookingFactory(
            confirmationLimitDate="2022-11-29 18:29",
            collectiveStock__collectiveOffer__bookingEmails=["pouet@example.com", "plouf@example.com"],
            collectiveStock__collectiveOffer__locationType=educational_models.CollectiveLocationType.SCHOOL,
        )

        educational_api_booking.notify_pro_pending_booking_confirmation_limit_in_3_days()

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
            "COLLECTIVE_OFFER_ADDRESS": "En établissement scolaire",
        }

    @mock.patch(
        "pcapi.core.mails.transactional.educational.eac_pending_booking_confirmation_limit_date_in_3_days.mails.send"
    )
    def test_with_pending_booking_limit_date_in_less_or_more_than_3_days(self, mock_mail_sender) -> None:
        # given
        educational_factories.PendingCollectiveBookingFactory(
            confirmationLimitDate="2022-11-28 18:29",
            collectiveStock__collectiveOffer__bookingEmails=["pouet@example.com", "plouf@example.com"],
        )

        educational_factories.PendingCollectiveBookingFactory(
            confirmationLimitDate="2022-12-01 18:29",
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
            confirmationLimitDate="2022-11-29 18:29",
            collectiveStock__collectiveOffer__bookingEmails=["pouet@example.com", "plouf@example.com"],
        )

        # when
        educational_api_booking.notify_pro_pending_booking_confirmation_limit_in_3_days()

        # then
        mock_mail_sender.assert_not_called()


@pytest.mark.usefixtures("db_session")
class NotifyProUserOneDayTest:
    @time_machine.travel("2020-01-05 10:00:00")
    @mock.patch("pcapi.core.mails.transactional.educational.eac_one_day_before_event.mails.send")
    def test_notify_pro_users_one_day_before(self, mock_mail_sender) -> None:
        # should send email
        booking1 = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking1",
            collectiveStock__collectiveOffer__bookingEmails=["booking1@example.com", "booking1-2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
        )
        # cancelled should not send email
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking2",
            collectiveStock__collectiveOffer__bookingEmails=["booking2+1@example.com", "booking2+2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            status=educational_models.CollectiveBookingStatus.CANCELLED,
        )
        # should send email (linked to a cancelled one)
        booking3 = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking3",
            collectiveStock__collectiveOffer__bookingEmails=["booking3+2@example.com", "booking3+1@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
        )
        # cancelled should not send email (linked to a good one)
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking4",
            collectiveStock__collectiveOffer__bookingEmails=["booking4+1@example.com", "booking4+2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            collectiveStock=booking3.collectiveStock,
            status=educational_models.CollectiveBookingStatus.CANCELLED,
        )
        # no emails registered, should not send email
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking5",
            collectiveStock__collectiveOffer__bookingEmails=[],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
        )
        # old booking should not be selected
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking6",
            collectiveStock__collectiveOffer__bookingEmails=["booking6+1@example.com", "booking6+2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2019, 1, 6),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
        )
        # too far in the future to be selected
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking7",
            collectiveStock__collectiveOffer__bookingEmails=["booking7+1@example.com", "booking7+2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2021, 1, 6),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
        )
        educational_api_booking.notify_pro_users_one_day_before()
        assert mock_mail_sender.call_count == 2
        for args in mock_mail_sender.call_args_list:
            data = args.kwargs["data"]
            assert data.params["OFFER_NAME"] in ("booking1", "booking3")
            if data.params["OFFER_NAME"] == booking1.collectiveStock.collectiveOffer.name:
                assert data.params == {
                    "OFFER_NAME": booking1.collectiveStock.collectiveOffer.name,
                    "VENUE_NAME": booking1.collectiveStock.collectiveOffer.venue.name,
                    "EVENT_HOUR": "01h00",
                    "QUANTITY": 1,
                    "PRICE": str(booking1.collectiveStock.price),
                    "FORMATTED_PRICE": "100 €",
                    "REDACTOR_FIRSTNAME": booking1.educationalRedactor.firstName,
                    "REDACTOR_LASTNAME": booking1.educationalRedactor.lastName,
                    "REDACTOR_EMAIL": booking1.educationalRedactor.email,
                    "EDUCATIONAL_INSTITUTION_NAME": booking1.educationalInstitution.name,
                    "COLLECTIVE_OFFER_ADDRESS": "À déterminer avec l'enseignant",
                }
                assert args.kwargs["recipients"] == [booking1.collectiveStock.collectiveOffer.bookingEmails[0]]
                assert args.kwargs["bcc_recipients"] == booking1.collectiveStock.collectiveOffer.bookingEmails[1:]
            elif data.params["OFFER_NAME"] == booking3.collectiveStock.collectiveOffer.name:
                assert data.params == {
                    "OFFER_NAME": booking3.collectiveStock.collectiveOffer.name,
                    "VENUE_NAME": booking3.collectiveStock.collectiveOffer.venue.name,
                    "EVENT_HOUR": "01h00",
                    "QUANTITY": 1,
                    "PRICE": str(booking3.collectiveStock.price),
                    "FORMATTED_PRICE": "100 €",
                    "REDACTOR_FIRSTNAME": booking3.educationalRedactor.firstName,
                    "REDACTOR_LASTNAME": booking3.educationalRedactor.lastName,
                    "REDACTOR_EMAIL": booking3.educationalRedactor.email,
                    "EDUCATIONAL_INSTITUTION_NAME": booking3.educationalInstitution.name,
                    "COLLECTIVE_OFFER_ADDRESS": "À déterminer avec l'enseignant",
                }
                assert args.kwargs["recipients"] == [booking3.collectiveStock.collectiveOffer.bookingEmails[0]]
                assert args.kwargs["bcc_recipients"] == booking3.collectiveStock.collectiveOffer.bookingEmails[1:]


@pytest.mark.usefixtures("db_session")
class NotifyProUserOneDayAfterTest:
    @time_machine.travel("2020-01-07 10:00:00")
    @mock.patch("pcapi.core.mails.transactional.educational.eac_one_day_after_event.mails.send")
    def test_notify_pro_users_one_day_after(self, mock_mail_sender) -> None:
        # should send email
        booking1 = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking1",
            collectiveStock__collectiveOffer__bookingEmails=["booking1@example.com", "booking1-2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
        )
        # cancelled should not send email
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking2",
            collectiveStock__collectiveOffer__bookingEmails=["booking2+1@example.com", "booking2+2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            status=educational_models.CollectiveBookingStatus.CANCELLED,
        )
        # should send email (linked to a cancelled one)
        booking3 = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking3",
            collectiveStock__collectiveOffer__bookingEmails=["booking3+2@example.com", "booking3+1@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
        )
        # cancelled should not send email (linked to a good one)
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking4",
            collectiveStock__collectiveOffer__bookingEmails=["booking4+1@example.com", "booking4+2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            collectiveStock=booking3.collectiveStock,
            status=educational_models.CollectiveBookingStatus.CANCELLED,
        )
        # no emails registered, should not send email
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking5",
            collectiveStock__collectiveOffer__bookingEmails=[],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
        )
        # old booking should not be selected
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking6",
            collectiveStock__collectiveOffer__bookingEmails=["booking6+1@example.com", "booking6+2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2019, 1, 6),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
        )
        # too far in the future to be selected
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking7",
            collectiveStock__collectiveOffer__bookingEmails=["booking7+1@example.com", "booking7+2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2021, 1, 6),
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
        )
        # should not send email only the endDate should be taken into account
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__name="booking8",
            collectiveStock__collectiveOffer__bookingEmails=["booking1@example.com", "booking1-2@example.com"],
            collectiveStock__startDatetime=datetime.datetime(2020, 1, 6),
            collectiveStock__endDatetime=datetime.datetime(2020, 1, 9),  # -> a different endDatetime
            status=educational_models.CollectiveBookingStatus.CONFIRMED,
        )

        educational_api_booking.notify_pro_users_one_day_after()
        assert mock_mail_sender.call_count == 2
        for args in mock_mail_sender.call_args_list:
            data = args.kwargs["data"]
            assert data.params["OFFER_NAME"] in ("booking1", "booking3")
            if data.params["OFFER_NAME"] == booking1.collectiveStock.collectiveOffer.name:
                assert data.params == {
                    "OFFER_NAME": booking1.collectiveStock.collectiveOffer.name,
                    "VENUE_NAME": booking1.collectiveStock.collectiveOffer.venue.name,
                    "EVENT_HOUR": "01h00",
                    "EVENT_DATE": "lundi 6 janvier 2020",
                    "EDUCATIONAL_INSTITUTION_NAME": booking1.educationalInstitution.name,
                    "COLLECTIVE_OFFER_ADDRESS": "À déterminer avec l'enseignant",
                }
                assert args.kwargs["recipients"] == [booking1.collectiveStock.collectiveOffer.bookingEmails[0]]
                assert args.kwargs["bcc_recipients"] == booking1.collectiveStock.collectiveOffer.bookingEmails[1:]
            elif data.params["OFFER_NAME"] == booking3.collectiveStock.collectiveOffer.name:
                assert data.params == {
                    "OFFER_NAME": booking3.collectiveStock.collectiveOffer.name,
                    "VENUE_NAME": booking3.collectiveStock.collectiveOffer.venue.name,
                    "EVENT_HOUR": "01h00",
                    "EVENT_DATE": "lundi 6 janvier 2020",
                    "EDUCATIONAL_INSTITUTION_NAME": booking3.educationalInstitution.name,
                    "COLLECTIVE_OFFER_ADDRESS": "À déterminer avec l'enseignant",
                }
                assert args.kwargs["recipients"] == [booking3.collectiveStock.collectiveOffer.bookingEmails[0]]
                assert args.kwargs["bcc_recipients"] == booking3.collectiveStock.collectiveOffer.bookingEmails[1:]


@pytest.mark.usefixtures("db_session")
class SynchroniseRuralityLevelTest:
    def test_should_update_rurality_level(self):
        et1 = educational_factories.EducationalInstitutionFactory(ruralLevel=None)
        et2 = educational_factories.EducationalInstitutionFactory(
            ruralLevel=educational_models.InstitutionRuralLevel.RURAL_A_HABITAT_DISPERSE
        )
        et3 = educational_factories.EducationalInstitutionFactory(
            ruralLevel=educational_models.InstitutionRuralLevel.RURAL_A_HABITAT_DISPERSE
        )
        et4 = educational_factories.EducationalInstitutionFactory(
            ruralLevel=educational_models.InstitutionRuralLevel.RURAL_A_HABITAT_DISPERSE
        )

        mock_path = "pcapi.connectors.big_query.TestingBackend.run_query"
        with mock.patch(mock_path) as mock_run_query:
            mock_run_query.return_value = [
                {
                    "institution_id": str(et1.id),
                    "institution_rural_level": educational_models.InstitutionRuralLevel.RURAL_A_HABITAT_DISPERSE.value,
                },
                {
                    "institution_id": str(et2.id),
                    "institution_rural_level": educational_models.InstitutionRuralLevel.RURAL_A_HABITAT_DISPERSE.value,
                },
                {
                    "institution_id": str(et3.id),
                    "institution_rural_level": educational_models.InstitutionRuralLevel.GRANDS_CENTRES_URBAINS.value,
                },
                {
                    "institution_id": str(et4.id),
                    "institution_rural_level": None,
                },
            ]
            institution_api.synchronise_rurality_level()

        institutions = (
            db.session.query(educational_models.EducationalInstitution)
            .order_by(educational_models.EducationalInstitution.id)
            .all()
        )
        assert [i.id for i in institutions] == [et1.id, et2.id, et3.id, et4.id]
        assert institutions[0].ruralLevel == educational_models.InstitutionRuralLevel.RURAL_A_HABITAT_DISPERSE
        assert institutions[1].ruralLevel == educational_models.InstitutionRuralLevel.RURAL_A_HABITAT_DISPERSE
        assert institutions[2].ruralLevel == educational_models.InstitutionRuralLevel.GRANDS_CENTRES_URBAINS
        assert institutions[3].ruralLevel == None


@pytest.mark.usefixtures("db_session")
class SynchroniseInstitutionsGeolocationTest:
    def test_synchronise_institutions_geolocation(self):
        educational_factories.EducationalCurrentYearFactory()

        institution = educational_factories.EducationalInstitutionFactory(
            institutionId="0470009E", latitude=None, longitude=None
        )
        institution_with_values = educational_factories.EducationalInstitutionFactory(
            institutionId="0470010E", latitude=42, longitude=2
        )

        # The backend for test is in AdageSpyClient#get_adage_educational_institutions
        institution_not_present = educational_factories.EducationalInstitutionFactory(
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
        program = educational_factories.EducationalInstitutionProgramFactory(name="The Program")
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
        institution_1 = educational_factories.EducationalInstitutionFactory(institutionId=uai_1)
        assert len(institution_1.programAssociations) == 0
        # institution not associated to the program, not added to the program
        # expected: no change
        institution_2 = educational_factories.EducationalInstitutionFactory(institutionId=uai_2)
        assert len(institution_2.programAssociations) == 0

        # institution previously associated to the program, added to the program
        # expected: no change, log an error
        institution_3 = educational_factories.EducationalInstitutionFactory(institutionId=uai_3)
        association_3 = educational_factories.EducationalInstitutionProgramAssociationFactory(
            institution=institution_3, program=program, timespan=past_timespan
        )
        association_3_timespan = association_3.timespan
        # institution previously associated to the program, not added to the program
        # expected: no change
        institution_4 = educational_factories.EducationalInstitutionFactory(institutionId=uai_4)
        association_4 = educational_factories.EducationalInstitutionProgramAssociationFactory(
            institution=institution_4, program=program, timespan=past_timespan
        )
        association_4_timespan = association_4.timespan

        # institution currently associated to the program, added to the program
        # expected: no change
        institution_5 = educational_factories.EducationalInstitutionFactory(institutionId=uai_5)
        association_5 = educational_factories.EducationalInstitutionProgramAssociationFactory(
            institution=institution_5, program=program, timespan=current_timespan
        )
        association_5_timespan = association_5.timespan
        # institution currently associated to the program, not added to the program
        # expected: no change, log an error
        institution_6 = educational_factories.EducationalInstitutionFactory(institutionId=uai_6)
        association_6 = educational_factories.EducationalInstitutionProgramAssociationFactory(
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

        assert len(caplog.records) == 3
        logs = {(log_record.message, log_record.levelname) for log_record in caplog.records}
        assert ("Linking UAI 11111111 to program The Program", "INFO") in logs
        assert (
            "UAI 11111113 was previously associated with program The Program, cannot add it back",
            "ERROR",
        ) in logs
        assert (
            "UAIs in DB are associated with program The Program but not present in data: 11111116",
            "ERROR",
        ) in logs


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
            "offerVenue",
            "location",
            "interventionArea",
            "durationMinutes",
            "audioDisabilityCompliant",
            "mentalDisabilityCompliant",
            "motorDisabilityCompliant",
            "visualDisabilityCompliant",
            "isActive",
            "imageCredit",
            "imageFile",
            "nationalProgramId",
        }
        assert len(educational_api_offer.PATCH_DETAILS_FIELDS_PUBLIC) == len(expected)
        assert set(educational_api_offer.PATCH_DETAILS_FIELDS_PUBLIC) == expected


@pytest.mark.usefixtures("db_session")
class OfferVenueByOfferIdTest:
    def test_get_collective_offer_venue_by_offer_id(self):
        venue_1 = offerers_factories.VenueFactory()
        venue_2 = offerers_factories.VenueFactory()
        offer_1 = educational_factories.CollectiveOfferFactory(
            offerVenue={"addressType": "offererVenue", "otherAddress": "", "venueId": venue_1.id},
            venue=venue_1,
            locationType=educational_models.CollectiveLocationType.ADDRESS,
            offererAddress=venue_1.offererAddress,
        )
        offer_2 = educational_factories.CollectiveOfferFactory(
            offerVenue={"addressType": "offererVenue", "otherAddress": "", "venueId": venue_1.id},
            venue=venue_1,
            locationType=educational_models.CollectiveLocationType.ADDRESS,
            offererAddress=venue_1.offererAddress,
        )
        offer_3 = educational_factories.CollectiveOfferFactory(
            offerVenue={"addressType": "offererVenue", "otherAddress": "", "venueId": venue_2.id},
            venue=venue_2,
            locationType=educational_models.CollectiveLocationType.ADDRESS,
            offererAddress=venue_2.offererAddress,
        )
        offer_4 = educational_factories.CollectiveOfferFactory(
            offerVenue={"addressType": "other", "otherAddress": "here", "venueId": None},
            locationType=educational_models.CollectiveLocationType.TO_BE_DEFINED,
        )

        result = educational_api_offer.get_collective_offer_venue_by_offer_id(
            offers=[offer_1, offer_2, offer_3, offer_4]
        )
        assert result == {
            offer_1.id: venue_1,
            offer_2.id: venue_1,
            offer_3.id: venue_2,
            offer_4.id: None,
        }
