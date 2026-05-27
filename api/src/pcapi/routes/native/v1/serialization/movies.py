import enum
import logging
import typing
from dataclasses import dataclass
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from decimal import Decimal

import pydantic as pydantic_v2

from pcapi.core.categories.genres.movie import get_movie_label
from pcapi.core.providers import api as providers_api
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel
from pcapi.utils import date as date_utils
from pcapi.utils.date import format_into_utc_date


logger = logging.getLogger(__name__)


class MovieScreeningsRequest(HttpQueryParamsModel):
    allocine_id: str | None = None
    visa: str | None = None
    latitude: float
    longitude: float
    around_radius: int = 50_000  # meters
    from_datetime: datetime = pydantic_v2.Field(alias="from", default_factory=date_utils.get_naive_utc_now)
    to_datetime: datetime = pydantic_v2.Field(
        alias="to", default_factory=lambda: datetime.combine(date.today(), time.max) + timedelta(days=15)
    )

    _datetime_serializer = pydantic_v2.field_serializer("from_datetime", "to_datetime")(format_into_utc_date)

    @pydantic_v2.model_validator(mode="after")
    def validate_params(self) -> typing.Self:
        if (not self.allocine_id and not self.visa) or (self.allocine_id and self.visa):
            raise ValueError("Only one of allocine_id and visa must be provided")

        return self


class VenueMovieScreeningsRequest(HttpBodyModel):
    from_datetime: datetime = pydantic_v2.Field(alias="from", default_factory=date_utils.get_naive_utc_now)
    to_datetime: datetime = pydantic_v2.Field(
        alias="to", default_factory=lambda: datetime.combine(date.today(), time.max) + timedelta(days=15)
    )

    _datetime_serializer = pydantic_v2.field_serializer("from_datetime", "to_datetime")(format_into_utc_date)


class Bookability(enum.Enum):
    BOOKABLE = "BOOKABLE"
    STOCK_BOOKING_IS_DISABLED = "STOCK_BOOKING_IS_DISABLED"
    STOCK_IS_SOLD_OUT = "STOCK_IS_SOLD_OUT"
    USER_CANNOT_BOOK = "USER_CANNOT_BOOK"
    USER_HAS_ALREADY_BOOKED_OFFER = "USER_HAS_ALREADY_BOOKED_OFFER"
    USER_HAS_INSUFFICIENT_CREDIT = "USER_HAS_INSUFFICIENT_CREDIT"


@dataclass
class ScreeningMovieData:
    duration: int | None
    genres: list[str]
    last_30_days_bookings: int
    movie_name: str


@dataclass
class ScreeningVenueData:
    city: str
    distance: float
    label: str
    postal_code: str
    street: str
    venue_id: int


@dataclass
class ScreeningUserData:
    has_already_booked_offer: bool
    has_enough_credit: bool
    is_allowed_to_book: bool


@dataclass
class RawScreening:
    beginning_datetime: datetime
    features: list[str]
    is_sold_out: bool
    offer_id: int
    price: Decimal
    provider_class: str | None
    stock_id: int
    thumb_url: str | None
    movie_data: ScreeningMovieData | None = None
    user_data: ScreeningUserData | None = None
    venue_data: ScreeningVenueData | None = None


class Screening(HttpBodyModel):
    beginning_datetime: datetime
    bookability: Bookability
    features: list[str]
    price: float
    stock_id: int

    @classmethod
    def _get_screening_bookability(cls, raw_screening: RawScreening) -> Bookability:
        is_booking_disabled = providers_api.get_is_cinema_provider_disabled(raw_screening.provider_class)
        if is_booking_disabled:
            return Bookability.STOCK_BOOKING_IS_DISABLED
        if raw_screening.is_sold_out:
            return Bookability.STOCK_IS_SOLD_OUT
        if raw_screening.user_data:
            if raw_screening.user_data.has_already_booked_offer:
                return Bookability.USER_HAS_ALREADY_BOOKED_OFFER
            if not raw_screening.user_data.is_allowed_to_book:
                return Bookability.USER_CANNOT_BOOK
            if not raw_screening.user_data.has_enough_credit:
                return Bookability.USER_HAS_INSUFFICIENT_CREDIT

        return Bookability.BOOKABLE

    @classmethod
    def from_raw_screening(cls, raw_screening: RawScreening) -> typing.Self:
        return cls(
            beginning_datetime=raw_screening.beginning_datetime,
            bookability=cls._get_screening_bookability(raw_screening),
            features=raw_screening.features,
            price=float(raw_screening.price),
            stock_id=raw_screening.stock_id,
        )


class VenueScreenings(HttpBodyModel):
    address: str
    distance: float
    label: str
    offer_id: int
    thumb_url: str | None
    venue_id: int
    day_screenings: list[Screening]
    next_screening: Screening | None

    @classmethod
    def from_raw_screening(cls, screening: RawScreening) -> "VenueScreenings":
        assert screening.venue_data
        return cls(
            address=f"{screening.venue_data.street}, {screening.venue_data.postal_code} {screening.venue_data.city}",
            distance=screening.venue_data.distance,
            label=screening.venue_data.label,
            offer_id=screening.offer_id,
            thumb_url=screening.thumb_url,
            venue_id=screening.venue_data.venue_id,
            day_screenings=[],
            next_screening=None,
        )


def _get_best_next_screening(current_best: Screening, candidate: Screening, day: date) -> Screening:
    current_delta_from_day = (current_best.beginning_datetime.date() - day).days
    new_delta_from_day = (candidate.beginning_datetime.date() - day).days
    if abs(new_delta_from_day) < abs(current_delta_from_day):
        return candidate

    return current_best


class MovieCalendarResponse(HttpBodyModel):
    calendar: dict[date, list[VenueScreenings]]

    @classmethod
    def from_raw_screenings(
        cls, raw_screenings: list[RawScreening], start_date: datetime, end_date: datetime
    ) -> typing.Self:
        calendar = {}
        for day_delta in range((end_date - start_date).days + 1):
            day = (start_date + timedelta(days=day_delta)).date()
            venues: dict[int, VenueScreenings] = {}
            for raw_screening in raw_screenings:
                assert raw_screening.venue_data
                venue_id = raw_screening.venue_data.venue_id
                if venue_id not in venues:
                    venues[venue_id] = VenueScreenings.from_raw_screening(raw_screening)

                venue = venues[venue_id]
                screening = Screening.from_raw_screening(raw_screening)
                if screening.beginning_datetime.date() == day:
                    venue.day_screenings.append(screening)

                if not venue.next_screening:
                    venue.next_screening = screening
                else:
                    venue.next_screening = _get_best_next_screening(
                        current_best=venue.next_screening, candidate=screening, day=day
                    )

            sorted_screenings = sorted(
                venues.values(), key=lambda venue: (len(venue.day_screenings) == 0, venue.distance)
            )
            for venue in venues.values():
                venue.day_screenings.sort(key=lambda screening: screening.beginning_datetime)

            calendar[day] = sorted_screenings

        return cls(calendar=calendar)


class MovieScreenings(HttpBodyModel):
    duration: int | None
    genres: list[str]
    last_30_days_bookings: int
    movie_name: str
    offer_id: int
    thumb_url: str | None
    day_screenings: list[Screening]
    next_screening: Screening | None

    @classmethod
    def from_raw_screening(cls, raw_screening: RawScreening) -> typing.Self:
        assert raw_screening.movie_data
        return cls(
            duration=raw_screening.movie_data.duration,
            genres=list(filter(bool, map(get_movie_label, raw_screening.movie_data.genres))),  # pyright: ignore[reportArgumentType]
            last_30_days_bookings=raw_screening.movie_data.last_30_days_bookings,
            movie_name=raw_screening.movie_data.movie_name,
            offer_id=raw_screening.offer_id,
            thumb_url=raw_screening.thumb_url,
            day_screenings=[],
            next_screening=None,
        )


class VenueMovieCalendarResponse(HttpBodyModel):
    calendar: dict[date, list[MovieScreenings]]

    @classmethod
    def from_raw_venue_screenings(
        cls, raw_screenings: list[RawScreening], start_date: datetime, end_date: datetime
    ) -> typing.Self:
        calendar = {}
        for day_delta in range((end_date - start_date).days + 1):
            day = (start_date + timedelta(days=day_delta)).date()
            movies: dict[int, MovieScreenings] = {}
            for raw_screening in raw_screenings:
                offer_id = raw_screening.offer_id
                if offer_id not in movies:
                    movies[offer_id] = MovieScreenings.from_raw_screening(raw_screening)

                movie = movies[offer_id]
                screening = Screening.from_raw_screening(raw_screening)
                if screening.beginning_datetime.date() == day:
                    movie.day_screenings.append(screening)

                if not movie.next_screening:
                    movie.next_screening = screening
                else:
                    movie.next_screening = _get_best_next_screening(movie.next_screening, screening, day)

            sorted_screenings = sorted(
                movies.values(), key=lambda movie: (len(movie.day_screenings) == 0, -movie.last_30_days_bookings)
            )
            for movie in movies.values():
                movie.day_screenings.sort(key=lambda screening: screening.beginning_datetime)

            calendar[day] = sorted_screenings

        return cls(calendar=calendar)
