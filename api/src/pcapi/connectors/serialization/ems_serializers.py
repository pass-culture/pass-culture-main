from decimal import Decimal

from pydantic import field_validator

import pcapi.core.offers.models as offers_models
from pcapi.routes.serialization import BaseModelV2


class Session(BaseModelV2):
    id: str
    date: str
    features: list[str]
    pass_culture_price: Decimal


class Event(BaseModelV2):
    id: str
    allocine_id: int | None
    title: str
    director: str | None
    synopsis: str | None
    bill_url: str | None
    duration: int | None
    sessions: list[Session]

    @field_validator("allocine_id", mode="before")
    def make_empty_string_null(cls, value: int | str | None) -> int | str | None:
        if value == "":
            return None
        return value

    def to_generic_movie(self) -> offers_models.Movie:
        poster_url = self.bill_url
        if poster_url:
            poster_url = poster_url.replace("/120/", "/600/")

        return offers_models.Movie(
            allocine_id=str(self.allocine_id) if self.allocine_id else None,
            duration=self.duration,
            description=self.synopsis,
            extra_data=None,
            poster_url=poster_url,
            title=self.title,
            visa=None,
        )


class Site(BaseModelV2):
    id: str
    allocine_id: str
    name: str
    address: str
    zip_code: str
    city: str
    siret: str | None


class SiteWithEvents(BaseModelV2):
    id: str
    name: str
    address: str | None = None
    zip_code: str | None = None
    city: str | None = None
    events: list[Event]


class ScheduleResponse(BaseModelV2):
    sites: list[SiteWithEvents]
    version: int


class Ticket(BaseModelV2):
    num_caisse: str
    code_barre: str
    num_trans: int
    num_ope: int
    code_tarif: str
    num_serie: int
    montant: float
    num_place: str


class ReservationPassCultureRequest(BaseModelV2):
    num_cine: str  # VenueProvider.venueIdAtOfferProvider
    id_seance: str  # show_id
    qte_place: int
    pass_culture_price: float
    total_price: float
    email: str
    num_pass_culture: str  # User.id
    num_cmde: str | None

    @field_validator("num_pass_culture", mode="before")
    def convert_num_pass_culture_to_str(cls, value: str | int) -> str:
        if isinstance(value, int):
            return str(value)
        return value


class GetTicketRequest(BaseModelV2):
    num_cine: str
    num_cmde: str


class AnnulationPassCultureRequest(BaseModelV2):
    num_cine: str
    num_caisse: str
    num_trans: int
    num_ope: int


class ReservationPassCultureResponse(ReservationPassCultureRequest):
    """EMS simply return our payload with additional fields."""

    statut: int
    billets: list[Ticket]


class AvailableShowsRequest(BaseModelV2):
    num_cine: str
    id_film: str


class AvailableShowsResponse(BaseModelV2):
    statut: int
    seances: list[str]


class SitesResponse(BaseModelV2):
    sites: list[Site]
    version: int
