import datetime
from pathlib import Path

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers.models import VenueProvider
from pcapi.local_providers.local_provider import LocalProvider
from pcapi.models import Model

import tests


class TestLocalProvider(LocalProvider):
    name = "LocalProvider Test"
    can_create = True

    def __init__(self, venue_provider: VenueProvider = None, enable_debug: bool = False):
        super().__init__(venue_provider)
        self.venue_provider = venue_provider
        self.enable_debug = enable_debug

    def fill_object_attributes(self, obj):
        obj.name = "New Product"
        obj.subcategoryId = subcategories.LIVRE_PAPIER.id
        if isinstance(obj, offers_models.Offer):
            obj.venue = offerers_factories.VenueFactory()

    def __next__(self):
        pass


class TestLocalProviderWithApiErrors(LocalProvider):
    name = "LocalProvider Test"
    can_create = True

    def __init__(self, venue_provider: VenueProvider = None):
        super().__init__(venue_provider)
        self.venue_provider = venue_provider

    def fill_object_attributes(self, obj):
        obj.name = "New Product"
        obj.subcategoryId = subcategories.ACHAT_INSTRUMENT.id
        obj.url = "http://url.com"
        if self.venue_provider:
            obj.venue = self.venue_provider.venue

    def __next__(self):
        pass


class TestLocalProviderNoCreation(LocalProvider):
    name = "LocalProvider Test No Creation"
    can_create = False

    def __init__(self, venue_provider: VenueProvider = None):
        super().__init__(venue_provider)
        self.venue_provider = venue_provider

    def fill_object_attributes(self, obj):
        obj.name = "New Product"
        obj.subcategoryId = subcategories.LIVRE_PAPIER.id

    def __next__(self):
        pass


class TestLocalProviderWithThumb(LocalProvider):
    name = "LocalProvider Test With Thumb"
    can_create = True

    def __init__(self, venue_provider: VenueProvider = None):
        super().__init__(venue_provider)
        self.venue_provider = venue_provider

    def get_object_thumb(self) -> bytes:
        file_path = Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(file_path, "rb") as f:
            return f.read()

    def shall_synchronize_thumbs(self) -> bool:
        return True

    def fill_object_attributes(self, pc_object: Model):
        pc_object.name = "New Product"
        pc_object.subcategoryId = subcategories.LIVRE_PAPIER.id

    def __next__(self):
        pass


class TestLocalProviderWithThumbIndexAt4(LocalProvider):
    name = "LocalProvider Test With ThumbIndex at 4th position"
    can_create = True

    def __init__(self, venue_provider: VenueProvider = None):
        super().__init__(venue_provider)
        self.venue_provider = venue_provider

    def get_object_thumb(self) -> bytes:
        file_path = Path(tests.__path__[0]) / "files" / "mouette_portrait.jpg"
        with open(file_path, "rb") as f:
            return f.read()

    def shall_synchronize_thumbs(self) -> bool:
        return True

    def fill_object_attributes(self, pc_object):
        pc_object.name = "New Product"
        pc_object.subcategoryId = subcategories.LIVRE_PAPIER.id

    def __next__(self):
        pass


def create_finance_event_to_update(stock, venue_provider):
    """Create the different objects in db for finance event update"""

    booking = bookings_factories.UsedBookingFactory(stock=stock, dateUsed=datetime.datetime.utcnow())
    event = finance_factories.FinanceEventFactory(
        booking=booking,
        pricingOrderingDate=stock.beginningDatetime,
        status=finance_models.FinanceEventStatus.PRICED,
        venue=venue_provider.venue,
    )
    finance_factories.PricingFactory(event=event, booking=event.booking)
    return event
