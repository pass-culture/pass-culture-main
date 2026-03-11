import enum

from pydantic import BaseModel as BaseModelV2

from pcapi import settings
from pcapi.connectors.big_query.queries.base import BaseQuery


class DeltaAction(str, enum.Enum):
    ADD = "add"
    REMOVE = "remove"
    UPDATE = "update"


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
    mediation_uuid: str | None = None


class DeltaArtistModel(ArtistModel):
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
            artist_mediation_uuid as mediation_uuid,
            action
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.artist_delta`
        ORDER BY
        CASE action
            WHEN 'remove' THEN 1
            WHEN 'add'    THEN 2
            WHEN 'update' THEN 3
        END,
        artist_name;
    """
    model = DeltaArtistModel


class ArtistProductLinkModel(BaseModelV2):
    artist_id: str
    product_id: int
    artist_type: str | None = None


class DeltaArtistProductLinkModel(ArtistProductLinkModel):
    action: DeltaAction


class ArtistProductLinkDeltaQuery(BaseQuery):
    raw_query = f"""
        SELECT
            artist_id,
            offer_product_id as product_id,
            artist_type,
            action
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.product_artist_link_delta`
        ORDER BY
            CASE action
            WHEN 'remove' THEN 1
            WHEN 'add'    THEN 2
        END,
        artist_id,
        product_id;
    """
    model = DeltaArtistProductLinkModel


class ArtistScoresModel(BaseModelV2):
    id: str
    app_search_score: float
    pro_search_score: float


class ArtistScoresQuery(BaseQuery):
    raw_query = f"""
        SELECT
            artist_id as id,
            artist_app_search_score as app_search_score,
            artist_pro_search_score as pro_search_score
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.artist_score`
    """

    model = ArtistScoresModel
