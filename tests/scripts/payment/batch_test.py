import base64
import datetime
import io
import zipfile

import pytest
from sqlalchemy import func

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.categories import subcategories
import pcapi.core.mails.testing as mails_testing
import pcapi.core.offers.factories as offers_factories
import pcapi.core.payments.factories as payments_factories
import pcapi.core.users.models as users_models
from pcapi.models.payment import Payment
from pcapi.models.payment_status import PaymentStatus
from pcapi.models.payment_status import TransactionStatus
from pcapi.scripts.payment.batch import generate_and_send_payments


@pytest.mark.usefixtures("db_session")
def test_generate_and_send_payments():
    # Comments below indicate what `generate_and_send_payments()` will
    # do, no what the setup does.
    cutoff = datetime.datetime.now()
    before_cutoff = cutoff - datetime.timedelta(days=1)

    # 1 new payment + 1 retried payment for venue 1
    venue1 = offers_factories.VenueFactory(name="venue1")
    offers_factories.BankInformationFactory(venue=venue1)
    booking11 = bookings_factories.UsedBookingFactory(dateUsed=before_cutoff, stock__offer__venue=venue1)
    booking12 = bookings_factories.UsedBookingFactory(dateUsed=before_cutoff, stock__offer__venue=venue1)
    payment12 = payments_factories.PaymentFactory(booking=booking12)
    payments_factories.PaymentStatusFactory(payment=payment12, status=TransactionStatus.ERROR)
    payment13 = payments_factories.PaymentFactory(booking__stock__offer__venue=venue1)
    payments_factories.PaymentStatusFactory(payment=payment13, status=TransactionStatus.SENT)
    bookings_factories.BookingFactory(stock__offer__venue=venue1)

    # 1 new payment for venue 2
    venue2 = offers_factories.VenueFactory(name="venue2")
    offers_factories.BankInformationFactory(offerer=venue2.managingOfferer)
    booking2 = bookings_factories.UsedBookingFactory(dateUsed=before_cutoff, stock__offer__venue=venue2)

    # 0 payment for venue 3 (existing booking has already been reimbursed)
    payment3 = payments_factories.PaymentFactory()
    payments_factories.PaymentStatusFactory(payment=payment3, status=TransactionStatus.SENT)

    # 1 new payment (not processable) for venue 4 (no IBAN nor BIC)
    venue4 = offers_factories.VenueFactory()
    booking4 = bookings_factories.UsedBookingFactory(dateUsed=before_cutoff, stock__offer__venue=venue4)

    # 0 payment for venue 5 (booking is not used)
    venue5 = offers_factories.VenueFactory()
    bookings_factories.BookingFactory(stock__offer__venue=venue5)

    # 0 payment for venue 6 (booking has been used after cutoff)
    venue6 = offers_factories.VenueFactory(name="venue2")
    offers_factories.BankInformationFactory(offerer=venue6.managingOfferer)
    bookings_factories.UsedBookingFactory(dateUsed=cutoff, stock__offer__venue=venue2)

    # 1 new payment for digital venue
    virtual_venue = offers_factories.VirtualVenueFactory()
    offers_factories.BankInformationFactory(offerer=virtual_venue.managingOfferer)
    digital_reimbursable_offer = offers_factories.DigitalOfferFactory(
        venue=virtual_venue, subcategoryId=subcategories.CINE_VENTE_DISTANCE.id
    )
    digital_booking = bookings_factories.UsedBookingFactory(
        dateUsed=before_cutoff, stock__offer=digital_reimbursable_offer
    )

    last_payment_id = Payment.query.with_entities(func.max(Payment.id)).scalar()
    last_status_id = PaymentStatus.query.with_entities(func.max(PaymentStatus.id)).scalar()

    generate_and_send_payments(cutoff)

    # Check new payments and statuses
    new_payments = Payment.query.filter(Payment.id > last_payment_id).all()
    assert set(p.booking for p in new_payments) == {booking11, booking2, booking4, digital_booking}

    new_statuses = (
        PaymentStatus.query.filter(PaymentStatus.id > last_status_id)
        .join(PaymentStatus.payment)
        .order_by(Payment.bookingId)
    )
    assert set((s.payment.booking, s.status) for s in new_statuses) == {
        (booking11, TransactionStatus.PENDING),
        (booking11, TransactionStatus.UNDER_REVIEW),
        (booking12, TransactionStatus.UNDER_REVIEW),
        (booking2, TransactionStatus.PENDING),
        (booking2, TransactionStatus.UNDER_REVIEW),
        (booking4, TransactionStatus.NOT_PROCESSABLE),
        (digital_booking, TransactionStatus.PENDING),
        (digital_booking, TransactionStatus.UNDER_REVIEW),
    }

    # Check "transaction" e-mail
    email = mails_testing.outbox[0]
    subject = email.sent_data["Subject"].split("-")[0].strip()  # ignore date
    assert subject == "Virements XML pass Culture Pro"
    xml = base64.b64decode(email.sent_data["Attachments"][0]["Content"]).decode("utf-8")
    assert "<NbOfTxs>4</NbOfTxs>" in xml
    assert "<CtrlSum>40.00</CtrlSum>" in xml
    assert xml.count("<EndToEndId>") == 4

    # Check "report" e-mail
    email = mails_testing.outbox[1]
    subject = email.sent_data["Subject"].split("-")[0].strip()  # ignore date
    assert subject == "Récapitulatif des paiements pass Culture Pro"
    html = email.sent_data["Html-part"]
    assert "Nombre total de paiements : 5" in html
    assert "NOT_PROCESSABLE : 1" in html
    assert "UNDER_REVIEW : 4" in html

    # Check "details" e-mail
    email = mails_testing.outbox[2]
    subject = email.sent_data["Subject"].split("-")[0].strip()  # ignore date
    assert subject == "Détails des paiements pass Culture Pro"
    zip_data = base64.b64decode(email.sent_data["Attachments"][0]["Content"])
    with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
        csv = zf.open(zf.namelist()[0]).read().decode("utf-8")
    rows = csv.splitlines()
    assert len(rows) == 5  # header + 4 payments

    # Check "wallet balance" e-mail
    email = mails_testing.outbox[3]
    subject = email.sent_data["Subject"].split("-")[0].strip()  # ignore date
    assert subject == "Soldes des utilisateurs pass Culture"
    zip_data = base64.b64decode(email.sent_data["Attachments"][0]["Content"])
    with zipfile.ZipFile(io.BytesIO(zip_data)) as zf:
        csv = zf.open(zf.namelist()[0]).read().decode("utf-8")
    rows = csv.splitlines()
    assert len(rows) == users_models.User.query.count() + 1  # + header
