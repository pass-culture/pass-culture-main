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

    # QUESTION: je ne sais pas si c'est mieux de recuperer
    # tous les paiements pour faire le detail des remboursements
    offerer_payments = find_all_offerer_payments(offerer_id)
    reimbursement_details = [
        ReimbursementDetails(
            offerer_payment,
            find_date_used(offerer_payment.booking)
        )
        for offerer_payment in offerer_payments
    ]

    # Ou de revenir à la maniere de creer premierement les objets remboursements
    # à partir des bookings
    # final_offerer_bookings = find_final_offerer_bookings(offerer_id)
    # booking_reimbursements = find_all_booking_reimbursements(final_offerer_bookings)
    # booking_reimbursements_to_pay = filter_out_bookings_without_cost(booking_reimbursements)
    # reimbursement_details = [
    #    ReimbursementDetails(
    #        booking_reimbursement_to_pay,
    #        find_date_used(booking_reimbursement_to_pay.booking)
    #    )
    #    for booking_reimbursement_to_pay in booking_reimbursements_to_pay
    # ]

    return reimbursement_details
