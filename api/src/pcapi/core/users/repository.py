from datetime import date
from datetime import datetime
import logging
from typing import Optional

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.query import Query

from pcapi.core.bookings.models import BookingStatus
from pcapi.core.bookings.models import IndividualBooking
from pcapi.domain.beneficiary_pre_subscription.validator import _is_postal_code_eligible
from pcapi.domain.favorite.favorite import FavoriteDomain
from pcapi.infrastructure.repository.favorite import favorite_domain_converter
from pcapi.models import Booking
from pcapi.models import Offer
from pcapi.models import Offerer
from pcapi.models import Stock
from pcapi.models import UserOfferer
from pcapi.models import Venue
from pcapi.repository import repository
from pcapi.repository.user_queries import find_user_by_email
from pcapi.utils import crypto

from . import constants
from . import exceptions
from . import models
from .models import User


logger = logging.getLogger(__name__)


HASHED_PLACEHOLDER = crypto.hash_password("placeholder")


def check_user_and_credentials(user: User, password: str) -> None:
    # Order is important to prevent end-user to guess user emails
    # We need to check email and password before checking email validation
    if not user:
        # Hash the given password, just like we would do if the user
        # existed. This avoids user enumeration by comparing server
        # response time.
        crypto.check_password(password, HASHED_PLACEHOLDER)
        raise exceptions.InvalidIdentifier()
    if not user.checkPassword(password) or not user.isActive:
        logging.info("Failed authentication attempt", extra={"user": user.id, "avoid_current_user": True})
        raise exceptions.InvalidIdentifier()
    if not user.isValidated or not user.isEmailValidated:
        raise exceptions.UnvalidatedAccount()


def get_user_with_credentials(identifier: str, password: str) -> User:
    user = find_user_by_email(identifier)
    check_user_and_credentials(user, password)
    return user


def get_user_with_valid_token(
    token_value: str, token_types: list[models.TokenType], use_token: bool = True
) -> Optional[User]:
    token = models.Token.query.filter(
        models.Token.value == token_value, models.Token.type.in_(token_types), models.Token.isUsed == False
    ).one_or_none()
    if not token:
        return None

    if token.expirationDate and token.expirationDate < datetime.now():
        return None

    if use_token:
        token.isUsed = True
        repository.save(token)

    return token.user


def get_and_lock_user(user_id: int) -> User:
    """Returns `user_id` user with a FOR UPDATE lock
    Raises UserDoesNotExist if no user is found.
    WARNING: MAKE SURE YOU FREE THE LOCK (with COMMIT or ROLLBACK) and don't hold it longer than
    strictly necessary.
    """
    # Use `with_for_update()` to make sure we lock the user while perfoming
    # the booking checks and update the `dnBookedQuantity`
    # This is required to prevent bugs due to concurent acces
    # Also call `populate_existing()` to make sure we don't use something
    # older from the SQLAlchemy's session.
    user = User.query.filter_by(id=user_id).populate_existing().with_for_update().one_or_none()
    if not user:
        raise exceptions.UserDoesNotExist()
    return user


def get_id_check_token(token_value: str) -> models.Token:
    return models.Token.query.filter(
        models.Token.value == token_value,
        models.Token.type == models.TokenType.ID_CHECK,
    ).one_or_none()


def get_newly_eligible_users(since: date) -> list[User]:
    """get users that are eligible between `since` (excluded) and now (included) and that have
    created their account before `since`"""
    today = datetime.combine(datetime.today(), datetime.min.time())
    since = datetime.combine(since, datetime.min.time())
    eligible_users = (
        User.query.outerjoin(UserOfferer)
        .filter(
            User.is_beneficiary == False,  # not already beneficiary
            User.isAdmin == False,  # not an admin
            UserOfferer.userId.is_(None),  # not a pro
            User.dateOfBirth > today - relativedelta(years=(constants.ELIGIBILITY_AGE_18 + 1)),  # less than 19yo
            User.dateOfBirth <= today - relativedelta(years=constants.ELIGIBILITY_AGE_18),  # more than or 18yo
            User.dateOfBirth > since - relativedelta(years=constants.ELIGIBILITY_AGE_18),  # less than 18yo at since
            User.dateCreated < today,
        )
        .all()
    )
    eligible_users = [user for user in eligible_users if _is_postal_code_eligible(user.departementCode)]
    return eligible_users


def find_favorite_for_offer_and_user(offer_id: int, user_id: int) -> Query:
    return models.Favorite.query.filter(models.Favorite.offerId == offer_id, models.Favorite.userId == user_id)


def get_favorites_for_offers(offer_ids: list[int]) -> list[models.Favorite]:
    return models.Favorite.query.filter(models.Favorite.offerId.in_(offer_ids)).all()


def find_favorites_domain_by_beneficiary(beneficiary_identifier: int) -> list[FavoriteDomain]:
    favorite_sql_entities = (
        models.Favorite.query.filter(models.Favorite.userId == beneficiary_identifier)
        .options(joinedload(models.Favorite.offer).joinedload(Offer.venue).joinedload(Venue.managingOfferer))
        .options(joinedload(models.Favorite.mediation))
        .options(joinedload(models.Favorite.offer).joinedload(Offer.stocks))
        .options(joinedload(models.Favorite.offer).joinedload(Offer.product))
        .options(joinedload(models.Favorite.offer).joinedload(Offer.mediations))
        .all()
    )

    offer_ids = [favorite_sql_entity.offer.id for favorite_sql_entity in favorite_sql_entities]

    bookings = (
        Offer.query.filter(Offer.id.in_(offer_ids))
        .join(Stock)
        .join(Booking)
        .join(IndividualBooking)
        .filter(IndividualBooking.userId == beneficiary_identifier)
        .filter(Booking.status != BookingStatus.CANCELLED)
        .with_entities(
            Booking.id.label("booking_id"),
            Booking.quantity,
            Offer.id.label("offer_id"),
            Stock.id.label("stock_id"),
        )
        .all()
    )

    bookings_by_offer_id = {
        booking.offer_id: {"id": booking.booking_id, "stock_id": booking.stock_id, "quantity": booking.quantity}
        for booking in bookings
    }

    return [
        favorite_domain_converter.to_domain(
            favorite_sql_entity, bookings_by_offer_id.get(favorite_sql_entity.offerId, None)
        )
        for favorite_sql_entity in favorite_sql_entities
    ]


def does_validated_phone_exist(phone_number: str):
    return bool(User.query.filter(User.phoneNumber == phone_number, User.is_phone_validated).count())


def get_users_with_validated_attachment_by_offerer(offerer: Offerer) -> User:
    return (
        User.query.join(UserOfferer)
        .filter(UserOfferer.validationToken.is_(None), UserOfferer.offererId == offerer.id)
        .all()
    )
