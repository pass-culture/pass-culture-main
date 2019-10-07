from domain.reimbursement import ReimbursementDetails

from models.booking import Booking
from models.offer import Offer
from models.payment import Payment
from models.stock import Stock
from models.venue import Venue
from repository import booking_queries


def find_all_offerer_payments(offerer_id):
    return Payment.query.join(Booking) \
        .join(Stock) \
        .join(Offer) \
        .join(Venue) \
        .filter(Venue.managingOffererId == offerer_id) \
        .all()


def find_all_offerer_reimbursement_details(offerer_id):
    offerer_payments = find_all_offerer_payments(offerer_id)
    reimbursement_details = [
        ReimbursementDetails(
            offerer_payment,
            booking_queries.find_date_used(offerer_payment.booking)
        )
        for offerer_payment in offerer_payments
    ]

    return reimbursement_details
