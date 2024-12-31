import uuid

from pcapi.connectors.big_query.queries.artist import ArtistAliasModel
from pcapi.connectors.big_query.queries.artist import ArtistModel
from pcapi.connectors.big_query.queries.artist import ArtistProductLinkModel


raw_artists_data = [
    {
        "artist_id": uuid.uuid4().hex,
        "artist_name": "Big Query",
        "artist_description": "Big Query is a Canadian singer-songwriter and musician.",
        "wikidata_image_file_url": "https://images.dog.ceo/breeds/eskimo/n02109961_546.jpg",
        "wikidata_image_author": "Big Query",
        "wikidata_image_license": "CC BY-SA 4.0",
        "wikidata_image_license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
    },
    {
        "artist_id": uuid.uuid4().hex,
        "artist_name": "Smol Reqvest",
        "artist_description": "Smol Reqvest est un écrivain biélorusse.",
        "wikidata_image_file_url": "https://images.dog.ceo/breeds/leonberg/n02111129_2062.jpg",
        "wikidata_image_author": "Big Query",
        "wikidata_image_license": "CC BY-SA 4.0",
        "wikidata_image_license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
    },
]


big_query_artist_fixture = [
    ArtistModel(
        id=raw_artist["artist_id"],
        name=raw_artist["artist_name"],
        description=raw_artist["artist_description"],
        image=raw_artist["wikidata_image_file_url"],
        image_author=raw_artist["wikidata_image_author"],
        image_license=raw_artist["wikidata_image_license"],
        image_license_url=raw_artist["wikidata_image_license_url"],
    )
    for raw_artist in raw_artists_data
]


def build_big_query_artist_product_link_fixture(product_ids: list[str], artist_id: str, artist_type: str) -> list:
    return [
        ArtistProductLinkModel(
            artist_id=artist_id,
            product_id=product_id,
            artist_type=artist_type,
        )
        for product_id in product_ids
    ]


big_query_artist_alias_fixture = [
    ArtistAliasModel(
        artist_id=raw_artists_data[0]["artist_id"],
        artist_alias_name="Big Query",
        artist_cluster_id="123456789",
        artist_type="performer",
        artist_wiki_data_id="Q123456789",
        offer_category_id="FESTIVAL_MUSIQUE",
    ),
    ArtistAliasModel(
        artist_id=raw_artists_data[1]["artist_id"],
        artist_alias_name="Big Q",
        artist_cluster_id="123456789",
        artist_type="performer",
        artist_wiki_data_id="Q123456789",
        offer_category_id="FESTIVAL_MUSIQUE",
    ),
    ArtistAliasModel(
        artist_id=raw_artists_data[1]["artist_id"],
        artist_alias_name="Smol Reqvest",
        artist_cluster_id="987654321",
        artist_type="author",
        artist_wiki_data_id="Q987654321",
        offer_category_id="LIVRE_PAPIER",
    ),
    ArtistAliasModel(
        artist_id=raw_artists_data[1]["artist_id"],
        artist_alias_name="Small Request",
        artist_cluster_id="987654321",
        artist_type="author",
        artist_wiki_data_id="Q987654321",
        offer_category_id="LIVRE_PAPIER",
    ),
]
