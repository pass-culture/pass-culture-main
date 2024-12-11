import random

import factory

from pcapi.core.factories import BaseFactory

from . import models


some_artist_images = [
    "https://commons.wikimedia.org/wiki/File:Colleen_Hoover_Video_Call.png",
    "https://commons.wikimedia.org/wiki/File:FIBD2023HajimeIsayama_01.jpg",
    "https://commons.wikimedia.org/wiki/File:Vincent_Willem_van_Gogh_107.jpg"
    "https://commons.wikimedia.org/w/index.php?search=jul&title=Special:MediaSearch&go=Go&type=image",
    "https://commons.wikimedia.org/wiki/File:Madsen_Niko_Maurer_2008_01.jpg",
    "https://commons.wikimedia.org/w/index.php?search=Taylor+Swift&title=Special:MediaSearch&type=image",
]


class ArtistFactory(BaseFactory):
    class Meta:
        model = models.Artist

    name = factory.Faker("name")
    description = factory.Faker("text")
    image_liscence_url = factory.Faker("url")
    image = factory.LazyAttribute(lambda o: random.choice(some_artist_images))


class ArtistAliasFactory(BaseFactory):
    class Meta:
        model = models.ArtistAlias

    artist_alias_name = factory.Faker("name")
    artist_cluster_id = factory.Faker("pystr", max_chars=10)
    artist_wiki_data_id = factory.Faker("pystr", max_chars=10)
    offer_category_id = factory.Faker("pystr", max_chars=10)
