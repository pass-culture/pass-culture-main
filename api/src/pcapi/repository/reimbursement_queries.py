from datetime import date
from typing import Optional

from sqlalchemy import Date
from sqlalchemy import cast

from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import IndividualBooking
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.educational.models import EducationalRedactor
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.models import User
from pcapi.models.payment import Payment
from pcapi.models.payment_status import PaymentStatus
from pcapi.models.payment_status import TransactionStatus


def find_all_offerer_payments(
    offerer_id: int, reimbursement_period: tuple[date, date], venue_id: Optional[int] = None
) -> list[tuple]:
    return find_all_offerers_payments(
        offerer_ids=[offerer_id],
        reimbursement_period=reimbursement_period,
        venue_id=venue_id,
    )


def find_all_offerers_payments(
    offerer_ids: list[int], reimbursement_period: tuple[date, date], venue_id: Optional[int] = None
) -> list[tuple]:
    payment_date = cast(PaymentStatus.date, Date)
    sent_payments = (
        Payment.query.join(PaymentStatus)
        .join(Booking)
        .filter(
            PaymentStatus.status == TransactionStatus.SENT,
            payment_date.between(*reimbursement_period, symmetric=True),
            Booking.offererId.in_(offerer_ids),
            Booking.isUsed,
            (Booking.venueId == venue_id) if venue_id else (Booking.venueId is not None),
        )
        .join(Offerer)
        .outerjoin(IndividualBooking)
        .outerjoin(User)
        .outerjoin(EducationalBooking)
        .outerjoin(EducationalRedactor)
        .join(Stock)
        .join(Offer)
        .join(Venue)
        .distinct(Payment.id)
        .order_by(Payment.id.desc(), PaymentStatus.date.desc())
        .with_entities(
            User.lastName.label("user_lastName"),
            User.firstName.label("user_firstName"),
            EducationalRedactor.firstName.label("redactor_firstname"),
            EducationalRedactor.lastName.label("redactor_lastname"),
            Booking.token.label("booking_token"),
            Booking.dateUsed.label("booking_dateUsed"),
            Booking.quantity.label("booking_quantity"),
            Booking.amount.label("booking_amount"),
            Offer.name.label("offer_name"),
            Offer.isEducational.label("offer_is_educational"),
            Offerer.address.label("offerer_address"),
            Venue.name.label("venue_name"),
            Venue.siret.label("venue_siret"),
            Venue.address.label("venue_address"),
            Payment.amount.label("amount"),
            Payment.reimbursementRate.label("reimbursement_rate"),
            Payment.iban.label("iban"),
            Payment.transactionLabel.label("transactionLabel"),
        )
    )

    return sent_payments.all()
