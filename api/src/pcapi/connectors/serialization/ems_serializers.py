from decimal import Decimal

from pcapi.routes.serialization import BaseModel


class Session(BaseModel):
    id: str
    date: str
    features: list[str]
    pass_culture_price: Decimal


class Event(BaseModel):
    id: str
    allocine_id: int
    title: str
    director: str | None
    synopsis: str | None
    bill_url: str | None
    duration: int
    sessions: list[Session]


class Site(BaseModel):
    id: str
    name: str
    address: str
    zip_code: str
    city: str
    events: list[Event]


class ScheduleResponse(BaseModel):
    sites: list[Site]
    version: int


class Ticket(BaseModel):
    num_caisse: str
    code_barre: str
    num_trans: int
    num_ope: int
    code_tarif: str
    num_serie: int
    montant: float
    num_place: str


class ReservationPassCultureRequest(BaseModel):
    num_cine: str  # VenueProvider.venueIdAtOfferProvider
    id_seance: str  # show_id
    qte_place: int
    pass_culture_price: float
    total_price: float
    email: str
    num_pass_culture: str  # User.id


class ReservationPassCultureResponse(ReservationPassCultureRequest):
    """EMS simply return our payload with additionnal fields."""

    statut: int
    billets: list[Ticket]
