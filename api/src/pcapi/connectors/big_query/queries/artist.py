import enum

import pydantic.v1 as pydantic_v1

from pcapi import settings
from pcapi.connectors.big_query.queries.base import BaseQuery


class ArtistModel(pydantic_v1.BaseModel):
    id: str
    name: str | None
    description: str | None
    image: str | None
    image_author: str | None
    image_license: str | None
    image_license_url: str | None


class ArtistProductLinkModel(pydantic_v1.BaseModel):
    artist_id: str
    product_id: int
    artist_type: str | None


class ArtistAliasModel(pydantic_v1.BaseModel):
    artist_id: str | None
    artist_alias_name: str | None
    artist_cluster_id: str | None
    artist_type: str | None
    artist_wiki_data_id: str | None
    offer_category_id: str | None


class ArtistQuery(BaseQuery):
    raw_query = f"""
        SELECT
            artist_id as id,
            artist_name as name,
            artist_description as description,
            wikidata_image_file_url as image,
            wikidata_image_author as author,
            wikidata_image_license as license,
            wikidata_image_license_url as license_url
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


class DeltaAction(str, enum.Enum):
    ADD = "add"
    REMOVE = "remove"


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
