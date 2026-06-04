import pytest

from pcapi.core.artist.models import Artist
from pcapi.core.artist.models import ArtistOfferLink
from pcapi.core.artist.models import ArtistProductLink
from pcapi.core.artist.models import ArtistType
from pcapi.core.categories import subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.models import db
from pcapi.sandboxes.scripts.creators.test_cases import _create_artist_without_offers
from pcapi.sandboxes.scripts.creators.test_cases import _create_multi_category_artist


@pytest.mark.usefixtures("db_session")
class CreateMultiCategoryArtistTest:
    def test_creates_one_artist_with_offers_in_several_subcategories(self):
        venue = offerers_factories.VenueFactory.create(name="QA — multi catégories")

        _create_multi_category_artist(venue)

        artist = db.session.query(Artist).filter_by(name="Charles Aznavour").one()
        assert artist.wikidata_id == "Q170348"
        assert artist.biography is not None
        assert artist.wikipedia_url == "https://fr.wikipedia.org/wiki/Charles_Aznavour"

        product_subcategories = {
            link.product.subcategoryId
            for link in db.session.query(ArtistProductLink).filter_by(artist_id=artist.id).all()
        }
        assert product_subcategories == {
            subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
            subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
            subcategories.SEANCE_CINE.id,
            subcategories.LIVRE_PAPIER.id,
        }

    def test_links_use_expected_artist_types_per_category(self):
        venue = offerers_factories.VenueFactory.create(name="QA — multi catégories types")

        _create_multi_category_artist(venue)

        artist = db.session.query(Artist).filter_by(name="Charles Aznavour").one()
        links_by_subcategory: dict[str, set[ArtistType]] = {}
        for link in db.session.query(ArtistProductLink).filter_by(artist_id=artist.id).all():
            links_by_subcategory.setdefault(link.product.subcategoryId, set()).add(link.artist_type)

        assert links_by_subcategory[subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id] == {ArtistType.PERFORMER}
        assert links_by_subcategory[subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id] == {ArtistType.PERFORMER}
        assert links_by_subcategory[subcategories.SEANCE_CINE.id] == {ArtistType.FILM_ACTOR}
        assert links_by_subcategory[subcategories.LIVRE_PAPIER.id] == {ArtistType.AUTHOR}


@pytest.mark.usefixtures("db_session")
class CreateArtistWithoutOffersTest:
    def test_creates_artist_without_any_offer_link(self):
        _create_artist_without_offers()

        artist = db.session.query(Artist).filter_by(name="Artiste sans offre").one()
        assert artist.biography is not None

        product_links = db.session.query(ArtistProductLink).filter_by(artist_id=artist.id).count()
        offer_links = db.session.query(ArtistOfferLink).filter_by(artist_id=artist.id).count()
        assert product_links == 0
        assert offer_links == 0
