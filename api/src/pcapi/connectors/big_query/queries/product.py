import logging
import typing

import pydantic.v1 as pydantic_v1
from pydantic.v1.class_validators import validator

from pcapi import settings
from pcapi.connectors.big_query.importer.base import DeltaAction
from pcapi.connectors.big_query.queries.base import BaseQuery
from pcapi.connectors.serialization.titelive_serializers import TiteLiveBookArticle
from pcapi.core.offers.models import OfferExtraData


logger = logging.getLogger(__name__)


class BigQueryProductModel(TiteLiveBookArticle):
    ean: str
    titre: str
    auteurs_multi: list[str]

    recto_uuid: str | None
    verso_uuid: str | None

    @validator("auteurs_multi", pre=True)
    def validate_auteurs_multi(cls, auteurs_multi: typing.Any) -> list:
        if isinstance(auteurs_multi, list):
            return auteurs_multi
        if isinstance(auteurs_multi, str):
            return [auteurs_multi]
        if isinstance(auteurs_multi, dict):
            return list(auteurs_multi.values())
        logger.error("unhandled auteurs_multi type %s", auteurs_multi)
        return []


class ProductsToSyncQuery(BaseQuery):
    raw_query = f"""
        SELECT
            ean,
            ean as gencod,
            name as titre,
            multiple_authors as auteurs_multi,
            description as resume,
            support_code as codesupport,
            gtl,
            publication_date as dateparution,
            publisher as editeur,
            price as prix,
            language_iso as langueiso,
            vat_rate as taux_tva,
            readership_id as id_lectorat,
            recto_uuid,
            verso_uuid,
            image,
            image_4
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.product_delta`
        ORDER BY ean
    """

    model = BigQueryProductModel


class ProductModel(pydantic_v1.BaseModel):
    name: str
    description: str | None = None
    ean: str | None = None
    subcategoryId: str
    extraData: OfferExtraData | None = None


class ProductDeltaModel(ProductModel):
    action: DeltaAction


class ProductDeltaQuery(BaseQuery):
    raw_query = f"""
        SELECT
            product_id AS id,
            name,
            description,
            duration_minutes AS durationMinutes,
            ean,
            subcategory_id AS subcategoryId,
            extra_data AS extraData,
            action
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.product_delta`
    """

    model = ProductDeltaModel
