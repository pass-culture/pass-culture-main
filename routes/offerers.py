from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from domain.admin_emails import maybe_send_offerer_validation_email
from models import Offerer, RightsType, Venue
from models.venue import create_digital_venue
from repository.offerer_queries import filter_offerers_with_keywords_string, \
    find_by_siren, query_filter_offerer_by_user, query_filter_offerer_is_validated, \
    query_filter_offerer_is_not_validated
from routes.serialization import as_dict
from utils.human_ids import dehumanize
from utils.includes import OFFERER_INCLUDES
from utils.mailing import MailServiceException, send_raw_email
from utils.rest import ensure_current_user_has_rights, \
    expect_json_data, \
    handle_rest_get_list, \
    load_or_404, \
    login_or_api_key_required
from validation.offerers import check_valid_edition, parse_boolean_param_validated


def get_dict_offerer(offerer):
    offerer.append_user_has_access_attribute(current_user)

    return as_dict(offerer, includes=OFFERER_INCLUDES)


@app.route('/offerers', methods=['GET'])
@login_required
def list_offerers():

    is_filtered_by_offerer_status = (request.args.get('validated') is not None)
    only_validated_offerers = parse_boolean_param_validated(request)

    query = Offerer.query

    if not current_user.isAdmin:
        query = query_filter_offerer_by_user(query)

    if is_filtered_by_offerer_status:
        if only_validated_offerers:
            query = query_filter_offerer_is_validated(query)
        else:
            query = query_filter_offerer_is_not_validated(query)

    keywords = request.args.get('keywords')
    if keywords is not None:
        query = filter_offerers_with_keywords_string(query.join(Venue), keywords)
        should_distinct_offerers=True
    else:
        should_distinct_offerers =False

    offerers = query.all()

    for offerer in offerers:
        offerer.append_user_has_access_attribute(current_user)


    return handle_rest_get_list(Offerer,
                                should_distinct=should_distinct_offerers,
                                query=query,
                                order_by=Offerer.name,
                                includes=OFFERER_INCLUDES,
                                paginate=10,
                                page=request.args.get('page'),
                                with_total_data_count=True)


@app.route('/offerers/<id>', methods=['GET'])
@login_required
def get_offerer(id):
    ensure_current_user_has_rights(RightsType.editor, dehumanize(id))
    offerer = load_or_404(Offerer, id)

    return jsonify(get_dict_offerer(offerer)), 200


@app.route('/offerers', methods=['POST'])
@login_or_api_key_required
@expect_json_data
def create_offerer():
    siren = request.json['siren']
    offerer = find_by_siren(siren)

    if offerer is not None:
        user_offerer = offerer.give_rights(current_user, RightsType.editor)
        user_offerer.generate_validation_token()
        Repository.save(user_offerer)

    else:
        offerer = Offerer()
        offerer.populate_from_dict(request.json)
        digital_venue = create_digital_venue(offerer)
        offerer.generate_validation_token()
        user_offerer = offerer.give_rights(current_user, RightsType.editor)
        Repository.save(offerer, digital_venue, user_offerer)

    try:
        maybe_send_offerer_validation_email(offerer, user_offerer, send_raw_email)
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
    offerer.populate_from_dict(data, skipped_keys=['validationToken'])
    Repository.save(offerer)
    return jsonify(get_dict_offerer(offerer)), 200
