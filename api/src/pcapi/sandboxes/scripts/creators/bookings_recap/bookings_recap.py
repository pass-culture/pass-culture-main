from datetime import datetime
from datetime import timedelta
import logging

from pcapi.core.bookings.exceptions import BookingIsAlreadyCancelled
from pcapi.core.bookings.exceptions import BookingIsAlreadyUsed
from pcapi.core.bookings.factories import IndividualBookingFactory
from pcapi.core.bookings.factories import UsedIndividualBookingFactory
from pcapi.core.categories import subcategories
from pcapi.core.offers.factories import EventOfferFactory
from pcapi.core.offers.factories import EventProductFactory
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.factories import OffererFactory
from pcapi.core.offers.factories import ThingOfferFactory
from pcapi.core.offers.factories import ThingProductFactory
from pcapi.core.offers.factories import ThingStockFactory
from pcapi.core.offers.factories import UserOffererFactory
from pcapi.core.offers.factories import VenueFactory
from pcapi.core.payments.factories import PaymentFactory
from pcapi.core.payments.factories import PaymentStatusFactory
from pcapi.core.users.factories import BeneficiaryGrant18Factory
from pcapi.core.users.factories import ProFactory
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def save_bookings_recap_sandbox():
    yesterday = datetime.utcnow() - timedelta(days=1)
    today = datetime.utcnow()

    beneficiary1 = BeneficiaryGrant18Factory(
        publicName="Riri Duck", firstName="Riri", lastName="Duck", email="riri.duck@example.com"
    )

    beneficiary2 = BeneficiaryGrant18Factory(
        publicName="Fifi Brindacier",
        firstName="Fifi",
        lastName="Brindacier",
        email="fifi.brindacier@example.com",
    )
    beneficiary3 = BeneficiaryGrant18Factory(
        publicName="LouLou Duck",
        firstName="Loulou",
        lastName="Duck",
        email="loulou.duck@example.com",
    )

    pro = ProFactory(
        publicName="Balthazar Picsou",
        firstName="Balthazar",
        lastName="Picsou",
        email="balthazar.picsou@example.com",
    )
    offerer = OffererFactory(siren="645389012")
    UserOffererFactory(user=pro, offerer=offerer)
    venue1 = VenueFactory(managingOfferer=offerer, name="Cinéma Le Monde Perdu", siret="64538901265877")
    venue2 = VenueFactory(managingOfferer=offerer, name="Librairie Atlantis", siret="64538901201379")
    venue3 = VenueFactory(managingOfferer=offerer, name="Théatre Mordor", siret="64538954601379")
    venue4_virtual = VenueFactory(managingOfferer=offerer, name="Un lieu virtuel", siret=None, isVirtual=True)

    product1_venue1 = EventProductFactory(name="Jurassic Park", subcategoryId=subcategories.SEANCE_CINE.id)
    offer1_venue1 = EventOfferFactory(product=product1_venue1, venue=venue1, isDuo=True)
    stock_1_offer1_venue1 = EventStockFactory(
        offer=offer1_venue1, beginningDatetime=yesterday, quantity=None, price=12.99
    )

    product2_venue1 = EventProductFactory(name="Matrix", subcategoryId=subcategories.SEANCE_CINE.id)

    offer2_venue1 = EventOfferFactory(product=product2_venue1, venue=venue1, isDuo=False)
    stock_2_offer2_venue1 = EventStockFactory(offer=offer2_venue1, beginningDatetime=today, quantity=None, price=0)

    product1_venue2 = ThingProductFactory(
        name="Fondation", subcategoryId=subcategories.LIVRE_PAPIER.id, extraData={"isbn": "9788804119135"}
    )
    offer1_venue2 = ThingOfferFactory(product=product1_venue2, venue=venue2)
    stock_1_offer1_venue2 = ThingStockFactory(offer=offer1_venue2, quantity=42, price=9.99)

    product2_venue2 = ThingProductFactory(
        name="Martine à la playa",
        subcategoryId=subcategories.LIVRE_PAPIER.id,
        extraData={"isbn": "9787605639121"},
    )
    offer2_venue2 = ThingOfferFactory(product=product2_venue2, venue=venue2)
    stock_1_offer2_venue2 = ThingStockFactory(offer=offer2_venue2, quantity=12, price=49.99)

    product1_venue3 = EventProductFactory(
        name="Danse des haricots", subcategoryId=subcategories.SPECTACLE_REPRESENTATION.id
    )
    offer1_venue3 = EventOfferFactory(product=product1_venue3, venue=venue3)
    stock_1_offer1_venue3 = EventStockFactory(offer=offer1_venue3, quantity=44, price=18.50)

    product1_venue4 = ThingProductFactory(name="Le livre des haricots", subcategoryId=subcategories.LIVRE_PAPIER.id)
    offer1_venue4 = ThingOfferFactory(product=product1_venue4, venue=venue4_virtual)
    stock_1_offer1_venue4 = ThingStockFactory(offer=offer1_venue4, quantity=70, price=10.99)

    UsedIndividualBookingFactory(
        individualBooking__user=beneficiary1,
        stock=stock_1_offer1_venue1,
        dateCreated=datetime(2020, 3, 18, 14, 56, 12, 0),
        dateUsed=datetime(2020, 3, 22, 17, 00, 10, 0),
        quantity=2,
    )

    IndividualBookingFactory(
        individualBooking__user=beneficiary1,
        stock=stock_2_offer2_venue1,
        dateCreated=datetime(2020, 4, 22, 9, 17, 12, 0),
    )

    UsedIndividualBookingFactory(
        individualBooking__user=beneficiary2,
        stock=stock_1_offer1_venue1,
        dateCreated=datetime(2020, 3, 18, 12, 18, 12, 0),
        dateUsed=datetime(2020, 5, 2),
        quantity=2,
    )

    booking2_beneficiary2 = IndividualBookingFactory(
        individualBooking__user=beneficiary2,
        stock=stock_1_offer1_venue2,
        dateCreated=datetime(2020, 4, 12, 14, 31, 12, 0),
    )

    booking1_beneficiary3 = UsedIndividualBookingFactory(
        individualBooking__user=beneficiary3,
        stock=stock_2_offer2_venue1,
        dateCreated=datetime(2020, 1, 4, 19, 31, 12, 0),
        dateUsed=datetime(2020, 1, 4, 23, 00, 10, 0),
        quantity=2,
    )

    booking2_beneficiary3 = IndividualBookingFactory(
        individualBooking__user=beneficiary3,
        stock=stock_1_offer1_venue2,
        dateCreated=datetime(2020, 3, 21, 22, 9, 12, 0),
    )

    booking3_beneficiary1 = UsedIndividualBookingFactory(
        individualBooking__user=beneficiary1,
        stock=stock_1_offer1_venue3,
        dateCreated=datetime(2020, 4, 12, 14, 31, 12, 0),
    )

    payment_booking3_beneficiary1 = PaymentFactory(booking=booking3_beneficiary1)
    PaymentStatusFactory(payment=payment_booking3_beneficiary1, status=TransactionStatus.PENDING)

    booking3_beneficiary2 = UsedIndividualBookingFactory(
        individualBooking__user=beneficiary2,
        stock=stock_1_offer1_venue3,
        dateCreated=datetime(2020, 4, 12, 19, 31, 12, 0),
        dateUsed=datetime(2020, 4, 22, 17, 00, 10, 0),
    )

    PaymentFactory(booking=booking3_beneficiary2)
    PaymentStatusFactory(payment=payment_booking3_beneficiary1, status=TransactionStatus.SENT)

    booking3_beneficiary3 = UsedIndividualBookingFactory(
        individualBooking__user=beneficiary3,
        stock=stock_1_offer1_venue3,
        dateCreated=datetime(2020, 4, 12, 22, 9, 12, 0),
    )

    payment_booking3_beneficiary3 = PaymentFactory(booking=booking3_beneficiary3)
    PaymentStatusFactory(payment=payment_booking3_beneficiary3, status=TransactionStatus.ERROR)

    UsedIndividualBookingFactory(
        individualBooking__user=beneficiary3,
        stock=stock_1_offer1_venue2,
        dateCreated=datetime(2020, 3, 21, 22, 9, 12, 0),
    )

    booking5_beneficiary3 = IndividualBookingFactory(
        individualBooking__user=beneficiary3,
        stock=stock_1_offer1_venue4,
        dateCreated=datetime(2020, 3, 21, 22, 9, 12, 0),
    )

    booking6_beneficiary3 = UsedIndividualBookingFactory(
        individualBooking__user=beneficiary3,
        stock=stock_1_offer2_venue2,
        dateCreated=datetime(2020, 3, 21, 22, 9, 12, 0),
        dateUsed=datetime(2020, 4, 22, 21, 9, 12, 0),
    )

    payment_booking6_beneficiary3 = PaymentFactory(booking=booking6_beneficiary3)
    PaymentStatusFactory(payment=payment_booking6_beneficiary3, status=TransactionStatus.SENT)

    booking7_beneficiary2 = UsedIndividualBookingFactory(
        individualBooking__user=beneficiary2,
        stock=stock_1_offer2_venue2,
        dateCreated=datetime(2020, 4, 21, 22, 6, 12, 0),
        dateUsed=datetime(2020, 4, 22, 22, 9, 12, 0),
    )

    payment_booking7_beneficiary2 = PaymentFactory(booking=booking7_beneficiary2)
    PaymentStatusFactory(payment=payment_booking7_beneficiary2, status=TransactionStatus.RETRY)

    UsedIndividualBookingFactory(
        individualBooking__user=beneficiary1,
        stock=stock_1_offer2_venue2,
        dateCreated=datetime(2020, 2, 21, 22, 6, 12, 0),
        dateUsed=datetime(2020, 4, 22, 23, 9, 12, 0),
    )

    payment_booking8_beneficiary1 = PaymentFactory(booking=booking7_beneficiary2)
    PaymentStatusFactory(payment=payment_booking8_beneficiary1, status=TransactionStatus.PENDING)

    bookings_to_cancel = [
        booking2_beneficiary2,
        booking1_beneficiary3,
        booking2_beneficiary3,
        booking3_beneficiary2,
        booking5_beneficiary3,
    ]

    for booking in bookings_to_cancel:
        try:
            booking.cancel_booking()
        except (BookingIsAlreadyUsed, BookingIsAlreadyCancelled) as e:
            logger.info(str(e), extra={"booking": booking.id})
    repository.save(*bookings_to_cancel)
