import datetime
import logging
import typing
from typing import Any

import pydantic as pydantic_v2

from pcapi import settings
from pcapi.connectors.big_query.queries.base import BaseQuery
from pcapi.connectors.titelive import TiteliveBase
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


def _format_gtl_code(code: str) -> str:
    # A GTL id is 8 characters long.
    # Each pair represents a GTL level.
    # The first 2 characters are level 1, the next 2 are level 2, etc.
    #  - example: 05030000 corresponds to a level 1 GTL of 05 and a level 2 of 03. So "Tourism & Travel World".

    # We receive gtl_ids without leading zeros, and sometimes without trailing ones.
    # We must add them to have an 8-character code.

    # We start by adding the missing zeros to the left.
    # If we receive a code with an odd number of characters, we must add a zero to the left.
    # '5030000'  -> '05030000'
    # Otherwise, we don't add anything.
    # '110400' -> '110400'

    if len(code) % 2 == 1:
        code = "0" + code

    # Then we add the missing zeros to the right to have 8 characters.
    # '050300' -> '05030000'
    # '110400' -> '11040000'
    code = code.ljust(8, "0")
    return code


class GenreTitelive(pydantic_v2.BaseModel):
    code: str = pydantic_v2.Field(min_length=8, max_length=8)
    libelle: str

    @pydantic_v2.field_validator("code", mode="before")
    @classmethod
    def validate_code(cls, code: str) -> str:
        return _format_gtl_code(code)


class TiteliveGtl(pydantic_v2.BaseModel):
    first: dict[str, GenreTitelive] | None = None


class BigQueryTiteliveProductBaseModel(pydantic_v2.BaseModel):
    model_config = pydantic_v2.ConfigDict(populate_by_name=True)

    ean: str
    titre: str
    recto_uuid: str | None = None
    verso_uuid: str | None = None
    has_image: bool = pydantic_v2.Field(alias="image", default=False)
    has_verso_image: bool = pydantic_v2.Field(alias="image_4", default=False)

    resume: str | None = None
    codesupport: str | None = None
    gtl: TiteliveGtl | None = None
    dateparution: datetime.date | None = None
    editeur: str | None = None
    prix: float | None = None

    gencod: str = pydantic_v2.Field(min_length=13, max_length=13)

    @pydantic_v2.model_validator(mode="before")
    @classmethod
    def parse_empty_strings_as_none(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {k: (None if v == "" else v) for k, v in data.items()}
        return data

    @pydantic_v2.field_validator("dateparution", mode="before")
    @classmethod
    def parse_dates(cls, v: Any) -> Any:
        return date_utils.parse_french_date(v)

    @pydantic_v2.field_validator("gtl", mode="before")
    @classmethod
    def validate_gtl(cls, gtl: TiteliveGtl | list) -> TiteliveGtl | None:
        if isinstance(gtl, list):
            return None
        return gtl

    @pydantic_v2.field_validator("has_image", "has_verso_image", mode="before")
    @classmethod
    def validate_image(cls, image: str | int | None) -> bool:
        # The API currently sends 0 (int) if no image is available, and "1" (str) if an image is available.
        # Because it has been famously flaky in the past, we are being defensive here and consider:
        # - all forms of 0 and None as False.
        # - all forms of "1" as True.
        if image is not None and int(image) not in (0, 1):
            raise ValueError(f"unhandled image value {image}")
        return bool(image and int(image) == 1)


class BigQueryTiteliveBookProductModel(BigQueryTiteliveProductBaseModel):
    auteurs_multi: list[str]
    langueiso: str | None = None
    taux_tva: str | None = None
    id_lectorat: str | None = None

    @pydantic_v2.field_validator("taux_tva", mode="before")
    @classmethod
    def validate_code_tva(cls, value: typing.Literal[0] | str | None) -> str | None:
        if value == 0:
            return None
        return value

    @pydantic_v2.field_validator("auteurs_multi", mode="before")
    @classmethod
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


class BigQueryTiteliveMusicProductModel(BigQueryTiteliveProductBaseModel):
    label: str | None = None
    compositeur: str | None = None
    interprete: str | None = None
    nb_galettes: str | None = None
    artiste: str | None = None
    commentaire: str | None = None
    contenu_explicite: int | None = None
    dispo: int | None = None
    distributeur: str | None = None


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
            comment as commentaire,
            explicit_content as contenu_explicite,
            availability as dispo,
            distributor as distributeur,
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
