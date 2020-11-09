from datetime import datetime
from datetime import timedelta

from pcapi.models import EventType
from pcapi.models import ThingType
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository import repository
from pcapi.sandboxes.scripts.creators.helpers.sql_creators import create_booking
from pcapi.sandboxes.scripts.creators.helpers.sql_creators import create_deposit
from pcapi.sandboxes.scripts.creators.helpers.sql_creators import create_offer_with_event_product
from pcapi.sandboxes.scripts.creators.helpers.sql_creators import create_offer_with_thing_product
from pcapi.sandboxes.scripts.creators.helpers.sql_creators import create_offerer
from pcapi.sandboxes.scripts.creators.helpers.sql_creators import create_payment
from pcapi.sandboxes.scripts.creators.helpers.sql_creators import create_stock
from pcapi.sandboxes.scripts.creators.helpers.sql_creators import create_user
from pcapi.sandboxes.scripts.creators.helpers.sql_creators import create_user_offerer
from pcapi.sandboxes.scripts.creators.helpers.sql_creators import create_venue


def save_bookings_recap_sandbox():
    yesterday = datetime.utcnow() - timedelta(days=1)
    today = datetime.utcnow()

    beneficiary1 = create_user(
        public_name='Riri Duck',
        first_name='Riri',
        last_name='Duck',
        email='riri.duck@example.com',
    )
    beneficiary2 = create_user(
        public_name='Fifi Brindacier',
        first_name='Fifi',
        last_name='Brindacier',
        email='fifi.brindacier@example.com',
    )
    beneficiary3 = create_user(
        public_name='LouLou Duck',
        first_name='Loulou',
        last_name='Duck',
        email='loulou.duck@example.com',
    )

    create_deposit(beneficiary1)
    create_deposit(beneficiary2)
    create_deposit(beneficiary3)

    pro = create_user(
        public_name='Balthazar Picsou',
        first_name='Balthazar',
        last_name='Picsou',
        email='balthazar.picsou@example.com',
        can_book_free_offers=False
    )
    offerer = create_offerer(
        siren='645389012',
    )
    user_offerer = create_user_offerer(user=pro, offerer=offerer)
    venue1 = create_venue(offerer, name='Cinéma Le Monde Perdu', siret='64538901265877')
    venue2 = create_venue(offerer, name='Librairie Atlantis', siret='64538901201379')
    venue3 = create_venue(offerer, name='Théatre Mordor', siret='64538954601379')
    venue4_virtual = create_venue(offerer, name='Un lieu virtuel', siret=None, is_virtual=True)

    offer1_venue1 = create_offer_with_event_product(
        venue=venue1,
        event_name='Jurassic Park',
        event_type=EventType.CINEMA,
        is_duo=True,
    )
    stock_1_offer1_venue1 = create_stock(
        offer=offer1_venue1,
        beginning_datetime=yesterday,
        quantity=None,
        price=12.99,
    )
    offer2_venue1 = create_offer_with_event_product(
        venue=venue1,
        event_name='Matrix',
        event_type=EventType.CINEMA,
        is_duo=False,
    )
    stock_2_offer2_venue1 = create_stock(
        offer=offer2_venue1,
        beginning_datetime=today,
        quantity=None,
        price=0,
    )

    offer1_venue2 = create_offer_with_thing_product(
        venue=venue2,
        thing_name='Fondation',
        thing_type=ThingType.LIVRE_EDITION,
        extra_data={'isbn': '9788804119135'}
    )
    stock_1_offer1_venue2 = create_stock(
        offer=offer1_venue2,
        quantity=42,
        price=9.99,
    )
    offer2_venue2 = create_offer_with_thing_product(
        venue=venue2,
        thing_name='Martine à la playa',
        thing_type=ThingType.LIVRE_EDITION,
        extra_data={'isbn': '9787605639121'}
    )
    stock_1_offer2_venue2 = create_stock(
        offer=offer2_venue2,
        quantity=12,
        price=49.99,
    )

    offer1_venue3 = create_offer_with_event_product(
        venue=venue3,
        event_name='Danse des haricots',
        event_type=EventType.SPECTACLE_VIVANT,
    )
    stock_1_offer1_venue3 = create_stock(
        offer=offer1_venue3,
        quantity=44,
        price=18.50,
    )

    offer1_venue4 = create_offer_with_thing_product(
        venue=venue4_virtual,
        thing_name='Le livre des haricots',
        thing_type=ThingType.LIVRE_EDITION,
    )
    stock_1_offer1_venue4 = create_stock(
        offer=offer1_venue4,
        quantity=70,
        price=10.99,
    )

    booking1_beneficiary1 = create_booking(
        user=beneficiary1,
        stock=stock_1_offer1_venue1,
        date_created=datetime(2020, 3, 18, 14, 56, 12, 0),
        is_used=True,
        date_used=datetime(2020, 3, 22, 17, 00, 10, 0),
        quantity=2,
    )
    booking2_beneficiary1 = create_booking(
        user=beneficiary1,
        stock=stock_2_offer2_venue1,
        date_created=datetime(2020, 4, 22, 9, 17, 12, 0),
    )
    booking1_beneficiary2 = create_booking(
        user=beneficiary2,
        stock=stock_1_offer1_venue1,
        date_created=datetime(2020, 3, 18, 12, 18, 12, 0),
        is_used=True,
        date_used=datetime(2020, 5, 2),
        quantity=2,
    )
    booking2_beneficiary2 = create_booking(
        user=beneficiary2,
        stock=stock_1_offer1_venue2,
        date_created=datetime(2020, 4, 12, 14, 31, 12, 0),
        is_cancelled=False,
    )
    booking1_beneficiary3 = create_booking(
        user=beneficiary3,
        stock=stock_2_offer2_venue1,
        date_created=datetime(2020, 1, 4, 19, 31, 12, 0),
        is_cancelled=False,
        is_used=True,
        date_used=datetime(2020, 1, 4, 23, 00, 10, 0),
        quantity=2,
    )
    booking2_beneficiary3 = create_booking(
        user=beneficiary3,
        stock=stock_1_offer1_venue2,
        date_created=datetime(2020, 3, 21, 22, 9, 12, 0),
        is_cancelled=False,
    )
    booking3_beneficiary1 = create_booking(
        user=beneficiary1,
        stock=stock_1_offer1_venue3,
        date_created=datetime(2020, 4, 12, 14, 31, 12, 0),
    )
    payment_booking3_beneficiary1 = create_payment(booking=booking3_beneficiary1, offerer=offerer,
                                                   status=TransactionStatus.PENDING)
    booking3_beneficiary2 = create_booking(
        user=beneficiary2,
        stock=stock_1_offer1_venue3,
        date_created=datetime(2020, 4, 12, 19, 31, 12, 0),
        is_used=True,
        date_used=datetime(2020, 4, 22, 17, 00, 10, 0),
        is_cancelled=False,
    )
    payment_booking3_beneficiary2 = create_payment(booking=booking3_beneficiary2, offerer=offerer,
                                                   status=TransactionStatus.SENT)
    booking3_beneficiary3 = create_booking(
        user=beneficiary3,
        stock=stock_1_offer1_venue3,
        date_created=datetime(2020, 4, 12, 22, 9, 12, 0),
    )
    payment_booking3_beneficiary3 = create_payment(booking=booking3_beneficiary3, offerer=offerer,
                                                   status=TransactionStatus.ERROR)
    booking4_beneficiary3 = create_booking(
        user=beneficiary3,
        stock=stock_1_offer1_venue2,
        date_created=datetime(2020, 3, 21, 22, 9, 12, 0),
        is_cancelled=False,
        is_used=False,
    )
    booking5_beneficiary3 = create_booking(
        user=beneficiary3,
        stock=stock_1_offer1_venue4,
        date_created=datetime(2020, 3, 21, 22, 9, 12, 0),
        is_cancelled=False,
    )

    booking6_beneficiary3 = create_booking(
        user=beneficiary3,
        stock=stock_1_offer2_venue2,
        date_created=datetime(2020, 3, 21, 22, 9, 12, 0),
        is_used=True,
        date_used=datetime(2020, 4, 22, 21, 9, 12, 0),
    )
    payment_booking6_beneficiary3 = create_payment(booking=booking6_beneficiary3, offerer=offerer,
                                                   status=TransactionStatus.SENT)

    booking7_beneficiary2 = create_booking(
        user=beneficiary2,
        stock=stock_1_offer2_venue2,
        date_created=datetime(2020, 4, 21, 22, 6, 12, 0),
        is_used=True,
        date_used=datetime(2020, 4, 22, 22, 9, 12, 0),
    )

    payment_booking7_beneficiary2 = create_payment(booking=booking7_beneficiary2, offerer=offerer,
                                                   status=TransactionStatus.RETRY)

    booking8_beneficiary1 = create_booking(
        user=beneficiary1,
        stock=stock_1_offer2_venue2,
        date_created=datetime(2020, 2, 21, 22, 6, 12, 0),
        is_used=True,
        date_used=datetime(2020, 4, 22, 23, 9, 12, 0),
    )

    payment_booking8_beneficiary1 = create_payment(booking=booking8_beneficiary1, offerer=offerer,
                                                   status=TransactionStatus.PENDING)

    repository.save(
        pro,
        booking1_beneficiary1, booking2_beneficiary1,
        booking1_beneficiary2, booking2_beneficiary2,
        booking1_beneficiary3, booking2_beneficiary3,
        booking5_beneficiary3,
        payment_booking3_beneficiary1, payment_booking3_beneficiary2,
        payment_booking3_beneficiary3, user_offerer, payment_booking6_beneficiary3,
        payment_booking7_beneficiary2, payment_booking8_beneficiary1,
        booking4_beneficiary3
    )

    bookings_to_cancel = [
        booking2_beneficiary2,
        booking1_beneficiary3,
        booking2_beneficiary3,
        booking3_beneficiary2,
        booking5_beneficiary3
    ]

    for booking in bookings_to_cancel:
        booking.isCancelled = True
    repository.save(*bookings_to_cancel)
