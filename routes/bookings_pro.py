""" pro bookings """
from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from domain.reimbursement import find_all_booking_reimbursement
from models import Event, Thing, Venue
from models.user_offerer import RightsType
from repository.booking_queries import find_all_by_offerers
from utils.human_ids import dehumanize
from utils.includes import BOOKING_INCLUDES
from utils.rest import ensure_current_user_has_rights
from utils.search import get_search_filter

@app.route('/bookings/pro', methods=['GET'])
@login_required
def get_bookings_pro():

    #offerer_ids = ','.split(request.args.get('offererIds', ''))
    offerer_ids = [request.args.get('offererId')]
    for offerer_id in offerer_ids:
        ensure_current_user_has_rights(RightsType.editor, dehumanize(offerer_id))

    booking_query = find_all_by_offerers(offerer_ids)

    search = request.args.get('search')
    if search:
        booking_query = booking_query.outerjoin(Event)\
                                     .outerjoin(Thing)\
                                     .filter(get_search_filter([Event, Thing, Venue], search))

    order_by = request.args.get('order_by')
    if order_by:
        booking_query = booking_query.order_by(*order_by)

    page = request.args.get('page', 1)
    bookings = booking_query.paginate(int(page), per_page=10, error_out=False)\
                            .items

    bookings_reimbursements = find_all_booking_reimbursement(bookings)

    return jsonify([b.as_dict(includes=BOOKING_INCLUDES) for b in bookings_reimbursements]), 200
