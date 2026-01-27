import factory

from pcapi.core.factories import BaseFactory
from pcapi.core.offers import models as offers_models

from . import models


some_artist_images = [
    "https://upload.wikimedia.org/wikipedia/commons/f/fa/Colleen_Hoover_Video_Call.png",
    "https://upload.wikimedia.org/wikipedia/commons/e/e9/FIBD2023HajimeIsayama_01.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/6/60/Vincent_Willem_van_Gogh_107.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/0/08/JUL_-_Julien_Mari_2018.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/6/62/Madsen_Niko_Maurer_2008_01.jpg",
]


class ArtistFactory(BaseFactory[models.Artist]):
    class Meta:
        model = models.Artist

    name = factory.Faker("name")
    description = factory.Faker("text")
    image_license_url = factory.Faker("url")
    image = factory.LazyAttributeSequence(lambda _, n: some_artist_images[n % len(some_artist_images)])
    wikidata_id = factory.Sequence(lambda n: f"Q{n + 1:05d}")


class ArtistAliasFactory(BaseFactory):
    class Meta:
        model = models.ArtistAlias

    artist_alias_name = factory.Faker("name")
    artist_cluster_id = factory.Faker("pystr", max_chars=10)
    artist_wiki_data_id = factory.Faker("pystr", max_chars=10)
    offer_category_id = factory.Faker("pystr", max_chars=10)


class ArtistProductLinkFactory(BaseFactory):
    class Meta:
        model = models.ArtistProductLink

    artist_id = factory.SubFactory(models.Artist)
    product_id = factory.SubFactory(offers_models.Product)


class ArtistOfferLinkFactory(BaseFactory):
    class Meta:
        model = models.ArtistOfferLink

    artist_type = models.ArtistType.PERFORMER
