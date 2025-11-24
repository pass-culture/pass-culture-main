import logging
import typing

from pydantic.v1.class_validators import validator

from pcapi import settings
from pcapi.connectors.big_query.queries.base import BaseQuery
from pcapi.connectors.serialization.titelive_serializers import TiteLiveBookArticle
from pcapi.connectors.serialization.titelive_serializers import TiteliveMusicArticle
from pcapi.connectors.titelive import TiteliveBase


logger = logging.getLogger(__name__)


class BigQueryTiteliveBookProductModel(TiteLiveBookArticle):
    ean: str
    titre: str
    recto_uuid: str | None
    verso_uuid: str | None
    auteurs_multi: list[str]

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


class BigQueryTiteliveBookProductDeltaQuery(BaseQuery):
    raw_query = f"""
        SELECT
            ean,
            ean as gencod,
            title as titre,
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
        WHERE
            product_type = '{TiteliveBase.BOOK.value}'
        ORDER BY ean
    """

    model = BigQueryTiteliveBookProductModel


class BigQueryTiteliveMusicProductModel(TiteliveMusicArticle):
    ean: str
    titre: str
    recto_uuid: str | None
    verso_uuid: str | None


class BigQueryTiteliveMusicProductDeltaQuery(BaseQuery):
    raw_query = f"""
        SELECT
            ean,
            ean as gencod,
            title as titre,
            description as resume,
            support_code as codesupport,
            gtl,
            publication_date as dateparution,
            publisher as editeur,
            price as prix,

            music_label as label,
            composer as compositeur,
            performer as interprete,
            nb_discs as nb_galettes,
            artist as artiste,

            recto_uuid,
            verso_uuid,
            image,
            image_4
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.product_delta`
        WHERE
            product_type = '{TiteliveBase.MUSIC.value}'
        ORDER BY ean
    """

    model = BigQueryTiteliveMusicProductModel
