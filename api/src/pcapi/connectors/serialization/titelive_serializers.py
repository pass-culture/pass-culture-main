import datetime
import logging
import typing

import pydantic.v1 as pydantic_v1
from pydantic.v1 import generics

from pcapi.routes.serialization import BaseModel
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)


class GenreTitelive(BaseModel):
    if typing.TYPE_CHECKING:
        code: str
    else:
        code: pydantic_v1.constr(min_length=8, max_length=8)
    libelle: str

    @pydantic_v1.validator("code", pre=True)
    def validate_code(cls, code: str) -> str:
        return _format_gtl_code(code)


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


class TiteliveGtl(BaseModel):
    first: dict[str, GenreTitelive]


class TiteliveImage(BaseModel):
    recto: str
    verso: str | None


class TiteliveArticle(BaseModel):
    codesupport: str | None
    commentaire: str | None
    contenu_explicite: str | None
    dateparution: datetime.date | None
    distributeur: str | None
    editeur: str | None
    if typing.TYPE_CHECKING:
        gencod: str
    else:
        gencod: pydantic_v1.constr(min_length=13, max_length=13)
    gtl: TiteliveGtl | None
    has_image: bool = pydantic_v1.Field(alias="image")
    imagesUrl: TiteliveImage
    # TODO: (lixxday, 2024-04-17): titlelive sends an int for dispo, casting to str works ; but we probably want to change this
    dispo: str
    # TODO: (lixxday, 2024-04-17): titlelive sends a float for prix, casting to str works ; but we probably want to change this
    prix: str | None
    resume: str | None
    datemodification: datetime.date | None

    _convert_dates = pydantic_v1.validator("dateparution", "datemodification", pre=True, allow_reuse=True)(
        date_utils.parse_french_date
    )

    @pydantic_v1.validator("gtl", pre=True)
    def validate_gtl(cls, gtl: TiteliveGtl | list) -> TiteliveGtl | None:
        if isinstance(gtl, list):
            return None
        return gtl

    @pydantic_v1.validator("has_image", pre=True)
    def validate_image(cls, image: str | int | None) -> bool:
        # The API currently sends 0 (int) if no image is available, and "1" (str) if an image is available.
        # Because it has been famously flaky in the past, we are being defensive here and consider:
        # - all forms of 0 and None as False.
        # - all forms of "1" as True.
        if image is None:
            return False
        if int(image) == 0:
            return False
        if int(image) == 1:
            return True
        raise ValueError(f"unhandled image value {image}")

    @pydantic_v1.validator("*", pre=True)
    def parse_empty_string_as_none(cls, value: str | None) -> str | None:
        if value == "":
            return None
        return value


class TiteLiveBookArticle(TiteliveArticle):
    code_clil: str | None
    code_tva: str | None
    taux_tva: str | None
    collection_no: str | None
    collection: str | None
    distributeur: str | None
    scolaire: str | None
    id_lectorat: str | None
    pages: str | None
    langue: str | None
    langueiso: str | None
    langueorigine: str | None
    libelledispo: str | None

    @pydantic_v1.validator("code_tva", "taux_tva", "scolaire", "pages", pre=True)
    def validate_code_tva(cls, value: typing.Literal[0] | str | None) -> str | None:
        if value == 0:
            return None
        return value


class TiteliveMusicArticle(TiteliveArticle):
    artiste: str | None
    compositeur: str | None
    interprete: str | None
    label: str | None
    nb_galettes: str | None


TiteliveArticleType = typing.TypeVar("TiteliveArticleType", bound=TiteliveArticle)


class BaseTiteliveWork(generics.GenericModel, typing.Generic[TiteliveArticleType]):
    article: list[TiteliveArticleType]

    @pydantic_v1.validator("article", pre=True)
    def validate_article_list(cls, article: list | dict) -> list:
        if isinstance(article, dict):
            return list(article.values())
        return article


class TiteLiveBookWork(BaseTiteliveWork[TiteLiveBookArticle]):
    article: list[TiteLiveBookArticle]  # repeated without generics so mypy understands
    auteurs_multi: list[str]
    titre: str

    @pydantic_v1.validator("auteurs_multi", pre=True)
    def validate_auteurs_multi(cls, auteurs_multi: typing.Any) -> list:
        if isinstance(auteurs_multi, list):
            return auteurs_multi
        if isinstance(auteurs_multi, str):
            return [auteurs_multi]
        if isinstance(auteurs_multi, dict):
            return list(auteurs_multi.values())
        logger.error("unhandled auteurs_multi type %s", auteurs_multi)
        return []


class TiteliveMusicWork(BaseTiteliveWork[TiteliveMusicArticle]):
    article: list[TiteliveMusicArticle]  # repeated without generics so mypy understands
    titre: str


TiteliveWorkType = typing.TypeVar("TiteliveWorkType", bound=BaseTiteliveWork)
