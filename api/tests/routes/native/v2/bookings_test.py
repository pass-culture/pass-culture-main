from datetime import datetime
from datetime import timedelta
from decimal import Decimal

import pytest

import pcapi.core.offers.factories as offers_factories
import pcapi.core.providers.repository as providers_api
from pcapi.core.bookings import factories as booking_factories
from pcapi.core.bookings import models as booking_models
from pcapi.core.categories import subcategories
from pcapi.core.external_bookings.factories import ExternalBookingFactory
from pcapi.core.geography.factories import AddressFactory
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import models as offer_models
from pcapi.core.reactions.factories import ReactionFactory
from pcapi.core.reactions.models import ReactionTypeEnum
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.utils import date as date_utils
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class GetBookingsTest:
    identifier = "pascal.ture@example.com"

    def test_get_bookings(self, client):
        OFFER_URL = "https://demo.pass/some/path?token={token}&email={email}&offerId={offerId}"
        user = users_factories.BeneficiaryFactory(email=self.identifier, age=18)

        permanent_booking = booking_factories.UsedBookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.TELECHARGEMENT_LIVRE_AUDIO.id,
            dateUsed=datetime(2023, 2, 3),
        )

        event_booking = booking_factories.BookingFactory(
            user=user,
            stock=offers_factories.EventStockFactory(
                beginningDatetime=date_utils.get_naive_utc_now() + timedelta(days=2),
                offer__bookingContact="contact@example.net",
            ),
        )

        digital_stock = offers_factories.StockWithActivationCodesFactory()
        first_activation_code = digital_stock.activationCodes[0]
        second_activation_code = digital_stock.activationCodes[1]
        digital_booking = booking_factories.UsedBookingFactory(
            user=user,
            stock=digital_stock,
            activationCode=first_activation_code,
        )
        ended_digital_booking = booking_factories.UsedBookingFactory(
            user=user,
            displayAsEnded=True,
            stock=digital_stock,
            activationCode=second_activation_code,
        )
        expire_tomorrow = booking_factories.BookingFactory(
            user=user, dateCreated=date_utils.get_naive_utc_now() - timedelta(days=29)
        )
        used_but_in_future = booking_factories.UsedBookingFactory(
            user=user,
            dateUsed=date_utils.get_naive_utc_now() - timedelta(days=1),
            stock=offers_factories.StockFactory(beginningDatetime=date_utils.get_naive_utc_now() + timedelta(days=3)),
        )

        cancelled_permanent_booking = booking_factories.CancelledBookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.TELECHARGEMENT_LIVRE_AUDIO.id,
            cancellation_date=datetime(2023, 3, 10),
        )
        cancelled = booking_factories.CancelledBookingFactory(user=user, cancellation_date=datetime(2023, 3, 8))
        used1 = booking_factories.UsedBookingFactory(user=user, dateUsed=datetime(2023, 3, 1))
        used2 = booking_factories.UsedBookingFactory(
            user=user,
            displayAsEnded=True,
            dateUsed=datetime(2023, 3, 2),
            stock__offer__url=OFFER_URL,
            stock__offer__subcategoryId=subcategories.ABO_LIVRE_NUMERIQUE.id,
            stock__features=["VO"],
            stock__offer__extraData=None,
            cancellation_limit_date=datetime(2023, 3, 2),
        )

        mediation = offers_factories.MediationFactory(
            id=111, offer=used2.stock.offer, thumbCount=1, credit="street credit"
        )

        client = client.with_token(self.identifier)
        with assert_num_queries(2):
            # select user, booking
            response = client.get("/native/v2/bookings")

        assert response.status_code == 200
        assert [b["id"] for b in response.json["ongoingBookings"]] == [
            expire_tomorrow.id,
            event_booking.id,
            used_but_in_future.id,
            digital_booking.id,
            permanent_booking.id,
        ]

        event_booking_json = next(
            booking for booking in response.json["ongoingBookings"] if booking["id"] == event_booking.id
        )
        assert event_booking_json["stock"]["offer"]["bookingContact"] == "contact@example.net"

        digital_booking_json = next(
            booking for booking in response.json["ongoingBookings"] if booking["id"] == digital_booking.id
        )
        assert digital_booking_json["ticket"]["activationCode"]

        assert [b["id"] for b in response.json["endedBookings"]] == [
            ended_digital_booking.id,
            cancelled_permanent_booking.id,
            cancelled.id,
            used2.id,
            used1.id,
        ]

        assert response.json["hasBookingsAfter18"] is True

        used2_json = next(booking for booking in response.json["endedBookings"] if booking["id"] == used2.id)
        assert used2_json == {
            "enablePopUpReaction": False,
            "canReact": False,
            "userReaction": None,
            "cancellationDate": None,
            "cancellationReason": None,
            "confirmationDate": "2023-03-02T00:00:00Z",
            "completedUrl": f"https://demo.pass/some/path?token={used2.token}&email=pascal.ture@example.com&offerId={humanize(used2.stock.offer.id)}",
            "dateCreated": used2.dateCreated.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "dateUsed": "2023-03-02T00:00:00Z",
            "expirationDate": None,
            "quantity": 1,
            "id": used2.id,
            "stock": {
                "beginningDatetime": None,
                "features": ["VO"],
                "id": used2.stock.id,
                "price": Decimal(used2.stock.price * 100),
                "priceCategoryLabel": None,
                "offer": {
                    "address": {
                        "id": used2.venue.offererAddress.address.id,
                        "city": used2.venue.offererAddress.address.city,
                        "coordinates": {
                            "latitude": float(used2.venue.offererAddress.address.latitude),
                            "longitude": float(used2.venue.offererAddress.address.longitude),
                        },
                        "label": None,
                        "postalCode": used2.venue.offererAddress.address.postalCode,
                        "street": used2.venue.offererAddress.address.street,
                        "timezone": used2.venue.offererAddress.address.timezone,
                    },
                    "bookingContact": None,
                    "subcategoryId": subcategories.ABO_LIVRE_NUMERIQUE.id,
                    "extraData": None,
                    "id": used2.stock.offer.id,
                    "image": {"credit": "street credit", "url": mediation.thumbUrl},
                    "isDigital": True,
                    "isPermanent": False,
                    "name": used2.stock.offer.name,
                    "url": "https://demo.pass/some/path?token={token}&email={email}&offerId={offerId}",
                    "venue": {
                        "id": used2.venue.id,
                        "address": {
                            "id": used2.venue.offererAddress.address.id,
                        },
                        "name": used2.venue.name,
                        "publicName": used2.venue.publicName,
                        # FIXME bdalbianco 28/04/2025 CLEAN_OA: check timezone relevance after regul venue
                        "timezone": "Europe/Paris",
                        "bannerUrl": None,
                        "isOpenToPublic": False,
                    },
                },
            },
            "ticket": {
                "activationCode": None,
                "externalBooking": None,
                "voucher": None,
                "token": {"data": used2.token},
                "withdrawal": {
                    "details": None,
                    "type": None,
                    "delay": None,
                },
                "display": "online_code",
            },
            "totalAmount": 1010,
        }

    def test_get_bookings_returns_user_reaction(self, client):
        now = date_utils.get_naive_utc_now()
        stock = offers_factories.EventStockFactory()
        ongoing_booking = booking_factories.BookingFactory(
            stock=stock, user__deposit__expirationDate=now + timedelta(days=180)
        )

        client = client.with_token(ongoing_booking.user.email)
        with assert_num_queries(2):
            # select user, booking
            response = client.get("/native/v2/bookings")

        assert response.status_code == 200
        assert response.json["ongoingBookings"][0]["userReaction"] is None

    def test_get_bookings_returns_user_reaction_when_one_exists(self, client):
        now = date_utils.get_naive_utc_now()
        stock = offers_factories.EventStockFactory()
        ongoing_booking = booking_factories.BookingFactory(
            stock=stock, user__deposit__expirationDate=now + timedelta(days=180)
        )
        ReactionFactory(user=ongoing_booking.user, offer=stock.offer)

        client = client.with_token(ongoing_booking.user.email)
        with assert_num_queries(2):
            # select user, booking
            response = client.get("/native/v2/bookings")

        assert response.status_code == 200
        assert response.json["ongoingBookings"][0]["userReaction"] == "NO_REACTION"

    def test_get_bookings_returns_user_reaction_when_reaction_is_on_the_product(self, client):
        now = date_utils.get_naive_utc_now()
        product = offers_factories.ProductFactory()
        stock = offers_factories.EventStockFactory(offer__product=product)
        ongoing_booking = booking_factories.BookingFactory(
            stock=stock, user__deposit__expirationDate=now + timedelta(days=180)
        )
        ReactionFactory(reactionType=ReactionTypeEnum.LIKE, user=ongoing_booking.user, product=stock.offer.product)
        client = client.with_token(ongoing_booking.user.email)
        with assert_num_queries(3):
            # select user, booking, offer
            response = client.get("/native/v2/bookings")

        assert response.status_code == 200
        assert response.json["ongoingBookings"][0]["userReaction"] == "LIKE"

    def test_get_bookings_returns_enable_pop_up_reaction(self, client):
        offer = offers_factories.OfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
        )
        booking = booking_factories.UsedBookingFactory(
            stock__offer=offer,
            dateUsed=date_utils.get_naive_utc_now() - timedelta(seconds=60 * 24 * 3600),
        )
        client = client.with_token(booking.user.email)
        with assert_num_queries(2):
            # select user, booking, offer
            response = client.get("/native/v2/bookings")

        assert response.status_code == 200
        assert response.json["ongoingBookings"][0]["enablePopUpReaction"] is True

    def test_get_bookings_returns_stock_price_and_price_category_label(self, client):
        now = date_utils.get_naive_utc_now()
        stock = offers_factories.EventStockFactory()
        ongoing_booking = booking_factories.BookingFactory(
            stock=stock, user__deposit__expirationDate=now + timedelta(days=180)
        )
        booking_factories.BookingFactory(
            stock=stock, user=ongoing_booking.user, status=booking_models.BookingStatus.CANCELLED
        )
        client = client.with_token(ongoing_booking.user.email)
        with assert_num_queries(2):
            # select user, booking
            response = client.get("/native/v2/bookings")

        assert response.status_code == 200
        assert (
            response.json["endedBookings"][0]["stock"]["priceCategoryLabel"]
            == stock.priceCategory.priceCategoryLabel.label
        )
        assert response.json["endedBookings"][0]["stock"]["price"] == stock.price * 100
        assert (
            response.json["ongoingBookings"][0]["stock"]["priceCategoryLabel"]
            == stock.priceCategory.priceCategoryLabel.label
        )
        assert response.json["ongoingBookings"][0]["stock"]["price"] == stock.price * 100

    def test_get_free_bookings_in_subcategory(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        ongoing_booking = booking_factories.UsedBookingFactory(
            user=user, stock=offers_factories.StockFactory(price=0, offer__subcategoryId=subcategories.CARTE_MUSEE.id)
        )
        ended_booking = booking_factories.UsedBookingFactory(
            user=user, stock=offers_factories.StockFactory(price=10, offer__subcategoryId=subcategories.CARTE_MUSEE.id)
        )

        client = client.with_token(ongoing_booking.user.email)
        with assert_num_queries(2):
            # select user, booking
            response = client.get("/native/v2/bookings")

        assert response.status_code == 200
        assert response.json["ongoingBookings"][0]["id"] == ongoing_booking.id
        assert response.json["endedBookings"][0]["id"] == ended_booking.id

    def test_get_bookings_15_17_user(self, client):
        user = users_factories.UnderageBeneficiaryFactory(email=self.identifier)

        booking = booking_factories.UsedBookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.TELECHARGEMENT_LIVRE_AUDIO.id,
        )

        test_client = client.with_token(user.email)
        with assert_num_queries(2):
            # select user, booking
            response = test_client.get("/native/v2/bookings")

        assert response.status_code == 200
        assert response.json["ongoingBookings"][0]["id"] == booking.id
        assert response.json["hasBookingsAfter18"] is False

    def test_get_bookings_with_address_on_venue(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        address = AddressFactory()
        venue = offerers_factories.VenueFactory(
            offererAddress=offerers_factories.OffererAddressFactory(address=address)
        )
        offer = offers_factories.OfferFactory(venue=venue, offererAddress=None)
        booking_factories.BookingFactory(stock__offer=offer, user=user)

        with assert_num_queries(2):  # user + booking
            response = client.with_token(self.identifier).get("/native/v2/bookings")

        assert response.status_code == 200
        assert response.json["ongoingBookings"][0]["stock"]["offer"]["address"]["label"] == venue.offererAddress.label
        assert response.json["ongoingBookings"][0]["stock"]["offer"]["address"]["city"] == address.city
        assert response.json["ongoingBookings"][0]["stock"]["offer"]["address"]["id"] == address.id
        assert response.json["ongoingBookings"][0]["stock"]["offer"]["venue"]["address"]["id"] == address.id

    def test_get_bookings_with_address_on_venue_and_offer(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        address_on_venue = AddressFactory()
        address_on_offer = AddressFactory()
        venue = offerers_factories.VenueFactory(
            offererAddress=offerers_factories.OffererAddressFactory(address=address_on_venue)
        )
        offer = offers_factories.OfferFactory(
            venue=venue, offererAddress=offerers_factories.OffererAddressFactory(address=address_on_offer)
        )
        booking_factories.BookingFactory(stock__offer=offer, user=user)

        with assert_num_queries(2):  # user + booking
            response = client.with_token(self.identifier).get("/native/v2/bookings")

        assert response.status_code == 200
        assert response.json["ongoingBookings"][0]["stock"]["offer"]["address"]["label"] == offer.offererAddress.label
        assert response.json["ongoingBookings"][0]["stock"]["offer"]["address"]["city"] == address_on_venue.city
        assert response.json["ongoingBookings"][0]["stock"]["offer"]["address"]["id"] == address_on_offer.id
        assert response.json["ongoingBookings"][0]["stock"]["offer"]["venue"]["address"]["id"] == address_on_venue.id

    def test_get_bookings_user_19_yo(self, client):
        user = users_factories.BeneficiaryFactory(age=19)
        booking_factories.BookingFactory(user=user)

        client = client.with_token(user.email)
        with assert_num_queries(2):  # user + booking
            response = client.get("/native/v2/bookings")

        assert response.status_code == 200
        assert response.json["hasBookingsAfter18"] is True

    def test_return_venue_public_name(self, client):
        venue = offerers_factories.VenueFactory(name="Legal name", publicName="Public name")
        booking = booking_factories.BookingFactory(stock__offer__venue=venue)

        client = client.with_token(booking.user.email)
        response = client.get("/native/v2/bookings")

        assert response.status_code == 200
        assert response.json["ongoingBookings"][0]["stock"]["offer"]["venue"]["name"] == "Public name"

    def test_return_venue_banner_url(self, client):
        venue = offerers_factories.VenueFactory(bannerUrl="http://bannerUrl.com")
        booking = booking_factories.BookingFactory(stock__offer__venue=venue)

        client = client.with_token(booking.user.email)
        response = client.get("/native/v2/bookings")

        assert response.status_code == 200
        assert response.json["ongoingBookings"][0]["stock"]["offer"]["venue"]["bannerUrl"] == "http://bannerUrl.com"

    def test_return_venue_is_open_to_public(self, client):
        venue = offerers_factories.VenueFactory(isOpenToPublic=True)
        booking = booking_factories.BookingFactory(stock__offer__venue=venue)

        client = client.with_token(booking.user.email)
        response = client.get("/native/v2/bookings")

        assert response.status_code == 200
        assert response.json["ongoingBookings"][0]["stock"]["offer"]["venue"]["isOpenToPublic"] is True


class GetBookingsListTest:
    identifier = "pascal.ture@example.com"

    def test_get_bookings_list_returns_ongoing_bookings(self, client):
        OFFER_URL = "https://demo.pass/some/path?token={token}&email={email}&offerId={offerId}"
        user = users_factories.BeneficiaryFactory(email=self.identifier, age=18)

        address_on_offer = AddressFactory()
        venue1 = offerers_factories.VenueFactory(
            city="Paris",
            name="fnac",
            venueLabel=offerers_factories.VenueLabelFactory(label="Fnac Paris"),
            timezone="Europe/Paris",
        )

        venue2 = offerers_factories.VenueFactory(
            city="Marseille",
            name="fnac",
            venueLabel=offerers_factories.VenueLabelFactory(label="Fnac Marseille"),
            timezone="Europe/Paris",
        )

        offer = offers_factories.OfferFactory(
            venue=venue1,
            offererAddress=offerers_factories.OffererAddressFactory(address=address_on_offer),
            withdrawalType=offer_models.WithdrawalTypeEnum.ON_SITE,
            withdrawalDelay=60 * 30,
        )

        stock = offers_factories.EventStockFactory(
            beginningDatetime=datetime.now() + timedelta(days=2),
            offer=offer,
        )

        ongoing_booking = booking_factories.BookingFactory(stock=stock, user=user)

        ended_booking_1 = booking_factories.UsedBookingFactory(
            user=user,
            stock__offer__venue=venue2,
            displayAsEnded=True,
            dateUsed=datetime(2023, 3, 2),
            stock__offer__url=OFFER_URL,
            stock__offer__name="ended booking - offer 1",
            stock__offer__subcategoryId=subcategories.ABO_LIVRE_NUMERIQUE.id,
            stock__features=["VO"],
            stock__offer__extraData=None,
            cancellation_limit_date=datetime(2023, 3, 2),
        )

        digital_stock = offers_factories.StockWithActivationCodesFactory()

        second_activation_code = digital_stock.activationCodes[1]

        ended_booking_2 = booking_factories.UsedBookingFactory(
            user=user,
            displayAsEnded=True,
            stock__offer__name="ended booking - offer 2",
            stock=digital_stock,
            activationCode=second_activation_code,
        )

        ongoing_booking_mediation = offers_factories.MediationFactory(
            id=1, offer=ongoing_booking.stock.offer, thumbCount=1, credit="photo credit"
        )
        offers_factories.MediationFactory(id=2, offer=ended_booking_1.stock.offer, thumbCount=1, credit="photo credit")
        offers_factories.MediationFactory(id=3, offer=ended_booking_2.stock.offer, thumbCount=1, credit="photo credit")

        with assert_num_queries(3):  # user + bookings + offer
            response = client.with_token(self.identifier).get("/native/v2/bookings/ongoing")

        assert response.status_code == 200

        bookings = response.json["bookings"]

        assert len(bookings) == 1

        booking_response = bookings[0]

        assert booking_response == {
            "activationCode": ongoing_booking.activationCode,
            "dateCreated": ongoing_booking.dateCreated.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "id": ongoing_booking.id,
            "quantity": ongoing_booking.quantity,
            "stock": {
                "beginningDatetime": ongoing_booking.stock.beginningDatetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "offer": {
                    "address": {"timezone": ongoing_booking.stock.offer.offererAddress.address.timezone},
                    "id": ongoing_booking.stock.offer.id,
                    "imageUrl": ongoing_booking_mediation.thumbUrl,
                    "isDigital": ongoing_booking.stock.offer.isDigital,
                    "isPermanent": ongoing_booking.stock.offer.isPermanent,
                    "name": ongoing_booking.stock.offer.name,
                    "subcategoryId": ongoing_booking.stock.offer.subcategoryId,
                    "venue": {
                        "city": ongoing_booking.stock.offer.venue.city,
                        "id": ongoing_booking.stock.offer.venue.id,
                        "label": ongoing_booking.stock.offer.venue.venueLabel.label,
                        "name": ongoing_booking.stock.offer.venue.name,
                        "timezone": ongoing_booking.stock.offer.venue.timezone,
                    },
                    "withdrawalDelay": ongoing_booking.stock.offer.withdrawalDelay,
                    "withdrawalType": ongoing_booking.stock.offer.withdrawalType.value,
                },
            },
        }

    def test_get_bookings_list_returns_ended_bookings(self, client):
        user = users_factories.BeneficiaryFactory(email=self.identifier, age=18)

        address_on_offer = AddressFactory()

        paris_timezone = "Europe/Paris"
        offer = offers_factories.OfferFactory(
            venue=offerers_factories.VenueFactory(
                name="fnac",
                venueLabel=offerers_factories.VenueLabelFactory(label="Fnac Paris"),
                timezone=paris_timezone,
            ),
            offererAddress=offerers_factories.OffererAddressFactory(address=address_on_offer),
            withdrawalType=offer_models.WithdrawalTypeEnum.ON_SITE,
            withdrawalDelay=60 * 30,
        )

        stock = offers_factories.EventStockFactory(
            beginningDatetime=datetime.now() + timedelta(days=2),
            offer=offer,
        )

        ongoing_booking = booking_factories.BookingFactory(stock=stock, user=user)

        booking_start_date = datetime(2023, 3, 2)
        ended_booking = booking_factories.UsedBookingFactory(
            user=user,
            stock__offer__venue=offerers_factories.VenueFactory(
                name="fnac",
                venueLabel=offerers_factories.VenueLabelFactory(label="Fnac Marseille"),
                timezone=paris_timezone,
            ),
            stock__offer__offererAddress=offerers_factories.OffererAddressFactory(address=address_on_offer),
            displayAsEnded=True,
            dateUsed=booking_start_date,
            stock__offer__subcategoryId=subcategories.ABO_LIVRE_NUMERIQUE.id,
            stock__offer__withdrawalType=offer_models.WithdrawalTypeEnum.ON_SITE,
            stock__offer__withdrawalDelay=60 * 30,
            stock__beginningDatetime=booking_start_date,
        )

        offers_factories.ActivationCodeFactory(
            booking=ended_booking,
            stock=ended_booking.stock,
            code="ended booking - activation code",
            expirationDate=booking_start_date + timedelta(days=2),
        )

        offers_factories.MediationFactory(id=1, offer=ongoing_booking.stock.offer, thumbCount=1, credit="photo credit")
        ended_booking_mediation = offers_factories.MediationFactory(
            id=2, offer=ended_booking.stock.offer, thumbCount=1, credit="photo credit"
        )

        with assert_num_queries(3):  # user + booking + offer
            response = client.with_token(self.identifier).get("/native/v2/bookings/ended")

        assert response.status_code == 200

        bookings = response.json["bookings"]
        assert len(bookings) == 1

        booking_response = bookings[0]

        assert booking_response == {
            "activationCode": {
                "code": ended_booking.activationCode.code,
                "expirationDate": ended_booking.activationCode.expirationDate.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            "dateCreated": ended_booking.dateCreated.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "id": ended_booking.id,
            "quantity": ended_booking.quantity,
            "stock": {
                "beginningDatetime": ended_booking.stock.beginningDatetime.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "offer": {
                    "address": {"timezone": ended_booking.stock.offer.offererAddress.address.timezone},
                    "id": ended_booking.stock.offer.id,
                    "imageUrl": ended_booking_mediation.thumbUrl,
                    "isDigital": ended_booking.stock.offer.isDigital,
                    "isPermanent": ended_booking.stock.offer.isPermanent,
                    "name": ended_booking.stock.offer.name,
                    "subcategoryId": ended_booking.stock.offer.subcategoryId,
                    "venue": {
                        "city": ended_booking.stock.offer.venue.city,
                        "id": ended_booking.stock.offer.venue.id,
                        "label": ended_booking.stock.offer.venue.venueLabel.label,
                        "name": ended_booking.stock.offer.venue.name,
                        "timezone": ended_booking.stock.offer.venue.timezone,
                    },
                    "withdrawalDelay": ended_booking.stock.offer.withdrawalDelay,
                    "withdrawalType": ended_booking.stock.offer.withdrawalType.value,
                },
            },
        }

    booking_start_date = datetime(2023, 3, 2)

    @pytest.mark.parametrize(
        "status,cancellationDate,cancellationReason,dateUsed,reimbursementDate",
        [
            (booking_models.BookingStatus.USED, None, None, booking_start_date, None),
            (
                booking_models.BookingStatus.REIMBURSED,
                None,
                None,
                booking_start_date,
                booking_start_date + timedelta(days=2),
            ),
            (
                booking_models.BookingStatus.CANCELLED,
                booking_start_date,
                booking_models.BookingCancellationReasons.BENEFICIARY,
                None,
                None,
            ),
        ],
        ids=["used_booking", "reimbursed_booking", "cancelled_booking"],
    )
    def test_get_bookings_list_returns_ended_bookings_when_offer_is_not_permanent(
        self, client, status, cancellationDate, cancellationReason, dateUsed, reimbursementDate
    ):
        user = users_factories.BeneficiaryFactory(email=self.identifier, age=18)

        address_on_offer = AddressFactory()

        paris_timezone = "Europe/Paris"
        offer = offers_factories.OfferFactory(
            venue=offerers_factories.VenueFactory(
                name="fnac",
                venueLabel=offerers_factories.VenueLabelFactory(label="Fnac Paris"),
                timezone=paris_timezone,
            ),
            offererAddress=offerers_factories.OffererAddressFactory(address=address_on_offer),
            withdrawalType=offer_models.WithdrawalTypeEnum.ON_SITE,
            withdrawalDelay=60 * 30,
        )

        stock = offers_factories.EventStockFactory(
            beginningDatetime=datetime.now() + timedelta(days=2),
            offer=offer,
        )

        ongoing_booking = booking_factories.BookingFactory(stock=stock, user=user)

        booking_start_date = datetime(2023, 3, 2)
        ended_booking = booking_factories.UsedBookingFactory(
            user=user,
            status=status,
            stock__offer__venue=offerers_factories.VenueFactory(
                name="fnac",
                venueLabel=offerers_factories.VenueLabelFactory(label="Fnac Marseille"),
                timezone=paris_timezone,
            ),
            stock__offer__offererAddress=offerers_factories.OffererAddressFactory(address=address_on_offer),
            displayAsEnded=False,
            dateUsed=dateUsed,
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
            stock__offer__withdrawalType=offer_models.WithdrawalTypeEnum.ON_SITE,
            stock__offer__withdrawalDelay=60 * 30,
            stock__beginningDatetime=booking_start_date,
            cancellation_limit_date=booking_start_date - timedelta(days=2),
            cancellation_date=cancellationDate,
            cancellationReason=cancellationReason,
            reimbursementDate=reimbursementDate,
        )

        offers_factories.MediationFactory(id=1, offer=ongoing_booking.stock.offer, thumbCount=1, credit="photo credit")
        ended_booking_mediation = offers_factories.MediationFactory(
            id=2, offer=ended_booking.stock.offer, thumbCount=1, credit="photo credit"
        )

        with assert_num_queries(3):  # user + booking + offer
            response = client.with_token(self.identifier).get("/native/v2/bookings/ended")

        assert response.status_code == 200

        bookings = response.json["bookings"]
        assert len(bookings) == 1

        booking_response = bookings[0]

        assert booking_response == {
            "activationCode": None,
            "dateCreated": ended_booking.dateCreated.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "id": ended_booking.id,
            "quantity": ended_booking.quantity,
            "stock": {
                "beginningDatetime": ended_booking.stock.beginningDatetime.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "offer": {
                    "address": {"timezone": ended_booking.stock.offer.offererAddress.address.timezone},
                    "id": ended_booking.stock.offer.id,
                    "imageUrl": ended_booking_mediation.thumbUrl,
                    "isDigital": ended_booking.stock.offer.isDigital,
                    "isPermanent": ended_booking.stock.offer.isPermanent,
                    "name": ended_booking.stock.offer.name,
                    "subcategoryId": ended_booking.stock.offer.subcategoryId,
                    "venue": {
                        "city": ended_booking.stock.offer.venue.city,
                        "id": ended_booking.stock.offer.venue.id,
                        "label": ended_booking.stock.offer.venue.venueLabel.label,
                        "name": ended_booking.stock.offer.venue.name,
                        "timezone": ended_booking.stock.offer.venue.timezone,
                    },
                    "withdrawalDelay": ended_booking.stock.offer.withdrawalDelay,
                    "withdrawalType": ended_booking.stock.offer.withdrawalType.value,
                },
            },
        }

    def test_get_bookings_list_raises_error_when_status_is_unknown(self, client):
        users_factories.BeneficiaryFactory(email=self.identifier, age=18)

        with assert_num_queries(1):  # user
            response_to_unknown_status = client.with_token(self.identifier).get("/native/v2/bookings/invalid_status")

        assert response_to_unknown_status.status_code == 404


class GetBookingTicketTest:
    identifier = "pascal.ture@example.com"

    def test_get_booking_withdrawal_informations(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking_factories.BookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.CONCERT.id,
            stock__offer__withdrawalDetails="Veuillez aller chercher votre billet au guichet",
            stock__offer__withdrawalType=offer_models.WithdrawalTypeEnum.ON_SITE,
            stock__offer__withdrawalDelay=60 * 30,
        )

        with assert_num_queries(2):  # user + booking
            response = client.with_token(self.identifier).get("/native/v2/bookings")
            assert response.status_code == 200

        ticket = response.json["ongoingBookings"][0]["ticket"]
        assert ticket["withdrawal"]["details"] == "Veuillez aller chercher votre billet au guichet"
        assert ticket["withdrawal"]["type"] == "on_site"
        assert ticket["withdrawal"]["delay"] == 60 * 30

    def test_get_booking_no_ticket(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking_factories.BookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.CONCERT.id,
            stock__offer__withdrawalType=offer_models.WithdrawalTypeEnum.NO_TICKET,
        )

        with assert_num_queries(2):  # user + booking
            response = client.with_token(self.identifier).get("/native/v2/bookings")
            assert response.status_code == 200

        ticket = response.json["ongoingBookings"][0]["ticket"]
        assert ticket["display"] == "no_ticket"

    def test_get_booking_not_event_no_ticket(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = booking_factories.BookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.LIVRE_PAPIER.id,
            stock__offer__withdrawalType=offer_models.WithdrawalTypeEnum.NO_TICKET,
        )

        with assert_num_queries(2):  # user + booking
            response = client.with_token(self.identifier).get("/native/v2/bookings")
            assert response.status_code == 200

        ticket = response.json["ongoingBookings"][0]["ticket"]
        assert ticket["token"] == {
            "data": booking.token,
        }
        assert ticket["voucher"] == {"data": f"PASSCULTURE:v3;TOKEN:{booking.token}"}
        assert ticket["display"] == "voucher"

    @pytest.mark.parametrize(
        "withdrawal_delay,delta,display",
        [
            (60 * 60 * 25, 2, "email_will_be_sent"),
            (None, 1, "email_will_be_sent"),
            (60 * 60 * 49, 2, "email_sent"),
            (60 * 60 * 12, 0, "email_sent"),
        ],
    )
    def test_get_booking_ticket_by_email(self, client, withdrawal_delay, delta, display):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        beginningDatetime = date_utils.get_naive_utc_now() + timedelta(days=delta)
        booking_factories.BookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.CONCERT.id,
            stock__offer__withdrawalType=offer_models.WithdrawalTypeEnum.BY_EMAIL,
            stock__offer__withdrawalDelay=withdrawal_delay,
            stock__beginningDatetime=beginningDatetime,
        )

        with assert_num_queries(2):  # user + booking
            response = client.with_token(self.identifier).get("/native/v2/bookings")
            assert response.status_code == 200

        ticket = response.json["ongoingBookings"][0]["ticket"]
        assert ticket["token"] is None
        assert ticket["voucher"] is None
        assert ticket["display"] == display

    def test_get_booking_digital_ticket_with_activation_code(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        digital_stock = offers_factories.StockWithActivationCodesFactory()
        booking_factories.BookingFactory(
            user=user,
            stock=digital_stock,
            activationCode=digital_stock.activationCodes[0],
        )

        with assert_num_queries(2):  # user + booking
            response = client.with_token(self.identifier).get("/native/v2/bookings")
            assert response.status_code == 200

        ticket = response.json["ongoingBookings"][0]["ticket"]
        assert ticket["token"] is None
        assert ticket["voucher"] is None
        booking_id = response.json["ongoingBookings"][0]["id"]
        booking_activation_code = next(code for code in digital_stock.activationCodes if code.bookingId == booking_id)
        assert ticket["activationCode"] == {
            "code": booking_activation_code.code,
            "expirationDate": None,
        }
        assert ticket["display"] == "online_code"

    def test_get_booking_digital_ticket_with_token(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        digital_stock = offers_factories.StockWithActivationCodesFactory()
        booking = booking_factories.BookingFactory(
            user=user,
            stock=digital_stock,
        )

        with assert_num_queries(2):  # user + booking
            response = client.with_token(self.identifier).get("/native/v2/bookings")
            assert response.status_code == 200

        ticket = response.json["ongoingBookings"][0]["ticket"]
        assert ticket["token"] == {
            "data": booking.token,
        }
        assert ticket["voucher"] is None
        assert ticket["activationCode"] == None
        assert ticket["display"] == "online_code"

    def test_get_booking_goods(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = booking_factories.BookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.LIVRE_PAPIER.id,
        )

        with assert_num_queries(2):  # user + booking
            response = client.with_token(self.identifier).get("/native/v2/bookings")
            assert response.status_code == 200

        ticket = response.json["ongoingBookings"][0]["ticket"]
        assert ticket["token"] == {
            "data": booking.token,
        }
        assert ticket["voucher"] == {"data": f"PASSCULTURE:v3;TOKEN:{booking.token}"}
        assert ticket["display"] == "voucher"

    @pytest.mark.parametrize(
        "subcategory,withdrawal_type,voucher,display",
        [
            (subcategories.CONCERT.id, offer_models.WithdrawalTypeEnum.ON_SITE, False, "ticket"),
            (
                subcategories.EVENEMENT_CINE.id,
                offer_models.WithdrawalTypeEnum.ON_SITE,
                False,
                "ticket",
            ),
            (
                subcategories.SEANCE_CINE.id,
                offer_models.WithdrawalTypeEnum.ON_SITE,
                True,
                "qr_code",
            ),
            (
                subcategories.FESTIVAL_MUSIQUE.id,
                offer_models.WithdrawalTypeEnum.ON_SITE,
                False,
                "ticket",
            ),
        ],
    )
    def test_get_internal_event_ticket(self, client, subcategory, withdrawal_type, voucher, display):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)
        booking = booking_factories.BookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategory,
            stock__offer__withdrawalType=withdrawal_type,
        )

        with assert_num_queries(2):  # user + booking
            response = client.with_token(self.identifier).get("/native/v2/bookings")
            assert response.status_code == 200

        ticket = response.json["ongoingBookings"][0]["ticket"]
        if voucher:
            assert ticket["voucher"] == {"data": f"PASSCULTURE:v3;TOKEN:{booking.token}"}
        else:
            assert ticket["voucher"] == None
        assert ticket["token"] == {
            "data": booking.token,
        }
        assert ticket["display"] == display

    @pytest.mark.features(ENABLE_CDS_IMPLEMENTATION=True)
    def test_get_external_event_ticket_visible(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        provider = providers_api.get_provider_by_local_class("CDSStocks")
        beginningDatetime = date_utils.get_naive_utc_now() + timedelta(days=1)
        booking = booking_factories.BookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.SEANCE_CINE.id,
            stock__offer__withdrawalType=offer_models.WithdrawalTypeEnum.IN_APP,
            stock__idAtProviders="11#11#CDS",
            stock__lastProvider=provider,
            stock__offer__lastProvider=provider,
            stock__beginningDatetime=beginningDatetime,
        )
        ExternalBookingFactory(booking=booking, barcode="111111111", seat="A_1")
        ExternalBookingFactory(booking=booking, barcode="111111112", seat="A_2")

        with assert_num_queries(2):  # user + booking
            response = client.with_token(self.identifier).get("/native/v2/bookings")
            assert response.status_code == 200

        ticket = response.json["ongoingBookings"][0]["ticket"]
        response_data = sorted(ticket["externalBooking"]["data"], key=lambda x: x["seat"])
        assert response_data == [
            {"barcode": "111111111", "seat": "A_1"},
            {"barcode": "111111112", "seat": "A_2"},
        ]

        assert ticket["token"] is None
        assert ticket["voucher"] is None
        assert ticket["display"] == "qr_code"

    @pytest.mark.features(ENABLE_CDS_IMPLEMENTATION=True)
    def test_get_external_event_ticket_hidden(self, client):
        user = users_factories.BeneficiaryGrant18Factory(email=self.identifier)

        provider = providers_api.get_provider_by_local_class("CDSStocks")
        beginningDatetime = date_utils.get_naive_utc_now() + timedelta(days=2, seconds=200)
        booking = booking_factories.BookingFactory(
            user=user,
            stock__offer__subcategoryId=subcategories.CONFERENCE.id,
            stock__offer__withdrawalType=offer_models.WithdrawalTypeEnum.IN_APP,
            stock__idAtProviders="11#11#CDS",
            stock__lastProvider=provider,
            stock__offer__lastProvider=provider,
            stock__beginningDatetime=beginningDatetime,
        )
        ExternalBookingFactory(booking=booking, barcode="111111111", seat="A_1")
        ExternalBookingFactory(booking=booking, barcode="111111112", seat="A_2")

        with assert_num_queries(2):  # user + booking
            response = client.with_token(self.identifier).get("/native/v2/bookings")
            assert response.status_code == 200

        ticket = response.json["ongoingBookings"][0]["ticket"]
        assert ticket["externalBooking"] == {
            "data": None,
        }

        assert ticket["token"] is None
        assert ticket["voucher"] is None
        assert ticket["display"] == "not_visible"
