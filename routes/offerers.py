from flask import current_app as app, jsonify, request
from flask_login import current_user, login_required

from domain.admin_emails import maybe_send_offerer_validation_email
from domain.user_emails import send_ongoing_offerer_attachment_information_email_to_pro, \
    send_pro_user_waiting_for_validation_by_admin_email
from infrastructure.container import list_offerers_for_pro_user
from models import Offerer, RightsType, UserSQLEntity, UserOfferer, ApiErrors
from models.venue_sql_entity import create_digital_venue
from repository import repository
from repository.offerer_queries import find_by_siren
from routes.serialization import as_dict
from use_cases.list_offerers_for_pro_user import OfferersRequestParameters
from utils.human_ids import dehumanize
from utils.includes import OFFERER_INCLUDES
from utils.mailing import MailServiceException, send_raw_email
from utils.rest import ensure_current_user_has_rights, \
    expect_json_data, \
    load_or_404, \
    login_or_api_key_required
from validation.routes.offerers import check_valid_edition


def get_dict_offerer(offerer):
    offerer.append_user_has_access_attribute(current_user)

    return as_dict(offerer, includes=OFFERER_INCLUDES)


@app.route('/offerers', methods=['GET'])
@login_required
def list_offerers():
    keywords = request.args.get('keywords')
    only_validated_offerers = request.args.get('validated')

    is_filtered_by_offerer_status = only_validated_offerers is not None

    if is_filtered_by_offerer_status:
        if only_validated_offerers.lower() not in ('true', 'false'):
            errors = ApiErrors()
            errors.add_error('validated', 'Le paramètre \'validated\' doit être \'true\' ou \'false\'')
            raise errors

        only_validated_offerers = only_validated_offerers.lower() == 'true'

    offerers_request_parameters = OfferersRequestParameters(
        user_id=current_user.id,
        user_is_admin=current_user.isAdmin,
        is_filtered_by_offerer_status=is_filtered_by_offerer_status,
        only_validated_offerers=only_validated_offerers,
        keywords=keywords,
    )

    paginated_offerers = list_offerers_for_pro_user.execute(
        offerers_request_parameters=offerers_request_parameters
    )

    response = jsonify(paginated_offerers.offerers)
    response.headers['Total-Data-Count'] = paginated_offerers.total
    response.headers['Access-Control-Expose-Headers'] = 'Total-Data-Count'

    return response, 200


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
        repository.save(user_offerer)

        try:
            send_ongoing_offerer_attachment_information_email_to_pro(user_offerer, send_raw_email)
        except MailServiceException as mail_service_exception:
            app.logger.error('[send_ongoing_offerer_attachment_information_email_to_pro] '
                             'Mail service failure', mail_service_exception)
    else:
        offerer = Offerer()
        offerer.populate_from_dict(request.json)
        digital_venue = create_digital_venue(offerer)
        offerer.generate_validation_token()
        user_offerer = offerer.give_rights(current_user, RightsType.editor)
        repository.save(offerer, digital_venue, user_offerer)
        user = UserSQLEntity.query.filter_by(id=user_offerer.userId).first()

        _send_to_pro_offer_validation_in_progress_email(user, offerer)

    _send_to_pc_admin_offerer_to_validate_email(offerer, user_offerer)

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
    repository.save(offerer)
    return jsonify(get_dict_offerer(offerer)), 200


def _send_to_pro_offer_validation_in_progress_email(user: UserSQLEntity, offerer: Offerer) -> bool:
    try:
        send_pro_user_waiting_for_validation_by_admin_email(user, send_raw_email, offerer)
    except MailServiceException as mail_service_exception:
        app.logger.error('[send_pro_user_waiting_for_validation_by_admin_email] '
                         'Mail service failure', mail_service_exception)


def _send_to_pc_admin_offerer_to_validate_email(offerer: Offerer, user_offerer: UserOfferer) -> bool:
    try:
        maybe_send_offerer_validation_email(offerer, user_offerer, send_raw_email)
    except MailServiceException as mail_service_exception:
        app.logger.error('[maybe_send_offerer_validation_email] '
                         'Mail service failure', mail_service_exception)
