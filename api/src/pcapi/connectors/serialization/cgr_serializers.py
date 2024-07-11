import datetime
from decimal import Decimal
import logging

from pydantic.v1 import validator

from pcapi.core.offers import models as offers_models
from pcapi.routes.serialization import BaseModel


logger = logging.getLogger(__name__)


class Seance(BaseModel):
    IDSeance: int
    Date: datetime.date
    Heure: datetime.time
    NbPlacesRestantes: int
    bAvecPlacement: bool
    bAvecDuo: bool
    bICE: bool
    Relief: str
    Version: str
    bAVP: bool
    PrixUnitaire: Decimal
    libTarif: str


class Film(BaseModel):
    IDFilm: int
    IDFilmAlloCine: int
    Titre: str
    NumVisa: int
    Duree: int
    Synopsis: str
    Affiche: str
    TypeFilm: str
    Seances: list[Seance]

    @validator("Seances")
    def skip_showtimes_with_negative_remaining_quantity(cls, seances: list[Seance]) -> list[Seance]:
        sanitized_showtimes = []
        for seance in seances:
            if seance.NbPlacesRestantes < 0:
                logger.warning(
                    "Skipping CGR showtime because of negative remaining places",
                    extra={"showtime_quantity": seance.NbPlacesRestantes, "showtime_id": seance.IDSeance},
                )
                continue
            sanitized_showtimes.append(seance)
        return sanitized_showtimes

    def to_generic_movie(self) -> offers_models.Movie:
        return offers_models.Movie(
            allocine_id=str(self.IDFilmAlloCine),
            duration=self.Duree,
            description=self.Synopsis,
            extra_data=None,
            poster_url=self.Affiche,
            title=self.Titre,
            visa=str(self.NumVisa),
        )


class GetSancesPassCultureResponseBody(BaseModel):
    NumCine: int
    Films: list[Film]


class GetSancesPassCultureResponse(BaseModel):
    CodeErreur: int
    IntituleErreur: str
    ObjetRetour: GetSancesPassCultureResponseBody


class ReservationPassCultureBody(BaseModel):
    pIDSeances: int
    pNumCinema: int
    pPUTTC: Decimal
    pNBPlaces: int
    pNom: str
    pPrenom: str
    pEmail: str
    pToken: str
    pDateLimiteAnnul: str


class ReservationPassCultureResponse(BaseModel):
    CodeErreur: int
    IntituleErreur: str
    QrCode: str
    Placement: str
