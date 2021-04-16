from datetime import date
from datetime import datetime
from typing import List
from typing import Optional

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.query import Query

from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription_validator import _is_postal_code_eligible
from pcapi.domain.favorite.favorite import FavoriteDomain
from pcapi.infrastructure.repository.favorite import favorite_domain_converter
from pcapi.models import Booking
from pcapi.models import Offer
from pcapi.models import Stock
from pcapi.models import UserOfferer
from pcapi.models import Venue
from pcapi.repository.user_queries import find_user_by_email

from . import constants
from . import exceptions
from . import models
from .models import User


def check_user_and_credentials(user: User, password: str) -> None:
    # Order is important to prevent end-user to guess user emails
    # We need to check email and password before checking email validation
    if not user or not user.isActive or not user.checkPassword(password):
        raise exceptions.InvalidIdentifier()
    if not user.isValidated or not user.isEmailValidated:
        raise exceptions.UnvalidatedAccount()


def get_user_with_credentials(identifier: str, password: str) -> User:
    user = find_user_by_email(identifier)
    check_user_and_credentials(user, password)
    return user


def get_user_with_valid_token(
    token_value: str, token_types: List[models.TokenType], delete_token: bool = False
) -> Optional[User]:
    token = models.Token.query.filter(models.Token.value == token_value, models.Token.type.in_(token_types)).first()
    if not token:
        return None

    if token.expirationDate and token.expirationDate < datetime.now():
        return None

    if delete_token:
        models.Token.query.filter_by(id=token.id).delete()

    return token.user


def get_id_check_token(token_value: str) -> models.Token:
    return models.Token.query.filter(
        models.Token.value == token_value, models.Token.type == models.TokenType.ID_CHECK
    ).first()


def get_newly_eligible_users(since: date) -> List[User]:
    """get users that are eligible between `since` (excluded) and now (included) and that have
    created their account before `since`"""
    today = datetime.combine(datetime.today(), datetime.min.time())
    since = datetime.combine(since, datetime.min.time())
    eligible_users = (
        User.query.outerjoin(UserOfferer)
        .filter(
            User.isBeneficiary == False,  # not already beneficiary
            User.isAdmin == False,  # not an admin
            UserOfferer.userId.is_(None),  # not a pro
            User.dateOfBirth > today - relativedelta(years=(constants.ELIGIBILITY_AGE + 1)),  # less than 19yo
            User.dateOfBirth <= today - relativedelta(years=constants.ELIGIBILITY_AGE),  # more than or 18yo
            User.dateOfBirth > since - relativedelta(years=constants.ELIGIBILITY_AGE),  # less than 18yo at since
            User.dateCreated < today,
        )
        .all()
    )
    eligible_users = [user for user in eligible_users if _is_postal_code_eligible(user.departementCode)]
    return eligible_users


def find_favorite_for_offer_and_user(offer_id: int, user_id: int) -> Query:
    return models.Favorite.query.filter(models.Favorite.offerId == offer_id, models.Favorite.userId == user_id)


def get_favorites_for_offers(offer_ids: List[int]) -> List[models.Favorite]:
    return models.Favorite.query.filter(models.Favorite.offerId.in_(offer_ids)).all()


def find_favorites_domain_by_beneficiary(beneficiary_identifier: int) -> List[FavoriteDomain]:
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
        .filter(Booking.userId == beneficiary_identifier)
        .filter(Booking.isCancelled == False)
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
