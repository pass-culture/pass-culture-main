import enum
import logging
import typing
from dataclasses import dataclass
from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta

import pydantic as pydantic_v2

from pcapi.core.categories.genres.movie import get_movie_label
from pcapi.core.offers import models
from pcapi.core.providers import api as providers_api
from pcapi.routes.serialization import HttpBodyModel
from pcapi.routes.serialization import HttpQueryParamsModel
from pcapi.utils import date as date_utils
from pcapi.utils.date import format_into_utc_date


logger = logging.getLogger(__name__)


class Bookability(enum.Enum):
    BOOKABLE = "BOOKABLE"
    STOCK_BOOKING_IS_DISABLED = "STOCK_BOOKING_IS_DISABLED"
    STOCK_IS_SOLD_OUT = "STOCK_IS_SOLD_OUT"
    USER_CANNOT_BOOK = "USER_CANNOT_BOOK"
    USER_HAS_ALREADY_BOOKED_OFFER = "USER_HAS_ALREADY_BOOKED_OFFER"
    USER_HAS_INSUFFICIENT_CREDIT = "USER_HAS_INSUFFICIENT_CREDIT"


@dataclass
class RawScreening:
    city: str
    beginning_datetime: datetime
    distance: float
    features: list[str]
    is_sold_out: bool
    label: str
    offer_id: int
    price: float
    postal_code: str
    provider_class: str
    stock_id: int
    street: str
    thumb_url: str
    venue_id: int


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
    def validate_params(self) -> "MovieScreeningsRequest":
        if (not self.allocine_id and not self.visa) or (self.allocine_id and self.visa):
            raise ValueError("Only one of allocine_id and visa must be provided")

        return self


class Screening(HttpBodyModel):
    beginning_datetime: datetime
    bookability: Bookability
    features: list[str]
    price: float
    stock_id: int

    @classmethod
    def _get_screening_bookability(cls, provider_class: str | None, is_sold_out: bool) -> Bookability:
        is_booking_disabled = providers_api.get_is_cinema_provider_disabled(provider_class)
        if is_booking_disabled:
            return Bookability.STOCK_BOOKING_IS_DISABLED
        if is_sold_out:
            return Bookability.STOCK_IS_SOLD_OUT

        return Bookability.BOOKABLE

    @classmethod
    def from_raw_screening(cls, screening: RawScreening) -> "Screening":
        return cls(
            beginning_datetime=screening.beginning_datetime,
            bookability=cls._get_screening_bookability(screening.provider_class, screening.is_sold_out),
            features=screening.features,
            price=screening.price,
            stock_id=screening.stock_id,
        )

    @classmethod
    def from_stock(cls, stock: models.Stock) -> "Screening":
        assert stock.beginningDatetime is not None
        provider_class = stock.offer.lastProvider.localClass if stock.offer.lastProvider else None
        return cls(
            beginning_datetime=stock.beginningDatetime,
            bookability=cls._get_screening_bookability(provider_class, stock.isSoldOut),
            features=stock.features,
            price=float(stock.price),
            stock_id=stock.id,
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
        return cls(
            address=f"{screening.street}, {screening.postal_code} {screening.city}",
            distance=screening.distance,
            label=screening.label,
            offer_id=screening.offer_id,
            thumb_url=screening.thumb_url,
            venue_id=screening.venue_id,
            day_screenings=[],
            next_screening=None,
        )


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
                venue_id = raw_screening.venue_id
                if venue_id not in venues:
                    venues[venue_id] = VenueScreenings.from_raw_screening(raw_screening)

                venue = venues[venue_id]
                screening = Screening.from_raw_screening(raw_screening)
                if screening.beginning_datetime.date() == day:
                    venue.day_screenings.append(screening)

                if not venue.next_screening:
                    venue.next_screening = screening
                    continue

                current_delta_from_day = (venue.next_screening.beginning_datetime.date() - day).days
                new_delta_from_day = (screening.beginning_datetime.date() - day).days
                if abs(new_delta_from_day) < abs(current_delta_from_day):
                    venue.next_screening = screening

            sorted_screenings = sorted(
                venues.values(), key=lambda venue: (len(venue.day_screenings) == 0, venue.distance)
            )
            for venue in venues.values():
                venue.day_screenings.sort(key=lambda screening: screening.beginning_datetime)

            calendar[day] = sorted_screenings

        return cls(calendar=calendar)


@dataclass
class RawScreeningForUser(RawScreening):
    user_has_already_booked_offer: bool
    user_has_enough_credit: bool
    user_is_allowed_to_book: bool


class ScreeningForUser(HttpBodyModel):
    beginning_datetime: datetime
    bookability: Bookability
    features: list[str]
    price: float
    stock_id: int

    @classmethod
    def _get_screening_bookability(cls, screening: RawScreeningForUser) -> Bookability:
        is_booking_disabled = providers_api.get_is_cinema_provider_disabled(screening.provider_class)
        if is_booking_disabled:
            return Bookability.STOCK_BOOKING_IS_DISABLED
        if screening.is_sold_out:
            return Bookability.STOCK_IS_SOLD_OUT
        if screening.user_has_already_booked_offer:
            return Bookability.USER_HAS_ALREADY_BOOKED_OFFER
        if not screening.user_is_allowed_to_book:
            return Bookability.USER_CANNOT_BOOK
        if not screening.user_has_enough_credit:
            return Bookability.USER_HAS_INSUFFICIENT_CREDIT

        return Bookability.BOOKABLE

    @classmethod
    def from_raw_screening(cls, screening: RawScreeningForUser) -> typing.Self:
        return cls(
            beginning_datetime=screening.beginning_datetime,
            bookability=cls._get_screening_bookability(screening),
            features=screening.features,
            price=screening.price,
            stock_id=screening.stock_id,
        )


class VenueScreeningsForUser(HttpBodyModel):
    address: str
    distance: float
    label: str
    offer_id: int
    thumb_url: str | None
    venue_id: int
    day_screenings: list[ScreeningForUser]
    next_screening: ScreeningForUser | None

    @classmethod
    def from_raw_screening(cls, screening: RawScreeningForUser) -> typing.Self:
        return cls(
            address=f"{screening.street}, {screening.postal_code} {screening.city}",
            distance=screening.distance,
            label=screening.label,
            offer_id=screening.offer_id,
            thumb_url=screening.thumb_url,
            venue_id=screening.venue_id,
            day_screenings=[],
            next_screening=None,
        )


class MovieCalendarForUserResponse(HttpBodyModel):
    calendar: dict[date, list[VenueScreeningsForUser]]

    @classmethod
    def from_raw_screenings(
        cls, raw_screenings: list[RawScreeningForUser], start_date: datetime, end_date: datetime
    ) -> typing.Self:
        calendar = {}
        for day_delta in range((end_date - start_date).days + 1):
            day = (start_date + timedelta(days=day_delta)).date()
            venues: dict[int, VenueScreeningsForUser] = {}
            for raw_screening in raw_screenings:
                venue_id = raw_screening.venue_id
                if venue_id not in venues:
                    venues[venue_id] = VenueScreeningsForUser.from_raw_screening(raw_screening)

                venue = venues[venue_id]
                screening = ScreeningForUser.from_raw_screening(raw_screening)
                if screening.beginning_datetime.date() == day:
                    venue.day_screenings.append(screening)

                if not venue.next_screening:
                    venue.next_screening = screening
                    continue

                current_delta_from_day = (venue.next_screening.beginning_datetime.date() - day).days
                new_delta_from_day = (screening.beginning_datetime.date() - day).days
                if abs(new_delta_from_day) < abs(current_delta_from_day):
                    venue.next_screening = screening

            sorted_screenings = sorted(
                venues.values(), key=lambda venue: (len(venue.day_screenings) == 0, venue.distance)
            )
            for venue in venues.values():
                venue.day_screenings.sort(key=lambda screening: screening.beginning_datetime)

            calendar[day] = sorted_screenings

        return cls(calendar=calendar)


class VenueMovieScreeningsRequest(HttpBodyModel):
    from_datetime: datetime = pydantic_v2.Field(alias="from", default_factory=date_utils.get_naive_utc_now)
    to_datetime: datetime = pydantic_v2.Field(
        alias="to", default_factory=lambda: datetime.combine(date.today(), time.max) + timedelta(days=15)
    )

    _datetime_serializer = pydantic_v2.field_serializer("from_datetime", "to_datetime")(format_into_utc_date)


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
    def from_offer(cls, offer: models.Offer) -> "MovieScreenings":
        genres = []
        if offer.extraData:
            for genre in offer.extraData.get("genres") or []:
                label = get_movie_label(genre)
                if label:
                    genres.append(label)

        last_30_days_bookings = 0
        if offer.product and offer.product.last_30_days_booking:
            last_30_days_bookings = offer.product.last_30_days_booking

        return cls(
            duration=offer.durationMinutes,
            genres=genres,
            last_30_days_bookings=last_30_days_bookings,
            movie_name=offer.name,
            offer_id=offer.id,
            thumb_url=offer.thumbUrl,
            day_screenings=[],
            next_screening=None,
        )


class VenueMovieCalendarResponse(HttpBodyModel):
    calendar: dict[date, list[MovieScreenings]]

    @classmethod
    def from_offers(
        cls, offers: list[models.Offer], start_date: datetime, end_date: datetime
    ) -> "VenueMovieCalendarResponse":
        calendar = {}
        for day_delta in range((end_date - start_date).days + 1):
            day = (start_date + timedelta(days=day_delta)).date()
            movies: dict[int, MovieScreenings] = {}
            for offer in offers:
                if offer.id not in movies:
                    movies[offer.id] = MovieScreenings.from_offer(offer)

                movie = movies[offer.id]
                for stock in offer.stocks:
                    screening = Screening.from_stock(stock)
                    if screening.beginning_datetime.date() == day:
                        movie.day_screenings.append(screening)

                    if not movie.next_screening:
                        movie.next_screening = screening
                        continue

                    current_delta_from_day = (movie.next_screening.beginning_datetime.date() - day).days
                    new_delta_from_day = (screening.beginning_datetime.date() - day).days
                    if abs(new_delta_from_day) < abs(current_delta_from_day):
                        movie.next_screening = screening

            sorted_screenings = sorted(
                movies.values(), key=lambda movie: (len(movie.day_screenings) == 0, -movie.last_30_days_bookings)
            )
            for movie in movies.values():
                movie.day_screenings.sort(key=lambda screening: screening.beginning_datetime)

            calendar[day] = sorted_screenings

        return cls(calendar=calendar)


class MovieScreeningsForUser(HttpBodyModel):
    duration: int | None
    genres: list[str]
    last_30_days_bookings: int
    movie_name: str
    offer_id: int
    thumb_url: str | None
    day_screenings: list[Screening]
    next_screening: Screening | None

    @classmethod
    def from_offer(cls, offer: models.Offer) -> "MovieScreenings":
        genres = []
        if offer.extraData:
            for genre in offer.extraData.get("genres") or []:
                label = get_movie_label(genre)
                if label:
                    genres.append(label)

        last_30_days_bookings = 0
        if offer.product and offer.product.last_30_days_booking:
            last_30_days_bookings = offer.product.last_30_days_booking

        return cls(
            duration=offer.durationMinutes,
            genres=genres,
            last_30_days_bookings=last_30_days_bookings,
            movie_name=offer.name,
            offer_id=offer.id,
            thumb_url=offer.thumbUrl,
            day_screenings=[],
            next_screening=None,
        )


class VenueMovieCalendarForUserResponse(HttpBodyModel):
    calendar: dict[date, list[MovieScreenings]]

    @classmethod
    def from_offers(
        cls, offers: list[models.Offer], start_date: datetime, end_date: datetime
    ) -> "VenueMovieCalendarResponse":
        calendar = {}
        for day_delta in range((end_date - start_date).days + 1):
            day = (start_date + timedelta(days=day_delta)).date()
            movies: dict[int, MovieScreenings] = {}
            for offer in offers:
                if offer.id not in movies:
                    movies[offer.id] = MovieScreenings.from_offer(offer)

                movie = movies[offer.id]
                for stock in offer.stocks:
                    screening = Screening.from_stock(stock)
                    if screening.beginning_datetime.date() == day:
                        movie.day_screenings.append(screening)

                    if not movie.next_screening:
                        movie.next_screening = screening
                        continue

                    current_delta_from_day = (movie.next_screening.beginning_datetime.date() - day).days
                    new_delta_from_day = (screening.beginning_datetime.date() - day).days
                    if abs(new_delta_from_day) < abs(current_delta_from_day):
                        movie.next_screening = screening

            sorted_screenings = sorted(
                movies.values(), key=lambda movie: (len(movie.day_screenings) == 0, -movie.last_30_days_bookings)
            )
            for movie in movies.values():
                movie.day_screenings.sort(key=lambda screening: screening.beginning_datetime)

            calendar[day] = sorted_screenings

        return cls(calendar=calendar)
