from datetime import datetime
import hashlib
import logging
from typing import Iterable
from typing import Optional

from lxml.etree import DocumentInvalid
from sqlalchemy import orm
from sqlalchemy import sql

from pcapi.core.bookings.models import Booking
import pcapi.core.bookings.repository as booking_repository
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
import pcapi.core.payments.api as payments_api
from pcapi.domain.admin_emails import send_payment_details_email
from pcapi.domain.admin_emails import send_payment_message_email
from pcapi.domain.admin_emails import send_payments_report_emails
from pcapi.domain.admin_emails import send_wallet_balances_email
from pcapi.domain.payments import create_payment_for_booking
from pcapi.domain.payments import filter_out_already_paid_for_bookings
from pcapi.domain.payments import filter_out_bookings_without_cost
from pcapi.domain.payments import generate_message_file
from pcapi.domain.payments import generate_payment_details_csv
from pcapi.domain.payments import generate_wallet_balances_csv
from pcapi.domain.payments import validate_message_file_structure
from pcapi.domain.reimbursement import RULES
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


def get_venues_to_reimburse() -> Iterable[tuple[id, str]]:
    # FIXME (dbaty, 2021-06-02): this query is very slow (around 2
    # minutes). It's still better than iterating over all venues, but
    # we should look into it.
    booking_alias = orm.aliased(Booking)
    return [
        (venue.id, venue.publicName or venue.name)
        for venue in (
            Venue.query.distinct(Venue.id)
            .join(Offer)
            .join(Stock)
            .join(booking_alias)
            .outerjoin(Payment, sql.and_(booking_alias.id == Payment.bookingId))
            .filter(sql.and_(booking_alias.isUsed, ~booking_alias.isCancelled))
            .filter(Payment.id.is_(None))
            .with_entities(Venue.id, Venue.publicName, Venue.name)
        )
    ]


def generate_new_payments(batch_date: datetime) -> None:
    n_payments = 0
    logger.info("Fetching venues to reimburse")
    venues_to_reimburse = get_venues_to_reimburse()
    logger.info("Found %d venues to reimburse", len(venues_to_reimburse))
    for venue_id, venue_name in venues_to_reimburse:
        logger.info("[BATCH][PAYMENTS] Fetching bookings for venue: %s", venue_name, extra={"venue": venue_id})
        bookings = booking_repository.find_bookings_eligible_for_payment_for_venue(venue_id)
        logger.info("[BATCH][PAYMENTS] Calculating reimbursements for venue: %s", venue_name, extra={"venue": venue_id})
        reimbursements = find_all_booking_reimbursements(bookings, RULES)
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

    message_name = "passCulture-SCT-%s" % datetime.strftime(datetime.utcnow(), "%Y%m%d-%H%M%S")
    xml_file = generate_message_file(
        payment_query, pass_culture_iban, pass_culture_bic, message_name, pass_culture_remittance_code
    )

    logger.info("[BATCH][PAYMENTS] Payment message name : %s", message_name)

    try:
        validate_message_file_structure(xml_file)
    except DocumentInvalid as exception:
        # FIXME (dbaty, 2021-05-31): what is the point of updating the
        # status? If the XML file is not valid, we surely want to fix
        # the problem and run the payment script again with the same
        # batch date. This will be quicker and clearer if the script
        # does not have to change the status again.
        payments_api.bulk_create_payment_statuses(
            payment_query, TransactionStatus.NOT_PROCESSABLE, detail=str(exception)
        )
        raise

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
    logger.info("[BATCH][PAYMENTS] Recipients of email : %s", recipients)

    # FIXME (dbaty, 2021-05-31): what is the point of going further in
    # the payment script if we fail to send this e-mail? All payments
    # will be set to ERROR and send_payment_details will not send
    # anything. We should rather raise an error (and we should not
    # update the payment status to error) and let the operator re-run
    # the script with the same batch date.
    if send_payment_message_email(xml_file, checksum, recipients):
        status = TransactionStatus.UNDER_REVIEW
        detail = None
    else:
        status = TransactionStatus.ERROR
        detail = "Erreur d'envoi à MailJet"
    logger.info("[BATCH][PAYMENTS] Updating status of payments to %s", status)
    payments_api.bulk_create_payment_statuses(payment_query, status, detail)


def send_payments_details(payment_query, recipients: list[str]) -> None:
    if not recipients:
        raise Exception("[BATCH][PAYMENTS] Missing PASS_CULTURE_PAYMENTS_DETAILS_RECIPIENTS in environment variables")

    count = payment_query.count()
    if count == 0:
        logger.warning("[BATCH][PAYMENTS] Not sending payments details as all payments have an ERROR status")
        return

    csv = generate_payment_details_csv(payment_query)
    logger.info("[BATCH][PAYMENTS] Sending CSV details of %s payments", count)
    logger.info("[BATCH][PAYMENTS] Recipients of email : %s", recipients)
    try:
        send_payment_details_email(csv, recipients)
    except MailServiceException as exception:
        logger.exception("[BATCH][PAYMENTS] Error while sending payment details email to MailJet: %s", exception)


def send_wallet_balances(recipients: list[str]) -> None:
    if not recipients:
        raise Exception("[BATCH][PAYMENTS] Missing PASS_CULTURE_WALLET_BALANCES_RECIPIENTS in environment variables")

    balances = get_all_users_wallet_balances()
    csv = generate_wallet_balances_csv(balances)
    logger.info("[BATCH][PAYMENTS] Sending %s wallet balances", len(balances))
    logger.info("[BATCH][PAYMENTS] Recipients of email : %s", recipients)
    try:
        send_wallet_balances_email(csv, recipients)
    except MailServiceException as exception:
        logger.exception("[BATCH][PAYMENTS] Error while sending users wallet balances email to MailJet: %s", exception)


def send_payments_report(batch_date: datetime, recipients: list[str]) -> None:
    error_payments = payment_queries.join_for_payment_details(
        payment_queries.get_payments_by_status([TransactionStatus.ERROR], batch_date)
    )
    not_processable_payments = payment_queries.join_for_payment_details(
        payment_queries.get_payments_by_status([TransactionStatus.NOT_PROCESSABLE], batch_date)
    )

    logger.info(
        "[BATCH][PAYMENTS] Sending report on %d payments in ERROR and %d payments NOT_PROCESSABLE",
        error_payments.count(),
        not_processable_payments.count(),
    )
    logger.info("[BATCH][PAYMENTS] Recipients of email : %s", recipients)

    error_csv = generate_payment_details_csv(error_payments)
    not_processable_csv = generate_payment_details_csv(not_processable_payments)

    n_payments_by_status = payment_queries.get_payment_count_by_status(batch_date)

    try:
        send_payments_report_emails(not_processable_csv, error_csv, n_payments_by_status, recipients)
    except MailServiceException as exception:
        logger.exception("[BATCH][PAYMENTS] Error while sending payments reports to MailJet: %s", exception)


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
        payment.setStatus(TransactionStatus.RETRY)
    repository.save(*payments_to_retry)
