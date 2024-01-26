import datetime
from enum import Enum
import re

import pydantic


class AllocineMovieGenre(Enum):
    ACTION = "ACTION"
    ADVENTURE = "ADVENTURE"
    ANIMATION = "ANIMATION"
    BIOPIC = "BIOPIC"
    BOLLYWOOD = "BOLLYWOOD"
    CARTOON = "CARTOON"
    CLASSIC = "CLASSIC"
    COMEDY = "COMEDY"
    COMEDY_DRAMA = "COMEDY_DRAMA"
    CONCERT = "CONCERT"
    DETECTIVE = "DETECTIVE"
    DIVERS = "DIVERS"
    DOCUMENTARY = "DOCUMENTARY"
    DRAMA = "DRAMA"
    EROTIC = "EROTIC"
    EXPERIMENTAL = "EXPERIMENTAL"
    FAMILY = "FAMILY"
    FANTASY = "FANTASY"
    HISTORICAL = "HISTORICAL"
    HISTORICAL_EPIC = "HISTORICAL_EPIC"
    HORROR = "HORROR"
    JUDICIAL = "JUDICIAL"
    KOREAN_DRAMA = "KOREAN_DRAMA"
    MARTIAL_ARTS = "MARTIAL_ARTS"
    MEDICAL = "MEDICAL"
    MOVIE_NIGHT = "MOVIE_NIGHT"
    MUSIC = "MUSIC"
    MUSICAL = "MUSICAL"
    OPERA = "OPERA"
    ROMANCE = "ROMANCE"
    SCIENCE_FICTION = "SCIENCE_FICTION"
    PERFORMANCE = "PERFORMANCE"
    SOAP = "SOAP"
    SPORT_EVENT = "SPORT_EVENT"
    SPY = "SPY"
    THRILLER = "THRILLER"
    WARMOVIE = "WARMOVIE"
    WEB_SERIES = "WEB_SERIES"
    WESTERN = "WESTERN"


class AllocineBacklink(pydantic.BaseModel):
    url: pydantic.HttpUrl
    label: str


class AllocineMovieData(pydantic.BaseModel):
    eidr: str | None
    productionYear: int


class AllocineMoviePoster(pydantic.BaseModel):
    url: pydantic.HttpUrl


class AllocineReleaseDate(pydantic.BaseModel):
    date: datetime.date


class AllocineReleaseDataTech(pydantic.BaseModel):
    auto_update_info: str


class AllocineReleaseData(pydantic.BaseModel):
    tech: AllocineReleaseDataTech
    visa_number: str | None = None


class AllocineMovieRelease(pydantic.BaseModel):
    name: str
    releaseDate: AllocineReleaseDate | None
    data: AllocineReleaseData
    certificate: str | None

    @pydantic.field_validator("certificate", mode="before")
    def get_certificate_from_label(cls, certificate: dict[str, str] | None) -> str | None:
        return certificate["label"] if certificate else None


class AllocineMoviePerson(pydantic.BaseModel):
    firstName: str | None
    lastName: str | None


class AllocineMovieCreditPosition(pydantic.BaseModel):
    name: str


class AllocineMovieCredit(pydantic.BaseModel):
    person: AllocineMoviePerson
    position: AllocineMovieCreditPosition


class AllocineMovieCastItem(pydantic.BaseModel):
    actor: AllocineMoviePerson | None
    role: str | None


class AllocineMovieCast(pydantic.BaseModel):
    backlink: AllocineBacklink
    items: list[AllocineMovieCastItem] = pydantic.Field(alias="edges")

    @pydantic.field_validator("items", mode="before")
    def squash_edges_and_node(cls, edges: list[dict[str, AllocineMovieCastItem]]) -> list[AllocineMovieCastItem]:
        return [item["node"] for item in edges]


class AllocineMovieCountry(pydantic.BaseModel):
    name: str
    alpha3: str


class AllocineMovieCompany(pydantic.BaseModel):
    activity: str
    name: str | None = pydantic.Field(alias="company")

    @pydantic.field_validator("name", mode="before")
    def get_company_from_name(cls, company: dict | None) -> str:
        return company["name"] if company else None


class AllocineMovie(pydantic.BaseModel):
    id: str
    internalId: int
    backlink: AllocineBacklink
    data: AllocineMovieData
    title: str
    originalTitle: str
    type: str
    runtime: int | None
    poster: AllocineMoviePoster | None
    synopsis: str
    releases: list[AllocineMovieRelease]
    credits: list[AllocineMovieCredit]
    cast: AllocineMovieCast
    countries: list[AllocineMovieCountry]
    genres: list[AllocineMovieGenre]
    companies: list[AllocineMovieCompany]

    @pydantic.field_validator("credits", mode="before")
    def squash_edges_and_node(
        cls, credits_: dict[str, list[dict[str, AllocineMovieCredit]]]
    ) -> list[AllocineMovieCredit]:
        return [item["node"] for item in credits_["edges"]]

    @pydantic.field_validator("runtime", mode="before")
    def convert_runtime_to_minutes(cls, raw: str | None) -> int | None:
        # Given format is PT1H2M3S for 1 hour 2 minutes 3 seconds
        if not raw:
            return None

        match = re.match(r"^PT(\d+)H(\d+)M\d+S$", raw)
        if not match:
            return None

        hours, minutes = map(int, match.groups())
        return hours * 60 + minutes


class AllocinePageInfo(pydantic.BaseModel):
    hasNextPage: bool
    endCursor: str


class AllocineMovieNode(pydantic.BaseModel):
    node: AllocineMovie


class AllocineMovieList(pydantic.BaseModel):
    totalCount: int
    pageInfo: AllocinePageInfo
    movies: list[AllocineMovie] = pydantic.Field(alias="edges")

    @pydantic.field_validator("movies", mode="before")
    def squash_edges_and_node(cls, edges: list[dict[str, AllocineMovie]]) -> list[AllocineMovie]:
        return [item["node"] for item in edges]


class AllocineMovieListResponse(pydantic.BaseModel):
    movieList: AllocineMovieList


AllocineMovieListResponseAdapter = pydantic.TypeAdapter(AllocineMovieListResponse)
