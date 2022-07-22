import datetime
import json
from unittest import mock

import dateutil
from flask import current_app
from freezegun.api import freeze_time
import pytest

from pcapi.core import search
from pcapi.core.educational import api as educational_api
from pcapi.core.educational import exceptions
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.offers import exceptions as offers_exceptions
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


# @freeze_time("2020-11-17 15:00:00")
@pytest.mark.usefixtures("db_session")
class EditCollectiveOfferStocksTest:
    def test_should_update_all_fields_when_all_changed(self) -> None:
        # Given
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        initial_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            beginningDatetime=initial_event_date,
            price=1200,
            numberOfTickets=30,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            beginningDatetime=datetime.datetime.now(datetime.timezone.utc)  # pylint: disable=datetime-now
            + datetime.timedelta(days=7, hours=5),
            bookingLimitDatetime=datetime.datetime.now(datetime.timezone.utc)  # pylint: disable=datetime-now
            + datetime.timedelta(days=5, hours=16),
            totalPrice=1500,
            numberOfTickets=35,
        )

        # When
        educational_api.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.beginningDatetime == new_stock_data.beginningDatetime.replace(tzinfo=None)
        assert stock.bookingLimitDatetime == new_stock_data.bookingLimitDatetime.replace(tzinfo=None)
        assert stock.price == 1500
        assert stock.numberOfTickets == 35

    def test_should_update_some_fields_and_keep_non_edited_ones(self) -> None:
        # Given
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        initial_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            beginningDatetime=initial_event_date,
            price=1200,
            numberOfTickets=30,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            beginningDatetime=datetime.datetime.now(datetime.timezone.utc)  # pylint: disable=datetime-now
            + datetime.timedelta(days=7, hours=5),
            numberOfTickets=35,
        )

        # When
        educational_api.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.beginningDatetime == new_stock_data.beginningDatetime.replace(tzinfo=None)
        assert stock.bookingLimitDatetime == initial_booking_limit_date
        assert stock.price == 1200
        assert stock.numberOfTickets == 35

    def test_should_replace_bookingLimitDatetime_with_new_event_datetime_if_provided_but_none(self) -> None:
        # Given
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        initial_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            beginningDatetime=initial_event_date,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_event_datetime = datetime.datetime.now(  # pylint: disable=datetime-now
            datetime.timezone.utc
        ) + datetime.timedelta(days=7, hours=5)
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            beginningDatetime=new_event_datetime,
            bookingLimitDatetime=None,
        )

        # When
        educational_api.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.bookingLimitDatetime == new_event_datetime.replace(tzinfo=None)

    def test_should_replace_bookingLimitDatetime_with_old_event_datetime_if_provided_but_none_and_event_date_unchanged(
        self,
    ) -> None:
        # Given
        initial_event_date = datetime.datetime.utcnow() + datetime.timedelta(days=5)
        initial_booking_limit_date = datetime.datetime.utcnow() + datetime.timedelta(days=3)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            beginningDatetime=initial_event_date,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            bookingLimitDatetime=None,
        )

        # When
        educational_api.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        # Then
        stock = CollectiveStock.query.filter_by(id=stock_to_be_updated.id).one()
        assert stock.bookingLimitDatetime == initial_event_date

    # FIXME (rpaoloni, 2022-03-09) -> None: Uncomment for when pc-13428 is merged
    # @mock.patch("pcapi.core.search.async_index_offer_ids")
    # def test_should_reindex_offer_on_algolia(self, mocked_async_index_offer_ids) -> None:
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

    def test_should_not_allow_stock_edition_when_booking_status_is_not_PENDING(self) -> None:
        # Given
        stock_to_be_updated = educational_factories.CollectiveStockFactory(price=1200)
        educational_factories.CollectiveBookingFactory(
            confirmationLimitDate=datetime.datetime.utcnow() + datetime.timedelta(days=1337),
            collectiveStock=stock_to_be_updated,
        )

        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
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
    def should_update_bookings_cancellation_limit_date_if_event_postponed(self) -> None:
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

        new_event_date = datetime.datetime.now(  # pylint: disable=datetime-now
            datetime.timezone.utc
        ) + datetime.timedelta(days=25, hours=5)
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            beginningDatetime=new_event_date,
        )

        # When
        educational_api.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        # Then
        booking_updated = CollectiveBooking.query.filter_by(id=booking.id).one()
        assert booking_updated.cancellationLimitDate == new_event_date.replace(tzinfo=None) - datetime.timedelta(
            days=15
        )

    @freeze_time("2020-11-17 15:00:00")
    def should_update_bookings_cancellation_limit_date_if_beginningDatetime_earlier(self) -> None:
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

        new_event_date = datetime.datetime.now(  # pylint: disable=datetime-now
            datetime.timezone.utc
        ) + datetime.timedelta(days=5, hours=5)
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            beginningDatetime=new_event_date,
            bookingLimitDatetime=datetime.datetime.now(datetime.timezone.utc)  # pylint: disable=datetime-now
            + datetime.timedelta(days=3, hours=5),
        )

        # When
        educational_api.edit_collective_stock(
            stock=stock_to_be_updated, stock_data=new_stock_data.dict(exclude_unset=True)
        )

        # Then
        booking_updated = CollectiveBooking.query.filter_by(id=booking.id).one()
        assert booking_updated.cancellationLimitDate == datetime.datetime.utcnow()

    @freeze_time("2020-11-17 15:00:00")
    def test_should_allow_stock_edition_and_not_modify_cancellation_limit_date_when_booking_cancelled(self) -> None:
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

        new_event_date = datetime.datetime.now(  # pylint: disable=datetime-now
            datetime.timezone.utc
        ) + datetime.timedelta(days=25, hours=5)
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
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
        assert stock.beginningDatetime == new_event_date.replace(tzinfo=None)

    def test_does_not_allow_edition_of_an_expired_event_stock(self) -> None:
        # Given
        initial_event_date = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        initial_booking_limit_date = datetime.datetime.utcnow() - datetime.timedelta(days=10)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            beginningDatetime=initial_event_date,
            price=1200,
            numberOfTickets=30,
            bookingLimitDatetime=initial_booking_limit_date,
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            beginningDatetime=datetime.datetime.now(datetime.timezone.utc)  # pylint: disable=datetime-now
            + datetime.timedelta(days=7, hours=5),
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

    def test_edit_stock_of_non_approved_offer_fails(self) -> None:
        # Given
        offer = educational_factories.CollectiveOfferFactory(validation=OfferValidationStatus.PENDING)
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            collectiveOffer=offer,
            price=1200,
            numberOfTickets=30,
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
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
    ) -> None:
        # Given
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime.datetime(2021, 12, 10), bookingLimitDatetime=datetime.datetime(2021, 12, 5)
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            bookingLimitDatetime=datetime.datetime(2021, 12, 20, tzinfo=datetime.timezone.utc)
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
    ) -> None:
        # Given
        stock_to_be_updated = educational_factories.CollectiveStockFactory(
            beginningDatetime=datetime.datetime(2021, 12, 10), bookingLimitDatetime=datetime.datetime(2021, 12, 5)
        )
        new_stock_data = collective_stock_serialize.CollectiveStockEditionBodyModel(
            beginningDatetime=datetime.datetime(2021, 12, 4, tzinfo=datetime.timezone.utc)
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
        stock_created = educational_api.create_collective_stock(stock_data=new_stock, user=user_pro)

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
            educational_api.create_collective_stock(stock_data=created_stock_data, user=user)

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
        educational_api.create_collective_stock(stock_data=created_stock_data, user=user)

        # Then
        assert not mocked_offer_creation_notification_to_admin.called


@freeze_time("2020-11-17 15:00:00")
@pytest.mark.usefixtures("db_session")
class EditEducationalInstitutionTest:
    @mock.patch("pcapi.domain.admin_emails.send_offer_creation_notification_to_administration")
    @mock.patch("pcapi.core.offers.api.set_offer_status_based_on_fraud_criteria")
    def test_send_email_when_offer_automatically_approved_based_on_fraud_criteria(
        self, mocked_set_offer_status_based_on_fraud_criteria, mocked_offer_creation_notification_to_admin
    ) -> None:
        # Given
        user = users_factories.ProFactory()
        stock = educational_factories.CollectiveStockFactory(collectiveOffer__validation=OfferValidationStatus.DRAFT)
        mocked_set_offer_status_based_on_fraud_criteria.return_value = OfferValidationStatus.APPROVED

        # When
        educational_api.update_collective_offer_educational_institution(
            offer_id=stock.collectiveOfferId, educational_institution_id=None, is_creating_offer=True, user=user
        )

        # Then
        mocked_offer_creation_notification_to_admin.assert_called_once_with(stock.collectiveOffer)


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
        educational_api.unindex_expired_collective_offers()

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
        educational_api.unindex_expired_collective_offers(process_all_expired=True)

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
        result = educational_api.get_cultural_partners()

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
        result = educational_api.get_cultural_partners()

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
        result = educational_api.get_cultural_partners(force_update=True)

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
