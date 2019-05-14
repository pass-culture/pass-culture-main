from domain.reimbursement import find_all_booking_reimbursements, \
                                 ReimbursementDetails
from repository.booking_queries import find_date_used, \
                                       find_final_offerer_bookings


def find_all_offerer_reimbursement_details(offerer_id):

    final_offerer_bookings = find_final_offerer_bookings(offerer_id)
    booking_reimbursements = find_all_booking_reimbursements(final_offerer_bookings)

    reimbursement_details = [
        ReimbursementDetails(booking_reimbursement, find_date_used(booking_reimbursement.booking))
        for booking_reimbursement in booking_reimbursements
        if booking_reimbursement.booking.payments
    ]

    return reimbursement_details
