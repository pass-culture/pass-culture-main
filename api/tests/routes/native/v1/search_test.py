import pytest

from pcapi.core.artist import factories as artist_factories
from pcapi.core.categories import subcategories
from pcapi.core.offers import factories as offers_factories


pytestmark = pytest.mark.usefixtures("db_session")


class SearchOffersTest:
    def test_empty_query(self, client):
        response = client.get("/native/v1/search/offers?query=")

        assert response.status_code == 200
        assert response.json["hits"] == []
        assert response.json["nbHits"] == 0

    @pytest.mark.settings(ALGOLIA_OFFERS_INDEX_NAME="offers-index")
    def test_suggestions(self, client):
        offers = offers_factories.OfferFactory.create_batch(
            2, name="Concert de Jazz", subcategoryId=subcategories.CONCERT.id
        )
        offers_factories.OfferFactory(name="Livre <b>", subcategoryId=subcategories.LIVRE_PAPIER.id)

        response = client.get("/native/v1/search/offers?query=jazz", headers={"Origin": "http://localhost:3000"})

        assert response.status_code == 200
        assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"
        assert response.json["nbHits"] == 2
        hit = response.json["hits"][0]
        assert hit["objectID"] == str(offers[0].id)
        assert hit["query"] == "concert de jazz"
        assert hit["_highlightResult"]["query"] == {
            "value": "concert de __ais-highlight__jazz__/ais-highlight__",
            "matchLevel": "partial",
            "matchedWords": ["jazz"],
        }
        index_data = hit["offers-index"]
        assert index_data["exact_nb_hits"] == 2
        assert {"value": "CONCERTS_FESTIVALS", "count": 2} in index_data["facets"]["analytics"]["offer.searchGroups"]

    def test_offer_fields(self, client):
        stock = offers_factories.EventStockFactory(offer__name="Lapin", price=12.5)
        offer = stock.offer

        response = client.get("/native/v1/search/offers?query=lapin")

        hit = response.json["hits"][0]
        assert hit["offer"]["name"] == "Lapin"
        assert hit["offer"]["subcategoryId"] == offer.subcategoryId
        assert hit["offer"]["prices"] == [12.5]
        assert hit["offer"]["dates"] == [stock.beginningDatetime.timestamp()]
        assert hit["offer"]["isDigital"] is False
        assert hit["offer"]["searchGroupName"] is not None
        assert set(hit["_geoloc"]) == {"lat", "lng"}
        assert hit["venue"]["id"] == offer.venue.id
        assert hit["venue"]["publicName"] == offer.venue.publicName

    def test_highlight_does_not_escape_html(self, client):
        offers_factories.OfferFactory(name="Livre <b>")

        response = client.get("/native/v1/search/offers?query=livre")

        assert response.json["hits"][0]["_highlightResult"]["query"]["value"] == (
            "__ais-highlight__livre__/ais-highlight__ <b>"
        )


class SearchArtistsTest:
    def test_empty_query(self, client):
        artist_factories.ArtistFactory(name="Daft Punk")

        response = client.get("/native/v1/search/artists?query=")

        assert response.status_code == 200
        assert response.json["hits"] == []
        assert response.json["nbHits"] == 0

    def test_exact_match_first(self, client):
        artist_factories.ArtistFactory(name="Les Daft")
        artist_factories.ArtistFactory(name="Daft Punk")
        exact = artist_factories.ArtistFactory(name="Daft")
        artist_factories.ArtistFactory(name="Justice")

        response = client.get("/native/v1/search/artists?query=daft")

        assert [hit["name"] for hit in response.json["hits"]] == ["Daft", "Daft Punk", "Les Daft"]
        assert response.json["hits"][0]["objectID"] == exact.id
        assert response.json["hits"][0]["_highlightResult"]["name"] == {
            "value": "__ais-highlight__Daft__/ais-highlight__",
            "matchLevel": "full",
            "matchedWords": ["daft"],
        }

    def test_partial_match(self, client):
        artist_factories.ArtistFactory(name="Daft Punk")

        response = client.get("/native/v1/search/artists?query=punk")

        assert response.json["hits"][0]["_highlightResult"]["name"] == {
            "value": "Daft __ais-highlight__Punk__/ais-highlight__",
            "matchLevel": "partial",
            "matchedWords": ["punk"],
        }

    def test_match_ignores_case_and_accents(self, client):
        artist_factories.ArtistFactory(name="Céline Dion")

        response = client.get("/native/v1/search/artists?query=CELINE")

        assert response.json["nbHits"] == 1
        assert response.json["hits"][0]["_highlightResult"]["name"]["value"] == (
            "__ais-highlight__Céline__/ais-highlight__ Dion"
        )

    def test_hit_format(self, client):
        artist = artist_factories.ArtistFactory(name="Daft Punk", description="Duo électro")
        artist_factories.ArtistFactory(name="Daft Blacklisted", is_blacklisted=True)

        response = client.get("/native/v1/search/artists?query=daft", headers={"Origin": "http://localhost:3000"})

        assert response.status_code == 200
        assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"
        assert response.json == {
            "hits": [
                {
                    "objectID": artist.id,
                    "name": "Daft Punk",
                    "image": artist.thumbUrl,
                    "description": "Duo électro",
                    "_highlightResult": {
                        "name": {
                            "value": "__ais-highlight__Daft__/ais-highlight__ Punk",
                            "matchLevel": "partial",
                            "matchedWords": ["daft"],
                        }
                    },
                }
            ],
            "nbHits": 1,
            "page": 0,
            "nbPages": 1,
            "hitsPerPage": 20,
            "processingTimeMS": response.json["processingTimeMS"],
            "exhaustiveNbHits": True,
            "query": "daft",
            "params": "query=daft",
        }
