from datetime import date
from typing import Optional

import sqlalchemy as sqla

from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import IndividualBooking
from pcapi.core.educational.models import EducationalBooking
from pcapi.core.educational.models import EducationalRedactor
import pcapi.core.finance.models as finance_models
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.models import User
from pcapi.models.bank_information import BankInformation
from pcapi.models.feature import FeatureToggle


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
    payment_date = sqla.cast(finance_models.PaymentStatus.date, sqla.Date)
    sent_payments = (
        finance_models.Payment.query.join(finance_models.PaymentStatus)
        .join(Booking)
        .filter(
            finance_models.PaymentStatus.status == finance_models.TransactionStatus.SENT,
            payment_date.between(*reimbursement_period, symmetric=True),
            Booking.offererId.in_(offerer_ids),
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
        .distinct(finance_models.Payment.id)
        .order_by(finance_models.Payment.id.desc(), finance_models.PaymentStatus.date.desc())
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
            finance_models.Payment.amount.label("amount"),
            finance_models.Payment.reimbursementRate.label("reimbursement_rate"),
            finance_models.Payment.iban.label("iban"),
            finance_models.Payment.transactionLabel.label("transactionLabel"),
        )
    )

    sent_pricings = (
        finance_models.Pricing.query.join(finance_models.Pricing.booking)
        .join(finance_models.Pricing.cashflows)
        .join(finance_models.Cashflow.bankAccount)
        .outerjoin(finance_models.Pricing.customRule)
        .filter(
            finance_models.Pricing.status == finance_models.PricingStatus.INVOICED,
            sqla.cast(finance_models.Cashflow.creationDate, sqla.Date).between(
                *reimbursement_period,
                symmetric=True,
            ),
            Booking.offererId.in_(offerer_ids),
            (Booking.venueId == venue_id) if venue_id else sqla.true(),
        )
        .join(Booking.offerer)
        .outerjoin(IndividualBooking)
        .outerjoin(User)
        .outerjoin(EducationalBooking)
        .outerjoin(EducationalRedactor)
        .join(Stock)
        .join(Offer)
        .join(Venue)
        .order_by(Booking.dateUsed.desc(), Booking.id.desc())
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
            # See note about `amount` in `core/finance/models.py`.
            (-finance_models.Pricing.amount).label("amount"),
            finance_models.Pricing.standardRule.label("rule_name"),
            finance_models.Pricing.customRuleId.label("rule_id"),
            finance_models.Cashflow.creationDate.label("cashflow_date"),
            BankInformation.iban.label("iban"),
        )
    )

    results = sent_pricings.all()
    if FeatureToggle.INCLUDE_LEGACY_PAYMENTS_FOR_REIMBURSEMENTS.is_active():
        results.extend(sent_payments.all())

    return results
