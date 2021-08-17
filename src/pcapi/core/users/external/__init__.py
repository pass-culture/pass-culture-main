from sqlalchemy.orm import joinedload

from pcapi.core.bookings.models import Booking
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.models import User
from pcapi.models.db import db

from .batch import update_user_attributes as update_batch_user
from .sendinblue import update_contact_attributes as update_sendinblue_user


def update_external_user(user: User):
    user_bookings = get_user_bookings(user)

    update_batch_user(user, user_bookings)
    update_sendinblue_user(user)


def get_user_bookings(user: User) -> list[Booking]:
    return (
        Booking.query.options(
            joinedload(Booking.stock).joinedload(Stock.offer).load_only(Offer.type, Offer.url, Offer.productId)
        )
        .filter_by(userId=user.id)
        .order_by(db.desc(Booking.dateCreated))
        .all()
    )
