import datetime
from decimal import Decimal

from pcapi.routes.serialization import BaseModel


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
    pDateLimiteAnnul: datetime.datetime


class ReservationPassCultureResponse(BaseModel):
    CodeErreur: int
    IntituleErreur: str
    QrCode: str
    Placement: str
