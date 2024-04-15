import datetime
import typing

import pydantic.v1 as pydantic_v1
from pydantic.v1 import generics

from pcapi.routes.serialization import BaseModel
from pcapi.utils import date as date_utils


class GenreTitelive(BaseModel):
    if typing.TYPE_CHECKING:
        code: str
    else:
        code: pydantic_v1.constr(min_length=8, max_length=8)
    libelle: str

    @pydantic_v1.validator("code", pre=True)
    def validate_code(cls, code: str) -> str:
        # '50300' -> '05030000'; '110400' -> '11040000'
        return code.zfill(6).ljust(8, "0")


class TiteliveGtl(BaseModel):
    first: dict[str, GenreTitelive]


class TiteliveImage(BaseModel):
    recto: str
    verso: str | None


class TiteliveArticle(BaseModel):
    codesupport: str | None
    commentaire: str | None
    contenu_explicite: str
    dateparution: datetime.date | None
    distributeur: str | None
    editeur: str | None
    if typing.TYPE_CHECKING:
        gencod: str
    else:
        gencod: pydantic_v1.constr(min_length=13, max_length=13)
    gtl: TiteliveGtl | None
    image: str
    imagesUrl: TiteliveImage
    dispo: str
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
    nb_galettes: str


TiteliveArticleType = typing.TypeVar("TiteliveArticleType", bound=TiteliveArticle)


class BaseTiteliveOeuvre(generics.GenericModel, typing.Generic[TiteliveArticleType]):
    article: list[TiteliveArticleType]

    @pydantic_v1.validator("article", pre=True)
    def validate_article_list(cls, article: list | dict) -> list:
        if isinstance(article, dict):
            return list(article.values())
        return article


class TiteLiveBookOeuvre(BaseTiteliveOeuvre[TiteLiveBookArticle]):
    article: list[TiteLiveBookArticle]  # repeated without generics so mypy understands
    auteurs_multi: list[str]
    titre: str


class TiteliveMusicOeuvre(BaseTiteliveOeuvre[TiteliveMusicArticle]):
    article: list[TiteliveMusicArticle]  # repeated without generics so mypy understands
    titre: str


TiteliveSearchResultType = typing.TypeVar("TiteliveSearchResultType", bound=BaseTiteliveOeuvre)


class TiteliveProductSearchResponse(generics.GenericModel, typing.Generic[TiteliveSearchResultType]):
    type: int
    nombre: int
    page: int
    result: list[TiteliveSearchResultType]
