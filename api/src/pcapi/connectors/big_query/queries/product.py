import logging
import typing
from datetime import date

from pydantic.v1.class_validators import validator

from pcapi import settings
from pcapi.connectors.big_query.queries.base import BaseQuery
from pcapi.connectors.serialization.titelive_serializers import TiteLiveBookArticle


logger = logging.getLogger(__name__)


class BigQueryProductModel(TiteLiveBookArticle):
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
    base_query = f"""
        SELECT
            titre,
            auteurs_multi,
            resume,
            gencod,
            codesupport,
            gtl,
            dateparution,
            editeur,
            prix,
            langueiso,
            taux_tva,
            id_lectorat,
            datemodification,
            recto_uuid,
            verso_uuid
        FROM
            `{settings.BIG_QUERY_TABLE_BASENAME}.wip_titelive_books`
    """  # FIXME (jmontagnat, 2025-09-11): switch to final table when its name will be decided

    model = BigQueryProductModel

    def __init__(self, from_date: date, to_date: date):
        super().__init__()
        self.from_date = from_date
        self.to_date = to_date

    @property
    def raw_query(self) -> str:
        query = self.base_query
        from_date_str = self.from_date.isoformat()
        to_date_str = self.to_date.isoformat()

        where_clause = f"""
        WHERE
            (PARSE_TIMESTAMP('%d/%m/%Y', datemodification) BETWEEN TIMESTAMP('{from_date_str}') AND TIMESTAMP('{to_date_str}'))
            OR datemodification IS NULL
        """
        query += where_clause

        logger.info(f"Executing BigQuery query: {query}")
        return query
