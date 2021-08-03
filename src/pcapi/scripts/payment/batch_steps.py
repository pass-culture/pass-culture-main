from datetime import datetime
import hashlib
import logging
import pathlib
import tempfile
from typing import Iterable
from typing import Optional

from pcapi.core.bookings.models import Booking
import pcapi.core.bookings.repository as booking_repository
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
import pcapi.core.payments.api as payments_api
import pcapi.core.payments.models as payments_models
from pcapi.domain.admin_emails import send_payment_details_email
from pcapi.domain.admin_emails import send_payment_message_email
from pcapi.domain.admin_emails import send_payments_report_emails
from pcapi.domain.admin_emails import send_wallet_balances_email
from pcapi.domain.payments import create_payment_for_booking
from pcapi.domain.payments import filter_out_already_paid_for_bookings
from pcapi.domain.payments import filter_out_bookings_without_cost
from pcapi.domain.payments import generate_message_file
from pcapi.domain.payments import generate_payment_details_csv
from pcapi.domain.payments import generate_venues_csv
from pcapi.domain.payments import generate_wallet_balances_csv
from pcapi.domain.payments import make_transaction_label
from pcapi.domain.payments import validate_message_file_structure
from pcapi.domain.reimbursement import find_all_booking_reimbursements
from pcapi.models.db import db
from pcapi.models.payment import Payment
from pcapi.models.payment_message import PaymentMessage
from pcapi.models.payment_status import TransactionStatus
from pcapi.repository import payment_queries
from pcapi.repository import repository
from pcapi.repository.user_queries import get_all_users_wallet_balances
from pcapi.utils.mailing import MailServiceException


logger = logging.getLogger(__name__)


def include_error_and_retry_payments_in_batch(batch_date: datetime):
    statuses = [TransactionStatus.RETRY, TransactionStatus.ERROR]
    payments = payment_queries.get_payments_by_status(statuses)
    # We cannot directly call "update()" when "join()" has been called.
    ids = payments.with_entities(Payment.id)
    payments = db.session.query(Payment).filter(Payment.id.in_(ids))
    payments.update({"batchDate": batch_date}, synchronize_session=False)
    db.session.commit()


def get_venues_to_reimburse(cutoff_date: datetime) -> Iterable[tuple[id, str]]:
    # FIXME (dbaty, 2021-06-02): this query is very slow (around 2
    # minutes). It's still better than iterating over all venues, but
    # we should look into it.
    query = (
        Venue.query.distinct(Venue.id)
        .join(Offer)
        .join(Stock)
        .join(Booking)
        .filter(Booking.dateUsed < cutoff_date, ~Booking.isCancelled, Booking.amount > 0)
        .outerjoin(Payment, Booking.id == Payment.bookingId)
        .filter(Payment.id.is_(None))
        .with_entities(Venue.id, Venue.publicName, Venue.name)
    )
    return [(venue.id, venue.publicName or venue.name) for venue in query]


def generate_new_payments(cutoff_date: datetime, batch_date: datetime) -> None:
    n_payments = 0
    logger.info("Fetching venues to reimburse")
    venues_to_reimburse = get_venues_to_reimburse(cutoff_date)
    logger.info("Found %d venues to reimburse", len(venues_to_reimburse))
    custom_reimbursement_rules = payments_models.CustomReimbursementRule.query.all()
    n_payments = 0
    for venue_id, venue_name in venues_to_reimburse:
        logger.info("[BATCH][PAYMENTS] Fetching bookings for venue: %s", venue_name, extra={"venue": venue_id})
        bookings = booking_repository.find_bookings_eligible_for_payment_for_venue(venue_id, cutoff_date)
        logger.info("[BATCH][PAYMENTS] Calculating reimbursements for venue: %s", venue_name, extra={"venue": venue_id})
        reimbursements = find_all_booking_reimbursements(bookings, custom_reimbursement_rules)
        to_pay = filter_out_already_paid_for_bookings(filter_out_bookings_without_cost(reimbursements))
        if not to_pay:
            logger.info("[BATCH][PAYMENTS] No payments generated for venue: %s", venue_name, extra={"venue": venue_id})
            continue
        n_payments += len(to_pay)

        logger.info(
            "[BATCH][PAYMENTS] Creating Payment objects for venue: %s",
            venue_name,
            extra={"venue": venue_id, "payments": len(to_pay)},
        )
        payments = [create_payment_for_booking(reimbursement, batch_date) for reimbursement in to_pay]
        logger.info(
            "[BATCH][PAYMENTS] Inserting Payment objects for venue: %s",
            venue_name,
            extra={"venue": venue_id, "payments": len(to_pay)},
        )
        db.session.bulk_save_objects(payments)
        db.session.commit()

        logger.info(
            "[BATCH][PAYMENTS] Saved %i payments for venue: %s",
            len(payments),
            venue_name,
            extra={"venue": venue_id, "payments": len(payments)},
        )

    # Create all payment statuses. We get payments created above by
    # looking at their batch date.
    if n_payments:
        base_payment_query = Payment.query.filter_by(batchDate=batch_date)
        payments_api.bulk_create_payment_statuses(
            base_payment_query.filter(Payment.iban.isnot(None)),
            status=TransactionStatus.PENDING,
        )
        payments_api.bulk_create_payment_statuses(
            base_payment_query.filter(Payment.iban.is_(None)),
            status=TransactionStatus.NOT_PROCESSABLE,
            detail="IBAN et BIC manquants sur l'offreur",
        )
        db.session.commit()

    logger.info(
        "[BATCH][PAYMENTS] Generated %i payments for %i venues",
        n_payments,
        len(venues_to_reimburse),
    )


def send_transactions(
    payment_query,
    batch_date: datetime,
    pass_culture_iban: Optional[str],
    pass_culture_bic: Optional[str],
    pass_culture_remittance_code: Optional[str],
    recipients: list[str],
) -> None:
    if not pass_culture_iban or not pass_culture_bic or not pass_culture_remittance_code:
        raise Exception(
            "[BATCH][PAYMENTS] Missing PASS_CULTURE_IBAN[%s], PASS_CULTURE_BIC[%s] or "
            "PASS_CULTURE_REMITTANCE_CODE[%s] in environment variables"
            % (pass_culture_iban, pass_culture_bic, pass_culture_remittance_code)
        )

    logger.info("[BATCH][PAYMENTS] Generating venues file")
    venues_csv = generate_venues_csv(payment_query)

    logger.info("[BATCH][PAYMENTS] Generating XML file")

    message_name = "passCulture-SCT-%s" % datetime.strftime(datetime.utcnow(), "%Y%m%d-%H%M%S")
    xml_file = generate_message_file(
        payment_query, batch_date, pass_culture_iban, pass_culture_bic, message_name, pass_culture_remittance_code
    )

    logger.info("[BATCH][PAYMENTS] Payment message name : %s", message_name)

    # The following may raise a DocumentInvalid exception. This is
    # usually because the data is incorrect. In that case, let the
    # exception bubble up and stop the calling function so that we can
    # fix the data and run the function again.
    validate_message_file_structure(xml_file)

    checksum = hashlib.sha256(xml_file.encode("utf-8")).digest()
    message = PaymentMessage(name=message_name, checksum=checksum)
    db.session.add(message)
    db.session.commit()
    # We cannot directly call "update()" when "join()" has been called.
    # fmt: off
    (
        db.session.query(Payment)
        .filter(Payment.id.in_(payment_query.with_entities(Payment.id)))
        .update({"paymentMessageId": message.id}, synchronize_session=False)
    )
    # fmt: on
    db.session.commit()

    logger.info(
        "[BATCH][PAYMENTS] Sending file with message ID [%s] and checksum [%s]", message.name, message.checksum.hex()
    )
    logger.info("[BATCH][PAYMENTS] Recipients of email: %s", recipients)

    venues_csv_path = _save_file_on_disk("venues", venues_csv, "csv")
    xml_path = _save_file_on_disk("banque_de_france", xml_file, "xml")
    if not send_payment_message_email(xml_file, venues_csv, checksum, recipients):
        logger.info(
            "[BATCH][PAYMENTS] Could not send payment message email. Files have been stored at %s and %s",
            venues_csv_path,
            xml_path,
        )
    logger.info("[BATCH][PAYMENTS] Updating status of payments to UNDER_REVIEW")
    payments_api.bulk_create_payment_statuses(payment_query, TransactionStatus.UNDER_REVIEW, detail=None)


def send_payments_details(payment_query, recipients: list[str]) -> None:
    if not recipients:
        raise Exception("[BATCH][PAYMENTS] Missing PASS_CULTURE_PAYMENTS_DETAILS_RECIPIENTS in environment variables")

    count = payment_query.count()
    if count == 0:
        logger.warning("[BATCH][PAYMENTS] Not sending payments details as all payments have an ERROR status")
        return

    csv = generate_payment_details_csv(payment_query)
    logger.info("[BATCH][PAYMENTS] Sending CSV details of %s payments", count)
    logger.info("[BATCH][PAYMENTS] Recipients of email: %s", recipients)
    path = _save_file_on_disk("payments_details", csv, "csv")
    if not send_payment_details_email(csv, recipients):
        # FIXME (dbaty, 2021-06-16): we are likely to end up here
        # because the attachment is now over Mailjet's 15Mb limit.
        # This is an ugly quick fix.
        logger.info("[BATCH][PAYMENTS] Could not send payment details email. CSV file has been stored at %s", path)


def send_wallet_balances(recipients: list[str]) -> None:
    if not recipients:
        raise Exception("[BATCH][PAYMENTS] Missing PASS_CULTURE_WALLET_BALANCES_RECIPIENTS in environment variables")

    balances = get_all_users_wallet_balances()
    csv = generate_wallet_balances_csv(balances)
    logger.info("[BATCH][PAYMENTS] Sending %s wallet balances", len(balances))
    logger.info("[BATCH][PAYMENTS] Recipients of email: %s", recipients)
    try:
        send_wallet_balances_email(csv, recipients)
    except MailServiceException as exception:
        logger.exception("[BATCH][PAYMENTS] Error while sending users wallet balances email to MailJet: %s", exception)


def _save_file_on_disk(filename_prefix: str, content: str, extension: str) -> pathlib.Path:
    dt = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = pathlib.Path(tempfile.gettempdir()) / f"{filename_prefix}_{dt}.{extension}"
    path.write_text(content, encoding="utf-8")
    return path


def send_payments_report(batch_date: datetime, recipients: list[str]) -> None:
    not_processable_payments = payment_queries.join_for_payment_details(
        payment_queries.get_payments_by_status([TransactionStatus.NOT_PROCESSABLE], batch_date)
    )

    logger.info(
        "[BATCH][PAYMENTS] Sending report on %d payments NOT_PROCESSABLE",
        not_processable_payments.count(),
    )
    logger.info("[BATCH][PAYMENTS] Recipients of email: %s", recipients)

    not_processable_csv = generate_payment_details_csv(not_processable_payments)

    n_payments_by_status = payment_queries.get_payment_count_by_status(batch_date)

    path = _save_file_on_disk("payments_not_processable", not_processable_csv, "csv")
    if not send_payments_report_emails(not_processable_csv, n_payments_by_status, recipients):
        # FIXME (dbaty, 2021-06-16): we are likely to end up here
        # because the attachment is now over Mailjet's 15Mb limit.
        # This is an ugly quick fix.
        logger.info("[BATCH][PAYMENTS] Could not send payment reports email. CSV file has been stored at %s", path)


def set_not_processable_payments_with_bank_information_to_retry(batch_date: datetime) -> None:
    payments_to_retry = payment_queries.find_not_processable_with_bank_information()
    for payment in payments_to_retry:
        payment_bank_information_is_on_venue = (
            payment.booking.stock.offer.venue.bic and payment.booking.stock.offer.venue.bic
        )
        payment_bank_information_is_on_offerer = (
            payment.booking.stock.offer.venue.managingOfferer.bic
            and payment.booking.stock.offer.venue.managingOfferer.bic
        )
        if payment_bank_information_is_on_venue:
            payment.bic = payment.booking.stock.offer.venue.bic
            payment.iban = payment.booking.stock.offer.venue.iban
        elif payment_bank_information_is_on_offerer:
            payment.bic = payment.booking.stock.offer.venue.managingOfferer.bic
            payment.iban = payment.booking.stock.offer.venue.managingOfferer.iban
        payment.batchDate = batch_date
        payment.transactionLabel = make_transaction_label(datetime.utcnow())
        payment.setStatus(TransactionStatus.RETRY)
    repository.save(*payments_to_retry)
