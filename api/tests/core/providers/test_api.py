from dataclasses import asdict
from decimal import Decimal
from unittest import mock

import pytest

import pcapi.core.mails.testing as mails_testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.factories as providers_factories
from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.factories import CancelledBookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.history import models as history_models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.factories import StockFactory
from pcapi.core.providers import api
from pcapi.core.providers import exceptions
from pcapi.core.providers import models as providers_models
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.routes.serialization.venue_provider_serialize import PostVenueProviderBody


pytestmark = pytest.mark.usefixtures("db_session")


class CreateVenueProviderTest:
    @pytest.mark.parametrize(
        "venue_type",
        (
            offerers_models.VenueTypeCode.BOOKSTORE,
            offerers_models.VenueTypeCode.MOVIE,
            offerers_models.VenueTypeCode.DIGITAL,
        ),
    )
    def test_permanent_venue_marking(self, venue_type):
        venue = offerers_factories.VenueFactory(venueTypeCode=venue_type, isPermanent=False)
        provider = providers_factories.ProviderFactory(
            enabledForPro=True,
            isActive=True,
            localClass=None,
        )
        author = users_factories.UserFactory()
        api.create_venue_provider(provider, venue, current_user=author)

        assert venue.isPermanent is False


def create_product(ean, **kwargs):
    return offers_factories.ProductFactory(
        idAtProviders=ean,
        subcategoryId=subcategories.LIVRE_PAPIER.id,
        extraData={"prix_livre": 12},
        **kwargs,
    )


def create_offer(ean, venue: offerers_models.Venue):
    return offers_factories.OfferFactory(product=create_product(ean), idAtProvider=ean, venue=venue)


def create_stock(ean, siret, venue: offerers_models.Venue, **kwargs):
    return offers_factories.StockFactory(offer=create_offer(ean, venue), idAtProviders=f"{ean}@{siret}", **kwargs)


def test_reset_stock_quantity():
    offer = OfferFactory(idAtProvider="1")
    venue = offer.venue
    stock1_no_bookings = StockFactory(offer=offer, quantity=10)
    stock2_only_cancelled_bookings = StockFactory(offer=offer, quantity=10)
    CancelledBookingFactory(stock=stock2_only_cancelled_bookings)
    stock3_mix_of_bookings = StockFactory(offer=offer, quantity=10)
    BookingFactory(stock=stock3_mix_of_bookings)
    CancelledBookingFactory(stock=stock3_mix_of_bookings)
    manually_added_offer = OfferFactory(venue=venue)
    stock4_manually_added = StockFactory(offer=manually_added_offer, quantity=10)
    stock5_other_venue = StockFactory(quantity=10)

    api.reset_stock_quantity(venue)

    assert stock1_no_bookings.quantity == 0
    assert stock2_only_cancelled_bookings.quantity == 0
    assert stock3_mix_of_bookings.quantity == 1
    assert stock4_manually_added.quantity == 10
    assert stock5_other_venue.quantity == 10


class DeleteVenueProviderTest:
    @mock.patch("pcapi.core.providers.api.update_venue_synchronized_offers_active_status_job.delay")
    def test_delete_venue_provider(self, mocked_update_all_offers_active_status_job):
        user = users_factories.UserFactory()
        venue_provider = providers_factories.VenueProviderFactory()
        venue = venue_provider.venue
        provider = venue_provider.provider

        api.delete_venue_provider(venue_provider, author=user)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == venue.bookingEmail
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.VENUE_SYNC_DELETED.value)

        assert not venue.venueProviders
        mocked_update_all_offers_active_status_job.assert_called_once_with(venue.id, venue_provider.providerId, False)

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.LINK_VENUE_PROVIDER_DELETED
        assert action.authorUserId == user.id
        assert action.venueId == venue.id
        assert action.extraData["provider_id"] == provider.id
        assert action.extraData["provider_name"] == provider.name


class DisableVenueProviderTest:
    @mock.patch("pcapi.core.providers.api.update_venue_synchronized_offers_active_status_job.delay")
    def test_disable_venue_provider(self, mocked_update_all_offers_active_status_job):
        user = users_factories.UserFactory()
        venue_provider = providers_factories.VenueProviderFactory()
        venue = venue_provider.venue

        request = PostVenueProviderBody(venueId=venue.id, providerId=venue_provider.providerId, isActive=False)
        api.update_venue_provider(venue_provider, request, user)

        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0]["To"] == venue.bookingEmail
        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.VENUE_SYNC_DISABLED.value)

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.LINK_VENUE_PROVIDER_UPDATED
        assert action.authorUserId == user.id
        assert action.venueId == venue.id
        assert action.extraData["provider_id"] == venue_provider.provider.id
        assert action.extraData["provider_name"] == venue_provider.provider.name
        assert action.extraData["modified_info"] == {"isActive": {"old_info": True, "new_info": False}}


class ConnectVenueToAllocineTest:
    def test_connect_venue_with_siret_to_allocine_provider(self):
        allocine_provider = providers_factories.AllocineProviderFactory()
        venue = offerers_factories.VenueFactory()
        providers_factories.AllocineTheaterFactory(
            siret=venue.siret,
            internalId="PXXXXXX",
            theaterId="123VHJ==",
        )

        payload = providers_models.VenueProviderCreationPayload(
            price="9.99",
            isDuo=True,
            quantity=50,
        )
        api.connect_venue_to_allocine(venue, allocine_provider.id, payload)

        venue_provider = db.session.query(providers_models.AllocineVenueProvider).one()
        pivot = db.session.query(providers_models.AllocinePivot).one()
        assert venue_provider.venue == venue
        assert venue_provider.isDuo
        assert venue_provider.quantity == 50
        assert venue_provider.internalId == "PXXXXXX"
        assert venue_provider.venueIdAtOfferProvider == "123VHJ=="
        assert venue_provider.price == Decimal("9.99")
        assert pivot.venueId == venue.id

    def test_connect_venue_without_siret_to_allocine_provider(self):
        allocine_provider = providers_factories.AllocineProviderFactory()
        venue = offerers_factories.VenueWithoutSiretFactory()
        pivot = providers_factories.AllocinePivotFactory(venue=venue)

        payload = providers_models.VenueProviderCreationPayload(
            price="9.99",
            isDuo=True,
            quantity=50,
        )
        api.connect_venue_to_allocine(venue, allocine_provider.id, payload)

        venue_provider = db.session.query(providers_models.AllocineVenueProvider).one()
        assert venue_provider.venue == venue
        assert venue_provider.isDuo
        assert venue_provider.quantity == 50
        assert venue_provider.internalId == pivot.internalId
        assert venue_provider.venueIdAtOfferProvider == pivot.theaterId
        assert venue_provider.price == Decimal("9.99")

    def test_should_throw_when_venue_is_unknown_by_allocine(self):
        venue = offerers_factories.VenueFactory()
        allocine_provider = providers_factories.AllocineProviderFactory()
        # No AllocineTheaterFactory nor AllocinePivotFactory

        payload = providers_models.VenueProviderCreationPayload(
            price="9.99",
            isDuo=True,
            quantity=50,
        )
        with pytest.raises(exceptions.NoMatchingAllocineTheater):
            api.connect_venue_to_allocine(venue, allocine_provider.id, payload)


class UpdateProviderExternalUrlsTest:
    def test_should_raise_because_ticketing_urls_cannot_be_unset(self):
        provider = providers_factories.PublicApiProviderFactory()
        previous_booking_url = provider.bookingExternalUrl
        previous_cancel_url = provider.cancelExternalUrl
        venue = offerers_factories.VenueFactory()
        providers_factories.VenueProviderFactory(provider=provider, venue=venue)
        event_offer = offers_factories.EventOfferFactory(
            lastProvider=provider, venue=venue, withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP
        )
        offers_factories.StockFactory(offer=event_offer)

        with pytest.raises(exceptions.ProviderException) as e:
            api.update_provider_external_urls(provider, booking_external_url=None, cancel_external_url=None)

        assert e.value.errors == {
            "ticketing_urls": [
                f"You cannot unset your `booking_url` and `cancel_url` because you have event(s) with stocks linked to your ticketing system. Blocking event ids: {[event_offer.id]}"
            ]
        }
        # Should not have changed
        assert provider.bookingExternalUrl == previous_booking_url
        assert provider.cancelExternalUrl == previous_cancel_url

    def test_should_raise_because_update_would_lead_to_incoherent_ticketing_set_up(self):
        provider = providers_factories.PublicApiProviderFactory()
        previous_booking_url = provider.bookingExternalUrl
        previous_cancel_url = provider.cancelExternalUrl

        # ---- UNSET
        # Try to unset only `bookingExternalUrl`
        with pytest.raises(exceptions.ProviderException):
            api.update_provider_external_urls(provider, booking_external_url=None)

        # Should not have changed
        assert provider.bookingExternalUrl == previous_booking_url
        assert provider.cancelExternalUrl == previous_cancel_url

        # Try to unset only `cancelExternalUrl`
        with pytest.raises(exceptions.ProviderException):
            api.update_provider_external_urls(provider, cancel_external_url=None)

        # Should not have changed
        assert provider.bookingExternalUrl == previous_booking_url
        assert provider.cancelExternalUrl == previous_cancel_url

        # ---- SET
        provider_with_no_ticketing_urls = providers_factories.ProviderFactory()
        # Try to set only `bookingExternalUrl`
        with pytest.raises(exceptions.ProviderException):
            api.update_provider_external_urls(
                provider_with_no_ticketing_urls, booking_external_url="https://coucou.com"
            )

        # Should not have changed
        assert provider_with_no_ticketing_urls.bookingExternalUrl == None
        assert provider_with_no_ticketing_urls.cancelExternalUrl == None

        # Try to set only `cancelExternalUrl`
        with pytest.raises(exceptions.ProviderException):
            api.update_provider_external_urls(
                provider_with_no_ticketing_urls, cancel_external_url="https://aurevoir.com"
            )

        # Should not have changed
        assert provider_with_no_ticketing_urls.bookingExternalUrl == None
        assert provider_with_no_ticketing_urls.cancelExternalUrl == None

    def test_should_do_nothing(self):
        provider = providers_factories.PublicApiProviderFactory()
        previous_booking_url = provider.bookingExternalUrl
        previous_cancel_url = provider.cancelExternalUrl
        previous_notification_url = provider.notificationExternalUrl

        api.update_provider_external_urls(provider)

        # Should not have changed
        assert provider.bookingExternalUrl == previous_booking_url
        assert provider.cancelExternalUrl == previous_cancel_url
        assert provider.notificationExternalUrl == previous_notification_url

    def test_should_unset_ticketing_urls_because_there_is_no_future_stocks(self):
        provider = providers_factories.PublicApiProviderFactory()
        venue = offerers_factories.VenueFactory()
        providers_factories.VenueProviderFactory(provider=provider, venue=venue)
        offers_factories.EventOfferFactory(
            lastProvider=provider, venue=venue, withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP
        )
        api.update_provider_external_urls(provider, booking_external_url=None, cancel_external_url=None)

        # Should have unset the ticketing urls
        assert provider.bookingExternalUrl == None
        assert provider.cancelExternalUrl == None

    def test_should_update_ticketing_urls(self):
        provider = providers_factories.PublicApiProviderFactory()
        previous_notification_url = provider.notificationExternalUrl

        api.update_provider_external_urls(
            provider,
            booking_external_url="https://coucou.com",
            cancel_external_url="https://aurevoir.com",
        )

        assert provider.bookingExternalUrl == "https://coucou.com"
        assert provider.cancelExternalUrl == "https://aurevoir.com"
        assert provider.notificationExternalUrl == previous_notification_url

    def test_should_update_notification_external_url(self):
        provider = providers_factories.PublicApiProviderFactory()
        previous_booking_url = provider.bookingExternalUrl
        previous_cancel_url = provider.cancelExternalUrl

        api.update_provider_external_urls(
            provider,
            notification_external_url="https://hello.com",
        )

        assert provider.bookingExternalUrl == previous_booking_url
        assert provider.cancelExternalUrl == previous_cancel_url
        assert provider.notificationExternalUrl == "https://hello.com"

    def test_should_update_booking_external_url(self):
        provider = providers_factories.PublicApiProviderFactory()
        previous_cancel_url = provider.cancelExternalUrl
        previous_notification_url = provider.notificationExternalUrl

        api.update_provider_external_urls(provider, booking_external_url="https://coucou.com")

        # Should not have changed
        assert provider.bookingExternalUrl == "https://coucou.com"
        assert provider.cancelExternalUrl == previous_cancel_url
        assert provider.notificationExternalUrl == previous_notification_url

    def test_should_update_cancel_external_url(self):
        provider = providers_factories.PublicApiProviderFactory()
        previous_booking_url = provider.bookingExternalUrl
        previous_notification_url = provider.notificationExternalUrl

        api.update_provider_external_urls(provider, cancel_external_url="https://aurevoir.com")

        # Should not have changed
        assert provider.bookingExternalUrl == previous_booking_url
        assert provider.cancelExternalUrl == "https://aurevoir.com"
        assert provider.notificationExternalUrl == previous_notification_url


class UpdateVenueProviderExternalUrlsTest:
    def test_should_raise_because_ticketing_urls_cannot_be_unset(self):
        provider_without_ticketing_urls = providers_factories.ProviderFactory()
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=provider_without_ticketing_urls, venue=venue)
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        previous_booking_url = venue_provider_external_urls.bookingExternalUrl
        previous_cancel_url = venue_provider_external_urls.cancelExternalUrl
        event_offer = offers_factories.EventOfferFactory(
            lastProvider=provider_without_ticketing_urls,
            venue=venue,
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
        )
        offers_factories.StockFactory(offer=event_offer)

        with pytest.raises(exceptions.ProviderException) as e:
            api.update_venue_provider_external_urls(venue_provider, booking_external_url=None, cancel_external_url=None)

        assert e.value.errors == {
            "ticketing_urls": [
                f"You cannot unset your `booking_url` and `cancel_url` because you have event(s) with stocks linked to your ticketing system. Blocking event ids: {[event_offer.id]}"
            ]
        }
        # Should not have changed
        assert venue_provider_external_urls.bookingExternalUrl == previous_booking_url
        assert venue_provider_external_urls.cancelExternalUrl == previous_cancel_url

    def test_should_raise_because_update_unset_only_one_ticketing_url(self):
        provider_without_ticketing_urls = providers_factories.ProviderFactory()
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=provider_without_ticketing_urls, venue=venue)
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        previous_booking_url = venue_provider_external_urls.bookingExternalUrl
        previous_cancel_url = venue_provider_external_urls.cancelExternalUrl

        # Try to unset only `booking_external_url`
        with pytest.raises(exceptions.ProviderException) as e:
            api.update_venue_provider_external_urls(venue_provider, booking_external_url=None)
        assert e.value.errors == {
            "ticketing_urls": ["Your `booking_url` and `cancel_url` must be either both set or both unset"]
        }

        # Try to unset only `cancel_external_url`
        with pytest.raises(exceptions.ProviderException) as e:
            api.update_venue_provider_external_urls(venue_provider, cancel_external_url=None)
        assert e.value.errors == {
            "ticketing_urls": ["Your `booking_url` and `cancel_url` must be either both set or both unset"]
        }

        # Should not have changed
        assert venue_provider_external_urls.bookingExternalUrl == previous_booking_url
        assert venue_provider_external_urls.cancelExternalUrl == previous_cancel_url

    def test_should_raise_because_update_set_only_one_ticketing_url(self):
        provider_without_ticketing_urls = providers_factories.ProviderFactory()
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=provider_without_ticketing_urls, venue=venue)

        # Try to set only `booking_external_url`
        with pytest.raises(exceptions.ProviderException):
            api.update_venue_provider_external_urls(venue_provider, booking_external_url="https://coucou.com")

        # Try to set only `cancel_external_url`
        with pytest.raises(exceptions.ProviderException):
            api.update_venue_provider_external_urls(venue_provider, cancel_external_url="https://aurevoir.com")

    def test_should_do_nothing(self):
        provider = providers_factories.ProviderFactory()
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=provider, venue=venue)
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        previous_booking_url = venue_provider_external_urls.bookingExternalUrl
        previous_cancel_url = venue_provider_external_urls.cancelExternalUrl
        previous_notification_url = venue_provider_external_urls.notificationExternalUrl

        api.update_venue_provider_external_urls(venue_provider)

        # Should not have changed
        assert venue_provider_external_urls.bookingExternalUrl == previous_booking_url
        assert venue_provider_external_urls.cancelExternalUrl == previous_cancel_url
        assert venue_provider_external_urls.notificationExternalUrl == previous_notification_url

    def test_should_update_notification_url(self):
        provider = providers_factories.ProviderFactory()
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=provider, venue=venue)
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        previous_booking_url = venue_provider_external_urls.bookingExternalUrl
        previous_cancel_url = venue_provider_external_urls.cancelExternalUrl

        api.update_venue_provider_external_urls(venue_provider, notification_external_url="https://jado.re/les/notifs")

        # Should have updated `notificationExternalUrl`
        assert venue_provider_external_urls.bookingExternalUrl == previous_booking_url
        assert venue_provider_external_urls.cancelExternalUrl == previous_cancel_url
        assert venue_provider_external_urls.notificationExternalUrl == "https://jado.re/les/notifs"

    def test_should_update_cancel_url(self):
        provider = providers_factories.ProviderFactory()
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=provider, venue=venue)
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        previous_booking_url = venue_provider_external_urls.bookingExternalUrl
        previous_notification_url = venue_provider_external_urls.notificationExternalUrl

        api.update_venue_provider_external_urls(venue_provider, cancel_external_url="https://adieu.com")

        # Should have updated `cancelExternalUrl`
        assert venue_provider_external_urls.bookingExternalUrl == previous_booking_url
        assert venue_provider_external_urls.cancelExternalUrl == "https://adieu.com"
        assert venue_provider_external_urls.notificationExternalUrl == previous_notification_url

    def test_should_update_booking_url(self):
        provider = providers_factories.ProviderFactory()
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=provider, venue=venue)
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        previous_cancel_url = venue_provider_external_urls.cancelExternalUrl
        previous_notification_url = venue_provider_external_urls.notificationExternalUrl

        api.update_venue_provider_external_urls(venue_provider, booking_external_url="https://bonjour.com")

        # Should have updated `bookingExternalUrl`
        assert venue_provider_external_urls.bookingExternalUrl == "https://bonjour.com"
        assert venue_provider_external_urls.cancelExternalUrl == previous_cancel_url
        assert venue_provider_external_urls.notificationExternalUrl == previous_notification_url

    def test_should_unset_ticketing_urls_because_no_linked_events(self):
        provider = providers_factories.ProviderFactory()
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=provider, venue=venue)
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        previous_notification_url = venue_provider_external_urls.notificationExternalUrl

        api.update_venue_provider_external_urls(venue_provider, booking_external_url=None, cancel_external_url=None)

        # Should have unset ticketing urls
        assert venue_provider_external_urls.bookingExternalUrl == None
        assert venue_provider_external_urls.cancelExternalUrl == None
        assert venue_provider_external_urls.notificationExternalUrl == previous_notification_url

    def test_should_unset_ticketing_urls_because_ticketing_urls_are_defined_at_provider_level(self):
        provider_with_ticketing_urls = providers_factories.PublicApiProviderFactory()
        # Venue
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=provider_with_ticketing_urls, venue=venue)
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )
        # Event
        event_offer = offers_factories.EventOfferFactory(
            lastProvider=provider_with_ticketing_urls,
            venue=venue,
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
        )
        offers_factories.StockFactory(offer=event_offer)
        previous_notification_url = venue_provider_external_urls.notificationExternalUrl

        api.update_venue_provider_external_urls(venue_provider, booking_external_url=None, cancel_external_url=None)

        # Should have unset ticketing urls
        assert venue_provider_external_urls.bookingExternalUrl == None
        assert venue_provider_external_urls.cancelExternalUrl == None
        assert venue_provider_external_urls.notificationExternalUrl == previous_notification_url

    def test_should_delete_venue_provider_external_urls(self):
        provider = providers_factories.ProviderFactory()
        # Venue
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=provider, venue=venue)
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider
        )

        assert venue_provider.externalUrls == venue_provider_external_urls

        api.update_venue_provider_external_urls(
            venue_provider, booking_external_url=None, cancel_external_url=None, notification_external_url=None
        )
        db.session.refresh(venue_provider)

        # Should have deleted `venue_provider_external_urls`
        assert venue_provider.externalUrls == None

    def test_should_delete_venue_provider_external_urls_even_if_it_is_a_partial_unset_of_ticket_urls(self):
        provider = providers_factories.ProviderFactory()
        # Venue
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=provider, venue=venue)
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider,
            notificationExternalUrl=None,
        )

        assert venue_provider.externalUrls == venue_provider_external_urls

        api.update_venue_provider_external_urls(
            venue_provider,
            booking_external_url=None,
            cancel_external_url=None,
        )
        db.session.refresh(venue_provider)

        # Should have deleted `venue_provider_external_urls`
        assert venue_provider.externalUrls == None

    def test_should_delete_venue_provider_external_urls_even_if_it_is_a_partial_unset_of_notif_url(self):
        provider = providers_factories.ProviderFactory()
        # Venue
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=provider, venue=venue)
        venue_provider_external_urls = providers_factories.VenueProviderExternalUrlsFactory(
            venueProvider=venue_provider,
            bookingExternalUrl=None,
            cancelExternalUrl=None,
        )

        assert venue_provider.externalUrls == venue_provider_external_urls

        api.update_venue_provider_external_urls(
            venue_provider,
            notification_external_url=None,
        )
        db.session.refresh(venue_provider)

        # Should have deleted `venue_provider_external_urls`
        assert venue_provider.externalUrls == None

    def test_should_create_venue_provider_external_urls(self):
        provider = providers_factories.ProviderFactory()
        # Venue
        venue = offerers_factories.VenueFactory()
        venue_provider = providers_factories.VenueProviderFactory(provider=provider, venue=venue)

        assert venue_provider.externalUrls == None

        api.update_venue_provider_external_urls(
            venue_provider, booking_external_url="https://helloooooo.co", cancel_external_url="https://byyyyyye.co"
        )

        # Should have created `venue_provider_external_urls`
        assert venue_provider.externalUrls.bookingExternalUrl == "https://helloooooo.co"
        assert venue_provider.externalUrls.cancelExternalUrl == "https://byyyyyye.co"
        assert venue_provider.externalUrls.notificationExternalUrl == None
