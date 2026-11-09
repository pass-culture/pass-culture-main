from pcapi.core.artist.factories import ArtistFactory
from pcapi.core.highlights.factories import HighlightFactory


def create_tiny_engagement() -> None:
    ArtistFactory.create(name="Georges Brassens")
    ArtistFactory.create_batch(2)
    HighlightFactory.create(
        name="Temps fort petit",
        description="Temps fort auquel rattacher les offres de la petite sandbox.",
    )
