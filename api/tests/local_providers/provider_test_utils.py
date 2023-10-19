from pathlib import Path

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.providers.models import VenueProvider
from pcapi.local_providers.local_provider import LocalProvider
from pcapi.models import Model

import tests


class TestLocalProvider(LocalProvider):
    name = "LocalProvider Test"
    can_create = True

    def __init__(self, venue_provider: VenueProvider = None):
        super().__init__(venue_provider)
        self.venue_provider = venue_provider

    def fill_object_attributes(self, obj):
        obj.name = "New Product"
        obj.subcategoryId = subcategories.LIVRE_PAPIER.id

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
