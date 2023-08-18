import datetime
import decimal
import typing

import pydantic
from pydantic import generics

from pcapi.routes.serialization import BaseModel
from pcapi.utils import date as date_utils


class GenreTitelive(BaseModel):
    code: str
    libelle: str


class TiteliveGtl(BaseModel):
    first: dict[str, GenreTitelive]


class TiteliveImage(BaseModel):
    recto: str


class TiteliveArticle(BaseModel):
    codesupport: str
    commentaire: str | None
    datemodification: datetime.date
    dateparution: datetime.date | None
    distributeur: str
    editeur: str
    if typing.TYPE_CHECKING:
        gencod: str
    else:
        gencod: pydantic.constr(min_length=13, max_length=13)
    gtl: TiteliveGtl | None
    image: str
    imagesUrl: TiteliveImage
    libelledispo: str
    prix: decimal.Decimal
    resume: str | None

    _convert_datemodification = pydantic.validator("datemodification", pre=True, allow_reuse=True)(
        date_utils.parse_french_date
    )
    _convert_dateparution = pydantic.validator("dateparution", pre=True, allow_reuse=True)(date_utils.parse_french_date)

    @pydantic.validator("gtl", pre=True)
    def validate_gtl(cls, gtl: TiteliveGtl | list) -> TiteliveGtl | None:
        if isinstance(gtl, list):
            return None
        return gtl


class TiteliveMusicArticle(TiteliveArticle):
    artiste: str
    compositeur: str
    interprete: str
    label: str
    nb_galettes: str


TiteliveArticleType = typing.TypeVar("TiteliveArticleType", bound=TiteliveArticle)


class BaseTiteliveOeuvre(generics.GenericModel, typing.Generic[TiteliveArticleType]):
    article: list[TiteliveArticleType]

    @pydantic.validator("article", pre=True)
    def validate_article_list(cls, article: list | dict) -> list:
        if isinstance(article, dict):
            return list(article.values())
        return article


class TiteliveMusicOeuvre(BaseTiteliveOeuvre[TiteliveMusicArticle]):
    article: list[TiteliveMusicArticle]  # repeated without generics so mypy understands
    titre: str


TiteliveSearchResultType = typing.TypeVar("TiteliveSearchResultType", bound=BaseTiteliveOeuvre)


class TiteliveProductSearchResponse(generics.GenericModel, typing.Generic[TiteliveSearchResultType]):
    type: int
    nombre: int
    page: int
    result: list[TiteliveSearchResultType]
