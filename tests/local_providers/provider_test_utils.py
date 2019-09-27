from local_providers.local_provider import LocalProvider
from models import Product, VenueProvider, ThingType


class TestLocalProvider(LocalProvider):
    help = ""
    identifierDescription = "Code LocalProvider"
    identifierRegexp = "*"
    name = "LocalProvider Test"
    object_type = Product
    canCreate = True

    def __init__(self, venue_provider: VenueProvider = None):
        super().__init__(venue_provider)
        self.venue_provider = venue_provider

    def fill_object_attributes(self, obj):
        obj.name = 'New Product'
        obj.type = str(ThingType.LIVRE_EDITION)

    def __next__(self):
        pass


class TestLocalProviderWithApiErrors(LocalProvider):
    help = ""
    identifierDescription = "Code LocalProvider With Api Errors"
    identifierRegexp = "*"
    name = "LocalProvider Test"
    object_type = Product
    canCreate = True

    def __init__(self, venue_provider: VenueProvider = None):
        super().__init__(venue_provider)
        self.venue_provider = venue_provider

    def fill_object_attributes(self, obj):
        obj.name = 'New Product'
        obj.type = str(ThingType.LIVRE_EDITION)
        obj.url = 'http://url.com'
        obj.type = str(ThingType.JEUX)

    def __next__(self):
        pass


class TestLocalProviderNoCreation(LocalProvider):
    help = ""
    identifierDescription = "Code LocalProvider No Creation"
    identifierRegexp = "*"
    name = "LocalProvider Test No Creation"
    object_type = Product
    canCreate = False

    def __init__(self, venue_provider: VenueProvider = None):
        super().__init__(venue_provider)
        self.venue_provider = venue_provider

    def fill_object_attributes(self, obj):
        obj.name = 'New Product'
        obj.type = str(ThingType.LIVRE_EDITION)

    def __next__(self):
        pass