from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from domain.admin_emails import maybe_send_offerer_validation_email
from domain.discard_pc_objects import invalidate_recommendations_if_deactivating_object
from domain.reimbursement import find_all_booking_reimbursement
from models import Offerer, PcObject, RightsType, Venue
from models.venue import create_digital_venue
from repository.booking_queries import find_offerer_bookings
from repository.offerer_queries import find_all_recommendations_for_offerer,\
                                       filter_offerers_with_keywords_string
from repository.user_offerer_queries import filter_query_where_user_is_user_offerer_and_is_not_validated, \
                                            filter_query_where_user_is_user_offerer_and_is_validated
from utils.human_ids import dehumanize
from utils.includes import PRO_BOOKING_INCLUDES, OFFERER_INCLUDES, NOT_VALIDATED_OFFERER_INCLUDES
from utils.mailing import MailServiceException, save_and_send
from utils.rest import ensure_current_user_has_rights, \
    expect_json_data, \
    handle_rest_get_list, \
    load_or_404, \
    login_or_api_key_required
from validation.offerers import check_valid_edition, parse_boolean_param_validated


def get_dict_offerer(offerer):
    return offerer._asdict(include=OFFERER_INCLUDES)


@app.route('/offerers', methods=['GET'])
@login_required
def list_offerers():
    only_validated_offerers = parse_boolean_param_validated(request)
    query = Offerer.query

    if not current_user.isAdmin:
        if only_validated_offerers:
            query = filter_query_where_user_is_user_offerer_and_is_validated(
                query,
                current_user
            )
        else:
            query = filter_query_where_user_is_user_offerer_and_is_not_validated(
                query,
                current_user
            )

    keywords = request.args.get('keywords')
    if keywords is not None:
        query = filter_offerers_with_keywords_string(query, keywords)

    return handle_rest_get_list(Offerer,
                                include=OFFERER_INCLUDES if (
                                        only_validated_offerers or current_user.isAdmin) else NOT_VALIDATED_OFFERER_INCLUDES,
                                order_by=Offerer.name,
                                page=request.args.get('page'),
                                paginate=10,
                                query=query)


@app.route('/offerers/<id>', methods=['GET'])
@login_required
def get_offerer(id):
    ensure_current_user_has_rights(RightsType.editor, dehumanize(id))
    offerer = load_or_404(Offerer, id)
    return jsonify(get_dict_offerer(offerer)), 200


@app.route('/offerers/<id>/bookings', methods=['GET'])
@login_required
def get_offerer_bookings(id):
    ensure_current_user_has_rights(RightsType.editor, dehumanize(id))
    order_by_key = request.args.get('order_by_column')
    order = request.args.get('order')
    order_by = _generate_orderby_criterium(order, order_by_key)
    bookings = find_offerer_bookings(
        dehumanize(id),
        search=request.args.get('search'),
        order_by=order_by,
        page=request.args.get('page', 1)
    )

    bookings_reimbursements = find_all_booking_reimbursement(bookings)

    return jsonify([b.as_dict(include=PRO_BOOKING_INCLUDES) for b in bookings_reimbursements]), 200


@app.route('/offerers', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def create_offerer():
    offerer = Offerer()
    offerer.populateFromDict(request.json)

    digital_venue = create_digital_venue(offerer)

    PcObject.check_and_save(offerer, digital_venue)

    if not current_user.isAdmin:
        offerer.generate_validation_token()
        user_offerer = offerer.give_rights(current_user,
                                           RightsType.admin)
        PcObject.check_and_save(offerer, user_offerer)
        try:
            maybe_send_offerer_validation_email(offerer, user_offerer, save_and_send)
        except MailServiceException as e:
            app.logger.error('Mail service failure', e)
    return jsonify(get_dict_offerer(offerer)), 201


@app.route('/offerers/<offererId>', methods=['PATCH'])
@login_or_api_key_required
@expect_json_data
def patch_offerer(offererId):
    ensure_current_user_has_rights(RightsType.admin, dehumanize(offererId))
    data = request.json
    check_valid_edition(data)
    offerer = Offerer.query.filter_by(id=dehumanize(offererId)).first()
    offerer.populateFromDict(data, skipped_keys=['validationToken'])
    recommendations = find_all_recommendations_for_offerer(offerer)
    invalidate_recommendations_if_deactivating_object(data, recommendations)
    PcObject.check_and_save(offerer)
    return jsonify(get_dict_offerer(offerer)), 200


def _generate_orderby_criterium(order, order_by_key):
    allowed_columns_for_order = {'booking_id': 'booking.id', 'venue_name': 'venue.name',
                                 'date': 'booking."dateCreated"', 'category': "COALESCE(thing.type, event.type)",
                                 'amount': 'booking.amount'}
    if order_by_key and order:
        column = allowed_columns_for_order[order_by_key]
        order_by = '{} {}'.format(column, order)
    else:
        order_by = None
    return order_by
