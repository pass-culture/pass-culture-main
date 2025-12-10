from pydantic import BaseModel as BaseModelV2

from pcapi import settings
from pcapi.connectors.big_query.importer.base import DeltaAction
from pcapi.connectors.big_query.queries.base import BaseQuery


class ArtistModel(BaseModelV2):
    id: str
    name: str
    description: str | None = None
    image: str | None = None
    image_author: str | None = None
    image_license: str | None = None
    image_license_url: str | None = None
    wikidata_id: str | None = None
    biography: str | None = None
    wikipedia_url: str | None = None


class ArtistProductLinkModel(BaseModelV2):
    artist_id: str
    product_id: int
    artist_type: str | None = None


class ArtistAliasModel(BaseModelV2):
    artist_id: str | None = None
    artist_alias_name: str | None = None
    artist_cluster_id: str | None = None
    artist_type: str | None = None
    artist_wiki_data_id: str | None = None
    offer_category_id: str | None = None


class ArtistQuery(BaseQuery):
    raw_query = f"""
        SELECT
            artist_id as id,
            artist_name as name,
            artist_description as description,
            wikidata_image_file_url as image,
            wikidata_image_author as author,
            wikidata_image_license as license,
            wikidata_image_license_url as license_url,
            wikidata_id,
            artist_biography as biography,
            wikipedia_url
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.artist`
    """

    model = ArtistModel


class ArtistProductLinkQuery(BaseQuery):
    raw_query = f"""
        SELECT
            artist_id,
            offer_product_id as product_id,
            artist_type
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.product_artist_link`
    """

    model = ArtistProductLinkModel


class ArtistAliasQuery(BaseQuery):
    raw_query = f"""
        SELECT
            artist_id,
            artist_offer_name as artist_alias_name,
            artist_cluster_id,
            artist_wiki_id as artist_wiki_data_id,
            offer_category_id as offer_category_id,
            artist_type
            
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.artist_alias`
    """

    model = ArtistAliasModel


class DeltaArtistModel(ArtistModel):
    action: DeltaAction


class DeltaArtistProductLinkModel(ArtistProductLinkModel):
    action: DeltaAction


class DeltaArtistAliasModel(ArtistAliasModel):
    action: DeltaAction


class ArtistDeltaQuery(BaseQuery):
    raw_query = f"""
        SELECT
            artist_id as id,
            artist_name as name,
            artist_description as description,
            wikidata_image_file_url as image,
            wikidata_image_author as author,
            wikidata_image_license as license,
            wikidata_image_license_url as license_url,
            wikidata_id,
            artist_biography as biography,
            wikipedia_url,
            action
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.artist_delta`
    """
    model = DeltaArtistModel


class ArtistProductLinkDeltaQuery(BaseQuery):
    raw_query = f"""
        SELECT
            artist_id,
            offer_product_id as product_id,
            artist_type,
            action
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.product_artist_link_delta`
    """
    model = DeltaArtistProductLinkModel


class ArtistAliasDeltaQuery(BaseQuery):
    raw_query = f"""
        SELECT
            artist_id,
            artist_offer_name as artist_alias_name,
            artist_cluster_id,
            artist_wiki_id as artist_wiki_data_id,
            offer_category_id as offer_category_id,
            artist_type,
            action
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.artist_alias_delta`
    """
    model = DeltaArtistAliasModel
