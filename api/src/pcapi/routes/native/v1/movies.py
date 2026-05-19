from flask_login import current_user
from werkzeug.exceptions import BadRequest

from pcapi.core.bookings import repository as bookings_repository
from pcapi.core.offers import repository
from pcapi.core.offers.models import Product
from pcapi.core.users import api as users_api
from pcapi.models import db
from pcapi.models.utils import first_or_404
from pcapi.routes.native.security import authenticated_and_active_user_required
from pcapi.serialization.decorator import spectree_serialize

from .. import blueprint
from .serialization import movies as serializers


@blueprint.native_route("/movie/calendar", methods=["GET"])
@spectree_serialize(response_model=serializers.MovieCalendarResponse, api=blueprint.api, on_error_statuses=[400, 404])
def get_movie_screenings(query: serializers.MovieScreeningsRequest) -> serializers.MovieCalendarResponse:
    if query.allocine_id:
        product_query = db.session.query(Product).filter(Product.extraData.op("->")("allocineId") == query.allocine_id)
    elif query.visa:
        product_query = db.session.query(Product).filter(Product.extraData["visa"].astext == query.visa)
    else:
        raise BadRequest()  # shoud not happen

    product = first_or_404(product_query)

    results = repository.get_nearby_bookable_screenings_from_product(
        product,
        query.latitude,
        query.longitude,
        query.around_radius,
        query.from_datetime,
        query.to_datetime,
    )

    return serializers.MovieCalendarResponse.from_raw_screenings(
        [serializers.RawScreening(**row) for row in results], query.from_datetime, query.to_datetime
    )


@blueprint.native_route("/movie/calendar/me", methods=["GET"])
@authenticated_and_active_user_required
@spectree_serialize(
    response_model=serializers.MovieCalendarForUserResponse, api=blueprint.api, on_error_statuses=[400, 404]
)
def get_movie_screenings_for_user(
    query: serializers.MovieScreeningsRequest,
) -> serializers.MovieCalendarForUserResponse:
    if query.allocine_id:
        product_query = db.session.query(Product).filter(Product.extraData.op("->")("allocineId") == query.allocine_id)
    elif query.visa:
        product_query = db.session.query(Product).filter(Product.extraData["visa"].astext == query.visa)
    else:
        raise BadRequest()  # shoud not happen

    product = first_or_404(product_query)
    results = repository.get_nearby_bookable_screenings_from_product(
        product,
        query.latitude,
        query.longitude,
        query.around_radius,
        query.from_datetime,
        query.to_datetime,
    )

    user_bookings = (
        bookings_repository.get_bookings_from_deposit(current_user.deposit.id) if current_user.deposit else []
    )
    booked_offers = [booking.stock.offer.id for booking in user_bookings]
    user_domains_credit = users_api.get_domains_credit(current_user, user_bookings)
    remaining_credit = user_domains_credit.all.remaining if user_domains_credit else 0
    raw_screenings = [
        serializers.RawScreeningForUser(
            **row,
            user_has_already_booked_offer=row["offer_id"] in booked_offers,
            user_has_enough_credit=row["price"] <= remaining_credit,
            user_is_allowed_to_book=current_user.is_beneficiary,
        )
        for row in results
    ]

    return serializers.MovieCalendarForUserResponse.from_raw_screenings(
        raw_screenings, query.from_datetime, query.to_datetime
    )


@blueprint.native_route("/venue/<int:venue_id>/movie/calendar", methods=["GET"])
@spectree_serialize(response_model=serializers.VenueMovieCalendarResponse, api=blueprint.api, on_error_statuses=[400])
def get_movie_screenings_by_venue(
    venue_id: int, query: serializers.VenueMovieScreeningsRequest
) -> serializers.VenueMovieCalendarResponse:
    offers = repository.get_bookable_screenings_from_venue(
        venue_id,
        query.from_datetime,
        query.to_datetime,
    )

    return serializers.VenueMovieCalendarResponse.from_offers(offers, query.from_datetime, query.to_datetime)
