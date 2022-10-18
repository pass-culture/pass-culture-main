import pcapi.core.external_bookings.models as external_bookings_models
from pcapi.routes.serialization import BaseModel


class LoginBoost(BaseModel):
    code: int
    message: str
    token: str | None


class Film2(BaseModel):
    """We transcribe their API schema and keep their name convention"""

    id: int
    titleCnc: str
    numVisa: int
    posterUrl: str
    thumbUrl: str | None
    idFilmAllocine: int

    def to_generic_movie(self) -> external_bookings_models.Movie:
        return external_bookings_models.Movie(
            id=str(self.id),
            title=self.titleCnc,
            duration=1,  # FIXME
            description="",  # FIXME
            posterpath=self.posterUrl,
            visa=str(self.numVisa),
        )


class Collection(BaseModel):
    data: list
    message: str
    page: int
    previousPage: int
    nextPage: int
    totalPages: int
    totalCount: int


class FilmCollection(Collection):
    data: list[Film2]
