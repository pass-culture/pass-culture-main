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


class AllocineShowtimeDiffusionVersion(Enum):
    LOCAL = "LOCAL"
    DUBBED = "DUBBED"
    ORIGINAL = "ORIGINAL"


class AllocineShowtimeExperience(Enum):
    E_4DX = "E_4DX"
    BUTT_KICKER = "BUTT_KICKER"
    DBOX = "DBOX"
    DOLBY_ATMOS = "DOLBY_ATMOS"
    ATMOS_EXPERIENCE = "ATMOS_EXPERIENCE"
    DOLBY_CINEMA = "DOLBY_CINEMA"
    ECLAIR_COLOR = "ECLAIR_COLOR"
    ICE = "ICE"
    JUMBO = "JUMBO"
    LIGHT_VIBES = "LIGHT_VIBES"
    MX4D = "MX4D"
    PLATINUM = "PLATINUM"
    PREMIUM = "PREMIUM"
    PLF = "PLF"
    SCREEN_X = "SCREEN_X"
    TRADITIONAL_AUDITORIUM = "TRADITIONAL_AUDITORIUM"
    TREMOR_FX = "TREMOR_FX"
    E_4D_EMOTION = "E_4D_EMOTION"
    GRAND_LARGE = "GRAND_LARGE"
    LASER_ULTRA = "LASER_ULTRA"
    ONYX_LED = "ONYX_LED"


class AllocineShowtimeLanguage(Enum):
    ABORIGINAL_LANGUAGE = "ABORIGINAL_LANGUAGE"
    AFRICAN_DIALECT = "AFRICAN_DIALECT"
    AFRIKAANS = "AFRIKAANS"
    ALBANIAN = "ALBANIAN"
    ALGERIAN = "ALGERIAN"
    AMHARIC = "AMHARIC"
    ARABIC = "ARABIC"
    ARAMAIC = "ARAMAIC"
    ARMENIAN = "ARMENIAN"
    AZERI = "AZERI"
    BAMBARA = "BAMBARA"
    BENGALI = "BENGALI"
    BOSNIAN = "BOSNIAN"
    BRITON = "BRITON"
    BULGARIAN = "BULGARIAN"
    BURMESE = "BURMESE"
    CANTONESE = "CANTONESE"
    CATALAN = "CATALAN"
    CHINESE = "CHINESE"
    CREOLE = "CREOLE"
    CZECH = "CZECH"
    DANISH = "DANISH"
    DUTCH = "DUTCH"
    ENGLISH = "ENGLISH"
    ESTONIAN = "ESTONIAN"
    EUSKERA = "EUSKERA"
    FARSI = "FARSI"
    FILIPINO = "FILIPINO"
    FINNISH = "FINNISH"
    FLEMISH = "FLEMISH"
    FRENCH = "FRENCH"
    GAELIC = "GAELIC"
    GALLEGO = "GALLEGO"
    GEORGIAN = "GEORGIAN"
    GERMAN = "GERMAN"
    GREEK = "GREEK"
    GUARANI = "GUARANI"
    HEBREW = "HEBREW"
    HINDI = "HINDI"
    HOKKIEN = "HOKKIEN"
    HUNGARIAN = "HUNGARIAN"
    ICELANDIC = "ICELANDIC"
    INDONESIAN = "INDONESIAN"
    INUKTITUT = "INUKTITUT"
    ITALIAN = "ITALIAN"
    JAPANESE = "JAPANESE"
    KANNADA = "KANNADA"
    KAZAKH = "KAZAKH"
    KHMER = "KHMER"
    KIRGIZIAN = "KIRGIZIAN"
    KLINGON = "KLINGON"
    KOREAN = "KOREAN"
    KURDISH = "KURDISH"
    LATIN = "LATIN"
    LATVIAN = "LATVIAN"
    LINGALA = "LINGALA"
    LITHUANIAN = "LITHUANIAN"
    MACEDONIAN = "MACEDONIAN"
    MALAGASY = "MALAGASY"
    MALAY = "MALAY"
    MALAYALAM = "MALAYALAM"
    MANDARIN = "MANDARIN"
    MARATHI = "MARATHI"
    MAYA = "MAYA"
    MONGOLESE = "MONGOLESE"
    NORWEGIAN = "NORWEGIAN"
    OTHER = "OTHER"
    PASHTO = "PASHTO"
    PERSIAN = "PERSIAN"
    POLISH = "POLISH"
    PORTUGUESE = "PORTUGUESE"
    PUNJABI = "PUNJABI"
    ROMANIAN = "ROMANIAN"
    ROMANY = "ROMANY"
    RUSSIAN = "RUSSIAN"
    SERB = "SERB"
    SERBO_CROAT = "SERBO_CROAT"
    SIGN_LANGUAGE = "SIGN_LANGUAGE"
    SILENT = "SILENT"
    SLOVAK = "SLOVAK"
    SLOVENIAN = "SLOVENIAN"
    SOMALI = "SOMALI"
    SOTHO = "SOTHO"
    SPANISH = "SPANISH"
    SWAHILI = "SWAHILI"
    SWEDISH = "SWEDISH"
    SWISS_GERMAN = "SWISS_GERMAN"
    TADZHIK = "TADZHIK"
    TAMIL = "TAMIL"
    THAI = "THAI"
    TELUGU = "TELUGU"
    TIBETAN = "TIBETAN"
    TURKISH = "TURKISH"
    UKRAINIAN = "UKRAINIAN"
    UNDETERMINED_LANGUAGE = "UNDETERMINED_LANGUAGE"
    URDU = "URDU"
    VIETNAMESE = "VIETNAMESE"
    WOLOF = "WOLOF"
    YIDDISH = "YIDDISH"
    ZANSKARI = "ZANSKARI"
    ZULU = "ZULU"


class AllocineShowtimeProjection(Enum):
    F_2D = "F_2D"
    F_3D = "F_3D"
    F_4K = "F_4K"
    F_3D70MM = "F_3D70MM"
    F_35MM = "F_35MM"
    F_70MM = "F_70MM"
    F_4K3D = "F_4K3D"
    F_ATMOS = "F_ATMOS"
    ANALOG = "ANALOG"
    REALD_3D = "REALD_3D"
    DIGITAL = "DIGITAL"
    IMAX = "IMAX"
    IMAX_3D = "IMAX_3D"
    IMAX_70MM = "IMAX_70MM"
    HFR = "HFR"
    F_3DHFR = "F_3DHFR"
    IMAX_3D_HFR = "IMAX_3D_HFR"
    LASER = "LASER"


class AllocineBacklink(pydantic.BaseModel):
    url: pydantic.HttpUrl
    label: str


class AllocineMovieData(pydantic.BaseModel):
    eidr: str | None
    productionYear: int | None


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

    @pydantic.field_validator("releases", "countries", "genres", "companies", mode="before")
    def convert_none_to_empty_list(cls, nullable_field: list | None) -> list:
        return [] if not nullable_field else nullable_field


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


class AllocineShowtime(pydantic.BaseModel):
    diffusionVersion: AllocineShowtimeDiffusionVersion
    experience: list[AllocineShowtimeExperience | None] | AllocineShowtimeExperience | None
    languages: list[AllocineShowtimeLanguage] | None
    projection: AllocineShowtimeProjection
    startsAt: datetime.datetime

    @pydantic.field_validator("projection", mode="before")
    def get_first_projection_mode(cls, projection: list[AllocineShowtimeProjection]) -> AllocineShowtimeProjection:
        return projection[0]

    @pydantic.field_validator("languages", mode="before")
    def drop_none_values(cls, languages: list | None) -> list | None:
        if languages:
            return [l for l in languages if l is not None]
        return languages


class AllocineMovieShowtime(pydantic.BaseModel):
    movie: AllocineMovie
    showtimes: list[AllocineShowtime]


class AllocineMovieShowtimeList(pydantic.BaseModel):
    totalCount: int
    moviesShowtimes: list[AllocineMovieShowtime] = pydantic.Field(alias="edges")

    @pydantic.field_validator("moviesShowtimes", mode="before")
    def squash_edges_and_node(cls, edges: list[dict[str, AllocineMovieShowtime]]) -> list[AllocineMovieShowtime]:
        return [item["node"] for item in edges]


class AllocineMovieShowtimeListResponse(pydantic.BaseModel):
    movieShowtimeList: AllocineMovieShowtimeList
