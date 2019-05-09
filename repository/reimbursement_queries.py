from models.reimbursement import Reimbursement
from repository.booking_queries import filter_bookings_by_offerer_id

def find_all_offerer_reimbursements(offerer_id):
    query = filter_bookings_by_offerer_id(offerer_id)

    reimbursements = [Reimbursement(b) for b in query.all()]

    return reimbursements
