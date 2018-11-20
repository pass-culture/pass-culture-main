from datetime import datetime, timedelta
from decimal import Decimal
from io import BytesIO
from unittest.mock import patch
from uuid import UUID

import pytest
from freezegun import freeze_time
from lxml import etree
from lxml.etree import DocumentInvalid

from domain.payments import create_payment_for_booking, filter_out_already_paid_for_bookings, generate_transaction_file, \
    validate_transaction_file
from domain.reimbursement import BookingReimbursement, ReimbursementRules
from models import Offer, Venue, Booking
from models.payment import Payment
from models.payment_status import TransactionStatus
from utils.test_utils import create_booking, create_stock, create_user, create_offerer, create_payment, \
    create_stock_from_offer, create_thing_offer, create_venue

XML_NAMESPACE = {'ns': 'urn:iso:std:iso:20022:tech:xsd:pain.001.001.03'}
MESSAGE_ID = 'passCulture-SCT-20181015-114356'


@pytest.mark.standalone
def test_create_payment_for_booking_with_common_information():
    # given
    user = create_user()
    stock = create_stock(price=10, available=5)
    booking = create_booking(user, stock=stock, quantity=1)
    booking.stock.offer = Offer()
    booking.stock.offer.venue = Venue()
    booking.stock.offer.venue.managingOfferer = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert payment.booking == booking
    assert payment.amount == Decimal(10)
    assert payment.reimbursementRule == ReimbursementRules.PHYSICAL_OFFERS.value.description
    assert payment.comment == None
    assert payment.author == 'batch'


@pytest.mark.standalone
def test_create_payment_for_booking_when_iban_is_on_venue_should_take_payment_info_from_venue():
    # given
    user = create_user()
    stock = create_stock(price=10, available=5)
    booking = create_booking(user, stock=stock, quantity=1)
    booking.stock.offer = Offer()
    offerer = create_offerer(name='Test Offerer', iban='B135TGGEG532TG', bic='LAJR93')
    booking.stock.offer.venue = create_venue(
        offerer,
        siret='12345678912345',
        name='Test Venue',
        iban='KD98765RFGHZ788',
        bic='LOKIJU76'
    )
    booking.stock.offer.venue.managingOfferer = offerer
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert payment.iban == 'KD98765RFGHZ788'
    assert payment.bic == 'LOKIJU76'
    assert payment.recipient == 'Test Venue'


@pytest.mark.standalone
def test_create_payment_for_booking_when_iban_is_on_venue_should_take_venue_siret_has_registration_number_if_it_has_one():
    # given
    user = create_user()
    stock = create_stock(price=10, available=5)
    booking = create_booking(user, stock=stock, quantity=1)
    booking.stock.offer = Offer()
    offerer = create_offerer(name='Test Offerer', iban='B135TGGEG532TG', bic='LAJR93')
    booking.stock.offer.venue = create_venue(
        offerer,
        siret='12345678912345',
        name='Test Venue',
        iban='KD98765RFGHZ788',
        bic='LOKIJU76'
    )
    booking.stock.offer.venue.managingOfferer = offerer
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert payment.organisationRegistrationNumber == '12345678912345'


@pytest.mark.standalone
def test_create_payment_for_booking_when_iban_is_on_venue_should_take_offerer_siren_has_registration_number_if_venue_has_no_siret():
    # given
    user = create_user()
    stock = create_stock(price=10, available=5)
    booking = create_booking(user, stock=stock, quantity=1)
    booking.stock.offer = Offer()
    offerer = create_offerer(
        name='Test Offerer',
        siren='123456789',
        iban='B135TGGEG532TG',
        bic='LAJR93'
    )
    booking.stock.offer.venue = create_venue(
        offerer,
        siret=None,
        name='Test Venue',
        iban='KD98765RFGHZ788',
        bic='LOKIJU76'
    )
    booking.stock.offer.venue.managingOfferer = offerer
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert payment.organisationRegistrationNumber == '123456789'


@pytest.mark.standalone
def test_create_payment_for_booking_when_no_iban_on_venue_should_take_payment_info_from_offerer():
    # given
    user = create_user()
    stock = create_stock(price=10, available=5)
    booking = create_booking(user, stock=stock, quantity=1)
    booking.stock.offer = Offer()
    offerer = create_offerer(
        name='Test Offerer',
        siren='123456789',
        iban='CF13QSDFGH456789',
        bic='QSDFGH8Z555'
    )
    booking.stock.offer.venue = create_venue(offerer, name='Test Venue', iban=None, bic=None)
    booking.stock.offer.venue.managingOfferer = offerer
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert payment.iban == 'CF13QSDFGH456789'
    assert payment.bic == 'QSDFGH8Z555'
    assert payment.recipient == 'Test Offerer'
    assert payment.organisationRegistrationNumber == '123456789'


@pytest.mark.standalone
def test_create_payment_for_booking_with_not_processable_status_when_iban_is_missing_on_offerer():
    # given
    user = create_user()
    stock = create_stock(price=10, available=5)
    booking = create_booking(user, stock=stock, quantity=1)
    booking.stock.offer = Offer()
    booking.stock.offer.venue = Venue()
    booking.stock.offer.venue.managingOfferer = create_offerer(name='Test Offerer', iban=None, bic=None)
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert len(payment.statuses) == 1
    assert payment.statuses[0].status == TransactionStatus.NOT_PROCESSABLE
    assert payment.statuses[0].detail == 'IBAN et BIC manquants sur l\'offreur'


@pytest.mark.standalone
@freeze_time('2018-10-15 09:21:34')
def test_create_payment_for_booking_with_pending_status():
    # given
    one_second = timedelta(seconds=1)
    now = datetime.utcnow()
    user = create_user()
    stock = create_stock(price=10, available=5)
    booking = create_booking(user, stock=stock, quantity=1)
    booking.stock.offer = Offer()
    booking.stock.offer.venue = Venue()
    booking.stock.offer.venue.managingOfferer = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
    booking_reimbursement = BookingReimbursement(booking, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))

    # when
    payment = create_payment_for_booking(booking_reimbursement)

    # then
    assert len(payment.statuses) == 1
    assert payment.statuses[0].status == TransactionStatus.PENDING
    assert payment.statuses[0].detail is None
    assert payment.statuses[0].date == datetime(2018, 10, 15, 9, 21, 34)


@pytest.mark.standalone
def test_filter_out_already_paid_for_bookings():
    # Given
    booking_paid = Booking()
    booking_paid.payments = [Payment()]
    booking_reimbursement1 = BookingReimbursement(booking_paid, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))
    booking_not_paid = Booking()
    booking_reimbursement2 = BookingReimbursement(booking_not_paid, ReimbursementRules.PHYSICAL_OFFERS, Decimal(10))
    booking_reimbursements = [booking_reimbursement1, booking_reimbursement2]

    # When
    bookings_not_paid = filter_out_already_paid_for_bookings(booking_reimbursements)
    # Then
    assert len(bookings_not_paid) == 1
    assert not bookings_not_paid[0].booking.payments


@pytest.mark.standalone
def test_generate_transaction_file_has_custom_message_id_in_group_header(app):
    # Given
    offerer = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    user = create_user()
    venue = create_venue(offerer, idx=2)
    stock = create_stock_from_offer(create_thing_offer(venue))
    booking = create_booking(user, stock)
    offerer = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
    payment1 = create_payment(booking, offerer, Decimal(10), idx=3)
    payment2 = create_payment(booking, offerer, Decimal(20), idx=4)
    payments = [
        payment1,
        payment2
    ]

    # When
    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # Then
    assert find_node('//ns:GrpHdr/ns:MsgId', xml) == MESSAGE_ID, \
        'The message id should look like "passCulture-SCT-YYYYMMDD-HHMMSS"'


@pytest.mark.standalone
@freeze_time('2018-10-15 09:21:34')
def test_generate_transaction_file_has_creation_datetime_in_group_header(app):
    # Given
    offerer = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    user = create_user()
    venue = create_venue(offerer, idx=2)
    stock = create_stock_from_offer(create_thing_offer(venue))
    booking = create_booking(user, stock)
    offerer = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
    payment1 = create_payment(booking, offerer, Decimal(10), idx=3)
    payment2 = create_payment(booking, offerer, Decimal(20), idx=4)
    payments = [
        payment1,
        payment2
    ]

    # When
    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # Then
    assert find_node('//ns:GrpHdr/ns:CreDtTm', xml) == '2018-10-15T09:21:34', \
        'The creation datetime should look like YYYY-MM-DDTHH:MM:SS"'


@pytest.mark.standalone
def test_generate_transaction_file_has_initiating_party_in_group_header(app):
    # Given
    offerer = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    user = create_user()
    venue = create_venue(offerer, idx=2)
    stock = create_stock_from_offer(create_thing_offer(venue))
    booking = create_booking(user, stock)
    offerer = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
    payment1 = create_payment(booking, offerer, Decimal(10), idx=3)
    payment2 = create_payment(booking, offerer, Decimal(20), idx=4)
    payments = [
        payment1,
        payment2
    ]

    # When
    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # Then
    assert find_node('//ns:GrpHdr/ns:InitgPty/ns:Nm', xml) == 'pass Culture', \
        'The initiating party should be "pass Culture"'


@pytest.mark.standalone
def test_generate_transaction_file_has_control_sum_in_group_header(app):
    # Given
    user = create_user()
    offerer1 = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    offerer2 = create_offerer(iban=None, bic=None, idx=2)
    venue1 = create_venue(offerer1, idx=3)
    venue2 = create_venue(offerer2, idx=4)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    stock2 = create_stock_from_offer(create_thing_offer(venue2))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock2)

    payments = [
        create_payment(booking1, offerer1, Decimal(10), idx=7),
        create_payment(booking1, offerer1, Decimal(20), idx=8),
        create_payment(booking2, offerer2, Decimal(30), idx=9)
    ]

    # When
    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # Then
    assert find_node('//ns:GrpHdr/ns:CtrlSum', xml) == '30', \
        'The control sum should match the total amount of money to pay'


@pytest.mark.standalone
def test_generate_transaction_file_has_number_of_transactions_in_group_header(app):
    # Given
    offerer1 = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    offerer2 = create_offerer(iban='FR14WXCVBN123456', bic='WXCVBN7B444', idx=2)
    offerer3 = create_offerer(iban=None, bic=None, idx=3)
    user = create_user()
    venue1 = create_venue(offerer1, idx=4)
    venue2 = create_venue(offerer2, idx=5)
    venue3 = create_venue(offerer3, idx=6)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    stock2 = create_stock_from_offer(create_thing_offer(venue2))
    stock3 = create_stock_from_offer(create_thing_offer(venue3))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock2)
    booking3 = create_booking(user, stock3)

    payments = [
        create_payment(booking1, offerer1, Decimal(10), idx=7),
        create_payment(booking2, offerer2, Decimal(20), idx=8),
        create_payment(booking3, offerer3, Decimal(20), idx=9)
    ]

    # When
    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # Then
    assert find_node('//ns:GrpHdr/ns:NbOfTxs', xml) == '2', \
        'The number of transactions should match the distinct number of IBANs'


@pytest.mark.standalone
def test_generate_transaction_file_has_payment_info_id_in_payment_info(app):
    # Given
    offerer1 = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    user = create_user()
    venue1 = create_venue(offerer1, idx=4)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    booking1 = create_booking(user, stock1)

    payments = [create_payment(booking1, offerer1, Decimal(10), idx=7)]

    # When
    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # Then
    assert find_node('//ns:PmtInf/ns:PmtInfId', xml) == MESSAGE_ID, \
        'The payment info id should be the same as message id since we only send one payment per XML message'


@pytest.mark.standalone
def test_generate_transaction_file_has_number_of_transactions_in_payment_info(app):
    # Given
    offerer1 = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    offerer2 = create_offerer(iban='FR14WXCVBN123456', bic='WXCVBN7B444', idx=2)
    offerer3 = create_offerer(iban=None, bic=None, idx=3)
    user = create_user()
    venue1 = create_venue(offerer1, idx=4)
    venue2 = create_venue(offerer2, idx=5)
    venue3 = create_venue(offerer3, idx=6)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    stock2 = create_stock_from_offer(create_thing_offer(venue2))
    stock3 = create_stock_from_offer(create_thing_offer(venue3))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock2)
    booking3 = create_booking(user, stock3)

    payments = [
        create_payment(booking1, offerer1, Decimal(10), idx=7),
        create_payment(booking2, offerer2, Decimal(20), idx=8),
        create_payment(booking3, offerer3, Decimal(20), idx=9)
    ]

    # When
    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # Then
    assert find_node('//ns:PmtInf/ns:NbOfTxs', xml) == '2', \
        'The number of transactions should match the distinct number of IBANs'


@pytest.mark.standalone
def test_generate_transaction_file_has_control_sum_in_payment_info(app):
    # Given
    user = create_user()
    offerer1 = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    offerer2 = create_offerer(iban=None, bic=None, idx=2)
    venue1 = create_venue(offerer1, idx=3)
    venue2 = create_venue(offerer2, idx=4)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    stock2 = create_stock_from_offer(create_thing_offer(venue2))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock2)

    payments = [
        create_payment(booking1, offerer1, Decimal(10), idx=7),
        create_payment(booking1, offerer1, Decimal(20), idx=8),
        create_payment(booking2, offerer2, Decimal(30), idx=9)
    ]

    # When
    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # Then
    assert find_node('//ns:PmtInf/ns:CtrlSum', xml) == '30', \
        'The control sum should match the total amount of money to pay'


@pytest.mark.standalone
def test_generate_transaction_file_has_payment_method_in_payment_info(app):
    # Given
    offerer = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    user = create_user()
    venue = create_venue(offerer, idx=4)
    stock = create_stock_from_offer(create_thing_offer(venue))
    booking = create_booking(user, stock)

    payments = [create_payment(booking, offerer, Decimal(10), idx=7)]

    # When
    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # Then
    assert find_node('//ns:PmtInf/ns:PmtMtd', xml) == 'TRF', \
        'The payment method should be TRF because we want to transfer money'


@pytest.mark.standalone
def test_generate_transaction_file_has_service_level_in_payment_info(app):
    # Given
    offerer = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    user = create_user()
    venue = create_venue(offerer, idx=4)
    stock = create_stock_from_offer(create_thing_offer(venue))
    booking = create_booking(user, stock)

    payments = [create_payment(booking, offerer, Decimal(10), idx=7)]

    # When
    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # Then
    assert find_node('//ns:PmtInf/ns:PmtTpInf/ns:SvcLvl/ns:Cd', xml) == 'SEPA', \
        'The service level should be SEPA'


@pytest.mark.standalone
def test_generate_transaction_file_has_category_purpose_in_payment_info(app):
    # Given
    offerer = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    user = create_user()
    venue = create_venue(offerer, idx=4)
    stock = create_stock_from_offer(create_thing_offer(venue))
    booking = create_booking(user, stock)

    payments = [create_payment(booking, offerer, Decimal(10), idx=7)]

    # When
    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # Then
    assert find_node('//ns:PmtInf/ns:PmtTpInf/ns:CtgyPurp/ns:Cd', xml) == 'GOVT', \
        'The category purpose should be GOVT since we handle government subventions'


@pytest.mark.standalone
def test_generate_transaction_file_has_banque_de_france_bic_in_debtor_agent(app):
    # Given
    offerer = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    user = create_user()
    venue = create_venue(offerer, idx=4)
    stock = create_stock_from_offer(create_thing_offer(venue))
    booking = create_booking(user, stock)

    payments = [create_payment(booking, offerer, Decimal(10), idx=7)]

    # When
    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # Then
    assert find_node('//ns:PmtInf/ns:DbtrAgt/ns:FinInstnId/ns:BIC', xml) == 'AZERTY9Q666'


@pytest.mark.standalone
def test_generate_transaction_file_has_banque_de_france_iban_in_debtor_account(app):
    # Given
    offerer = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    user = create_user()
    venue = create_venue(offerer, idx=4)
    stock = create_stock_from_offer(create_thing_offer(venue))
    booking = create_booking(user, stock)

    payments = [create_payment(booking, offerer, Decimal(10), idx=7)]

    # When
    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # Then
    assert find_node('//ns:PmtInf/ns:DbtrAcct/ns:Id/ns:IBAN', xml) == 'BD12AZERTY123456'


@pytest.mark.standalone
def test_generate_transaction_file_has_debtor_name_in_payment_info(app):
    # Given
    offerer = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    user = create_user()
    venue = create_venue(offerer, idx=4)
    stock = create_stock_from_offer(create_thing_offer(venue))
    booking = create_booking(user, stock)

    payments = [create_payment(booking, offerer, Decimal(10), idx=7)]

    # When
    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # Then
    assert find_node('//ns:PmtInf/ns:Dbtr/ns:Nm', xml) == 'pass Culture', \
        'The name of the debtor should be "pass Culture"'


@pytest.mark.standalone
@freeze_time('2018-10-15 09:21:34')
def test_generate_transaction_file_has_requested_execution_datetime_in_payment_info(app):
    # Given
    offerer = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    user = create_user()
    venue = create_venue(offerer, idx=4)
    stock = create_stock_from_offer(create_thing_offer(venue))
    booking = create_booking(user, stock)

    payments = [create_payment(booking, offerer, Decimal(10), idx=7)]

    # When
    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # Then
    assert find_node('//ns:PmtInf/ns:ReqdExctnDt', xml) == '2018-10-22', \
        'The requested execution datetime should be in one week from now'


@pytest.mark.standalone
def test_generate_transaction_file_has_charge_bearer_in_payment_info(app):
    # Given
    offerer = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    user = create_user()
    venue = create_venue(offerer, idx=4)
    stock = create_stock_from_offer(create_thing_offer(venue))
    booking = create_booking(user, stock)

    payments = [create_payment(booking, offerer, Decimal(10), idx=7)]

    # When
    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # Then
    assert find_node('//ns:PmtInf/ns:ChrgBr', xml) == 'SLEV', \
        'The charge bearer should be SLEV as in "following service level"'


@pytest.mark.standalone
def test_generate_transaction_file_has_iban_in_credit_transfer_transaction_info(app):
    # Given
    offerer1 = create_offerer(name='first offerer', iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    offerer2 = create_offerer(name='second offerer', iban='FR14WXCVBN123456', bic='WXCVBN7B444', idx=2)
    offerer3 = create_offerer(name='third offerer', iban=None, bic=None, idx=3)
    user = create_user()
    venue1 = create_venue(offerer1, idx=4)
    venue2 = create_venue(offerer2, idx=5)
    venue3 = create_venue(offerer3, idx=6)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    stock2 = create_stock_from_offer(create_thing_offer(venue2))
    stock3 = create_stock_from_offer(create_thing_offer(venue3))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock2)
    booking3 = create_booking(user, stock3)

    payments = [
        create_payment(booking1, offerer1, Decimal(10), idx=7),
        create_payment(booking2, offerer2, Decimal(20), idx=8),
        create_payment(booking3, offerer3, Decimal(20), idx=9)
    ]

    # When
    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # Then
    assert find_all_nodes('//ns:PmtInf/ns:CdtTrfTxInf/ns:CdtrAcct/ns:Id/ns:IBAN', xml)[0] == 'CF13QSDFGH456789'
    assert find_all_nodes('//ns:PmtInf/ns:CdtTrfTxInf/ns:CdtrAcct/ns:Id/ns:IBAN', xml)[1] == 'FR14WXCVBN123456'


@pytest.mark.standalone
def test_generate_transaction_file_has_bic_in_credit_transfer_transaction_info(app):
    # Given
    offerer1 = create_offerer(name='first offerer', iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    offerer2 = create_offerer(name='second offerer', iban='FR14WXCVBN123456', bic='WXCVBN7B444', idx=2)
    offerer3 = create_offerer(name='third offerer', iban=None, bic=None, idx=3)
    user = create_user()
    venue1 = create_venue(offerer1, idx=4)
    venue2 = create_venue(offerer2, idx=5)
    venue3 = create_venue(offerer3, idx=6)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    stock2 = create_stock_from_offer(create_thing_offer(venue2))
    stock3 = create_stock_from_offer(create_thing_offer(venue3))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock2)
    booking3 = create_booking(user, stock3)

    payments = [
        create_payment(booking1, offerer1, Decimal(10), idx=7),
        create_payment(booking2, offerer2, Decimal(20), idx=8),
        create_payment(booking3, offerer3, Decimal(20), idx=9)
    ]

    # When
    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # Then
    assert find_all_nodes('//ns:PmtInf/ns:CdtTrfTxInf/ns:CdtrAgt/ns:FinInstnId/ns:BIC', xml)[0] == 'QSDFGH8Z555'
    assert find_all_nodes('//ns:PmtInf/ns:CdtTrfTxInf/ns:CdtrAgt/ns:FinInstnId/ns:BIC', xml)[1] == 'WXCVBN7B444'


@pytest.mark.standalone
def test_generate_transaction_file_has_amount_in_credit_transfer_transaction_info(app):
    # Given
    offerer1 = create_offerer(name='first offerer', iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    offerer2 = create_offerer(name='second offerer', iban='FR14WXCVBN123456', bic='WXCVBN7B444', idx=2)
    user = create_user()
    venue1 = create_venue(offerer1, idx=4)
    venue2 = create_venue(offerer2, idx=5)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    stock2 = create_stock_from_offer(create_thing_offer(venue1))
    stock3 = create_stock_from_offer(create_thing_offer(venue2))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock2)
    booking3 = create_booking(user, stock3)

    payments = [
        create_payment(booking1, offerer1, Decimal(10), idx=7),
        create_payment(booking2, offerer1, Decimal(20), idx=8),
        create_payment(booking3, offerer2, Decimal(20), idx=9)
    ]

    # When
    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # Then
    nodes_amount = find_all_nodes('//ns:PmtInf/ns:CdtTrfTxInf/ns:Amt/ns:InstdAmt', xml)
    assert nodes_amount[0] == '30'
    assert nodes_amount[1] == '20'


@pytest.mark.standalone
@patch('domain.payments.uuid.uuid4')
def test_generate_transaction_file_has_hexadecimal_uuids_as_end_to_end_ids_in_transaction_info(uuid4, app):
    # Given
    user = create_user()
    offerer1 = create_offerer(name='first offerer', iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    offerer2 = create_offerer(name='second offerer', iban='DE14QSDFGH456789', bic='MLKJHG8Z555', idx=1)
    venue1 = create_venue(offerer1, idx=4)
    venue2 = create_venue(offerer2, idx=4)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    stock2 = create_stock_from_offer(create_thing_offer(venue2))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock2)
    uuid1 = UUID(hex='abcd1234abcd1234abcd1234abcd1234', version=4)
    uuid2 = UUID(hex='cdef5678cdef5678cdef5678cdef5678', version=4)
    uuid4.side_effect = [uuid1, uuid2]

    payments = [
        create_payment(booking1, offerer1, Decimal(10), idx=7),
        create_payment(booking2, offerer2, Decimal(20), idx=7)
    ]

    # When
    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # Then
    nodes_id = find_all_nodes('//ns:PmtInf/ns:CdtTrfTxInf/ns:PmtId/ns:EndToEndId', xml)
    assert nodes_id[0] == uuid1.hex
    assert nodes_id[1] == uuid2.hex


@pytest.mark.standalone
def test_generate_transaction_file_has_initiating_party_id_in_payment_info(app):
    # Given
    offerer = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    user = create_user()
    venue = create_venue(offerer, idx=4)
    stock = create_stock_from_offer(create_thing_offer(venue))
    booking = create_booking(user, stock)

    payments = [create_payment(booking, offerer, Decimal(10), idx=7)]

    # When
    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # Then
    assert find_node('//ns:InitgPty/ns:Id/ns:OrgId/ns:Othr/ns:Id', xml) == '0000', \
        'The initiating party id should be 0000"'


@pytest.mark.standalone
def test_generate_transaction_file_has_initiating_party_in_group_header(app):
    # Given
    offerer = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    user = create_user()
    venue = create_venue(offerer, idx=2)
    stock = create_stock_from_offer(create_thing_offer(venue))
    booking = create_booking(user, stock)
    offerer = create_offerer(iban='CF13QSDFGH456789', bic='QSDFGH8Z555')
    payment1 = create_payment(booking, offerer, Decimal(10), idx=3)
    payment2 = create_payment(booking, offerer, Decimal(20), idx=4)
    payments = [
        payment1,
        payment2
    ]

    # When
    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # Then
    assert find_node('//ns:PmtInf/ns:CdtTrfTxInf/ns:UltmtDbtr/ns:Nm', xml) == 'pass Culture', \
        'The ultimate debitor name should be "pass Culture"'


@pytest.mark.standalone
def test_validate_transaction_file_does_not_raise_an_exception_when_generated_xml_is_valid(app):
    # given
    offerer1 = create_offerer(name='first offerer', iban='CF13QSDFGH456789', bic='QSDFGH8Z555', idx=1)
    offerer2 = create_offerer(name='second offerer', iban='FR14WXCVBN123456', bic='WXCVBN7B444', idx=2)
    user = create_user()
    venue1 = create_venue(offerer1, idx=4)
    venue2 = create_venue(offerer2, idx=5)
    stock1 = create_stock_from_offer(create_thing_offer(venue1))
    stock2 = create_stock_from_offer(create_thing_offer(venue1))
    stock3 = create_stock_from_offer(create_thing_offer(venue2))
    booking1 = create_booking(user, stock1)
    booking2 = create_booking(user, stock2)
    booking3 = create_booking(user, stock3)

    payments = [
        create_payment(booking1, offerer1, Decimal(10), idx=7),
        create_payment(booking2, offerer1, Decimal(20), idx=8),
        create_payment(booking3, offerer2, Decimal(20), idx=9)
    ]

    xml = generate_transaction_file(payments, 'BD12AZERTY123456', 'AZERTY9Q666', MESSAGE_ID, '0000')

    # when
    try:
        validate_transaction_file(xml)
    except Exception:
        assert False


@pytest.mark.standalone
def test_validate_transaction_file_raises_a_document_invalid_exception_with_specific_error_when_xml_is_invalid(app):
    # given
    transaction_file = '''
        <broken><xml></xml></broken>
    '''

    # when
    with pytest.raises(DocumentInvalid) as e:
        validate_transaction_file(transaction_file)

    # then
    assert str(e.value) == "Element 'broken': No matching global declaration available for the validation root., line 2"


def find_node(xpath, transaction_file):
    xml = BytesIO(transaction_file.encode())
    tree = etree.parse(xml, etree.XMLParser())
    node = tree.find(xpath, namespaces=XML_NAMESPACE)
    return node.text


def find_all_nodes(xpath, transaction_file):
    xml = BytesIO(transaction_file.encode())
    tree = etree.parse(xml, etree.XMLParser())
    nodes = tree.findall(xpath, namespaces=XML_NAMESPACE)
    return [node.text for node in nodes]
