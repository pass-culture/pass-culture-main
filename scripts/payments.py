from domain.payments import filter_out_already_paid_for_bookings, create_payment_for_booking
from domain.reimbursement import find_all_booking_reimbursement
from models import Offerer, PcObject
from repository.booking_queries import find_final_offerer_bookings


def do_generate_payments():
    offerers = Offerer.query.all()
    for offerer in offerers:
        final_offerer_bookings = find_final_offerer_bookings(offerer.id)
        booking_reimbursements = find_all_booking_reimbursement(final_offerer_bookings)
        booking_reimbursements_to_pay = filter_out_already_paid_for_bookings(booking_reimbursements)
        payments = list(map(create_payment_for_booking, booking_reimbursements_to_pay))
        PcObject.check_and_save(*payments)
