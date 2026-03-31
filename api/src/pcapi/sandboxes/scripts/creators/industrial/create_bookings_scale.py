"""
Sandbox: large bookings dataset for scale testing.

Creates 1 venue with 5500+ bookings across diverse offer types and statuses.
Login: bookings.scale@example.com / user@AZERTY123
"""

import logging
from datetime import timedelta
from decimal import Decimal

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.finance.factories as finance_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories import subcategories
from pcapi.core.offerers.models import Offerer
from pcapi.models import db
from pcapi.utils import date as date_utils


logger = logging.getLogger(__name__)

PRO_EMAIL = "bookings.scale@example.com"
SIREN = "998877000"
N_USERS = 55

# (label_prefix, subcategory, is_event, is_past, price, n_offers)
OFFER_SPECS = [
    # Events — past (beginningDatetime in the past → "confirmed" recap status for CONFIRMED bookings)
    ("Séance de cinéma", subcategories.SEANCE_CINE, True, True, Decimal("7.50"), 5),
    ("Concert", subcategories.CONCERT, True, True, Decimal("20.00"), 5),
    ("Spectacle vivant", subcategories.SPECTACLE_REPRESENTATION, True, True, Decimal("25.00"), 5),
    ("Festival de musique", subcategories.FESTIVAL_MUSIQUE, True, True, Decimal("30.00"), 5),
    ("Conférence", subcategories.CONFERENCE, True, True, Decimal("5.00"), 5),
    # Events — future (beginningDatetime in the future → "booked" recap status for CONFIRMED bookings)
    ("Séance de cinéma", subcategories.SEANCE_CINE, True, False, Decimal("7.50"), 5),
    ("Concert", subcategories.CONCERT, True, False, Decimal("20.00"), 5),
    ("Spectacle vivant", subcategories.SPECTACLE_REPRESENTATION, True, False, Decimal("25.00"), 5),
    ("Festival de musique", subcategories.FESTIVAL_MUSIQUE, True, False, Decimal("30.00"), 5),
    ("Conférence", subcategories.CONFERENCE, True, False, Decimal("5.00"), 5),
    # Things (no event date → "booked" recap status for CONFIRMED bookings)
    ("Livre papier", subcategories.LIVRE_PAPIER, False, None, Decimal("15.00"), 10),
    ("Livre numérique", subcategories.LIVRE_NUMERIQUE, False, None, Decimal("8.99"), 10),
    ("CD musical", subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD, False, None, Decimal("10.00"), 10),
    ("Achat instrument", subcategories.ACHAT_INSTRUMENT, False, None, Decimal("0.00"), 10),
    ("Jeu en ligne", subcategories.JEU_EN_LIGNE, False, None, Decimal("3.00"), 10),
]
# Total: 5 × 5 + 5 × 5 + 5 × 10 = 100 offers × 55 bookings = 5500 bookings

# 55 statuses cycling per offer, covering all BookingRecapStatus values:
# "confirmed" (CONFIRMED on past event) → 12
# "booked"    (CONFIRMED on future event / thing) → 12
# "validated" (USED)                    → 14
# "cancelled" (CANCELLED)               → 10
# "reimbursed" (REIMBURSED)             → 5
# "pending"   (PENDING_REIMBURSEMENT)   → 2
# = 55 total
STATUS_CYCLE = (
    [BookingStatus.CONFIRMED] * 24  # 24 = 12 + 12 (split between past/future events)
    + [BookingStatus.USED] * 14
    + [BookingStatus.CANCELLED] * 10
    + [BookingStatus.REIMBURSED] * 5
    + [BookingStatus.PENDING_REIMBURSEMENT] * 2
)
assert len(STATUS_CYCLE) == N_USERS


def create_bookings_scale_sandbox() -> None:
    # Idempotency guard

    if db.session.query(Offerer).filter_by(siren=SIREN).one_or_none():
        logger.info("bookings_scale sandbox already exists, skipping")
        return

    logger.info("Creating bookings_scale sandbox")

    # --- Pro user, offerer, venue, bank account ---
    pro_user = users_factories.ProFactory.create(
        email=PRO_EMAIL,
        firstName="Scale",
        lastName="Test",
        password="user@AZERTY123",
    )
    offerer = offerers_factories.OffererFactory.create(
        name="Structure Scale Test",
        siren=SIREN,
    )
    offerers_factories.UserOffererFactory.create(user=pro_user, offerer=offerer)
    venue = offerers_factories.VenueFactory.create(
        name="Lieu Scale Test",
        managingOfferer=offerer,
        bookingEmail=PRO_EMAIL,
    )
    bank_account = finance_factories.BankAccountFactory.create(
        offerer=offerer,
        dsApplicationId=9_800_000,
    )
    offerers_factories.VenueBankAccountLinkFactory.create(venue=venue, bankAccount=bank_account)
    logger.info("Created offerer, venue, bank account")

    # --- Beneficiary users ---
    # Each user books 100 offers — give them enough deposit to cover the total cost
    # (max price per offer is 30€ × 100 offers = 3000€)
    users = [
        users_factories.BeneficiaryFactory.create(
            email=f"scale.user.{i:03d}@example.com",
            firstName=f"User{i:03d}",
            lastName="Scale",
            deposit__amount=Decimal("5000"),
        )
        for i in range(N_USERS)
    ]
    logger.info("Created %d beneficiary users", N_USERS)

    # --- Offers, stocks and bookings ---
    now = date_utils.get_naive_utc_now()
    past = now - timedelta(days=60)
    future = now + timedelta(days=30)
    past_used = now - timedelta(days=30)
    past_reimbursed = now - timedelta(days=15)

    total_bookings = 0
    offer_index = 0

    for label, subcategory, is_event, is_past, price, n_offers in OFFER_SPECS:
        for i in range(n_offers):
            offer_name = f"{label} #{offer_index + 1}"

            if is_event:
                beginning = past if is_past else future
                offer = offers_factories.EventOfferFactory.create(
                    name=offer_name,
                    venue=venue,
                    subcategoryId=subcategory.id,
                )
                stock = offers_factories.EventStockFactory.create(
                    offer=offer,
                    price=price,
                    quantity=N_USERS + 10,
                    beginningDatetime=beginning,
                    bookingLimitDatetime=beginning - timedelta(days=1),
                )
            else:
                offer = offers_factories.ThingOfferFactory.create(
                    name=offer_name,
                    venue=venue,
                    subcategoryId=subcategory.id,
                )
                stock = offers_factories.ThingStockFactory.create(
                    offer=offer,
                    price=price,
                    quantity=N_USERS + 10,
                )

            for user, status in zip(users, STATUS_CYCLE):
                booking_kwargs: dict = dict(user=user, stock=stock, status=status)

                if status in (
                    BookingStatus.USED,
                    BookingStatus.REIMBURSED,
                    BookingStatus.PENDING_REIMBURSEMENT,
                ):
                    booking_kwargs["dateUsed"] = past_used

                if status == BookingStatus.REIMBURSED:
                    booking_kwargs["reimbursementDate"] = past_reimbursed

                if status == BookingStatus.CANCELLED:
                    booking_kwargs["cancellationReason"] = BookingCancellationReasons.BENEFICIARY

                bookings_factories.BookingFactory.create(**booking_kwargs)
                total_bookings += 1

            if total_bookings % 500 == 0:
                logger.info("  %d bookings created so far...", total_bookings)

            offer_index += 1

    logger.info("bookings_scale sandbox done: %d offers, %d bookings", offer_index, total_bookings)
