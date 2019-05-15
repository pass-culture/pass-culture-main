from domain.payments import filter_out_bookings_without_cost
from domain.reimbursement import find_all_booking_reimbursements, \
                                 ReimbursementDetails

from models.booking import Booking
from models.offer import Offer
from models.payment import Payment
from models.stock import Stock
from models.venue import Venue
from repository.booking_queries import find_date_used, \
                                       find_final_offerer_bookings


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
            find_date_used(offerer_payment.booking)
        )
        for offerer_payment in offerer_payments
    ]

    return reimbursement_details
