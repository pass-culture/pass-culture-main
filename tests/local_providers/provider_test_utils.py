import os
from pathlib import Path

from pcapi.local_providers.local_provider import LocalProvider
from pcapi.models import VenueProvider, ThingType
from pcapi.models.db import Model
import pcapi.sandboxes


class TestLocalProvider(LocalProvider):
    name = "LocalProvider Test"
    can_create = True

    def __init__(self, venue_provider: VenueProvider = None):
        super().__init__(venue_provider)
        self.venue_provider = venue_provider

    def fill_object_attributes(self, obj):
        obj.name = 'New Product'
        obj.type = str(ThingType.LIVRE_EDITION)

    def __next__(self):
        pass


class TestLocalProviderWithApiErrors(LocalProvider):
    name = "LocalProvider Test"
    can_create = True

    def __init__(self, venue_provider: VenueProvider = None):
        super().__init__(venue_provider)
        self.venue_provider = venue_provider

    def fill_object_attributes(self, obj):
        obj.name = 'New Product'
        obj.type = str(ThingType.JEUX)
        obj.url = 'http://url.com'

    def __next__(self):
        pass


class TestLocalProviderNoCreation(LocalProvider):
    name = "LocalProvider Test No Creation"
    can_create = False

    def __init__(self, venue_provider: VenueProvider = None):
        super().__init__(venue_provider)
        self.venue_provider = venue_provider

    def fill_object_attributes(self, obj):
        obj.name = 'New Product'
        obj.type = str(ThingType.LIVRE_EDITION)

    def __next__(self):
        pass


class TestLocalProviderWithThumb(LocalProvider):
    name = "LocalProvider Test With Thumb"
    can_create = True

    def __init__(self, venue_provider: VenueProvider = None):
        super().__init__(venue_provider)
        self.venue_provider = venue_provider

    def get_object_thumb(self) -> bytes:
        file_path = Path(pcapi.sandboxes.__path__[0]) / 'providers' / 'titelive_mocks' / 'provider_thumb.jpeg'
        return open(file_path, "rb").read()

    def get_object_thumb_index(self) -> int:
        return 1

    def fill_object_attributes(self, pc_object: Model):
        pc_object.name = 'New Product'
        pc_object.type = str(ThingType.LIVRE_EDITION)

    def __next__(self):
        pass


class TestLocalProviderWithThumbIndexAt4(LocalProvider):
    name = "LocalProvider Test With ThumbIndex at 4th position"
    can_create = True

    def __init__(self, venue_provider: VenueProvider = None):
        super().__init__(venue_provider)
        self.venue_provider = venue_provider

    def get_object_thumb(self) -> bytes:
        file_path = Path(pcapi.sandboxes.__path__[0]) / 'providers' / 'titelive_mocks' / 'provider_thumb.jpeg'
        return open(file_path, "rb").read()

    def get_object_thumb_index(self) -> int:
        return 4

    def fill_object_attributes(self, pc_object):
        pc_object.name = 'New Product'
        pc_object.type = str(ThingType.LIVRE_EDITION)

    def __next__(self):
        pass
